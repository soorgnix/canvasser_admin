from datetime import datetime, timedelta
from pickle import FALSE
import firebase_admin
from firebase_admin import firestore
from django.shortcuts import render
from .config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD
import psycopg2
from django.utils.safestring import mark_safe
from .utils.queryFieldsPointerUtils import CUSTOMERQUERY_CUSTOMER_ID, CUSTOMERQUERY_CUSTOMER_ADDRESS, CUSTOMERQUERY_CUSTOMER_CONTACT_PERSON, CUSTOMERQUERY_CUSTOMER_NAME, CUSTOMERQUERY_CUSTOMER_NO_TELP, CUSTOMERQUERY_CUSTOMER_DAERAH, CUSTOMERQUERY_MASTER_LIST_NAME, CUSTOMERQUERY_SALES_ORDER_ID, CUSTOMERQUERY_SALES_ORDER_DATE, CUSTOMERQUERY_SALES_ORDER_DELIVERY_DATE, CUSTOMERQUERY_SALES_ORDER_INVOICE_ID, CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE, CUSTOMERQUERY_SALES_ORDER_INVOICE_DUE_DATE, CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE_COMPLETED, CUSTOMERQUERY_SALES_ORDER_TOTAL, CUSTOMERQUERY_SALES_ORDER_STATUS_ID, CUSTOMERQUERY_PAYMENT_METHOD_NAME, CUSTOMERQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER, CUSTOMERQUERY_CUSTOMER_REFERENCE_CODE, CUSTOMERQUERY_APPROVAL_STATUS_NAME, CUSTOMERQUERY_TOTAL_PAYMENT_AMOUNT
from .utils.queryFieldsPointerUtils import ITEMQUERY_SALES_ORDER_DETAIL_SALES_ORDER_ID, ITEMQUERY_SALES_ORDER_DETAIL_ID, ITEMQUERY_ITEM_NAME, ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY, ITEMQUERY_SALES_ORDER_DETAIL_PRICE
from .utils.queryFieldsPointerUtils import DEBTQUERY_CUSTOMER_ID, DEBTQUERY_SALES_ORDER_ID, DEBTQUERY_SALES_ORDER_DATE, DEBTQUERY_SALES_ORDER_DELIVERY_DATE, DEBTQUERY_SALES_ORDER_INVOICE_ID, DEBTQUERY_SALES_ORDER_INVOICE_DATE, DEBTQUERY_SALES_ORDER_INVOICE_DUE_DATE, DEBTQUERY_SALES_ORDER_INVOICE_TOTAL, DEBTQUERY_PAYMENT_METHOD_NAME, DEBTQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER, DEBTQUERY_TOTAL_PAYMENT_AMOUNT, DEBTQUERY_DEBT
from .utils.queryFieldsPointerUtils import PAYMENTDETAILSQUERY_CUSTOMER_ID, PAYMENTDETAILSQUERY_SALES_ORDER_ID, PAYMENTDETAILSQUERY_SALES_ORDER_INVOICE_ID, PAYMENTDETAILSQUERY_SALES_ORDER_INVOICE_DATE, PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_DATE, PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_AMOUNT, PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_DESCRIPTION, PAYMENTDETAILSQUERY_TOTAL_PAYMENT_AMOUNT
from .utils.queryFieldsPointerUtils import INACTIVECUSTOMERQUERY_CUSTOMER_ID, INACTIVECUSTOMERQUERY_CUSTOMER_ADDRESS, INACTIVECUSTOMERQUERY_CUSTOMER_CONTACT_PERSON, INACTIVECUSTOMERQUERY_CUSTOMER_NAME, INACTIVECUSTOMERQUERY_CUSTOMER_NO_TELP, INACTIVECUSTOMERQUERY_CUSTOMER_DAERAH, INACTIVECUSTOMERQUERY_MASTER_LIST_NAME, INACTIVECUSTOMERQUERY_CUSTOMER_REFERENCE_CODE

from cnvadmin.dto.dto import customerDto

# Initialize Firestore database
db = firestore.client()

def save_selected_items(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        selected_date = request.POST.get('visitDate')
        selected_canvasser = request.POST.get('canvasser_id')

        locationDocs = db.collection('locations').stream()
        locationDataDict = {}

        for locationDoc in locationDocs:
            locationData = locationDoc.to_dict()
            customerCode = locationData.get('customerCode')
            if customerCode is not None:
                if customerCode not in locationDataDict:
                    locationDataDict[customerCode] = []
                    locationDataDict[customerCode].append(locationData)
        
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        # Open a cursor to perform database operations
        cur = conn.cursor()

        customerQuery = """
        WITH RankedSalesOrders AS (
            SELECT
                customer.id as customer_id,
                customer.address as customer_address, 
                customer.contact_person as customer_contact_person,
                customer.name as customer_name,
                customer.no_telp as customer_no_telp,
                customer.daerah as customer_daerah,
                master_list.name as master_list_name,
                sales_order.id as sales_order_id,
                sales_order.date as sales_order_date,
                sales_order.delivery_date as sales_order_delivery_date,
                sales_order_invoice.id as sales_order_invoice_id,
                sales_order_invoice.date as sales_order_invoice_date,
                sales_order_invoice.due_date as sales_order_invoice_due_date,
                sales_order_invoice.date_completed as sales_order_invoice_date_completed,
                COALESCE(sales_order_invoice.total,0) as sales_order_invoice_total,
                sales_order.status_id as sales_order_status_id,
                approval_status.name as approval_status_name,
                payment_method.name as payment_method_name, 
                sales_order_invoice.invoice_number as sales_order_invoice_invoice_number,
                customer.reference_code as customer_reference_code,
                SUM(sales_order_payment.amount) AS total_payment_amount,
                ROW_NUMBER() OVER (PARTITION BY customer.id ORDER BY sales_order_invoice.date DESC) AS rn
            FROM
                customer
                LEFT JOIN master_list on (customer.master_list_id = master_list.id)
                LEFT JOIN sales_order ON (customer.id = sales_order.customer_id)
                LEFT JOIN sales_order_invoice ON (sales_order.id = sales_order_invoice.sales_order_id)            
                LEFT JOIN approval_status ON (approval_status.id = sales_order.status_id)
                LEFT JOIN payment_method ON (sales_order_invoice.payment_method_id = payment_method.id)
                LEFT JOIN sales_order_invoice_payment_details ON (sales_order_invoice.id = sales_order_invoice_payment_details.sales_order_invoice_payment_details_id)
                LEFT JOIN sales_order_payment ON (sales_order_invoice_payment_details.sales_order_payment_id = sales_order_payment.id)
            WHERE sales_order.status_id != 3
                GROUP BY
                    customer.id,
                    customer.address, 
                    customer.contact_person,
                    customer.name,
                    customer.no_telp,
                    customer.daerah,
                    master_list.name,
                    sales_order.id,
                    sales_order.date,
                    sales_order.delivery_date,
                    sales_order_invoice.id,
                    sales_order_invoice.date,
                    sales_order_invoice.due_date,
                    sales_order_invoice.date_completed,
                    sales_order_invoice.total,
                    sales_order.status_id,
                    approval_status.name,
                    payment_method.name, 
                    sales_order_invoice.invoice_number,
                    customer.reference_code
        )
        SELECT
            customer_id,
            customer_address, 
            customer_contact_person,
            customer_name,
            customer_no_telp,
            customer_daerah,
            master_list_name,
            sales_order_id,
            sales_order_date,
            sales_order_delivery_date,
            sales_order_invoice_id,
            sales_order_invoice_date,
            sales_order_invoice_due_date,
            sales_order_invoice_date_completed,
            sales_order_invoice_total,
            sales_order_status_id,
            approval_status_name,
            payment_method_name, 
            sales_order_invoice_invoice_number,
            customer_reference_code,
            total_payment_amount
        FROM RankedSalesOrders
        WHERE rn = 1
        ORDER BY
            master_list_name, 
            customer_reference_code,
            customer_address,
            customer_name,
            sales_order_id
            """
        # Execute a query
        cur.execute(customerQuery)
        # Retrieve query results
        records = cur.fetchall()

        sales_order_ids = [record[CUSTOMERQUERY_SALES_ORDER_ID] for record in records]

        item_query = """
            SELECT 
                sales_order_detail.sales_order_id, 
                sales_order_detail.id, 
                item.name, 
                sales_order_detail.quantity, 
                sales_order_detail.price
            FROM sales_order_detail
            JOIN inventory ON sales_order_detail.inventory_id = inventory.id
            JOIN item ON inventory.item_id = item.id
            WHERE sales_order_detail.sales_order_id = ANY(%s)
            ORDER BY sales_order_detail.sales_order_id
            """

        # Execute the query and fetch the results
        cur.execute(item_query, (sales_order_ids,))
        itemRecords = cur.fetchall()

        debtQuery = """
            SELECT 
                customer.id,
                sales_order.id,
                sales_order.date,
                sales_order.delivery_date,
                sales_order_invoice.id,
                sales_order_invoice.date,
                sales_order_invoice.due_date,
                sales_order_invoice.total,
                payment_method.name,
                sales_order_invoice.invoice_number,
                COALESCE(SUM(sales_order_payment.amount), 0) AS total_payment_amount,
                (sales_order_invoice.total - COALESCE(SUM(sales_order_payment.amount), 0)) AS debt
            FROM
                sales_order
                JOIN customer ON (sales_order.customer_id = customer.id)
                JOIN sales_order_invoice ON (sales_order_invoice.sales_order_id = sales_order.id)
                LEFT JOIN payment_method ON (sales_order_invoice.payment_method_id = payment_method.id)
                LEFT JOIN sales_order_invoice_payment_details ON (sales_order_invoice.id = sales_order_invoice_payment_details.sales_order_invoice_payment_details_id)
                LEFT JOIN sales_order_payment ON (sales_order_invoice_payment_details.sales_order_payment_id = sales_order_payment.id)
            WHERE
                delivery_date IS NOT NULL
                AND date_completed IS NULL
            GROUP BY
                customer.id,
                sales_order.id,
                sales_order_invoice.id,
                payment_method.name,
                sales_order_invoice.invoice_number
            ORDER BY
                customer.name,
                sales_order.id;
            """
        cur.execute(debtQuery)
        debtRecords = cur.fetchall()

        paymentDetailsQuery = """
            SELECT 
                customer.id,
                sales_order.id,
                sales_order_invoice.id,
                sales_order_invoice.date,
                sales_order_payment.date,
                sales_order_payment.amount,
                sales_order_payment.description,
                SUM(sales_order_payment.amount) AS total_payment_amount
            FROM
                (SELECT 
                    customer.id AS customer_id,
                    sales_order.id AS order_id,
                    sales_order_invoice.id AS invoice_id,
                    ROW_NUMBER() OVER (PARTITION BY customer.id ORDER BY sales_order.date DESC) AS row_num
                FROM
                    sales_order
                    JOIN customer ON (sales_order.customer_id = customer.id)
                    JOIN sales_order_invoice ON (sales_order_invoice.sales_order_id = sales_order.id)
                WHERE
                    sales_order.delivery_date IS NOT NULL
                    ) AS subquery    
                JOIN customer ON (subquery.customer_id = customer.id)
                JOIN master_list on (customer.master_list_id = master_list.id)
                JOIN sales_order ON (subquery.order_id = sales_order.id)
                JOIN sales_order_invoice ON (subquery.invoice_id = sales_order_invoice.id)
                LEFT JOIN payment_method ON (sales_order_invoice.payment_method_id = payment_method.id)
                LEFT JOIN sales_order_invoice_payment_details ON (sales_order_invoice.id = sales_order_invoice_payment_details.sales_order_invoice_payment_details_id)
                LEFT JOIN sales_order_payment ON (sales_order_invoice_payment_details.sales_order_payment_id = sales_order_payment.id)
            WHERE
                subquery.row_num <= 1            
                AND amount is not NULL
            GROUP BY
                customer.id,
                sales_order.id,
                sales_order_invoice.id,
                payment_method.name,
                sales_order_payment.date,
                sales_order_payment.amount,
                sales_order_payment.description
            ORDER BY
                customer.id,
                sales_order.id;
        """
        cur.execute(paymentDetailsQuery)
        paymentDetailsRecords = cur.fetchall()

        inactiveCustomerQuery = """
            SELECT 
                customer.id,
                customer.address, 
                customer.contact_person,
                customer.name,
                customer.no_telp,
                customer.daerah,
                master_list.name,
                customer.reference_code
            FROM
                customer 
                LEFT JOIN master_list on (customer.master_list_id = master_list.id)
                LEFT JOIN sales_order on (customer.id = sales_order.customer_id)
            WHERE
                sales_order.id is null
            ORDER BY
                master_list.name, 
                customer.postal_code,
                customer.address,
                customer.name            
            """
        # Execute a query
        cur.execute(inactiveCustomerQuery)
        # Retrieve query results
        inactiveRecords = cur.fetchall()

        customers = []
        for row in records:
            customerCode = str(row[CUSTOMERQUERY_CUSTOMER_ID])
            location = ''
            
            if customerCode in locationDataDict:
                locationData = locationDataDict[customerCode]
                location = locationData[0].get('location')

            customer = customerDto(
            id = row[CUSTOMERQUERY_CUSTOMER_ID],
            address = row[CUSTOMERQUERY_CUSTOMER_ADDRESS],
            contact_person = row[CUSTOMERQUERY_CUSTOMER_CONTACT_PERSON],
            name = row[CUSTOMERQUERY_CUSTOMER_NAME],
            no_telp = row[CUSTOMERQUERY_CUSTOMER_NO_TELP],
            daerah = '',
            master_list=row[CUSTOMERQUERY_MASTER_LIST_NAME],          
            last_complete=None,
            last_duedate=None,
            last_invoice=None,
            last_count_days=None,          
            raport='No Raport',
            last_order='',
            raport_string='No Raport',
            last_delivery='',
            last_payment='',
            debt='',
            payment_details='',
            debt_sort_last=None,
            debt_sort_first=None,
            payment_details_sort_first=None,
            payment_details_sort_last=None,
            master_list_order=row[CUSTOMERQUERY_MASTER_LIST_NAME] + '-99999',
            location=location,
            status_id='No Status'
            )

            if row[CUSTOMERQUERY_CUSTOMER_DAERAH] is not None:
                customer.daerah = row[CUSTOMERQUERY_CUSTOMER_DAERAH]
            if row[CUSTOMERQUERY_SALES_ORDER_DELIVERY_DATE] is not None:
                customer.last_delivery = row[CUSTOMERQUERY_SALES_ORDER_DELIVERY_DATE].strftime('%Y-%m-%d')
            if row[CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE] is not None:
                customer.last_invoice = row[CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE].strftime('%Y-%m-%d')
            if row[CUSTOMERQUERY_SALES_ORDER_INVOICE_DUE_DATE] is not None:
                customer.last_duedate = row[CUSTOMERQUERY_SALES_ORDER_INVOICE_DUE_DATE].strftime('%Y-%m-%d')
            if row[CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE_COMPLETED] is not None:
                customer.last_complete = row[CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE_COMPLETED].strftime('%Y-%m-%d')
            if row[CUSTOMERQUERY_PAYMENT_METHOD_NAME] is not None:
                customer.last_payment = row[CUSTOMERQUERY_PAYMENT_METHOD_NAME]
            if row[CUSTOMERQUERY_CUSTOMER_REFERENCE_CODE] is not None:
                customer.master_list_order = row[CUSTOMERQUERY_MASTER_LIST_NAME] + '-' + row[CUSTOMERQUERY_CUSTOMER_REFERENCE_CODE]
            if row[CUSTOMERQUERY_APPROVAL_STATUS_NAME] is not None:
                customer.status_id = row[CUSTOMERQUERY_APPROVAL_STATUS_NAME]

            lastorderRecords = list(filter(lambda record: record[ITEMQUERY_SALES_ORDER_DETAIL_SALES_ORDER_ID] == row[CUSTOMERQUERY_SALES_ORDER_ID], itemRecords))
            lastorderString = '';
            if len(lastorderRecords) > 0:
                lastorderString = f"{row[CUSTOMERQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER]}\n\n"
                total = 0
                for record in lastorderRecords:
                    lastorderString += f"{record[ITEMQUERY_ITEM_NAME]} \n({'{:,.0f}'.format(record[ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY])} X {'{:,.0f}'.format(record[ITEMQUERY_SALES_ORDER_DETAIL_PRICE])} = {'{:,.0f}'.format(record[ITEMQUERY_SALES_ORDER_DETAIL_PRICE]*record[ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY])})\n\n"
                    total = total + (record[ITEMQUERY_SALES_ORDER_DETAIL_PRICE]*record[ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY])
                lastorderString += f"TOTAL {'{:,.0f}'.format(total)}\n\n"
                customer.last_order = mark_safe(lastorderString)


            oldDebt = False
            currentDebtRecords = list(filter(lambda record: record[DEBTQUERY_CUSTOMER_ID] == row[CUSTOMERQUERY_CUSTOMER_ID], debtRecords))
            sortedDebtRecords = sorted(currentDebtRecords, key=lambda record: record[DEBTQUERY_SALES_ORDER_ID])
            debtString = ''
            if len(sortedDebtRecords) > 0:
                oldDebt = True
                total = 0
                for record in sortedDebtRecords:
                    debtString += f"{record[DEBTQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER]} \n{record[DEBTQUERY_SALES_ORDER_DELIVERY_DATE].strftime('%Y-%m-%d')} \n ({'{:,.0f}'.format(record[DEBTQUERY_SALES_ORDER_INVOICE_TOTAL])} - {'{:,.0f}'.format(record[DEBTQUERY_TOTAL_PAYMENT_AMOUNT])} = {'{:,.0f}'.format(record[DEBTQUERY_DEBT])})\n\n"
                    total = total + (record[DEBTQUERY_DEBT])
                debtString += f"TOTAL {'{:,.0f}'.format(total)}\n\n"
                customer.debt_sort_first = sortedDebtRecords[0][DEBTQUERY_SALES_ORDER_DELIVERY_DATE]
                customer.debt_sort_last = sortedDebtRecords[len(sortedDebtRecords)-1][DEBTQUERY_SALES_ORDER_DELIVERY_DATE]
                customer.debt = mark_safe(debtString)
            
            currentPaymentDetailsRecords = list(filter(lambda record: record[PAYMENTDETAILSQUERY_CUSTOMER_ID] == row[CUSTOMERQUERY_CUSTOMER_ID], paymentDetailsRecords))
            sortedPaymentDetailsRecords = sorted(currentPaymentDetailsRecords, key=lambda record: record[PAYMENTDETAILSQUERY_SALES_ORDER_ID])
            paymentDetailsString = '';
            if len(sortedPaymentDetailsRecords) > 0:
                total = 0
                for record in sortedPaymentDetailsRecords:
                    paymentDetailsString += f"{record[PAYMENTDETAILSQUERY_TOTAL_PAYMENT_AMOUNT]} \n{record[PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_DATE].strftime('%Y-%m-%d')} \n ({'{:,.0f}'.format(record[PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_AMOUNT])})\n\n"
                    total = total + (record[7])
                paymentDetailsString += f"TOTAL {'{:,.0f}'.format(total)}\n\n"
                customer.payment_details_sort_first = sortedPaymentDetailsRecords[0][PAYMENTDETAILSQUERY_SALES_ORDER_INVOICE_DATE]
                customer.payment_details_sort_last = sortedPaymentDetailsRecords[len(sortedPaymentDetailsRecords)-1][PAYMENTDETAILSQUERY_SALES_ORDER_INVOICE_DATE]
                customer.payment_details = mark_safe(paymentDetailsString)

            dateComplete = None
            dateNunggak = None
            diffInDays = 0

            if customer.last_complete is not None:
                if (oldDebt):
                    customer.raport = "Menunggak Invoice Lama"
                    customer.raport_string = "Menunggak Invoice Lama"
                else:
                    dateComplete = row[CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE_COMPLETED]
                    dateDelivery = row[CUSTOMERQUERY_SALES_ORDER_DELIVERY_DATE].date()
                    diffDate = dateComplete - dateDelivery
                    diffInDays = diffDate.days
                    if diffInDays > 0 :
                        customer.last_count_days = diffInDays
                        customer.raport = "Terlambat"
                        customer.raport_string = "Terlambat " + str(diffInDays) + " hari"
                    elif diffInDays <= 0 :
                        customer.raport = "Lancar"  
                        customer.raport_string = "Lancar"
            elif customer.last_complete is None and customer.last_duedate is not None:
                if (row[CUSTOMERQUERY_SALES_ORDER_DELIVERY_DATE] is not None):
                    dateDelivery = row[CUSTOMERQUERY_SALES_ORDER_DELIVERY_DATE].date()
                    dateNunggak = (datetime.now().date() - dateDelivery).days
                    if (dateNunggak > 0):
                        customer.last_count_days = dateNunggak
                        customer.raport = "Menunggak"
                        customer.raport_string = "Menunggak " + str(dateNunggak) + " hari"
                    else:
                        customer.last_count_days = dateNunggak
                        customer.raport = "In Order"
                        customer.raport_string = "In Order"
                else:
                    customer.raport = "Waiting"  
                    customer.raport_string = "Waiting"

            customers.append(customer)

        for row in inactiveRecords:
            customerCode = str(row[INACTIVECUSTOMERQUERY_CUSTOMER_ID])
            location = ''
            
            if customerCode in locationDataDict:
                locationData = locationDataDict[customerCode]
                location = locationData[0].get('location')

            thirty_days_ago = datetime.now() - timedelta(days=30)
            formatted_date = thirty_days_ago.strftime('%Y-%m-%d')

            customer = customerDto(
            id = row[INACTIVECUSTOMERQUERY_CUSTOMER_ID],
            address = row[INACTIVECUSTOMERQUERY_CUSTOMER_ADDRESS],
            contact_person = row[INACTIVECUSTOMERQUERY_CUSTOMER_CONTACT_PERSON],
            name = row[INACTIVECUSTOMERQUERY_CUSTOMER_NAME],
            no_telp = row[INACTIVECUSTOMERQUERY_CUSTOMER_NO_TELP],
            daerah = '',
            master_list=row[INACTIVECUSTOMERQUERY_MASTER_LIST_NAME],          
            last_complete=formatted_date,
            last_duedate=formatted_date,
            last_invoice=formatted_date,
            last_count_days=formatted_date,      
            raport='',
            last_order='',
            raport_string='',
            last_delivery=formatted_date,
            last_payment='',
            debt='',
            payment_details='',
            debt_sort_last=None,
            debt_sort_first=None,
            payment_details_sort_first=None,
            payment_details_sort_last=None,
            master_list_order=row[INACTIVECUSTOMERQUERY_MASTER_LIST_NAME] + '-99999',
            location=location,
            status_id="No Status"
            )

            if row[INACTIVECUSTOMERQUERY_CUSTOMER_DAERAH] is not None:
                customer.daerah = row[INACTIVECUSTOMERQUERY_CUSTOMER_DAERAH]
            if row[INACTIVECUSTOMERQUERY_CUSTOMER_REFERENCE_CODE] is not None:
                customer.master_list_order = row[INACTIVECUSTOMERQUERY_MASTER_LIST_NAME] + '-' + row[INACTIVECUSTOMERQUERY_CUSTOMER_REFERENCE_CODE]

            customer.raport = "Lancar"  
            customer.raport_string = "Lancar"

            customers.append(customer)

        for customer_id in selected_items:  # Update the loop variable
            customerItem = list(filter(lambda x: x.id == int(customer_id), customers))
            doc_ref = db.collection('visits').document()
            
            if (len(customerItem)>0):
                if customerItem[0].contact_person != '' and customerItem[0].contact_person is not None:
                    pic = (customerItem[0].name or "") + " (" + (customerItem[0].contact_person or "") + ")"
                else:
                    pic = (customerItem[0].name or "")
                    
                doc_ref.set({
                    'customerCode': str(customerItem[0].id),
                    'address': customerItem[0].address,
                    'area': customerItem[0].master_list,
                    'daerah': customerItem[0].daerah,
                    'skipTime': '',
                    'checkInLocation': '',
                    'checkInTime': '',
                    'checkOutLocation': '',
                    'checkOutTime': '',
                    'date': datetime.strptime(selected_date, '%Y-%m-%d'),  # Use the converted timestamp
                    'isSkip': False,
                    'isCheckIn': False,
                    'isCheckOut': False,
                    'note': '',
                    'phone': customerItem[0].no_telp,  # Update to the appropriate attribute of the Customer model
                    'pic': pic,
                    'last_complete':customerItem[0].last_complete,
                    'last_duedate':customerItem[0].last_duedate,
                    'last_invoice':customerItem[0].last_invoice,
                    'raport':customerItem[0].raport_string,
                    'last_order':customerItem[0].last_order,
                    'last_delivery':customerItem[0].last_delivery,
                    'last_payment':customerItem[0].last_payment,
                    'location':customerItem[0].location,
                    'debt':customerItem[0].debt,
                    'payment_details':customerItem[0].payment_details,
                    'master_list_order':customerItem[0].master_list_order,
                    'user_id': selected_canvasser
                })
        return render(request, 'cnvadmin\success.html')
    else:
        return render(request, 'cnvadmin\checkbox.html')
    
def visit_edit_execute(request):
    if request.method == 'POST':
        visitId = request.POST.get('Id')
        selected_canvasser = request.POST.get('canvasser_id')
        masterLocation = request.POST.get('masterLocation')
        
        doc_ref = db.collection('visits').document(visitId)
        doc_ref.update({'user_id': selected_canvasser})

        if masterLocation != '':
            doc_ref.update({'location': masterLocation})
            customerCode = ''
            visitDoc = doc_ref.get()
            if visitDoc.exists:
                customerCode = visitDoc.get('customerCode')
            
            if customerCode != '':
                locationDocs = db.collection('locations').where('customerCode', '==', str(customerCode)).stream()
                for doc in locationDocs:
                    doc.reference.update({'location': masterLocation})

        return render(request, 'cnvadmin\success.html')
    else:
        return render(request, 'cnvadmin\checkbox.html')
    
def visit_delete_execute(request):
    if request.method == 'POST':
        visitId = request.POST.get('Id')
        
        doc_ref = db.collection('visits').document(visitId)
        doc_ref.delete()

        return render(request, 'cnvadmin\success.html')
    else:
        return render(request, 'cnvadmin\checkbox.html')

def newcustomer_edit_execute(request):
    if request.method == 'POST':
        customerId = request.POST.get('Id')
        added = request.POST.get('added')
        note = request.POST.get('note')             
        
        doc_ref = db.collection('customers').document(customerId)
        doc_ref.update({'added': added, 'note': note})

        return render(request, 'cnvadmin\success.html')
    else:
        return render(request, 'cnvadmin\checkbox.html')
    
def newcustomer_delete_execute(request):
    if request.method == 'POST':
        customerId = request.POST.get('Id')
        
        doc_ref = db.collection('customers').document(customerId)
        doc_ref.delete()

        return render(request, 'cnvadmin\success.html')
    else:
        return render(request, 'cnvadmin\checkbox.html')
    
def set_location(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        locations = db.collection('locations')

        for visit_id in selected_items:
            visit = db.collection('visits').document(visit_id).get()

            if visit.get('checkInLocation') != '' and visit.get('checkInLocation') is not None:
                location = locations.where("customerCode", "==", visit.get('customerCode')).get()
                checkInPos = visit.get('checkInLocation')              

                if not location and checkInPos != '-6.914744, 107.60981':
                    newLoc = db.collection('locations').document()
                    newLoc.set({
                        'customerCode': visit.get('customerCode'),
                        'location': visit.get('checkInLocation'),
                    })

        return render(request, 'cnvadmin/success.html')  # Use forward slashes
    else:
        return render(request, 'cnvadmin/checkbox.html')  # Use forward slashes

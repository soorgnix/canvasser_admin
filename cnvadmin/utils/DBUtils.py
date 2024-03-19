from cnvadmin.dto.CustomersDto import customerDto
from cnvadmin.utils.DBQueryIndex import DBQueryIndex
from ..config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD
import psycopg2
from django.utils.html import mark_safe
from datetime import datetime, timedelta

class DBUtils:
    def GetConn():
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        return conn
    
    def GetSqlQuery(request):
        query = ""
        match request:
            case "customer":
                query = """
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
                            delivery_sheet.date as delivery_date,
                            delivery_sheet.status_id as delivery_status,
                            employee.name as driver_name,
                            SUM(sales_order_payment.amount) AS total_payment_amount,
                            ROW_NUMBER() OVER (PARTITION BY customer.id ORDER BY sales_order_invoice.date DESC) AS rn
                        FROM
                            customer
                            LEFT JOIN master_list on (customer.master_list_id = master_list.id)
                            LEFT JOIN sales_order ON (customer.id = sales_order.customer_id)
                            LEFT JOIN delivery_sheet_detail ON (sales_order.id = delivery_sheet_detail.sales_order_id)
                            LEFT JOIN delivery_sheet_driver_detail on (delivery_sheet_detail.delivery_sheet_driver_detail_id = delivery_sheet_driver_detail.id) 
                            LEFT JOIN delivery_sheet on (delivery_sheet_driver_detail.delivery_sheet_id = delivery_sheet.id)
                            LEFT JOIN employee on (delivery_sheet_driver_detail.driver_id = employee.id)
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
                                customer.reference_code,
                                delivery_sheet.date,
                                delivery_sheet.status_id,
                                employee.name
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
                        delivery_date,
                        delivery_status,
                        driver_name,
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
            case "item":
                query = """
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
            case "debt":
                query = """
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
            case "paymentDetails":
                query = """
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
            case "inactiveCustomer":
                query = """
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
        return query
    
    def GetCustomerList(records, itemRecords, debtRecords, paymentDetailsRecords, inactiveRecords, locationDataDict):
        customers = []
        for row in records:
            customerCode = str(row[DBQueryIndex.CustomerQuery.customer_id])
            location = ''
            
            if customerCode in locationDataDict:
                locationData = locationDataDict[customerCode]
                location = locationData[0].get('location')

            customer = customerDto(
                id = row[DBQueryIndex.CustomerQuery.customer_id],
                address = row[DBQueryIndex.CustomerQuery.customer_address],
                contact_person = row[DBQueryIndex.CustomerQuery.customer_contact_person],
                name = row[DBQueryIndex.CustomerQuery.customer_name],
                no_telp = row[DBQueryIndex.CustomerQuery.customer_no_telp],
                daerah = '',
                master_list=row[DBQueryIndex.CustomerQuery.master_list_name],          
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
                master_list_order=row[DBQueryIndex.CustomerQuery.master_list_name] + '-99999',
                location=location,
                status_id='No Status',
                delivery_date = '',
                delivery_status = '',
                driver_name = ''
            )

            if row[DBQueryIndex.CustomerQuery.customer_daerah] is not None:
                customer.daerah = row[DBQueryIndex.CustomerQuery.customer_daerah]
            if row[DBQueryIndex.CustomerQuery.sales_order_delivery_date] is not None:
                customer.last_delivery = row[DBQueryIndex.CustomerQuery.sales_order_delivery_date].strftime('%Y-%m-%d')
            if row[DBQueryIndex.CustomerQuery.sales_order_invoice_date] is not None:
                customer.last_invoice = row[DBQueryIndex.CustomerQuery.sales_order_invoice_date].strftime('%Y-%m-%d')
            if row[DBQueryIndex.CustomerQuery.sales_order_invoice_due_date] is not None:
                customer.last_duedate = row[DBQueryIndex.CustomerQuery.sales_order_invoice_due_date].strftime('%Y-%m-%d')
            if row[DBQueryIndex.CustomerQuery.sales_order_invoice_date_completed] is not None:
                customer.last_complete = row[DBQueryIndex.CustomerQuery.sales_order_invoice_date_completed].strftime('%Y-%m-%d')
            if row[DBQueryIndex.CustomerQuery.payment_method_name] is not None:
                customer.last_payment = row[DBQueryIndex.CustomerQuery.payment_method_name]
            if row[DBQueryIndex.CustomerQuery.customer_reference_code] is not None:
                customer.master_list_order = row[DBQueryIndex.CustomerQuery.master_list_name] + '-' + row[DBQueryIndex.CustomerQuery.customer_reference_code]
            if row[DBQueryIndex.CustomerQuery.approval_status_name] is not None:
                customer.status_id = row[DBQueryIndex.CustomerQuery.approval_status_name]
            if row[DBQueryIndex.CustomerQuery.delivery_date] is not None:
                customer.delivery_date = row[DBQueryIndex.CustomerQuery.delivery_date].strftime('%Y-%m-%d')
            if row[DBQueryIndex.CustomerQuery.delivery_status] is not None:
                customer.delivery_status = row[DBQueryIndex.CustomerQuery.delivery_status]
            if row[DBQueryIndex.CustomerQuery.driver_name] is not None:
                customer.driver_name = row[DBQueryIndex.CustomerQuery.driver_name]

            lastorderRecords = list(filter(lambda record: record[DBQueryIndex.ItemQuery.sales_order_detail_sales_order_id] == row[DBQueryIndex.CustomerQuery.sales_order_id], itemRecords))
            lastorderString = '';
            if len(lastorderRecords) > 0:
                lastorderString = f"{row[DBQueryIndex.CustomerQuery.sales_order_invoice_invoice_number]}<br><br>"
                total = 0
                for record in lastorderRecords:
                    lastorderString += f"{record[DBQueryIndex.ItemQuery.item_name]} <br>({'{:,.0f}'.format(record[DBQueryIndex.ItemQuery.sales_order_detail_quantity])} X {'{:,.0f}'.format(record[DBQueryIndex.ItemQuery.sales_order_detail_price])} = {'{:,.0f}'.format(record[DBQueryIndex.ItemQuery.sales_order_detail_price]*record[DBQueryIndex.ItemQuery.sales_order_detail_quantity])})<br><br>"
                    total = total + (record[DBQueryIndex.ItemQuery.sales_order_detail_price]*record[DBQueryIndex.ItemQuery.sales_order_detail_quantity])
                lastorderString += f"TOTAL {'{:,.0f}'.format(total)}<br><br>"
                customer.last_order = mark_safe(lastorderString)


            oldDebt = False
            currentDebtRecords = list(filter(lambda record: record[DBQueryIndex.DebtQuery.customer_id] == row[DBQueryIndex.CustomerQuery.customer_id], debtRecords))
            sortedDebtRecords = sorted(currentDebtRecords, key=lambda record: record[DBQueryIndex.DebtQuery.sales_order_id])
            debtString = ''
            if len(sortedDebtRecords) > 0:
                oldDebt = True
                total = 0
                for record in sortedDebtRecords:
                    debtString += f"{record[DBQueryIndex.DebtQuery.sales_order_invoice_invoice_number]} <br>{record[DBQueryIndex.DebtQuery.sales_order_delivery_date].strftime('%Y-%m-%d')} <br> ({'{:,.0f}'.format(record[DBQueryIndex.DebtQuery.sales_order_invoice_total])} - {'{:,.0f}'.format(record[DBQueryIndex.DebtQuery.total_payment_amount])} = {'{:,.0f}'.format(record[DBQueryIndex.DebtQuery.debt])})<br><br>"
                    total = total + (record[DBQueryIndex.DebtQuery.debt])
                debtString += f"TOTAL {'{:,.0f}'.format(total)}<br><br>"
                customer.debt_sort_first = sortedDebtRecords[0][DBQueryIndex.DebtQuery.sales_order_delivery_date]
                customer.debt_sort_last = sortedDebtRecords[len(sortedDebtRecords)-1][DBQueryIndex.DebtQuery.sales_order_delivery_date]
                customer.debt = mark_safe(debtString)
            
            currentPaymentDetailsRecords = list(filter(lambda record: record[DBQueryIndex.PaymentDetailsQuery.customer_id] == row[DBQueryIndex.CustomerQuery.customer_id], paymentDetailsRecords))
            sortedPaymentDetailsRecords = sorted(currentPaymentDetailsRecords, key=lambda record: record[DBQueryIndex.PaymentDetailsQuery.sales_order_id])
            paymentDetailsString = '';
            if len(sortedPaymentDetailsRecords) > 0:
                total = 0
                for record in sortedPaymentDetailsRecords:
                    paymentDetailsString += f"{record[DBQueryIndex.PaymentDetailsQuery.total_payment_amount]} <br>{record[DBQueryIndex.PaymentDetailsQuery.sales_order_payment_date].strftime('%Y-%m-%d')} <br> ({'{:,.0f}'.format(record[DBQueryIndex.PaymentDetailsQuery.sales_order_payment_amount])})<br><br>"
                    total = total + (record[7])
                paymentDetailsString += f"TOTAL {'{:,.0f}'.format(total)}<br><br>"
                customer.payment_details_sort_first = sortedPaymentDetailsRecords[0][DBQueryIndex.PaymentDetailsQuery.sales_order_invoice_date]
                customer.payment_details_sort_last = sortedPaymentDetailsRecords[len(sortedPaymentDetailsRecords)-1][DBQueryIndex.PaymentDetailsQuery.sales_order_invoice_date]
                customer.payment_details = mark_safe(paymentDetailsString)
            
            dateComplete = None
            dateNunggak = None
            diffInDays = 0

            if customer.last_complete is not None:
                if (oldDebt):
                    customer.raport = "Menunggak Invoice Lama"
                    customer.raport_string = "Menunggak Invoice Lama"
                else:
                    dateComplete = row[DBQueryIndex.CustomerQuery.sales_order_invoice_date_completed]
                    dateDelivery = row[DBQueryIndex.CustomerQuery.sales_order_delivery_date].date()
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
                if (row[DBQueryIndex.CustomerQuery.sales_order_delivery_date] is not None):
                    dateDelivery = row[DBQueryIndex.CustomerQuery.sales_order_delivery_date].date()
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
            customerCode = str(row[DBQueryIndex.InactiveCustomerQuery.customer_id])
            location = ''
            
            if customerCode in locationDataDict:
                locationData = locationDataDict[customerCode]
                location = locationData[0].get('location')

            thirty_days_ago = datetime.now() - timedelta(days=30)
            formatted_date = thirty_days_ago.strftime('%Y-%m-%d')

            customer = customerDto(
                id = row[DBQueryIndex.InactiveCustomerQuery.customer_id],
                address = row[DBQueryIndex.InactiveCustomerQuery.customer_address],
                contact_person = row[DBQueryIndex.InactiveCustomerQuery.customer_contact_person],
                name = row[DBQueryIndex.InactiveCustomerQuery.customer_name],
                no_telp = row[DBQueryIndex.InactiveCustomerQuery.customer_no_telp],
                daerah = '',
                master_list=row[DBQueryIndex.InactiveCustomerQuery.master_list_name],
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
                master_list_order=row[DBQueryIndex.InactiveCustomerQuery.master_list_name] + '-99999',
                location=location,
                status_id="No Status",
                delivery_date = '',
                delivery_status = '',
                driver_name = ''
            )

            if row[DBQueryIndex.InactiveCustomerQuery.customer_daerah] is not None:
                customer.daerah = row[DBQueryIndex.InactiveCustomerQuery.customer_daerah]
            if row[DBQueryIndex.InactiveCustomerQuery.customer_reference_code] is not None:
                customer.master_list_order = row[DBQueryIndex.InactiveCustomerQuery.master_list_name] + '-' + row[DBQueryIndex.InactiveCustomerQuery.customer_reference_code]

            customer.raport = "Lancar"  
            customer.raport_string = "Lancar"

            customers.append(customer)

        return customers

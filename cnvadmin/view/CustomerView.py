from datetime import datetime, timedelta
from django.shortcuts import render
from firebase_admin import firestore
from django.utils.html import mark_safe
from django.template.defaultfilters import escapejs
from ..utils.queryFieldsPointerUtils import CUSTOMERQUERY_CUSTOMER_ID, CUSTOMERQUERY_CUSTOMER_ADDRESS, CUSTOMERQUERY_CUSTOMER_CONTACT_PERSON, CUSTOMERQUERY_CUSTOMER_NAME, CUSTOMERQUERY_CUSTOMER_NO_TELP, CUSTOMERQUERY_CUSTOMER_DAERAH, CUSTOMERQUERY_MASTER_LIST_NAME, CUSTOMERQUERY_SALES_ORDER_ID, CUSTOMERQUERY_SALES_ORDER_DATE, CUSTOMERQUERY_SALES_ORDER_DELIVERY_DATE, CUSTOMERQUERY_SALES_ORDER_INVOICE_ID, CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE, CUSTOMERQUERY_SALES_ORDER_INVOICE_DUE_DATE, CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE_COMPLETED, CUSTOMERQUERY_SALES_ORDER_TOTAL, CUSTOMERQUERY_SALES_ORDER_STATUS_ID, CUSTOMERQUERY_PAYMENT_METHOD_NAME, CUSTOMERQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER, CUSTOMERQUERY_CUSTOMER_REFERENCE_CODE, CUSTOMERQUERY_APPROVAL_STATUS_NAME, CUSTOMERQUERY_DELIVERY_DATE, CUSTOMERQUERY_DELIVERY_STATUS, CUSTOMERQUERY_DRIVER_NAME, CUSTOMERQUERY_TOTAL_PAYMENT_AMOUNT
from ..utils.queryFieldsPointerUtils import ITEMQUERY_SALES_ORDER_DETAIL_SALES_ORDER_ID, ITEMQUERY_SALES_ORDER_DETAIL_ID, ITEMQUERY_ITEM_NAME, ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY, ITEMQUERY_SALES_ORDER_DETAIL_PRICE
from ..utils.queryFieldsPointerUtils import DEBTQUERY_CUSTOMER_ID, DEBTQUERY_SALES_ORDER_ID, DEBTQUERY_SALES_ORDER_DATE, DEBTQUERY_SALES_ORDER_DELIVERY_DATE, DEBTQUERY_SALES_ORDER_INVOICE_ID, DEBTQUERY_SALES_ORDER_INVOICE_DATE, DEBTQUERY_SALES_ORDER_INVOICE_DUE_DATE, DEBTQUERY_SALES_ORDER_INVOICE_TOTAL, DEBTQUERY_PAYMENT_METHOD_NAME, DEBTQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER, DEBTQUERY_TOTAL_PAYMENT_AMOUNT, DEBTQUERY_DEBT
from ..utils.queryFieldsPointerUtils import PAYMENTDETAILSQUERY_CUSTOMER_ID, PAYMENTDETAILSQUERY_SALES_ORDER_ID, PAYMENTDETAILSQUERY_SALES_ORDER_INVOICE_ID, PAYMENTDETAILSQUERY_SALES_ORDER_INVOICE_DATE, PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_DATE, PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_AMOUNT, PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_DESCRIPTION, PAYMENTDETAILSQUERY_TOTAL_PAYMENT_AMOUNT
from ..utils.queryFieldsPointerUtils import INACTIVECUSTOMERQUERY_CUSTOMER_ID, INACTIVECUSTOMERQUERY_CUSTOMER_ADDRESS, INACTIVECUSTOMERQUERY_CUSTOMER_CONTACT_PERSON, INACTIVECUSTOMERQUERY_CUSTOMER_NAME, INACTIVECUSTOMERQUERY_CUSTOMER_NO_TELP, INACTIVECUSTOMERQUERY_CUSTOMER_DAERAH, INACTIVECUSTOMERQUERY_MASTER_LIST_NAME, INACTIVECUSTOMERQUERY_CUSTOMER_REFERENCE_CODE
import psycopg2
from ..config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD
from ..dto.CustomersDto import customerMapFilterDto, customerFilterDto, customerDto

# Create a Firestore client
db = firestore.client()

def customer_list(request):
    locationDataDict = _GetLocationDataDict()

    # Connect to your postgres DB
    conn = _GetConn()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    customerQuery = _GetSqlQuery("customer")
    cur.execute(customerQuery)
    records = cur.fetchall()

    sales_order_ids = [record[CUSTOMERQUERY_SALES_ORDER_ID] for record in records]

    itemQuery = _GetSqlQuery("item")
    cur.execute(itemQuery, (sales_order_ids,))
    itemRecords = cur.fetchall()

    debt_query = _GetSqlQuery("debt")
    cur.execute(debt_query)
    debtRecords = cur.fetchall()

    paymentDetailsQuery = _GetSqlQuery("paymentDetails")
    cur.execute(paymentDetailsQuery)
    paymentDetailsRecords = cur.fetchall()

    inactiveCustomerQuery = _GetSqlQuery("inactiveCustomer")
    cur.execute(inactiveCustomerQuery)
    inactiveRecords = cur.fetchall()

    customers = _GetCustomerList(records, itemRecords, debtRecords, paymentDetailsRecords, inactiveRecords, locationDataDict)

    #customerItems = customer.objects.all().order_by('address')
    customer_ids = [str(item.id) for item in customers]

    if request.method == 'POST':
        # Get the selected date from the form
        valueDate = request.POST.get('dateFilter')
    else:
        # Use the current date as the default
        valueDate = str(datetime.now().date())

    selected_date = datetime.strptime(valueDate, '%Y-%m-%d')       
    selected_range_date = selected_date + timedelta(days=1)

    usersDocs = db.collection('users').where('deletedFlag','==', False).stream()
    userList = set()
    for doc in usersDocs:
        userList.add(doc.get('email'))
    userList = sorted(userList, key=lambda x: x.lower())
    userList = set(userList)

    docs = db.collection('visits').where('date', '>=', selected_date).where('date', '<', selected_range_date).stream()

    firestore_customer_ids = set()
    for doc in docs:
        firestore_customer_ids.add(doc.get('customerCode'))

    missing_customer_ids = set(customer_ids) - firestore_customer_ids

    #missing_customer_items = customers.filter(id__in=missing_customer_ids)
    missing_customer_items = filter(lambda customer: str(customer.id) in missing_customer_ids, customers)            

    if request.method == 'POST':
        id_filter = request.POST.get('idFilter')
        if id_filter:
            missing_customer_items = filter(lambda x: int(id_filter) == x.id, missing_customer_items)

        name_filter = request.POST.get('nameFilter')
        if name_filter:
            missing_customer_items = filter(lambda x: name_filter in x.name.lower(), missing_customer_items)

        address_filter = request.POST.get('addressFilter')
        if address_filter:
            missing_customer_items = filter(lambda x: address_filter in x.address.lower(), missing_customer_items)

        daerah_filter = request.POST.get('daerahFilter')
        if daerah_filter:
            missing_customer_items = filter(lambda x: daerah_filter in x.daerah.lower(), missing_customer_items)

        pic_filter = request.POST.get('picFilter')
        if pic_filter:
            missing_customer_items = filter(lambda x: pic_filter in x.contact_person.lower(), missing_customer_items)

        phone_filter = request.POST.get('phoneFilter')
        if phone_filter:
            missing_customer_items = filter(lambda x: phone_filter in x.phone.lower(), missing_customer_items)

        master_list_filter = request.POST.get('masterlistFilter')
        if master_list_filter:
            missing_customer_items = filter(lambda x: master_list_filter in x.master_list.lower(), missing_customer_items)

        invoice_date_filter = request.POST.get('invoiceDateFilter')
        invoice_date_to_filter = request.POST.get('invoiceDateToFilter')
        if invoice_date_filter and invoice_date_to_filter:
            missing_customer_items = filter(lambda x: x.last_invoice >= invoice_date_filter and x.last_invoice <= invoice_date_to_filter, missing_customer_items)

        due_date_filter = request.POST.get('dueDateFilter')
        due_date_to_filter = request.POST.get('dueDateToFilter')
        if due_date_filter and due_date_to_filter:
            missing_customer_items = filter(lambda x: x.last_duedate >= due_date_filter and x.last_duedate <= due_date_to_filter, missing_customer_items)

        delivery_date_filter = request.POST.get('deliveryDateFilter')
        delivery_date_to_filter = request.POST.get('deliveryDateToFilter')
        if delivery_date_filter and delivery_date_to_filter:
            missing_customer_items = filter(lambda x: x.last_delivery >= delivery_date_filter and x.last_delivery <= delivery_date_to_filter, missing_customer_items)

        complete_date_filter = request.POST.get('completeDateFilter')
        complete_date_to_filter = request.POST.get('completeDateToFilter')
        if complete_date_filter and complete_date_to_filter:
            missing_customer_items = filter(lambda x: x.last_complete >= complete_date_filter and x.complete_invoice <= complete_date_to_filter, missing_customer_items)

        last_order_filter = request.POST.get('lastOrderFilter')
        if last_order_filter:
            missing_customer_items = filter(lambda x: last_order_filter in x.last_order.lower(), missing_customer_items)
        
        payment_type_filter = request.POST.get('paymentTypeFilter')
        if payment_type_filter:
            missing_customer_items = filter(lambda x: payment_type_filter in x.last_payment.lower(), missing_customer_items)

        payment_details_filter = request.POST.get('paymentDetailsFilter')
        if payment_details_filter:
            missing_customer_items = filter(lambda x: payment_details_filter in x.payment_details.lower(), missing_customer_items)

        debt_filter = request.POST.get('debtFilter')
        if debt_filter:
            missing_customer_items = filter(lambda x: debt_filter in x.debt.lower(), missing_customer_items)

        status_filter = request.POST.get('statusFilter')
        if status_filter:
            missing_customer_items = filter(lambda x: status_filter in x.status_id.lower(), missing_customer_items)

        raport_filter = request.POST.get('raportFilter')
        if raport_filter and raport_filter != 'all':
            missing_customer_items = filter(lambda x: raport_filter in x.raport.lower(), missing_customer_items)

        delivery_sheet_date_filter = request.POST.get('deliverySheetDateFilter')
        delivery_sheet_date_to_filter = request.POST.get('deliverySheetDateToFilter')
        if delivery_sheet_date_filter and delivery_sheet_date_to_filter:
            missing_customer_items = filter(lambda x: x.delivery_date >= delivery_sheet_date_filter and x.delivery_date <= delivery_sheet_date_to_filter, missing_customer_items)

        driver_name_filter = request.POST.get('driverNameFilter')
        if driver_name_filter:
            missing_customer_items = filter(lambda x: driver_name_filter in x.driver_name.lower(), missing_customer_items)

        sortType_filter = request.POST.get('sortTypeFilter')
        sort_filter = request.POST.get('sortFilter')
        if sort_filter == 'id':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.id)
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.id, reverse=True)
        elif sort_filter == 'name':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.name.lower() if x.name is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.name.lower() if x.name is not None else '', reverse=True)
        elif sort_filter == 'address':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.address.lower() if x.address is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.address.lower() if x.address is not None else '', reverse=True)
        elif sort_filter == 'daerah':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.daerah.lower() if x.daerah is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.daerah.lower() if x.daerah is not None else '', reverse=True)
        elif sort_filter == 'contact_person':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.contact_person.lower() if x.contact_person is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.contact_person.lower() if x.contact_person is not None else '', reverse=True)
        elif sort_filter == 'no_telp':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.no_telp.lower() if x.no_telp is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.no_telp.lower() if x.no_telp is not None else '', reverse=True)
        elif sort_filter == 'master_list':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.master_list_order.lower() if x.master_list is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.master_list_order.lower() if x.master_list is not None else '', reverse=True)
        elif sort_filter == 'invoice_date':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min)
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min, reverse=True)
        elif sort_filter == 'due_date':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min)
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min, reverse=True)
        elif sort_filter == 'delivery_date':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min)
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min, reverse=True)
        elif sort_filter == 'complete_date':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min)
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min, reverse=True)
        elif sort_filter == 'payment_type':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '', reverse=True)
        elif sort_filter == 'payment_details':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.payment_details_sort_first if x.payment_details_sort_first is not None else datetime.min)
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.payment_details_sort_last if x.payment_details_sort_last is not None else datetime.min, reverse=True)
        elif sort_filter == 'debt':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.debt_sort_first if x.debt_sort_first is not None else datetime.min)
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.debt_sort_last if x.debt_sort_last is not None else datetime.min, reverse=True)
        elif sort_filter == 'status':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.status_id.lower() if x.status_id is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.status_id.lower() if x.status_id is not None else '', reverse=True)
        elif sort_filter == 'raport':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: (x.raport.lower(), x.last_count_days) if x.raport is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: (x.raport.lower, x.last_count_days) if x.raport is not None else '', reverse=True)
        elif sort_filter == 'delivery_sheet_date':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.delivery_date if x.delivery_date is not None else datetime.min)
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.delivery_date if x.delivery_date is not None else datetime.min, reverse=True)
        elif sort_filter == 'driver_name':
            if sortType_filter == 'asc':
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.driver_name.lower() if x.driver_name is not None else '')
            else:
                missing_customer_items = sorted(missing_customer_items, key=lambda x: x.driver_name.lower() if x.driver_name is not None else '', reverse=True)



    if request.method == 'POST':
        customerFilter = customerFilterDto(
            dateFilter= valueDate,
            idFilter = request.POST.get('addressFilter'),
            nameFilter = request.POST.get('nameFilter'),
            addressFilter = request.POST.get('addressFilter'),
            picFilter = request.POST.get('picFilter'),
            phoneFilter = request.POST.get('phoneFilter'),
            daerahFilter = request.POST.get('daerahFilter'),
            masterlistFilter = request.POST.get('masterlistFilter'),
            invoiceDateFilter = request.POST.get('invoiceDateFilter'),
            invoiceDateToFilter = request.POST.get('invoiceDateToFilter'),
            dueDateFilter = request.POST.get('dueDateFilter'),
            dueDateToFilter = request.POST.get('dueDateToFilter'),
            deliveryDateFilter = request.POST.get('deliveryDateFilter'),
            deliveryDateToFilter = request.POST.get('deliveryDateToFilter'),
            completeDateFilter = request.POST.get('completeDateFilter'),
            completeDateToFilter = request.POST.get('completeDateToFilter'),
            lastOrderFilter = request.POST.get('lastOrderFilter'),
            paymentTypeFilter = request.POST.get('paymentTypeFilter'),
            paymentDetailsFilter = request.POST.get('paymentDetailsFilter'),
            debtFilter = request.POST.get('debtFilter'),
            statusFilter = request.POST.get('statusFilter'),
            raportFilter = request.POST.get('raportFilter'),
            deliverySheetDateFilter= request.POST.get('deliverySheetDateFilter'),
            deliverySheetDateToFilter= request.POST.get('deliverySheetDateToFilter'),
            driverNameFilter=request.POST.get('driverNameFilter'),
            sortTypeFilter = request.POST.get('sortTypeFilter'),
            sortFilter = request.POST.get('sortFilter'),
        )
    else:
          customerFilter = customerFilterDto(
            dateFilter=valueDate,
            idFilter = '',
            nameFilter = '',
            addressFilter = '',
            daerahFilter = '',
            picFilter = '',
            phoneFilter = '',
            masterlistFilter = '',
            invoiceDateFilter = '',
            invoiceDateToFilter = '',
            dueDateFilter = '',
            dueDateToFilter = '',
            deliveryDateFilter = '',
            deliveryDateToFilter = '',
            completeDateFilter = '',
            completeDateToFilter = '',
            lastOrderFilter = '',
            paymentTypeFilter = '',
            paymentDetailsFilter = '',
            debtFilter = '',
            statusFilter = '',
            deliverySheetDateFilter= '',
            deliverySheetDateToFilter= '',
            driverNameFilter='',
            raportFilter='all',
            sortTypeFilter='Asc',
            sortFilter='master_list'
        )      

    return render(request, 'cnvadmin/customer_list.html', {'customers': missing_customer_items, 'users': userList, 'customerFilter':customerFilter})

def customer_location_edit(request):
    customerId = request.GET.get('id')
    location=''
    locationDocs = db.collection('locations').where('customerCode', '==', str(customerId)).stream()
    for doc in locationDocs:
        location = doc.get('location')
        
    return render(request, 'cnvadmin/customer_location_edit.html', {'location': location, 'id': customerId})

def customer_location_edit_execute(request):
    if request.method == 'POST':
        customerId = request.POST.get('Id')
        masterLocation = request.POST.get('masterLocation')
        
        if customerId != '':
            locationDocs = db.collection('locations').where('customerCode', '==', str(customerId)).stream()

            docs_found = False
            
            for doc in locationDocs:
                docs_found = True
                doc.reference.update({'location': masterLocation})
            
            if not docs_found:
                newLoc = db.collection('locations').document()
                newLoc.set({
                    'customerCode': customerId,
                    'location': masterLocation
                })

        return render(request, 'cnvadmin\success.html')
    else:
        return render(request, 'cnvadmin\checkbox.html')

def customer_map(request):
    locationDataDict = _GetLocationDataDict()

    # Connect to your postgres DB
    conn = _GetConn()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    customerQuery = _GetSqlQuery("customer")
    cur.execute(customerQuery)
    records = cur.fetchall()

    sales_order_ids = [record[CUSTOMERQUERY_SALES_ORDER_ID] for record in records]

    itemQuery = _GetSqlQuery("item")
    cur.execute(itemQuery, (sales_order_ids,))
    itemRecords = cur.fetchall()

    debt_query = _GetSqlQuery("debt")
    cur.execute(debt_query)
    debtRecords = cur.fetchall()

    paymentDetailsQuery = _GetSqlQuery("paymentDetails")
    cur.execute(paymentDetailsQuery)
    paymentDetailsRecords = cur.fetchall()

    inactiveCustomerQuery = _GetSqlQuery("inactiveCustomer")
    cur.execute(inactiveCustomerQuery)
    inactiveRecords = cur.fetchall()

    customers = _GetCustomerList(records, itemRecords, debtRecords, paymentDetailsRecords, inactiveRecords, locationDataDict)

    if request.method == 'POST':
        id_filter = request.POST.get('idFilter')
        if id_filter:
            customers = filter(lambda x: int(id_filter) == x.id, customers)

        name_filter = request.POST.get('nameFilter')
        if name_filter:
            customers = filter(lambda x: name_filter in x.name.lower(), customers)

        address_filter = request.POST.get('addressFilter')
        if address_filter:
            customers = filter(lambda x: address_filter in x.address.lower(), customers)

        daerah_filter = request.POST.get('daerahFilter')
        if daerah_filter:
            customers = filter(lambda x: daerah_filter in x.daerah.lower(), customers)

        pic_filter = request.POST.get('picFilter')
        if pic_filter:
            customers = filter(lambda x: pic_filter in x.contact_person.lower(), customers)

        phone_filter = request.POST.get('phoneFilter')
        if phone_filter:
            customers = filter(lambda x: phone_filter in x.phone.lower(), customers)
                               
        master_list_filter = request.POST.get('masterlistFilter')
        if master_list_filter:
            customers = filter(lambda x: master_list_filter in x.master_list.lower(), customers)

        invoice_date_filter = request.POST.get('invoiceDateFilter')
        invoice_date_to_filter = request.POST.get('invoiceDateToFilter')
        if invoice_date_filter and invoice_date_to_filter:
            customers = filter(lambda x: x.last_invoice >= invoice_date_filter and x.last_invoice <= invoice_date_to_filter, customers)

        due_date_filter = request.POST.get('dueDateFilter')
        due_date_to_filter = request.POST.get('dueDateToFilter')
        if due_date_filter and due_date_to_filter:
            customers = filter(lambda x: x.last_duedate >= due_date_filter and x.last_duedate <= due_date_to_filter, customers)

        delivery_date_filter = request.POST.get('deliveryDateFilter')
        delivery_date_to_filter = request.POST.get('deliveryDateToFilter')
        if delivery_date_filter and delivery_date_to_filter:
            customers = filter(lambda x: x.last_delivery >= delivery_date_filter and x.last_delivery <= delivery_date_to_filter, customers)

        complete_date_filter = request.POST.get('completeDateFilter')
        complete_date_to_filter = request.POST.get('completeDateToFilter')
        if complete_date_filter and complete_date_to_filter:
            customers = filter(lambda x: x.last_complete >= complete_date_filter and x.complete_invoice <= complete_date_to_filter, customers)

        last_order_filter = request.POST.get('lastOrderFilter')
        if last_order_filter:
            customers = filter(lambda x: last_order_filter in x.last_order.lower(), customers)
        
        payment_type_filter = request.POST.get('paymentTypeFilter')
        if payment_type_filter:
            customers = filter(lambda x: payment_type_filter in x.last_payment.lower(), customers)

        payment_details_filter = request.POST.get('paymentDetailsFilter')
        if payment_details_filter:
            customers = filter(lambda x: payment_details_filter in x.payment_details.lower(), customers)

        debt_filter = request.POST.get('debtFilter')
        if debt_filter:
            customers = filter(lambda x: debt_filter in x.debt.lower(), customers)

        status_filter = request.POST.get('statusFilter')
        if status_filter:
            customers = filter(lambda x: status_filter in x.status_id.lower(), customers)

        raport_filter = request.POST.get('raportFilter')
        if raport_filter and raport_filter != 'all':
            customers = filter(lambda x: raport_filter in x.raport.lower(), customers)
        
        delivery_sheet_date_filter = request.POST.get('deliverySheetDateFilter')
        delivery_sheet_date_to_filter = request.POST.get('deliverySheetDateToFilter')
        if delivery_sheet_date_filter and delivery_sheet_date_to_filter:
            customers = filter(lambda x: x.delivery_date >= delivery_sheet_date_filter and x.delivery_date <= delivery_sheet_date_to_filter, customers)

        driver_name_filter = request.POST.get('driverNameFilter')
        if driver_name_filter:
            customers = filter(lambda x: driver_name_filter in x.driver_name.lower(), customers)


        customers = sorted(customers, key=lambda x: x.master_list_order.lower() if x.master_list is not None else '')

    if request.method == 'POST':
        customerMapFilter = customerMapFilterDto(
            idFilter = request.POST.get('addressFilter'),
            nameFilter = request.POST.get('nameFilter'),
            addressFilter = request.POST.get('addressFilter'),
            picFilter = request.POST.get('picFilter'),
            phoneFilter = request.POST.get('phoneFilter'),
            daerahFilter = request.POST.get('daerahFilter'),
            masterlistFilter = request.POST.get('masterlistFilter'),
            invoiceDateFilter = request.POST.get('invoiceDateFilter'),
            invoiceDateToFilter = request.POST.get('invoiceDateToFilter'),
            dueDateFilter = request.POST.get('dueDateFilter'),
            dueDateToFilter = request.POST.get('dueDateToFilter'),
            deliveryDateFilter = request.POST.get('deliveryDateFilter'),
            deliveryDateToFilter = request.POST.get('deliveryDateToFilter'),
            completeDateFilter = request.POST.get('completeDateFilter'),
            completeDateToFilter = request.POST.get('completeDateToFilter'),
            lastOrderFilter = request.POST.get('lastOrderFilter'),
            paymentTypeFilter = request.POST.get('paymentTypeFilter'),
            paymentDetailsFilter = request.POST.get('paymentDetailsFilter'),
            debtFilter = request.POST.get('debtFilter'),
            statusFilter = request.POST.get('statusFilter'),
            raportFilter = request.POST.get('raportFilter'),
            deliverySheetDateFilter= request.POST.get('deliverySheetDateFilter'),
            deliverySheetDateToFilter= request.POST.get('deliverySheetDateToFilter'),
            driverNameFilter=request.POST.get('driverNameFilter'),
        )
    else:
        customerMapFilter = customerMapFilterDto(
            idFilter = '',
            nameFilter = '',
            addressFilter = '',
            daerahFilter = '',
            picFilter = '',
            phoneFilter = '',
            masterlistFilter = '',
            invoiceDateFilter = '',
            invoiceDateToFilter = '',
            dueDateFilter = '',
            dueDateToFilter = '',
            deliveryDateFilter = '',
            deliveryDateToFilter = '',
            completeDateFilter = '',
            completeDateToFilter = '',
            lastOrderFilter = '',
            paymentTypeFilter = '',
            paymentDetailsFilter = '',
            debtFilter = '',
            statusFilter = '',
            deliverySheetDateFilter= '',
            deliverySheetDateToFilter= '',
            driverNameFilter='',
            raportFilter='all'  
        )      
    
    coordinates = []
    for customer in customers:
            if (customer.location != ''):
                location = customer.location.split(",")
                description = 'Master List: ' + customer.master_list_order + '<br>' + 'Name: ' + customer.name + '<br>' + 'Address: ' + customer.address  + '<br>' + 'Location: ' + customer.location  + '<br>'
                lat = location[0]
                lng = location[1]
                coordinates.append({
                    'description': escapejs(description),
                    'lat': lat,
                    'lng': lng
                })
           
    return render(request, 'cnvadmin/customer_map.html', {'coordinates': coordinates, 'customerMapFilter':customerMapFilter})



def _GetLocationDataDict():
    locationDocs = db.collection('locations').stream()
    locationDataDict = {}

    for locationDoc in locationDocs:
        locationData = locationDoc.to_dict()
        customerCode = locationData.get('customerCode')
        if customerCode is not None:
            if customerCode not in locationDataDict:
                locationDataDict[customerCode] = []
                locationDataDict[customerCode].append(locationData)
    return locationDataDict

def _GetConn():
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
    return conn

def _GetCustomerList(records, itemRecords, debtRecords, paymentDetailsRecords, inactiveRecords, locationDataDict):
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
          status_id='No Status',
          delivery_date = '',
          delivery_status = '',
          driver_name = ''
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
        if row[CUSTOMERQUERY_DELIVERY_DATE] is not None:
            customer.delivery_date = row[CUSTOMERQUERY_DELIVERY_DATE].strftime('%Y-%m-%d')
        if row[CUSTOMERQUERY_DELIVERY_STATUS] is not None:
            customer.delivery_status = row[CUSTOMERQUERY_DELIVERY_STATUS]
        if row[CUSTOMERQUERY_DRIVER_NAME] is not None:
            customer.driver_name = row[CUSTOMERQUERY_DRIVER_NAME]

        lastorderRecords = list(filter(lambda record: record[ITEMQUERY_SALES_ORDER_DETAIL_SALES_ORDER_ID] == row[CUSTOMERQUERY_SALES_ORDER_ID], itemRecords))
        lastorderString = '';
        if len(lastorderRecords) > 0:
            lastorderString = f"{row[CUSTOMERQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER]}<br><br>"
            total = 0
            for record in lastorderRecords:
                lastorderString += f"{record[ITEMQUERY_ITEM_NAME]} <br>({'{:,.0f}'.format(record[ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY])} X {'{:,.0f}'.format(record[ITEMQUERY_SALES_ORDER_DETAIL_PRICE])} = {'{:,.0f}'.format(record[ITEMQUERY_SALES_ORDER_DETAIL_PRICE]*record[ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY])})<br><br>"
                total = total + (record[ITEMQUERY_SALES_ORDER_DETAIL_PRICE]*record[ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY])
            lastorderString += f"TOTAL {'{:,.0f}'.format(total)}<br><br>"
            customer.last_order = mark_safe(lastorderString)


        oldDebt = False
        currentDebtRecords = list(filter(lambda record: record[DEBTQUERY_CUSTOMER_ID] == row[CUSTOMERQUERY_CUSTOMER_ID], debtRecords))
        sortedDebtRecords = sorted(currentDebtRecords, key=lambda record: record[DEBTQUERY_SALES_ORDER_ID])
        debtString = ''
        if len(sortedDebtRecords) > 0:
            oldDebt = True
            total = 0
            for record in sortedDebtRecords:
                debtString += f"{record[DEBTQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER]} <br>{record[DEBTQUERY_SALES_ORDER_DELIVERY_DATE].strftime('%Y-%m-%d')} <br> ({'{:,.0f}'.format(record[DEBTQUERY_SALES_ORDER_INVOICE_TOTAL])} - {'{:,.0f}'.format(record[DEBTQUERY_TOTAL_PAYMENT_AMOUNT])} = {'{:,.0f}'.format(record[DEBTQUERY_DEBT])})<br><br>"
                total = total + (record[DEBTQUERY_DEBT])
            debtString += f"TOTAL {'{:,.0f}'.format(total)}<br><br>"
            customer.debt_sort_first = sortedDebtRecords[0][DEBTQUERY_SALES_ORDER_DELIVERY_DATE]
            customer.debt_sort_last = sortedDebtRecords[len(sortedDebtRecords)-1][DEBTQUERY_SALES_ORDER_DELIVERY_DATE]
            customer.debt = mark_safe(debtString)
        
        currentPaymentDetailsRecords = list(filter(lambda record: record[PAYMENTDETAILSQUERY_CUSTOMER_ID] == row[CUSTOMERQUERY_CUSTOMER_ID], paymentDetailsRecords))
        sortedPaymentDetailsRecords = sorted(currentPaymentDetailsRecords, key=lambda record: record[PAYMENTDETAILSQUERY_SALES_ORDER_ID])
        paymentDetailsString = '';
        if len(sortedPaymentDetailsRecords) > 0:
            total = 0
            for record in sortedPaymentDetailsRecords:
                paymentDetailsString += f"{record[PAYMENTDETAILSQUERY_TOTAL_PAYMENT_AMOUNT]} <br>{record[PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_DATE].strftime('%Y-%m-%d')} <br> ({'{:,.0f}'.format(record[PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_AMOUNT])})<br><br>"
                total = total + (record[7])
            paymentDetailsString += f"TOTAL {'{:,.0f}'.format(total)}<br><br>"
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
            status_id="No Status",
            delivery_date = '',
            delivery_status = '',
            driver_name = ''
        )

        if row[INACTIVECUSTOMERQUERY_CUSTOMER_DAERAH] is not None:
            customer.daerah = row[INACTIVECUSTOMERQUERY_CUSTOMER_DAERAH]
        if row[INACTIVECUSTOMERQUERY_CUSTOMER_REFERENCE_CODE] is not None:
            customer.master_list_order = row[INACTIVECUSTOMERQUERY_MASTER_LIST_NAME] + '-' + row[INACTIVECUSTOMERQUERY_CUSTOMER_REFERENCE_CODE]

        customer.raport = "Lancar"  
        customer.raport_string = "Lancar"

        customers.append(customer)

    return customers

def _GetUserList():
    usersDocs = db.collection('users').where('deletedFlag','==', False).stream()
    userList = set()
    for doc in usersDocs:
        userList.add(doc.get('email'))
    userList = sorted(userList, key=lambda x: x.lower())
    userList = set(userList)
    return userList

def _GetSqlQuery(request):
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
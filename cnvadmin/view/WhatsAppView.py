from datetime import datetime, timedelta
import random
from django.shortcuts import render
from firebase_admin import firestore
from cnvadmin.utils.DBQueryIndex import DBQueryIndex
from cnvadmin.utils.DBUtils import DBUtils
from cnvadmin.utils.FireStoreUtils import FireStoreUtils
import pywhatkit
from ..dto.CustomersDto import customerFilterDto


def whatsapp_view(request):    
    firestoreUtils = FireStoreUtils()
    locationDataDict = firestoreUtils.GetLocationDataDict()

    conn = DBUtils.GetConn()    
    cur = conn.cursor()

    customerQuery = DBUtils.GetSqlQuery("customer")
    cur.execute(customerQuery)
    records = cur.fetchall()

    sales_order_ids = [record[DBQueryIndex.CustomerQuery.sales_order_id] for record in records]

    itemQuery = DBUtils.GetSqlQuery("item")
    cur.execute(itemQuery, (sales_order_ids,))
    itemRecords = cur.fetchall()

    debt_query = DBUtils.GetSqlQuery("debt")
    cur.execute(debt_query)
    debtRecords = cur.fetchall()

    paymentDetailsQuery = DBUtils.GetSqlQuery("paymentDetails")
    cur.execute(paymentDetailsQuery)
    paymentDetailsRecords = cur.fetchall()

    inactiveCustomerQuery = DBUtils.GetSqlQuery("inactiveCustomer")
    cur.execute(inactiveCustomerQuery)
    inactiveRecords = cur.fetchall()

    customers = DBUtils.GetCustomerList(records, itemRecords, debtRecords, paymentDetailsRecords, inactiveRecords, locationDataDict)
    customers = filter(lambda x: len(x.no_telp) > 8, customers)

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

    sortType_filter = request.POST.get('sortTypeFilter')
    sort_filter = request.POST.get('sortFilter')
    if sort_filter == 'id':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.id)
        else:
            customers = sorted(customers, key=lambda x: x.id, reverse=True)
    elif sort_filter == 'name':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.name.lower() if x.name is not None else '')
        else:
            customers = sorted(customers, key=lambda x: x.name.lower() if x.name is not None else '', reverse=True)
    elif sort_filter == 'address':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.address.lower() if x.address is not None else '')
        else:
            customers = sorted(customers, key=lambda x: x.address.lower() if x.address is not None else '', reverse=True)
    elif sort_filter == 'daerah':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.daerah.lower() if x.daerah is not None else '')
        else:
            customers = sorted(customers, key=lambda x: x.daerah.lower() if x.daerah is not None else '', reverse=True)
    elif sort_filter == 'contact_person':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.contact_person.lower() if x.contact_person is not None else '')
        else:
            customers = sorted(customers, key=lambda x: x.contact_person.lower() if x.contact_person is not None else '', reverse=True)
    elif sort_filter == 'no_telp':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.no_telp.lower() if x.no_telp is not None else '')
        else:
            customers = sorted(customers, key=lambda x: x.no_telp.lower() if x.no_telp is not None else '', reverse=True)
    elif sort_filter == 'master_list':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.master_list_order.lower() if x.master_list is not None else '')
        else:
            customers = sorted(customers, key=lambda x: x.master_list_order.lower() if x.master_list is not None else '', reverse=True)
    elif sort_filter == 'invoice_date':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min)
        else:
            customers = sorted(customers, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min, reverse=True)
    elif sort_filter == 'due_date':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min)
        else:
            customers = sorted(customers, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min, reverse=True)
    elif sort_filter == 'delivery_date':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min)
        else:
            customers = sorted(customers, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min, reverse=True)
    elif sort_filter == 'complete_date':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min)
        else:
            customers = sorted(customers, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min, reverse=True)
    elif sort_filter == 'payment_type':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '')
        else:
            customers = sorted(customers, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '', reverse=True)
    elif sort_filter == 'payment_details':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.payment_details_sort_first if x.payment_details_sort_first is not None else datetime.min)
        else:
            customers = sorted(customers, key=lambda x: x.payment_details_sort_last if x.payment_details_sort_last is not None else datetime.min, reverse=True)
    elif sort_filter == 'debt':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.debt_sort_first if x.debt_sort_first is not None else datetime.min)
        else:
            customers = sorted(customers, key=lambda x: x.debt_sort_last if x.debt_sort_last is not None else datetime.min, reverse=True)
    elif sort_filter == 'status':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.status_id.lower() if x.status_id is not None else '')
        else:
            customers = sorted(customers, key=lambda x: x.status_id.lower() if x.status_id is not None else '', reverse=True)
    elif sort_filter == 'raport':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: (x.raport.lower(), x.last_count_days) if x.raport is not None else '')
        else:
            customers = sorted(customers, key=lambda x: (x.raport.lower, x.last_count_days) if x.raport is not None else '', reverse=True)
    elif sort_filter == 'delivery_sheet_date':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.delivery_date if x.delivery_date is not None else datetime.min)
        else:
            customers = sorted(customers, key=lambda x: x.delivery_date if x.delivery_date is not None else datetime.min, reverse=True)
    elif sort_filter == 'driver_name':
        if sortType_filter == 'asc':
            customers = sorted(customers, key=lambda x: x.driver_name.lower() if x.driver_name is not None else '')
        else:
            customers = sorted(customers, key=lambda x: x.driver_name.lower() if x.driver_name is not None else '', reverse=True)

    if request.method == 'POST':
        customerFilter = customerFilterDto(
            dateFilter= str(datetime.now().date()),
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
            dateFilter=str(datetime.now().date()),
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

    categorySelect = 0
    if request.POST.get('categorySelect') is not None:
        categorySelect = int(request.POST.get('categorySelect'))

    match categorySelect:
        case 1:
            lastThirtyDay = datetime.now().date() - timedelta(days=30)
            lastThirtyDay_datetime = datetime.combine(lastThirtyDay, datetime.min.time())
            date_format = '%Y-%m-%d'
            
            customers = list(filter(lambda customer: customer.last_complete is not None and datetime.strptime(customer.last_complete, date_format) < lastThirtyDay_datetime, customers))
        case 2:
            customers = list(filter(lambda customer: customer.debt != '', customers))
        case 3:
            customers = list(filter(lambda customer: customer.delivery_date == customer.last_complete and customer.delivery_date != '', customers))
        case 4:
            customers = list(filter(lambda customer: customer.delivery_date != '' and customer.delivery_date != '' and customer.debt != '', customers))
        case _:
            customers = list(customers)


    db = firestore.client()                
    docs = db.collection('message').where('category', '==', categorySelect).stream()
    
    inputMessage = ''
    try:
        first_doc = next(docs)
    except StopIteration:
        first_doc = None

    if first_doc:
        inputMessage = first_doc.get('message')

    if customers:
        randomCustomer = random.choice(customers)
        currentMessage = inputMessage
        if randomCustomer.name is not None:
            currentMessage = currentMessage.replace('[name]', randomCustomer.name)
        if randomCustomer.id is not None:
            currentMessage = currentMessage.replace('[customerCode]', str(randomCustomer.id))
        if randomCustomer.address is not None:
            currentMessage = currentMessage.replace('[address]', randomCustomer.address)
        if randomCustomer.master_list is not None:
            currentMessage = currentMessage.replace('[area]', randomCustomer.master_list)
        if randomCustomer.daerah is not None:
            currentMessage = currentMessage.replace('[daerah]', randomCustomer.daerah)
        if randomCustomer.no_telp is not None:
            currentMessage = currentMessage.replace('[phone]', randomCustomer.no_telp)
        if randomCustomer.last_complete is not None:
            currentMessage = currentMessage.replace('[last_complete]', randomCustomer.last_complete)
        if randomCustomer.last_duedate is not None:
            currentMessage = currentMessage.replace('[last_duedate]', randomCustomer.last_duedate)
        if randomCustomer.last_invoice is not None:
            currentMessage = currentMessage.replace('[last_invoice]', randomCustomer.last_invoice)
        if randomCustomer.raport is not None:
            currentMessage = currentMessage.replace('[raport]', randomCustomer.raport.replace("<br>", "\n"))
        if randomCustomer.last_order is not None:
            currentMessage = currentMessage.replace('[last_order]', randomCustomer.last_order.replace("<br>", "\n"))
        if randomCustomer.last_delivery is not None:
            currentMessage = currentMessage.replace('[last_delivery]', randomCustomer.last_delivery)
        if randomCustomer.last_payment is not None:
            currentMessage = currentMessage.replace('[last_payment]', randomCustomer.last_payment.replace("<br>", "\n"))
        if randomCustomer.location is not None:
            currentMessage = currentMessage.replace('[location]', randomCustomer.location)
        if randomCustomer.debt is not None:
            currentMessage = currentMessage.replace('[debt]', randomCustomer.debt.replace("<br>", "\n"))
        if randomCustomer.payment_details is not None:
            currentMessage = currentMessage.replace('[payment_details]', randomCustomer.payment_details.replace("<br>", "\n"))
        if randomCustomer.master_list_order is not None:
            currentMessage = currentMessage.replace('[master_list_order]', randomCustomer.master_list_order)
    else:
        currentMessage = ''         

    return render(request, 'cnvadmin/whatsapp_list.html', {'customers': customers, 'categorySelect': categorySelect, 'categorySelected': categorySelect, 'customerFilter': customerFilter, 'inputMessage': inputMessage, 'currentMessage': currentMessage, 'inputMessageExecute': inputMessage, 'categorySelectExecute':categorySelect})

def whatsapp_set_message(request):
    if request.method == 'POST':
        firestoreUtils = FireStoreUtils()
        locationDataDict = firestoreUtils.GetLocationDataDict()

        conn = DBUtils.GetConn()    
        cur = conn.cursor()

        customerQuery = DBUtils.GetSqlQuery("customer")
        cur.execute(customerQuery)
        records = cur.fetchall()

        sales_order_ids = [record[DBQueryIndex.CustomerQuery.sales_order_id] for record in records]

        itemQuery = DBUtils.GetSqlQuery("item")
        cur.execute(itemQuery, (sales_order_ids,))
        itemRecords = cur.fetchall()

        debt_query = DBUtils.GetSqlQuery("debt")
        cur.execute(debt_query)
        debtRecords = cur.fetchall()

        paymentDetailsQuery = DBUtils.GetSqlQuery("paymentDetails")
        cur.execute(paymentDetailsQuery)
        paymentDetailsRecords = cur.fetchall()

        inactiveCustomerQuery = DBUtils.GetSqlQuery("inactiveCustomer")
        cur.execute(inactiveCustomerQuery)
        inactiveRecords = cur.fetchall()

        customers = DBUtils.GetCustomerList(records, itemRecords, debtRecords, paymentDetailsRecords, inactiveRecords, locationDataDict)
        customers = filter(lambda x: len(x.no_telp) > 8, customers)

        id_filter = request.POST.get('idFilter2')
        if id_filter:
            customers = filter(lambda x: int(id_filter) == x.id, customers)

        name_filter = request.POST.get('nameFilter2')
        if name_filter:
            customers = filter(lambda x: name_filter in x.name.lower(), customers)

        address_filter = request.POST.get('addressFilter2')
        if address_filter:
            customers = filter(lambda x: address_filter in x.address.lower(), customers)

        daerah_filter = request.POST.get('daerahFilter2')
        if daerah_filter:
            customers = filter(lambda x: daerah_filter in x.daerah.lower(), customers)

        pic_filter = request.POST.get('picFilter2')
        if pic_filter:
            customers = filter(lambda x: pic_filter in x.contact_person.lower(), customers)

        phone_filter = request.POST.get('phoneFilter2')
        if phone_filter:
            customers = filter(lambda x: phone_filter in x.phone.lower(), customers)

        master_list_filter = request.POST.get('masterlistFilter2')
        if master_list_filter:
            customers = filter(lambda x: master_list_filter in x.master_list.lower(), customers)

        invoice_date_filter = request.POST.get('invoiceDateFilter2')
        invoice_date_to_filter = request.POST.get('invoiceDateToFilter2')
        if invoice_date_filter and invoice_date_to_filter:
            customers = filter(lambda x: x.last_invoice >= invoice_date_filter and x.last_invoice <= invoice_date_to_filter, customers)

        due_date_filter = request.POST.get('dueDateFilter2')
        due_date_to_filter = request.POST.get('dueDateToFilter2')
        if due_date_filter and due_date_to_filter:
            customers = filter(lambda x: x.last_duedate >= due_date_filter and x.last_duedate <= due_date_to_filter, customers)

        delivery_date_filter = request.POST.get('deliveryDateFilter2')
        delivery_date_to_filter = request.POST.get('deliveryDateToFilter2')
        if delivery_date_filter and delivery_date_to_filter:
            customers = filter(lambda x: x.last_delivery >= delivery_date_filter and x.last_delivery <= delivery_date_to_filter, customers)

        complete_date_filter = request.POST.get('completeDateFilter2')
        complete_date_to_filter = request.POST.get('completeDateToFilter2')
        if complete_date_filter and complete_date_to_filter:
            customers = filter(lambda x: x.last_complete >= complete_date_filter and x.complete_invoice <= complete_date_to_filter, customers)

        last_order_filter = request.POST.get('lastOrderFilter2')
        if last_order_filter:
            customers = filter(lambda x: last_order_filter in x.last_order.lower(), customers)
        
        payment_type_filter = request.POST.get('paymentTypeFilter2')
        if payment_type_filter:
            customers = filter(lambda x: payment_type_filter in x.last_payment.lower(), customers)

        payment_details_filter = request.POST.get('paymentDetailsFilter2')
        if payment_details_filter:
            customers = filter(lambda x: payment_details_filter in x.payment_details.lower(), customers)

        debt_filter = request.POST.get('debtFilter2')
        if debt_filter:
            customers = filter(lambda x: debt_filter in x.debt.lower(), customers)

        status_filter = request.POST.get('statusFilter2')
        if status_filter:
            customers = filter(lambda x: status_filter in x.status_id.lower(), customers)

        raport_filter = request.POST.get('raportFilter2')
        if raport_filter and raport_filter != 'all':
            customers = filter(lambda x: raport_filter in x.raport.lower(), customers)

        delivery_sheet_date_filter = request.POST.get('deliverySheetDateFilter2')
        delivery_sheet_date_to_filter = request.POST.get('deliverySheetDateToFilter2')
        if delivery_sheet_date_filter and delivery_sheet_date_to_filter:
            customers = filter(lambda x: x.delivery_date >= delivery_sheet_date_filter and x.delivery_date <= delivery_sheet_date_to_filter, customers)

        driver_name_filter = request.POST.get('driverNameFilter2')
        if driver_name_filter:
            customers = filter(lambda x: driver_name_filter in x.driver_name.lower(), customers)

        sortType_filter = request.POST.get('sortTypeFilter2')
        sort_filter = request.POST.get('sortFilter2')
        if sort_filter == 'id':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.id)
            else:
                customers = sorted(customers, key=lambda x: x.id, reverse=True)
        elif sort_filter == 'name':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.name.lower() if x.name is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.name.lower() if x.name is not None else '', reverse=True)
        elif sort_filter == 'address':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.address.lower() if x.address is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.address.lower() if x.address is not None else '', reverse=True)
        elif sort_filter == 'daerah':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.daerah.lower() if x.daerah is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.daerah.lower() if x.daerah is not None else '', reverse=True)
        elif sort_filter == 'contact_person':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.contact_person.lower() if x.contact_person is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.contact_person.lower() if x.contact_person is not None else '', reverse=True)
        elif sort_filter == 'no_telp':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.no_telp.lower() if x.no_telp is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.no_telp.lower() if x.no_telp is not None else '', reverse=True)
        elif sort_filter == 'master_list':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.master_list_order.lower() if x.master_list is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.master_list_order.lower() if x.master_list is not None else '', reverse=True)
        elif sort_filter == 'invoice_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min, reverse=True)
        elif sort_filter == 'due_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min, reverse=True)
        elif sort_filter == 'delivery_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min, reverse=True)
        elif sort_filter == 'complete_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min, reverse=True)
        elif sort_filter == 'payment_type':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '', reverse=True)
        elif sort_filter == 'payment_details':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.payment_details_sort_first if x.payment_details_sort_first is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.payment_details_sort_last if x.payment_details_sort_last is not None else datetime.min, reverse=True)
        elif sort_filter == 'debt':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.debt_sort_first if x.debt_sort_first is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.debt_sort_last if x.debt_sort_last is not None else datetime.min, reverse=True)
        elif sort_filter == 'status':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.status_id.lower() if x.status_id is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.status_id.lower() if x.status_id is not None else '', reverse=True)
        elif sort_filter == 'raport':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: (x.raport.lower(), x.last_count_days) if x.raport is not None else '')
            else:
                customers = sorted(customers, key=lambda x: (x.raport.lower, x.last_count_days) if x.raport is not None else '', reverse=True)
        elif sort_filter == 'delivery_sheet_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.delivery_date if x.delivery_date is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.delivery_date if x.delivery_date is not None else datetime.min, reverse=True)
        elif sort_filter == 'driver_name':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.driver_name.lower() if x.driver_name is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.driver_name.lower() if x.driver_name is not None else '', reverse=True)

        if request.method == 'POST':
            customerFilter = customerFilterDto(
                dateFilter= str(datetime.now().date()),
                idFilter = request.POST.get('addressFilter2'),
                nameFilter = request.POST.get('nameFilter2'),
                addressFilter = request.POST.get('addressFilter2'),
                picFilter = request.POST.get('picFilter2'),
                phoneFilter = request.POST.get('phoneFilter2'),
                daerahFilter = request.POST.get('daerahFilter2'),
                masterlistFilter = request.POST.get('masterlistFilter2'),
                invoiceDateFilter = request.POST.get('invoiceDateFilter2'),
                invoiceDateToFilter = request.POST.get('invoiceDateToFilter2'),
                dueDateFilter = request.POST.get('dueDateFilter2'),
                dueDateToFilter = request.POST.get('dueDateToFilter2'),
                deliveryDateFilter = request.POST.get('deliveryDateFilter2'),
                deliveryDateToFilter = request.POST.get('deliveryDateToFilter2'),
                completeDateFilter = request.POST.get('completeDateFilter2'),
                completeDateToFilter = request.POST.get('completeDateToFilter2'),
                lastOrderFilter = request.POST.get('lastOrderFilter2'),
                paymentTypeFilter = request.POST.get('paymentTypeFilter2'),
                paymentDetailsFilter = request.POST.get('paymentDetailsFilter2'),
                debtFilter = request.POST.get('debtFilter2'),
                statusFilter = request.POST.get('statusFilter2'),
                raportFilter = request.POST.get('raportFilter2'),
                deliverySheetDateFilter= request.POST.get('deliverySheetDateFilter2'),
                deliverySheetDateToFilter= request.POST.get('deliverySheetDateToFilter2'),
                driverNameFilter=request.POST.get('driverNameFilter2'),
                sortTypeFilter = request.POST.get('sortTypeFilter2'),
                sortFilter = request.POST.get('sortFilter2'),
            )
        else:
            customerFilter = customerFilterDto(
                dateFilter=str(datetime.now().date()),
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
        
        categorySelect = 0
        categorySelected = 0
        categorySelectExecute = 0
        if 'categorySelected' in request.POST:
            categorySelect = int(request.POST.get('categorySelected'))
            categorySelected = int(request.POST.get('categorySelected'))
            categorySelectExecute = int(request.POST.get('categorySelected'))

        match categorySelect:
            case 1:
                lastThirtyDay = datetime.now().date() - timedelta(days=30)
                lastThirtyDay_datetime = datetime.combine(lastThirtyDay, datetime.min.time())
                date_format = '%Y-%m-%d'
                
                customers = list(filter(lambda customer: customer.last_complete is not None and datetime.strptime(customer.last_complete, date_format) < lastThirtyDay_datetime, customers))
            case 2:
                customers = list(filter(lambda customer: customer.debt != '', customers))
            case 3:
                customers = list(filter(lambda customer: customer.delivery_date == customer.last_complete and customer.delivery_date != '', customers))
            case 4:
                customers = list(filter(lambda customer: customer.delivery_date != '' and customer.debt != '', customers))
            case _:
                customers = list(customers)

        inputMessage = request.POST.get('inputMessage')

        db = firestore.client()                
        docs = db.collection('message').where('category', '==', categorySelected).stream()
        
        try:
            first_doc = next(docs)
        except StopIteration:
            first_doc = None

        if first_doc:
            first_doc.reference.update({'message': inputMessage})
        else:
            doc_ref = db.collection('message').document()
            doc_ref.set({
                'category': categorySelected,
                'message': inputMessage,
            })

        if customers:
            randomCustomer = random.choice(customers)
            currentMessage = inputMessage
            if randomCustomer.name is not None:
                currentMessage = currentMessage.replace('[name]', randomCustomer.name)
            if randomCustomer.id is not None:
                currentMessage = currentMessage.replace('[customerCode]', str(randomCustomer.id))
            if randomCustomer.address is not None:
                currentMessage = currentMessage.replace('[address]', randomCustomer.address)
            if randomCustomer.master_list is not None:
                currentMessage = currentMessage.replace('[area]', randomCustomer.master_list)
            if randomCustomer.daerah is not None:
                currentMessage = currentMessage.replace('[daerah]', randomCustomer.daerah)
            if randomCustomer.no_telp is not None:
                currentMessage = currentMessage.replace('[phone]', randomCustomer.no_telp)
            if randomCustomer.last_complete is not None:
                currentMessage = currentMessage.replace('[last_complete]', randomCustomer.last_complete)
            if randomCustomer.last_duedate is not None:
                currentMessage = currentMessage.replace('[last_duedate]', randomCustomer.last_duedate)
            if randomCustomer.last_invoice is not None:
                currentMessage = currentMessage.replace('[last_invoice]', randomCustomer.last_invoice)
            if randomCustomer.raport is not None:
                currentMessage = currentMessage.replace('[raport]', randomCustomer.raport.replace("<br>", "\n"))
            if randomCustomer.last_order is not None:
                currentMessage = currentMessage.replace('[last_order]', randomCustomer.last_order.replace("<br>", "\n"))
            if randomCustomer.last_delivery is not None:
                currentMessage = currentMessage.replace('[last_delivery]', randomCustomer.last_delivery)
            if randomCustomer.last_payment is not None:
                currentMessage = currentMessage.replace('[last_payment]', randomCustomer.last_payment.replace("<br>", "\n"))
            if randomCustomer.location is not None:
                currentMessage = currentMessage.replace('[location]', randomCustomer.location)
            if randomCustomer.debt is not None:
                currentMessage = currentMessage.replace('[debt]', randomCustomer.debt.replace("<br>", "\n"))
            if randomCustomer.payment_details is not None:
                currentMessage = currentMessage.replace('[payment_details]', randomCustomer.payment_details.replace("<br>", "\n"))
            if randomCustomer.master_list_order is not None:
                currentMessage = currentMessage.replace('[master_list_order]', randomCustomer.master_list_order)
        else:
            currentMessage = ''         

        return render(request, 'cnvadmin/whatsapp_list.html', {'customers': customers, 'categorySelect': categorySelect, 'categorySelected': categorySelected, 'customerFilter': customerFilter, 'inputMessage': inputMessage, 'currentMessage': currentMessage, 'inputMessageExecute': inputMessage, 'categorySelectExecute':categorySelected})

def whatsapp_execute(request):
    if request.method == 'POST':
        firestoreUtils = FireStoreUtils()
        locationDataDict = firestoreUtils.GetLocationDataDict()

        conn = DBUtils.GetConn()    
        cur = conn.cursor()

        customerQuery = DBUtils.GetSqlQuery("customer")
        cur.execute(customerQuery)
        records = cur.fetchall()

        sales_order_ids = [record[DBQueryIndex.CustomerQuery.sales_order_id] for record in records]

        itemQuery = DBUtils.GetSqlQuery("item")
        cur.execute(itemQuery, (sales_order_ids,))
        itemRecords = cur.fetchall()

        debt_query = DBUtils.GetSqlQuery("debt")
        cur.execute(debt_query)
        debtRecords = cur.fetchall()

        paymentDetailsQuery = DBUtils.GetSqlQuery("paymentDetails")
        cur.execute(paymentDetailsQuery)
        paymentDetailsRecords = cur.fetchall()

        inactiveCustomerQuery = DBUtils.GetSqlQuery("inactiveCustomer")
        cur.execute(inactiveCustomerQuery)
        inactiveRecords = cur.fetchall()

        customers = DBUtils.GetCustomerList(records, itemRecords, debtRecords, paymentDetailsRecords, inactiveRecords, locationDataDict)
        customers = filter(lambda x: len(x.no_telp) > 8, customers)

        id_filter = request.POST.get('idFilter3')
        if id_filter:
            customers = filter(lambda x: int(id_filter) == x.id, customers)

        name_filter = request.POST.get('nameFilter3')
        if name_filter:
            customers = filter(lambda x: name_filter in x.name.lower(), customers)

        address_filter = request.POST.get('addressFilter3')
        if address_filter:
            customers = filter(lambda x: address_filter in x.address.lower(), customers)

        daerah_filter = request.POST.get('daerahFilter3')
        if daerah_filter:
            customers = filter(lambda x: daerah_filter in x.daerah.lower(), customers)

        pic_filter = request.POST.get('picFilter3')
        if pic_filter:
            customers = filter(lambda x: pic_filter in x.contact_person.lower(), customers)

        phone_filter = request.POST.get('phoneFilter3')
        if phone_filter:
            customers = filter(lambda x: phone_filter in x.phone.lower(), customers)

        master_list_filter = request.POST.get('masterlistFilter3')
        if master_list_filter:
            customers = filter(lambda x: master_list_filter in x.master_list.lower(), customers)

        invoice_date_filter = request.POST.get('invoiceDateFilter3')
        invoice_date_to_filter = request.POST.get('invoiceDateToFilter3')
        if invoice_date_filter and invoice_date_to_filter:
            customers = filter(lambda x: x.last_invoice >= invoice_date_filter and x.last_invoice <= invoice_date_to_filter, customers)

        due_date_filter = request.POST.get('dueDateFilter3')
        due_date_to_filter = request.POST.get('dueDateToFilter3')
        if due_date_filter and due_date_to_filter:
            customers = filter(lambda x: x.last_duedate >= due_date_filter and x.last_duedate <= due_date_to_filter, customers)

        delivery_date_filter = request.POST.get('deliveryDateFilter3')
        delivery_date_to_filter = request.POST.get('deliveryDateToFilter3')
        if delivery_date_filter and delivery_date_to_filter:
            customers = filter(lambda x: x.last_delivery >= delivery_date_filter and x.last_delivery <= delivery_date_to_filter, customers)

        complete_date_filter = request.POST.get('completeDateFilter3')
        complete_date_to_filter = request.POST.get('completeDateToFilter3')
        if complete_date_filter and complete_date_to_filter:
            customers = filter(lambda x: x.last_complete >= complete_date_filter and x.complete_invoice <= complete_date_to_filter, customers)

        last_order_filter = request.POST.get('lastOrderFilter3')
        if last_order_filter:
            customers = filter(lambda x: last_order_filter in x.last_order.lower(), customers)
        
        payment_type_filter = request.POST.get('paymentTypeFilter3')
        if payment_type_filter:
            customers = filter(lambda x: payment_type_filter in x.last_payment.lower(), customers)

        payment_details_filter = request.POST.get('paymentDetailsFilter3')
        if payment_details_filter:
            customers = filter(lambda x: payment_details_filter in x.payment_details.lower(), customers)

        debt_filter = request.POST.get('debtFilter3')
        if debt_filter:
            customers = filter(lambda x: debt_filter in x.debt.lower(), customers)

        status_filter = request.POST.get('statusFilter3')
        if status_filter:
            customers = filter(lambda x: status_filter in x.status_id.lower(), customers)

        raport_filter = request.POST.get('raportFilter3')
        if raport_filter and raport_filter != 'all':
            customers = filter(lambda x: raport_filter in x.raport.lower(), customers)

        delivery_sheet_date_filter = request.POST.get('deliverySheetDateFilter3')
        delivery_sheet_date_to_filter = request.POST.get('deliverySheetDateToFilter3')
        if delivery_sheet_date_filter and delivery_sheet_date_to_filter:
            customers = filter(lambda x: x.delivery_date >= delivery_sheet_date_filter and x.delivery_date <= delivery_sheet_date_to_filter, customers)

        driver_name_filter = request.POST.get('driverNameFilter3')
        if driver_name_filter:
            customers = filter(lambda x: driver_name_filter in x.driver_name.lower(), customers)
        
        sortType_filter = request.POST.get('sortTypeFilter3')
        sort_filter = request.POST.get('sortFilter3')
        if sort_filter == 'id':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.id)
            else:
                customers = sorted(customers, key=lambda x: x.id, reverse=True)
        elif sort_filter == 'name':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.name.lower() if x.name is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.name.lower() if x.name is not None else '', reverse=True)
        elif sort_filter == 'address':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.address.lower() if x.address is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.address.lower() if x.address is not None else '', reverse=True)
        elif sort_filter == 'daerah':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.daerah.lower() if x.daerah is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.daerah.lower() if x.daerah is not None else '', reverse=True)
        elif sort_filter == 'contact_person':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.contact_person.lower() if x.contact_person is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.contact_person.lower() if x.contact_person is not None else '', reverse=True)
        elif sort_filter == 'no_telp':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.no_telp.lower() if x.no_telp is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.no_telp.lower() if x.no_telp is not None else '', reverse=True)
        elif sort_filter == 'master_list':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.master_list_order.lower() if x.master_list is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.master_list_order.lower() if x.master_list is not None else '', reverse=True)
        elif sort_filter == 'invoice_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min, reverse=True)
        elif sort_filter == 'due_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min, reverse=True)
        elif sort_filter == 'delivery_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min, reverse=True)
        elif sort_filter == 'complete_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min, reverse=True)
        elif sort_filter == 'payment_type':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '', reverse=True)
        elif sort_filter == 'payment_details':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.payment_details_sort_first if x.payment_details_sort_first is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.payment_details_sort_last if x.payment_details_sort_last is not None else datetime.min, reverse=True)
        elif sort_filter == 'debt':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.debt_sort_first if x.debt_sort_first is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.debt_sort_last if x.debt_sort_last is not None else datetime.min, reverse=True)
        elif sort_filter == 'status':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.status_id.lower() if x.status_id is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.status_id.lower() if x.status_id is not None else '', reverse=True)
        elif sort_filter == 'raport':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: (x.raport.lower(), x.last_count_days) if x.raport is not None else '')
            else:
                customers = sorted(customers, key=lambda x: (x.raport.lower, x.last_count_days) if x.raport is not None else '', reverse=True)
        elif sort_filter == 'delivery_sheet_date':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.delivery_date if x.delivery_date is not None else datetime.min)
            else:
                customers = sorted(customers, key=lambda x: x.delivery_date if x.delivery_date is not None else datetime.min, reverse=True)
        elif sort_filter == 'driver_name':
            if sortType_filter == 'asc':
                customers = sorted(customers, key=lambda x: x.driver_name.lower() if x.driver_name is not None else '')
            else:
                customers = sorted(customers, key=lambda x: x.driver_name.lower() if x.driver_name is not None else '', reverse=True)

        if request.method == 'POST':
            customerFilter = customerFilterDto(
                dateFilter= str(datetime.now().date()),
                idFilter = request.POST.get('addressFilter3'),
                nameFilter = request.POST.get('nameFilter3'),
                addressFilter = request.POST.get('addressFilter3'),
                picFilter = request.POST.get('picFilter3'),
                phoneFilter = request.POST.get('phoneFilter3'),
                daerahFilter = request.POST.get('daerahFilter3'),
                masterlistFilter = request.POST.get('masterlistFilter3'),
                invoiceDateFilter = request.POST.get('invoiceDateFilter3'),
                invoiceDateToFilter = request.POST.get('invoiceDateToFilter3'),
                dueDateFilter = request.POST.get('dueDateFilter3'),
                dueDateToFilter = request.POST.get('dueDateToFilter3'),
                deliveryDateFilter = request.POST.get('deliveryDateFilter3'),
                deliveryDateToFilter = request.POST.get('deliveryDateToFilter3'),
                completeDateFilter = request.POST.get('completeDateFilter3'),
                completeDateToFilter = request.POST.get('completeDateToFilter3'),
                lastOrderFilter = request.POST.get('lastOrderFilter3'),
                paymentTypeFilter = request.POST.get('paymentTypeFilter3'),
                paymentDetailsFilter = request.POST.get('paymentDetailsFilter3'),
                debtFilter = request.POST.get('debtFilter3'),
                statusFilter = request.POST.get('statusFilter3'),
                raportFilter = request.POST.get('raportFilter3'),
                deliverySheetDateFilter= request.POST.get('deliverySheetDateFilter3'),
                deliverySheetDateToFilter= request.POST.get('deliverySheetDateToFilter3'),
                driverNameFilter=request.POST.get('driverNameFilter3'),
                sortTypeFilter = request.POST.get('sortTypeFilter3'),
                sortFilter = request.POST.get('sortFilter3'),
            )
        else:
            customerFilter = customerFilterDto(
                dateFilter=str(datetime.now().date()),
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

        categorySelect = 0
        categorySelected = 0
        categorySelectExecute = 0
        if 'categorySelected' in request.POST:
            categorySelect = int(request.POST.get('categorySelectExecute'))
            categorySelected = int(request.POST.get('categorySelectExecute'))
            categorySelectExecute = int(request.POST.get('categorySelectExecute'))
        
        match categorySelect:
            case 1:
                lastThirtyDay = datetime.now().date() - timedelta(days=30)
                lastThirtyDay_datetime = datetime.combine(lastThirtyDay, datetime.min.time())
                date_format = '%Y-%m-%d'
                
                customers = list(filter(lambda customer: customer.last_complete is not None and datetime.strptime(customer.last_complete, date_format) < lastThirtyDay_datetime, customers))
            case 2:
                customers = list(filter(lambda customer: customer.debt != '', customers))
            case 3:
                customers = list(filter(lambda customer: customer.delivery_date == customer.last_complete and customer.delivery_date != '', customers))
            case 4:
                customers = list(filter(lambda customer: customer.delivery_date != '' and customer.debt != '', customers))
            case _:
                customers = list(customers)   

        inputMessage = request.POST.get('inputMessageExecute')
        inputMessageExecute = request.POST.get('inputMessageExecute')

        selected_items = request.POST.getlist('selected_items')
        for customer_id in selected_items:  # Update the loop variable
            customerItem = list(filter(lambda x: x.id == int(customer_id), customers))

            if (len(customerItem)>0):
                if customerItem[0].no_telp is not None and customerItem[0].no_telp != '':
                    currentMessage = inputMessage
                    if customerItem[0].name is not None:
                        currentMessage = currentMessage.replace('[name]', customerItem[0].name)
                    if customerItem[0].id is not None:
                        currentMessage = currentMessage.replace('[customerCode]', str(customerItem[0].id))
                    if customerItem[0].address is not None:
                        currentMessage = currentMessage.replace('[address]', customerItem[0].address)
                    if customerItem[0].master_list is not None:
                        currentMessage = currentMessage.replace('[area]', customerItem[0].master_list)
                    if customerItem[0].daerah is not None:
                        currentMessage = currentMessage.replace('[daerah]', customerItem[0].daerah)
                    if customerItem[0].no_telp is not None:
                        currentMessage = currentMessage.replace('[phone]', customerItem[0].no_telp)
                    if customerItem[0].last_complete is not None:
                        currentMessage = currentMessage.replace('[last_complete]', customerItem[0].last_complete)
                    if customerItem[0].last_duedate is not None:
                        currentMessage = currentMessage.replace('[last_duedate]', customerItem[0].last_duedate)
                    if customerItem[0].last_invoice is not None:
                        currentMessage = currentMessage.replace('[last_invoice]', customerItem[0].last_invoice)
                    if customerItem[0].raport is not None:
                        currentMessage = currentMessage.replace('[raport]', customerItem[0].raport.replace("<br>", "\n"))
                    if customerItem[0].last_order is not None:
                        currentMessage = currentMessage.replace('[last_order]', customerItem[0].last_order.replace("<br>", "\n"))
                    if customerItem[0].last_delivery is not None:
                        currentMessage = currentMessage.replace('[last_delivery]', customerItem[0].last_delivery)
                    if customerItem[0].last_payment is not None:
                        currentMessage = currentMessage.replace('[last_payment]', customerItem[0].last_payment.replace("<br>", "\n"))
                    if customerItem[0].location is not None:
                        currentMessage = currentMessage.replace('[location]', customerItem[0].location)
                    if customerItem[0].debt is not None:
                        currentMessage = currentMessage.replace('[debt]', customerItem[0].debt.replace("<br>", "\n"))
                    if customerItem[0].payment_details is not None:
                        currentMessage = currentMessage.replace('[payment_details]', customerItem[0].payment_details.replace("<br>", "\n"))
                    if customerItem[0].master_list_order is not None:
                        currentMessage = currentMessage.replace('[master_list_order]', customerItem[0].master_list_order)
                
                    phone_number = customerItem[0].no_telp
                    phone_number = "0895323031823"
                    if phone_number[0] == '0':
                        # Replace the first digit with '+62'
                        phone_number = '+62' + phone_number[1:]
                    group_id = ''
                    message = currentMessage
                    waiting_time_to_send = 10
                    close_tab = True
                    waiting_time_to_close = 10

                    mode = "contact"

                    if mode == "contact":
                        pywhatkit.sendwhatmsg_instantly(phone_number, message, waiting_time_to_send, True, waiting_time_to_close)
                    else:
                        print("Error code: 97654")
                        print("Error Message: Please select a mode to send your message.")

        return render(request, 'cnvadmin/whatsapp_list.html', {'customers': customers, 'categorySelect': categorySelect, 'categorySelected': categorySelected, 'customerFilter': customerFilter, 'inputMessage': inputMessage, 'currentMessage': currentMessage, 'inputMessageExecute': inputMessageExecute, 'categorySelectExecute':categorySelectExecute})
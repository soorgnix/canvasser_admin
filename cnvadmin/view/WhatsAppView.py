from datetime import datetime, timedelta
import random
from django.shortcuts import render
from firebase_admin import firestore
from cnvadmin.utils.DBQueryIndex import DBQueryIndex
from cnvadmin.utils.DBUtils import DBUtils
from cnvadmin.utils.FireStoreUtils import FireStoreUtils
import pywhatkit


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
            customers = customers                       


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

    return render(request, 'cnvadmin/whatsapp_list.html', {'customers': customers, 'categorySelect': categorySelect, 'categorySelected': categorySelect, 'inputMessage': inputMessage, 'currentMessage': currentMessage, 'inputMessageExecute': inputMessage, 'categorySelectExecute':categorySelect})

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
                customers = customers   

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

        return render(request, 'cnvadmin/whatsapp_list.html', {'customers': customers, 'categorySelect': categorySelect, 'categorySelected': categorySelected, 'inputMessage': inputMessage, 'currentMessage': currentMessage, 'inputMessageExecute': inputMessage, 'categorySelectExecute':categorySelected})

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
                customers = customers   

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
                    phone_number = "+62895323031823"
                    group_id = ''
                    message = currentMessage
                    time_hour = 14
                    time_minute = 50
                    waiting_time_to_send = 15
                    close_tab = True
                    waiting_time_to_close = 10

                    mode = "contact"

                    if mode == "contact":
                        pywhatkit.sendwhatmsg_instantly(phone_number, message, waiting_time_to_send, True, waiting_time_to_close)
                    elif mode == "group":
                        pywhatkit.sendwhatmsg_to_group(group_id, message, time_hour, time_minute, waiting_time_to_send, close_tab, waiting_time_to_close)
                    else:
                        print("Error code: 97654")
                        print("Error Message: Please select a mode to send your message.")

        return render(request, 'cnvadmin/whatsapp_list.html', {'customers': customers, 'categorySelect': categorySelect, 'categorySelected': categorySelected, 'inputMessage': inputMessage, 'currentMessage': currentMessage, 'inputMessageExecute': inputMessageExecute, 'categorySelectExecute':categorySelectExecute})
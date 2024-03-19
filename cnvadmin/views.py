from datetime import datetime, timedelta
from django.shortcuts import render
from firebase_admin import firestore
import psycopg2
import pytz
from django.utils.html import mark_safe
from django.template.defaultfilters import escapejs
from .config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD
from .config import MAX_DISTANCE
ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY = 3
from .utils.queryFieldsPointerUtils import CUSTOMERQUERY_CUSTOMER_ID, CUSTOMERQUERY_CUSTOMER_ADDRESS, CUSTOMERQUERY_CUSTOMER_CONTACT_PERSON, CUSTOMERQUERY_CUSTOMER_NAME, CUSTOMERQUERY_CUSTOMER_NO_TELP, CUSTOMERQUERY_CUSTOMER_DAERAH, CUSTOMERQUERY_MASTER_LIST_NAME, CUSTOMERQUERY_SALES_ORDER_ID, CUSTOMERQUERY_SALES_ORDER_DATE, CUSTOMERQUERY_SALES_ORDER_DELIVERY_DATE, CUSTOMERQUERY_SALES_ORDER_INVOICE_ID, CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE, CUSTOMERQUERY_SALES_ORDER_INVOICE_DUE_DATE, CUSTOMERQUERY_SALES_ORDER_INVOICE_DATE_COMPLETED, CUSTOMERQUERY_SALES_ORDER_TOTAL, CUSTOMERQUERY_SALES_ORDER_STATUS_ID, CUSTOMERQUERY_PAYMENT_METHOD_NAME, CUSTOMERQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER, CUSTOMERQUERY_CUSTOMER_REFERENCE_CODE, CUSTOMERQUERY_APPROVAL_STATUS_NAME, CUSTOMERQUERY_TOTAL_PAYMENT_AMOUNT
from .utils.queryFieldsPointerUtils import ITEMQUERY_SALES_ORDER_DETAIL_SALES_ORDER_ID, ITEMQUERY_SALES_ORDER_DETAIL_ID, ITEMQUERY_ITEM_NAME, ITEMQUERY_SALES_ORDER_DETAIL_QUANTITY, ITEMQUERY_SALES_ORDER_DETAIL_PRICE
from .utils.queryFieldsPointerUtils import DEBTQUERY_CUSTOMER_ID, DEBTQUERY_SALES_ORDER_ID, DEBTQUERY_SALES_ORDER_DATE, DEBTQUERY_SALES_ORDER_DELIVERY_DATE, DEBTQUERY_SALES_ORDER_INVOICE_ID, DEBTQUERY_SALES_ORDER_INVOICE_DATE, DEBTQUERY_SALES_ORDER_INVOICE_DUE_DATE, DEBTQUERY_SALES_ORDER_INVOICE_TOTAL, DEBTQUERY_PAYMENT_METHOD_NAME, DEBTQUERY_SALES_ORDER_INVOICE_INVOICE_NUMBER, DEBTQUERY_TOTAL_PAYMENT_AMOUNT, DEBTQUERY_DEBT
from .utils.queryFieldsPointerUtils import PAYMENTDETAILSQUERY_CUSTOMER_ID, PAYMENTDETAILSQUERY_SALES_ORDER_ID, PAYMENTDETAILSQUERY_SALES_ORDER_INVOICE_ID, PAYMENTDETAILSQUERY_SALES_ORDER_INVOICE_DATE, PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_DATE, PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_AMOUNT, PAYMENTDETAILSQUERY_SALES_ORDER_PAYMENT_DESCRIPTION, PAYMENTDETAILSQUERY_TOTAL_PAYMENT_AMOUNT
from .utils.queryFieldsPointerUtils import INACTIVECUSTOMERQUERY_CUSTOMER_ID, INACTIVECUSTOMERQUERY_CUSTOMER_ADDRESS, INACTIVECUSTOMERQUERY_CUSTOMER_CONTACT_PERSON, INACTIVECUSTOMERQUERY_CUSTOMER_NAME, INACTIVECUSTOMERQUERY_CUSTOMER_NO_TELP, INACTIVECUSTOMERQUERY_CUSTOMER_DAERAH, INACTIVECUSTOMERQUERY_MASTER_LIST_NAME, INACTIVECUSTOMERQUERY_CUSTOMER_REFERENCE_CODE
from math import radians, sin, cos, sqrt, atan2


from django.utils.safestring import mark_safe

from cnvadmin.dto.dto import customerDto, customerFilterDto, newCustomerDto, newCustomerFilterDto, visitDto, visitFilterDto

# Create a Firestore client
db = firestore.client()

def visit_list(request):
    if request.method == 'POST':
        # Get the selected date from the form
        valueDate = request.POST.get('dateFilter')
    else:
        # Use the current date as the default
        valueDate = str(datetime.now().date())

    selected_date = datetime.strptime(valueDate, '%Y-%m-%d')       
    selected_range_date = selected_date + timedelta(days=1)

    
    docs = db.collection('visits').where('date', '>=', selected_date).where('date', '<', selected_range_date).stream()

    visits = []
    for doc in docs:        
        timezone = pytz.timezone('Asia/Bangkok')
        check_in_time = doc.get('checkInTime')
        if check_in_time != "":
            check_in_time = check_in_time.astimezone(timezone) + timedelta(hours=7)
        else:
            check_in_time = ""

        checkOutTime = doc.get('checkOutTime')
        if checkOutTime != "":
            checkOutTime = checkOutTime.astimezone(timezone) + timedelta(hours=7)
        else:
            checkOutTime = ""

        if "skipTime" in doc.to_dict():
            skipTime = doc.get('skipTime')
            if skipTime != "":
                skipTime = skipTime.astimezone(timezone) + timedelta(hours=7)
            else:
                skipTime = ""
        else:
            skipTime = ""


        docDict = doc.to_dict()
        location = ''
        if ('location' in docDict):
            location = doc.get('location')

        visit = visitDto(
            id = doc.id,
            customerCode = int(doc.get('customerCode')),
            address = doc.get('address'),      
            area = doc.get('area'),
            daerah = '',
            isSkip = False,
            skipTime = skipTime,
            checkInLocation = doc.get('checkInLocation'),
            checkInTime = check_in_time,
            checkInDistance= 0,
            checkOutLocation = doc.get('checkOutLocation'),
            checkOutTime = checkOutTime,
            checkOutDistance= 0,
            date = doc.get('date'),
            isCheckIn = doc.get('isCheckIn'),
            isCheckOut = doc.get('isCheckOut'),
            note = doc.get('note'),
            phone = doc.get('phone'),
            pic = doc.get('pic'),
            user_id = doc.get('user_id'),
            last_complete= '',
            last_duedate= '',
            last_invoice= '',
            raport= '',
            last_order='',
            last_delivery='',
            last_payment='',
            last_count_days='',
            debt='',
            payment_details='',
            master_list_order=doc.get('master_list_order'),
            location=location
        )
        if "daerah" in doc.to_dict():
            visit.daerah=doc.get('daerah')
        if "isSkip" in doc.to_dict():
            visit.isSkip=doc.get('isSkip')
        if "last_complete" in doc.to_dict():
            visit.last_complete=doc.get('last_complete')
        if "last_duedate" in doc.to_dict():
            visit.last_duedate=doc.get('last_duedate')
        if "last_invoice" in doc.to_dict():
            visit.last_invoice=doc.get('last_invoice')
        if "raport" in doc.to_dict():
            visit.raport=doc.get('raport')
        if "last_order" in doc.to_dict():
            visit.last_order=mark_safe(doc.get('last_order').replace("\n", "<br>"))
        if "last_delivery" in doc.to_dict():
            visit.last_delivery=doc.get('last_delivery')
        if "last_payment" in doc.to_dict():
            visit.last_payment=doc.get('last_payment')
        if "last_count_days" in doc.to_dict():
            visit.last_count_days=doc.get('last_count_days')
        if "debt" in doc.to_dict():
            visit.debt=mark_safe(doc.get('debt').replace("\n", "<br>"))
        if "payment_details" in doc.to_dict():
            visit.payment_details=mark_safe(doc.get('payment_details').replace("\n", "<br>"))
        if doc.get('checkInLocation') != '' and doc.get('location') != '':
            aPos = doc.get('location').split(',')
            bPos = doc.get('checkInLocation').split(',')
            visit.checkInDistance = round(calc_dist(float(aPos[0]), float(aPos[1]), float(bPos[0]), float(bPos[1])),2)
        if doc.get('checkOutLocation') != '' and doc.get('location') != '':
            aPos = doc.get('location').split(',')
            bPos = doc.get('checkOutLocation').split(',')
            visit.checkOutDistance = round(calc_dist(float(aPos[0]), float(aPos[1]), float(bPos[0]), float(bPos[1])),2)

        visits.append(visit)
    
    sorted_visits = sorted(visits, key=lambda x: x.address)

    if request.method == 'POST':
        customerCode_filter = request.POST.get('customerCodeFilter')
        if customerCode_filter:
            sorted_visits = filter(lambda x: customerCode_filter.lower() in str(x.customerCode).lower(), sorted_visits)

        name_filter = request.POST.get('nameFilter')
        if name_filter:
            sorted_visits = filter(lambda x: name_filter.lower() in x.pic.lower(), sorted_visits)

        address_filter = request.POST.get('addressFilter')
        if address_filter:
            sorted_visits = filter(lambda x: address_filter.lower() in x.address.lower(), sorted_visits)

        area_filter = request.POST.get('areaFilter')
        if area_filter:
            sorted_visits = filter(lambda x: area_filter.lower() in x.area.lower(), sorted_visits)

        daerah_filter = request.POST.get('daerahFilter')
        if daerah_filter:
            sorted_visits = filter(lambda x: daerah_filter.lower() in x.daerah.lower(), sorted_visits)

        phone_filter = request.POST.get('phoneFilter')
        if phone_filter:
            sorted_visits = filter(lambda x: phone_filter.lower() in x.phone.lower(), sorted_visits)

        invoice_date_filter = request.POST.get('invoiceDateFilter')
        invoice_date_to_filter = request.POST.get('invoiceDateToFilter')
        if invoice_date_filter and invoice_date_to_filter:
            sorted_visits = filter(lambda x: x.last_invoice >= invoice_date_filter and x.last_invoice <= invoice_date_to_filter, sorted_visits)

        due_date_filter = request.POST.get('dueDateFilter')
        due_date_to_filter = request.POST.get('dueDateToFilter')
        if due_date_filter and due_date_to_filter:
            sorted_visits = filter(lambda x: x.last_duedate >= due_date_filter and x.last_duedate <= due_date_to_filter, sorted_visits)

        delivery_date_filter = request.POST.get('deliveryDateFilter')
        delivery_date_to_filter = request.POST.get('deliveryDateToFilter')
        if delivery_date_filter and delivery_date_to_filter:
            sorted_visits = filter(lambda x: x.last_delivery >= delivery_date_filter and x.last_delivery <= delivery_date_to_filter, sorted_visits)

        complete_date_filter = request.POST.get('completeDateFilter')
        complete_date_to_filter = request.POST.get('completeDateToFilter')
        if complete_date_filter and complete_date_to_filter:
            sorted_visits = filter(lambda x: x.last_complete >= complete_date_filter and x.complete_invoice <= complete_date_to_filter, sorted_visits)

        last_order_filter = request.POST.get('lastOrderFilter')
        if last_order_filter:
            sorted_visits = filter(lambda x: last_order_filter in x.last_order.lower(), sorted_visits)
        
        payment_type_filter = request.POST.get('paymentTypeFilter')
        if payment_type_filter:
            sorted_visits = filter(lambda x: payment_type_filter in x.last_payment.lower(), sorted_visits)

        payment_details_filter = request.POST.get('paymentDetailsFilter')
        if payment_details_filter:
            sorted_visits = filter(lambda x: payment_details_filter in x.payment_details.lower(), sorted_visits)

        debt_filter = request.POST.get('debtFilter')
        if debt_filter:
            sorted_visits = filter(lambda x: debt_filter.lower() in x.debt.lower(), sorted_visits)

        user_filter = request.POST.get('userFilter')
        if user_filter:
            sorted_visits = filter(lambda x: user_filter.lower() in x.user_id.lower(), sorted_visits)

        raport_filter = request.POST.get('raportFilter')
        if raport_filter:
            if raport_filter != 'all':
                sorted_visits = filter(lambda x: raport_filter.lower() in x.raport.lower(), sorted_visits)

        checkIn_filter = request.POST.get('checkInFilter')
        if checkIn_filter == 'true':
            sorted_visits = [visit for visit in sorted_visits if visit.isCheckIn]
        elif checkIn_filter == 'false':
            sorted_visits = [visit for visit in sorted_visits if not visit.isCheckIn]

        checkOut_filter = request.POST.get('checkOutFilter')
        if checkOut_filter == 'true':
            sorted_visits = [visit for visit in sorted_visits if visit.isCheckOut]
        elif checkOut_filter == 'false':
            sorted_visits = [visit for visit in sorted_visits if not visit.isCheckOut]

        distance_filter = request.POST.get('distanceFilter')
        if distance_filter == 'out':
            sorted_visits = [visit for visit in sorted_visits if visit.checkInDistance > MAX_DISTANCE or visit.checkOutDistance > MAX_DISTANCE]

        skip_filter = request.POST.get('skipfilter')
        if skip_filter == 'true':
            sorted_visits = [visit for visit in sorted_visits if visit.isSkip]
        elif skip_filter == 'false':
            sorted_visits = [visit for visit in sorted_visits if not visit.isSkip]

        sortType_filter = request.POST.get('sortTypeFilter')
        sort_filter = request.POST.get('sortFilter')
        if sort_filter == 'customerCode':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.customerCode)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.customerCode, reverse=True)
        elif sort_filter == 'pic':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.pic.lower())
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.pic.lower(), reverse=True)
        elif sort_filter == 'address':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.address.lower())
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.address.lower(), reverse=True)
        elif sort_filter == 'area':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.master_list_order.lower())
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.master_list_order.lower(), reverse=True)
        elif sort_filter == 'phone':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.phone.lower())
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.phone.lower(), reverse=True)
        elif sort_filter == 'raport':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.raport.lower())
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.raport.lower(), reverse=True)
        elif sort_filter == 'invoice_date':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.last_invoice if x.last_invoice is not None else datetime.min, reverse=True)
        elif sort_filter == 'due_date':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.last_duedate if x.last_duedate is not None else datetime.min, reverse=True)
        elif sort_filter == 'delivery_date':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.last_delivery if x.last_delivery is not None else datetime.min, reverse=True)
        elif sort_filter == 'complete_date':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: datetime.strptime(x.last_complete, '%Y-%m-%d') if x.last_complete is not None else datetime.min, reverse=True)
        elif sort_filter == 'payment_type':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '')
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.last_payment.lower() if x.last_payment is not None else '', reverse=True)
        elif sort_filter == 'payment_details':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.payment_details if x.payment_details is not None else datetime.min)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.payment_details if x.payment_details is not None else datetime.min, reverse=True)
        elif sort_filter == 'debt':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.debt if x.debt is not None else datetime.min)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.debt if x.debt is not None else datetime.min, reverse=True)
        elif sort_filter == 'raport':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.raport.lower() if x.raport is not None else '')
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.raport.lower() if x.raport is not None else '', reverse=True)
        elif sort_filter == 'user_id':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.user_id.lower if x.user_id is not None else '')
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.user_id.lower if x.user_id is not None else '', reverse=True)
        elif sort_filter == 'note':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.note.lower() if x.note is not None else '')
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.note.lower if x.note is not None else '', reverse=True)
        elif sort_filter == 'isCheckIn':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.isCheckIn)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.isCheckIn, reverse=True)
        elif sort_filter == 'checkInTime':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkInTime.replace(tzinfo=None) if x.checkInTime else datetime.min)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkInTime.replace(tzinfo=None) if x.checkInTime else datetime.max, reverse=True)
        elif sort_filter == 'checkInLocation':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkInLocation)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkInLocation, reverse=True)
        elif sort_filter == 'checkInDistance':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkInDistance)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkInDistance, reverse=True)
        elif sort_filter == 'isCheckOut':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.isCheckOut)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.isCheckOut, reverse=True)
        elif sort_filter == 'checkOutTime':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkOutTime.replace(tzinfo=None) if x.checkOutTime else datetime.min)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkOutTime.replace(tzinfo=None) if x.checkOutTime else datetime.max, reverse=True)
        elif sort_filter == 'checkOutLocation':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkOutLocation)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkOutLocation, reverse=True)
        elif sort_filter == 'checkOutDistance':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkOutDistance)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.checkOutDistance, reverse=True)
        elif sort_filter == 'isSkip':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.isSkip)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.isSkip, reverse=True)
        elif sort_filter == 'skipTime':
            if sortType_filter == 'asc':
                sorted_visits = sorted(sorted_visits, key=lambda x: x.skipTime.replace(tzinfo=None) if x.skipTime else datetime.min)
            else:
                sorted_visits = sorted(sorted_visits, key=lambda x: x.skipTime.replace(tzinfo=None) if x.skipTime else datetime.max, reverse=True)

    if request.method == 'POST':
        visitFilter = visitFilterDto(
            dateFilter=valueDate,
            nameFilter=request.POST.get('nameFilter'),
            addressFilter=request.POST.get('addressFilter'),
            areaFilter=request.POST.get('areaFilter'),
            daerahFilter=request.POST.get('daerahFilter'),
            customerCodeFilter=request.POST.get('customerCodeFilter'),
            phoneFilter=request.POST.get('phoneFilter'),
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
            distanceFilter= request.POST.get('distanceFilter'),
            debtFilter = request.POST.get('debtFilter'),
            raportFilter = request.POST.get('raportFilter'),
            userFilter=request.POST.get('userFilter'),
            noteFilter=request.POST.get('noteFilter'),
            checkInFilter=request.POST.get('checkInFilter'),
            checkOutFilter=request.POST.get('checkOutFilter'),
            skipFilter=request.POST.get('skipFilter'),
            sortTypeFilter=request.POST.get('sortTypeFilter'),
            sortFilter=request.POST.get('sortFilter')
        )
    else:
        visitFilter = visitFilterDto(
            dateFilter=valueDate,
            nameFilter='',
            addressFilter='',
            daerahFilter='',
            areaFilter='',
            customerCodeFilter='',
            phoneFilter='',
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
            raportFilter='all',
            distanceFilter= 'all',
            userFilter='',
            noteFilter='',
            checkInFilter='all',
            checkOutFilter='all',
            skipFilter='all',
            sortTypeFilter='Asc',
            sortFilter='address'
        )      

    distinct_names = set(item.user_id for item in visits)
    distinct_names_list = list(distinct_names)
        
    action = request.POST.get('action')
    return render(request, 'cnvadmin/visit_list.html', {'visits': sorted_visits, 'visitFilter':visitFilter, 'assignment': distinct_names_list, 'MAX_DISTANCE':MAX_DISTANCE})


def visit_edit(request):
    visitId = request.GET.get('id')
   
    doc = db.collection('visits').document(visitId).get()

    timezone = pytz.timezone('Asia/Bangkok')
    checkInTime = doc.get('checkInTime')
    if checkInTime != "":
        checkInTime = checkInTime.astimezone(timezone)
    else:
        checkInTime = ""

    checkOutTime = doc.get('checkOutTime')
    if checkOutTime != "":
        checkOutTime = checkOutTime.astimezone(timezone)
    else:
        checkOutTime = ""

    if "skipTime" in doc.to_dict():
        skipTime = doc.get('skipTime')
        if skipTime != "":
            skipTime = skipTime.astimezone(timezone) + timedelta(hours=7)
        else:
            skipTime = ""
    else:
        skipTime = ""

    dateTime = doc.get('date')
    dateTime = dateTime.astimezone(timezone)

    visit = visitDto(
        id = doc.id,
        customerCode = int(doc.get('customerCode')),
        address = doc.get('address'),      
        area = doc.get('area'),
        daerah = '',
        checkInLocation = doc.get('checkInLocation'),
        checkInTime = checkInTime,
        checkInDistance=0,
        checkOutLocation = doc.get('checkOutLocation'),
        checkOutTime = checkOutTime,
        checkOutDistance=0,
        date = doc.get('date'),
        isCheckIn = doc.get('isCheckIn'),
        isCheckOut = doc.get('isCheckOut'),
        note = doc.get('note'),
        phone = doc.get('phone'),
        pic = doc.get('pic'),
        user_id = doc.get('user_id'),
        last_complete= '',
        last_duedate= '',
        last_invoice= '',
        raport= '',
        last_order='',
        last_delivery='',
        last_payment='',
        last_count_days='',
        debt='',
        payment_details='',
        isSkip = False,
        skipTime = skipTime,
        master_list_order=doc.get('master_list_order'),
        location= doc.get('location')
    )
    if "daerah" in doc.to_dict():
        visit.daerah=doc.get('daerah')
    if "isSkip" in doc.to_dict():
        visit.isSkip=doc.get('isSkip')
    if "last_complete" in doc.to_dict():
        visit.last_complete=doc.get('last_complete')
    if "last_duedate" in doc.to_dict():
        visit.last_duedate=doc.get('last_duedate')
    if "last_invoice" in doc.to_dict():
        visit.last_invoice=doc.get('last_invoice')
    if "raport" in doc.to_dict():
        visit.raport=doc.get('raport')
    if "last_order" in doc.to_dict():
        visit.last_order=mark_safe(doc.get('last_order').replace("\n", "<br>"))
    if "last_delivery" in doc.to_dict():
        visit.last_delivery=doc.get('last_delivery')
    if "last_payment" in doc.to_dict():
        visit.last_payment=doc.get('last_payment')
    if "last_count_days" in doc.to_dict():
        visit.last_count_days=doc.get('last_count_days')
    if "debt" in doc.to_dict():
        visit.debt=mark_safe(doc.get('debt').replace("\n", "<br>"))
    if "payment_details" in doc.to_dict():
        visit.payment_details=mark_safe(doc.get('payment_details').replace("\n", "<br>"))

    usersDocs = db.collection('users').stream()
    userList = set()
    for doc in usersDocs:
        userList.add(doc.get('email'))
    userList = sorted(userList, key=lambda x: x.lower())
    userList = set(userList)

    visit.location=''
    locationDocs = db.collection('locations').where('customerCode', '==', str(visit.customerCode)).stream()
    for doc in locationDocs:
        visit.location = doc.get('location')
        
    return render(request, 'cnvadmin/visit_edit.html', {'users': userList, 'visit': visit})

def visit_delete(request):
    visitId = request.GET.get('id')  
    return render(request, 'cnvadmin/visit_delete.html', {'visitId': visitId})

def newcustomer_list(request):   
    docs = db.collection('customers').stream()

    newcustomers = []
    for doc in docs:
        timezone = pytz.timezone('Asia/Bangkok')
        addedDate = doc.get('addedDate')
        if addedDate != "":
            addedDate = addedDate.astimezone(timezone) + timedelta(hours=7)
        else:
            addedDate = ""

        updateDate = doc.get('updateDate')
        if updateDate != "":
            updateDate = updateDate.astimezone(timezone) + timedelta(hours=7)
        else:
            updateDate = ""

        newcustomer = newCustomerDto(
            id = doc.id,
            name=doc.get('name'),
            address = doc.get('address'),      
            location = doc.get('location'),
            addedDate = addedDate,
            updateDate = updateDate,
            added = doc.get('added'),
            note = doc.get('note'),
            phone = doc.get('phone'),
            pic = doc.get('pic'),
            user_id = doc.get('user_id')
        )
        newcustomers.append(newcustomer)
    
    sorted_newcustomers = sorted(newcustomers, key=lambda x: x.address)

    if request.method == 'POST':
        address_filter = request.POST.get('addressFilter')
        if address_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if address_filter.lower() in newcustomer.address.lower()]

        name_filter = request.POST.get('nameFilter')
        if name_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if name_filter.lower() in newcustomer.name.lower()]

        pic_filter = request.POST.get('picFilter')
        if pic_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if pic_filter.lower() in newcustomer.pic.lower()]

        phone_filter = request.POST.get('phoneFilter')
        if phone_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if phone_filter.lower() in newcustomer.phone.lower()]

        user_filter = request.POST.get('userFilter')
        if user_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if user_filter.lower() in newcustomer.user_id.lower()]

        added_filter = request.POST.get('addedFilter')
        if added_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if added_filter.lower() in newcustomer.added.lower()]

        sortType_filter = request.POST.get('sortTypeFilter')
        sort_filter = request.POST.get('sortFilter')
        if sort_filter == 'pic':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.pic.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.pic.lower(), reverse=True)
        elif sort_filter == 'name':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.name.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.name.lower(), reverse=True)
        elif sort_filter == 'address':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.address.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.address.lower(), reverse=True)
        elif sort_filter == 'phone':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.phone.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.phone.lower(), reverse=True)
        if sort_filter == 'addedDate':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.addedDate.replace(tzinfo=None) if x.addedDate else datetime.min)
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.addedDate.replace(tzinfo=None) if x.addedDate else datetime.max, reverse=True)
        if sort_filter == 'updateDate':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.updateDate.replace(tzinfo=None) if x.updateDate else datetime.min)
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.updateDate.replace(tzinfo=None) if x.updateDate else datetime.max, reverse=True)
        elif sort_filter == 'location':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.location)
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.location, reverse=True)
        elif sort_filter == 'note':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.note.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.note.lower(), reverse=True)
        elif sort_filter == 'added':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.added.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.added.lower(), reverse=True)
        elif sort_filter == 'user_id':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.user_id.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.user_id.lower(), reverse=True)

    if request.method == 'POST':
        newcustomerFilter = newCustomerFilterDto(
            nameFilter=request.POST.get('nameFilter'),
            addressFilter=request.POST.get('addressFilter'),
            phoneFilter=request.POST.get('phoneFilter'),
            picFilter=request.POST.get('picFilter'),
            userFilter=request.POST.get('userFilter'),
            addedFilter=request.POST.get('addedFilter'),
            sortTypeFilter=request.POST.get('sortTypeFilter'),
            sortFilter=request.POST.get('sortFilter')
        )
    else:
        newcustomerFilter = newCustomerFilterDto(
            nameFilter='',
            addressFilter='',
            phoneFilter='',
            picFilter='',
            userFilter='',
            addedFilter='false',
            sortTypeFilter='desc',
            sortFilter='addedDate'
        )

    return render(request, 'cnvadmin/newcustomer_list.html', {'newcustomers': sorted_newcustomers, 'newcustomerFilter':newcustomerFilter})

def newcustomer_edit(request):
    customerId = request.GET.get('id')
   
    doc = db.collection('customers').document(customerId).get()

    timezone = pytz.timezone('Asia/Bangkok')
    addedDate = doc.get('addedDate')
    addedDate = addedDate.astimezone(timezone)
    updateDate = doc.get('updateDate')
    updateDate = updateDate.astimezone(timezone)

    newcustomer = newCustomerDto(
        id = doc.id,
        address = doc.get('address'),
        addedDate = addedDate,
        updateDate = updateDate,
        location = doc.get('location'),
        added = doc.get('added'),
        note = doc.get('note'),
        phone = doc.get('phone'),
        name = doc.get('name'),
        pic = doc.get('pic'),
        user_id = doc.get('user_id')
    )
  
    return render(request, 'cnvadmin/newcustomer_edit.html', {'newcustomer': newcustomer})

def newcustomer_map_view(request):   
    docs = db.collection('customers').stream()

    newcustomers = []
    for doc in docs:
        timezone = pytz.timezone('Asia/Bangkok')
        addedDate = doc.get('addedDate')
        if addedDate != "":
            addedDate = addedDate.astimezone(timezone)
        else:
            addedDate = ""

        updateDate = doc.get('updateDate')
        if updateDate != "":
            updateDate = updateDate.astimezone(timezone)
        else:
            updateDate = ""

        newcustomer = newCustomerDto(
            id = doc.id,
            name = doc.get('name'),
            address = doc.get('address'),      
            location = doc.get('location'),
            addedDate = addedDate,
            updateDate = updateDate,
            added = doc.get('added'),
            note = doc.get('note'),
            phone = doc.get('phone'),
            pic = doc.get('pic'),
            user_id = doc.get('user_id')
        )
        newcustomers.append(newcustomer)
    
    sorted_newcustomers = sorted(newcustomers, key=lambda x: x.address)

    if request.method == 'POST':
        address_filter = request.POST.get('addressFilter')
        if address_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if address_filter.lower() in newcustomer.address.lower()]

        name_filter = request.POST.get('nameFilter')
        if name_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if name_filter.lower() in newcustomer.name.lower()]

        pic_filter = request.POST.get('picFilter')
        if pic_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if pic_filter.lower() in newcustomer.pic.lower()]

        phone_filter = request.POST.get('phoneFilter')
        if phone_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if phone_filter.lower() in newcustomer.phone.lower()]

        user_filter = request.POST.get('userFilter')
        if user_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if user_filter.lower() in newcustomer.user_id.lower()]

        added_filter = request.POST.get('addedFilter')
        if added_filter:
            sorted_newcustomers = [newcustomer for newcustomer in sorted_newcustomers if added_filter.lower() in newcustomer.added.lower()]

        sortType_filter = request.POST.get('sortTypeFilter')
        sort_filter = request.POST.get('sortFilter')
        if sort_filter == 'pic':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.pic.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.pic.lower(), reverse=True)
        elif sort_filter == 'name':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.name.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.name.lower(), reverse=True)
        elif sort_filter == 'address':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.address.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.address.lower(), reverse=True)
        elif sort_filter == 'phone':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.phone.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.phone.lower(), reverse=True)
        if sort_filter == 'addedDate':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.addedDate.replace(tzinfo=None) if x.addedDate else datetime.min)
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.addedDate.replace(tzinfo=None) if x.addedDate else datetime.max, reverse=True)
        if sort_filter == 'updateDate':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.updateDate.replace(tzinfo=None) if x.updateDate else datetime.min)
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.updateDate.replace(tzinfo=None) if x.updateDate else datetime.max, reverse=True)
        elif sort_filter == 'location':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.location)
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.location, reverse=True)
        elif sort_filter == 'note':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.note.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.note.lower(), reverse=True)
        elif sort_filter == 'added':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.added.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.added.lower(), reverse=True)
        elif sort_filter == 'user_id':
            if sortType_filter == 'asc':
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.user_id.lower())
            else:
                sorted_newcustomers = sorted(sorted_newcustomers, key=lambda x: x.user_id.lower(), reverse=True)

    if request.method == 'POST':
        newcustomerFilter = newCustomerFilterDto(
            nameFilter=request.POST.get('nameFilter'),
            addressFilter=request.POST.get('addressFilter'),
            phoneFilter=request.POST.get('phoneFilter'),
            picFilter=request.POST.get('picFilter'),
            userFilter=request.POST.get('userFilter'),
            addedFilter=request.POST.get('addedFilter'),
            sortTypeFilter=request.POST.get('sortTypeFilter'),
            sortFilter=request.POST.get('sortFilter')
        )
    else:
        newcustomerFilter = newCustomerFilterDto(
            nameFilter='',
            addressFilter='',
            phoneFilter='',
            picFilter='',
            userFilter='',
            addedFilter='false',
            sortTypeFilter='desc',
            sortFilter='addedDate'
        )

    coordinates = []
    for newcustomer in sorted_newcustomers:
        location = newcustomer.location.split(",")
        description = newcustomer.name + '<br>' + newcustomer.address + "<br>" + newcustomer.pic + '(' + newcustomer.phone + ')<br>' + str(newcustomer.addedDate.strftime('%H:%M:%S')) + "(" + str(newcustomer.updateDate.strftime('%H:%M:%S')) + ")" + "<br>" + newcustomer.note
        lat = location[0]
        lng = location[1]
        coordinates.append({
            'description': escapejs(description),
            'lat': lat,
            'lng': lng
        })

    return render(request, 'cnvadmin/newcustomer_map.html', {'coordinates': coordinates, 'newcustomerFilter': newcustomerFilter})

def newcustomer_delete(request):
    newcustomerId = request.GET.get('id')  
    return render(request, 'cnvadmin/newcustomer_delete.html', {'visitId': newcustomerId})

def location_map(request):
    locationDocs = db.collection('locations').stream()
    locationDataDict = {}

    for locationDoc in locationDocs:
        locationData = locationDoc.to_dict()
        customerCode = locationData.get('customerCode')
        if customerCode is not None:
            if customerCode not in locationDataDict:
                locationDataDict[customerCode] = []
                locationDataDict[customerCode].append(locationData)
        
    # Connect to your postgres DB
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
        SELECT 
            customer.id,
            customer.address, 
            customer.contact_person,
            customer.name,
            customer.no_telp,
            master_list.name,
            customer.reference_code
        FROM
            customer JOIN master_list on (customer.master_list_id = master_list.id)
        ORDER BY
            master_list.name, 
            customer.reference_code,
            customer.postal_code,
            customer.address,
            customer.name
        """
    # Execute a query
    cur.execute(customerQuery)
    # Retrieve query results
    records = cur.fetchall()

    customers = []
    for row in records:
        customerCode = str(row[0])
        location = ''
        
        if customerCode in locationDataDict:
            locationData = locationDataDict[customerCode]
            location = locationData[0].get('location')

            customer = customerDto(
                id = row[0],
                address = row[1],
                contact_person = row[2],
                name = row[3],
                no_telp = row[4],
                master_list=row[5],          
                last_complete=None,
                last_duedate=None,
                last_invoice=None,
                last_count_days=None,          
                raport='',
                last_order='',
                raport_string='',
                last_delivery='',
                last_payment='',
                debt='',
                payment_details='',
                debt_sort_last=None,
                debt_sort_first=None,
                payment_details_sort_first=None,
                payment_details_sort_last=None,
                master_list_order=row[5] + '-99999',
                location=location,
                status_id=row[CUSTOMERQUERY_APPROVAL_STATUS_NAME]
            )
            if row[6] is not None:
                customer.master_list_order = row[5] + '-' + row[6]

            customers.append(customer)

        if request.method == 'POST':
            id_filter = request.POST.get('idFilter')
            if id_filter:
                customers = [customer for customer in customers if id_filter.lower() in customer.id.lower()]

            name_filter = request.POST.get('nameFilter')
            if name_filter:
                customers = [customer for customer in customers if name_filter.lower() in customer.name.lower()]

            address_filter = request.POST.get('addressFilter')
            if address_filter:
                customers = [customer for customer in customers if address_filter.lower() in customer.address.lower()]

            pic_filter = request.POST.get('picFilter')
            if pic_filter:
                customers = [customer for customer in customers if pic_filter.lower() in customer.contact_person.lower()]

            phone_filter = request.POST.get('phoneFilter')
            if phone_filter:
                customers = [customer for customer in customers if phone_filter.lower() in customer.phone.lower()]

            master_list_filter = request.POST.get('masterlistFilter')
            if master_list_filter:
                customers = [customer for customer in customers if master_list_filter.lower() in customer.master_list_order.lower()]

        if request.method == 'POST':
            customerFilter = customerFilterDto(
                dateFilter= '',
                idFilter = '',
                nameFilter = request.POST.get('nameFilter'),
                addressFilter = request.POST.get('addressFilter'),
                picFilter = request.POST.get('picFilter'),
                phoneFilter = request.POST.get('phoneFilter'),
                masterlistFilter = request.POST.get('masterlistFilter'),
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
                raportFilter = '',
                sortTypeFilter = '',
                sortFilter = '',
            )
        else:
            customerFilter = customerFilterDto(
                dateFilter='',
                idFilter = '',
                nameFilter = '',
                addressFilter = '',
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
                raportFilter='',
                sortTypeFilter='',
                sortFilter=''
            )      

    coordinates = []
    colorSwitch = "red"
    for customer in customers:
            location = customer.location.split(",")
            description = customer.master_list_order + '<br>' + str(customer.id) + '<br>' + customer.address + "<br>" + customer.name
            lat = location[0]
            lng = location[1]
            coordinates.append({
                'description': escapejs(description),
                'lat': lat,
                'lng': lng,
            })

    return render(request, 'cnvadmin/location_map.html', {'coordinates': coordinates, 'customerFilter':customerFilter})

def calc_dist(lat_a, long_a, lat_b, long_b):
    # Radius of the Earth in kilometers
    earth_radius_km = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat_a = radians(lat_a)
    long_a = radians(long_a)
    lat_b = radians(lat_b)
    long_b = radians(long_b)

    # Haversine formula to calculate the distance
    dlon = long_b - long_a
    dlat = lat_b - lat_a

    a = sin(dlat / 2)**2 + cos(lat_a) * cos(lat_b) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Calculate the distance in kilometers
    distance_km = earth_radius_km * c

    # Convert the distance to meters
    distance_meters = distance_km * 1000.0

    return distance_meters
from datetime import datetime, timedelta
from sre_parse import ESCAPES
from firebase_admin import firestore
from django.shortcuts import render
import pytz
from cnvadmin.dto.dto import visitDto, visitFilterDto
from django.utils.safestring import mark_safe
from django.template.defaultfilters import escapejs

# Create a Firestore client
db = firestore.client()

def map_view(request):
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


        visit = visitDto(
            id = doc.id,
            customerCode = int(doc.get('customerCode')),
            address = doc.get('address'),      
            area = doc.get('area'),
            daerah = '',
            isSkip = False,
            skipTime= skipTime,
            checkInLocation = doc.get('checkInLocation'),
            checkInTime = checkInTime,
            checkInDistance=0,
            checkOutLocation = doc.get('checkOutLocation'),
            checkOutTime = checkOutTime,
            checkOutDistance=0,
            date = doc.get('date'),
            isCheckIn = doc.get('isCheckIn'),
            isCheckOut = doc.get('isCheckOut'),
            note = '',
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
            location = doc.get('location')
        )
        if "note" in doc.to_dict() and doc.get('note') is not None:
            visit.note=doc.get('note')
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

        visits.append(visit)
    
    sorted_visits = sorted(visits, key=lambda x: x.checkInTime.replace(tzinfo=None) if x.checkInTime else datetime.min)

    distinct_names = set(item.user_id for item in visits)
    distinct_names_list = list(distinct_names)

    if request.method == 'POST':
        address_filter = request.POST.get('addressFilter')
        if address_filter:
            sorted_visits = [visit for visit in sorted_visits if address_filter.lower() in visit.address.lower()]

        daerah_filter = request.POST.get('daerahFilter')
        if daerah_filter:
            sorted_visits = [visit for visit in sorted_visits if daerah_filter.lower() in visit.daerah.lower()]

        name_filter = request.POST.get('nameFilter')
        if name_filter:
            sorted_visits = [visit for visit in sorted_visits if name_filter.lower() in visit.pic.lower()]

        area_filter = request.POST.get('areaFilter')
        if area_filter:
            sorted_visits = [visit for visit in sorted_visits if area_filter.lower() in visit.area.lower()]

        customerCode_filter = request.POST.get('customerCodeFilter')
        if customerCode_filter:
            sorted_visits = [visit for visit in sorted_visits if customerCode_filter.lower() in visit.customerCode.lower()]

        phone_filter = request.POST.get('phoneFilter')
        if phone_filter:
            sorted_visits = [visit for visit in sorted_visits if phone_filter.lower() in visit.phone.lower()]

        user_filter = request.POST.get('userFilter')
        if user_filter:
            sorted_visits = [visit for visit in sorted_visits if user_filter.lower() in visit.user_id.lower()]
    else:        
        if len(distinct_names_list) > 0:
            user_filter = distinct_names_list[0]
            if user_filter:
                sorted_visits = [visit for visit in sorted_visits if user_filter.lower() in visit.user_id.lower()]

    if request.method == 'POST':
        visitFilter = visitFilterDto(
            dateFilter=valueDate,
            nameFilter=request.POST.get('nameFilter'),
            addressFilter=request.POST.get('addressFilter'),
            areaFilter=request.POST.get('areaFilter'),
            daerahFilter=request.POST.get('daerahFilter'),
            customerCodeFilter=request.POST.get('customerCodeFilter'),
            phoneFilter=request.POST.get('phoneFilter'),
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
            userFilter=request.POST.get('userFilter'),
            noteFilter='',
            checkInFilter=request.POST.get('checkInFilter'),
            checkOutFilter=request.POST.get('checkOutFilter'),
            distanceFilter=request.POST.get('distanceFilter'),
            skipFilter='False',
            sortTypeFilter='Asc',
            sortFilter='area'
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
            distanceFilter='all',
            userFilter='',
            noteFilter='',
            checkInFilter='all',
            checkOutFilter='all',
            skipFilter='False',
            sortTypeFilter='Asc',
            sortFilter='area'
        )      

    coordinates = []    
    uncheckCoordinates = []
    for visit in sorted_visits:
        if (visit.checkInLocation != '' and visit.isCheckIn == True):
            location = visit.checkInLocation.split(",")
            checkInTime = str(visit.checkInTime.strftime('%H:%M:%S'))
            checkOutTime = str(visit.checkOutTime.strftime('%H:%M:%S')) if visit.checkOutTime != '' else '-'
            description = f"{visit.pic}<br>{visit.user_id}<br>{visit.address}<br>{visit.daerah}<br>Check-In: {checkInTime}<br>Check-Out: {checkOutTime}<br>{visit.note}"
            lat = location[0]
            lng = location[1]
            coordinates.append({
                'description': escapejs(description),
                'lat': lat,
                'lng': lng,
            })
                  
        if (visit.isCheckIn == False and visit.location != ''):
            location = visit.location.split(",")
            description = f"{visit.pic}<br>{visit.user_id}<br>{visit.address}<br>{visit.daerah}<br>Not Visited Yet"
            lat = location[0]
            lng = location[1]
            uncheckCoordinates.append({
                'description': escapejs(description),
                'lat': lat,
                'lng': lng,
            })
               
    return render(request, 'cnvadmin/map.html', {'coordinates': coordinates, 'uncheckCoordinates': uncheckCoordinates, 'assignment': distinct_names_list, 'visitFilter': visitFilter})

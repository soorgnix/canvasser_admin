class customerDto:
    def __init__(self, id, address, contact_person, name, no_telp, daerah, master_list, last_invoice, last_complete, last_duedate, raport, last_order, last_count_days, raport_string,last_delivery,last_payment,debt, payment_details, debt_sort_first,debt_sort_last,payment_details_sort_first,payment_details_sort_last, master_list_order, location, status_id):
        self.id = id
        self.address = address
        self.contact_person = contact_person
        self.name = name
        self.no_telp = no_telp
        self.daerah = daerah
        self.master_list = master_list
        self.last_invoice = last_invoice
        self.last_complete = last_complete
        self.last_duedate = last_duedate
        self.raport = raport
        self.last_order = last_order
        self.last_count_days = last_count_days
        self.raport_string = raport_string
        self.last_delivery = last_delivery
        self.last_payment = last_payment
        self.payment_details = payment_details
        self.payment_details_sort_first = payment_details_sort_first
        self.payment_details_sort_last = payment_details_sort_last
        self.debt = debt
        self.debt_sort_first = debt_sort_first
        self.debt_sort_last = debt_sort_last
        self.master_list_order = master_list_order
        self.location = location
        self.status_id = status_id        


class visitDto:
    def __init__(self, id, address, area,daerah, isSkip, skipTime, checkInLocation,checkInTime,checkInDistance,checkOutLocation,checkOutTime,checkOutDistance,customerCode,date,isCheckIn,isCheckOut,note,phone,pic,user_id,last_invoice,last_complete,last_duedate,raport,last_order,last_count_days,last_delivery,last_payment,debt, payment_details, master_list_order, location):
        self.id = id
        self.address = address        
        self.area = area
        self.daerah = daerah
        self.isSkip = isSkip
        self.skipTime = skipTime
        self.checkInLocation = checkInLocation
        self.checkInTime = checkInTime
        self.checkInDistance = checkInDistance
        self.checkOutLocation = checkOutLocation
        self.checkOutTime = checkOutTime
        self.checkOutDistance = checkOutDistance
        self.customerCode = customerCode
        self.date = date
        self.isCheckIn = isCheckIn
        self.isCheckOut = isCheckOut
        self.note = note
        self.phone = phone
        self.pic = pic
        self.user_id = user_id
        self.last_invoice = last_invoice
        self.last_complete = last_complete
        self.last_duedate = last_duedate
        self.raport = raport
        self.last_order = last_order
        self.last_count_days = last_count_days
        self.last_delivery = last_delivery
        self.last_payment = last_payment
        self.payment_details = payment_details
        self.debt = debt
        self.master_list_order = master_list_order
        self.location = location

class customerFilterDto:
    def __init__(self, dateFilter, idFilter, nameFilter, addressFilter, daerahFilter, picFilter, phoneFilter, masterlistFilter, invoiceDateFilter, invoiceDateToFilter, dueDateFilter, dueDateToFilter, deliveryDateFilter, deliveryDateToFilter, completeDateFilter, completeDateToFilter, lastOrderFilter, paymentTypeFilter, paymentDetailsFilter, debtFilter, raportFilter, statusFilter, sortFilter, sortTypeFilter):
        self.dateFilter = dateFilter
        self.idFilter = idFilter
        self.nameFilter = nameFilter
        self.addressFilter = addressFilter
        self.daerahFilter = daerahFilter
        self.picFilter = picFilter
        self.phoneFilter = phoneFilter
        self.masterlistFilter = masterlistFilter
        self.invoiceDateFilter = invoiceDateFilter
        self.invoiceDateToFilter = invoiceDateToFilter
        self.dueDateFilter = dueDateFilter
        self.dueDateToFilter = dueDateToFilter
        self.deliveryDateFilter = deliveryDateFilter
        self.deliveryDateToFilter = deliveryDateToFilter
        self.completeDateFilter = completeDateFilter
        self.completeDateToFilter = completeDateToFilter
        self.lastOrderFilter = lastOrderFilter
        self.paymentTypeFilter = paymentTypeFilter
        self.paymentDetailsFilter = paymentDetailsFilter
        self.debtFilter = debtFilter
        self.raportFilter = raportFilter
        self.sortFilter = sortFilter
        self.sortTypeFilter = sortTypeFilter
        self.statusFilter = statusFilter

class visitFilterDto:
    def __init__(self, dateFilter, addressFilter, areaFilter, daerahFilter, skipFilter, distanceFilter, customerCodeFilter, phoneFilter, userFilter, checkInFilter, checkOutFilter, invoiceDateFilter, invoiceDateToFilter, dueDateFilter, dueDateToFilter, deliveryDateFilter, deliveryDateToFilter, completeDateFilter, completeDateToFilter, lastOrderFilter, paymentTypeFilter, paymentDetailsFilter, debtFilter, raportFilter, nameFilter, noteFilter, sortFilter, sortTypeFilter):
        self.nameFilter = nameFilter
        self.dateFilter = dateFilter
        self.addressFilter = addressFilter        
        self.areaFilter = areaFilter
        self.daerahFilter = daerahFilter
        self.customerCodeFilter = customerCodeFilter
        self.phoneFilter = phoneFilter
        self.invoiceDateFilter = invoiceDateFilter
        self.invoiceDateToFilter = invoiceDateToFilter
        self.dueDateFilter = dueDateFilter
        self.dueDateToFilter = dueDateToFilter
        self.deliveryDateFilter = deliveryDateFilter
        self.deliveryDateToFilter = deliveryDateToFilter
        self.completeDateFilter = completeDateFilter
        self.completeDateToFilter = completeDateToFilter
        self.lastOrderFilter = lastOrderFilter
        self.paymentTypeFilter = paymentTypeFilter
        self.paymentDetailsFilter = paymentDetailsFilter
        self.debtFilter = debtFilter
        self.raportFilter = raportFilter
        self.userFilter = userFilter
        self.noteFilter = noteFilter
        self.checkInFilter = checkInFilter
        self.checkOutFilter = checkOutFilter
        self.skipFilter = skipFilter
        self.distanceFilter = distanceFilter
        self.sortFilter = sortFilter
        self.sortTypeFilter = sortTypeFilter

class newCustomerDto:
    def __init__(self, id, name, address, addedDate, updateDate, note, phone, pic, location, user_id, added):
        self.id = id
        self.name = name
        self.address = address        
        self.addedDate = addedDate
        self.updateDate = updateDate
        self.location = location
        self.note = note
        self.phone = phone
        self.pic = pic
        self.user_id = user_id
        self.added = added

class newCustomerFilterDto:
    def __init__(self, addressFilter, phoneFilter, userFilter, picFilter, nameFilter, addedFilter, sortFilter, sortTypeFilter):
        self.nameFilter = nameFilter
        self.addressFilter = addressFilter        
        self.addedFilter = addedFilter
        self.phoneFilter = phoneFilter
        self.userFilter = userFilter
        self.picFilter = picFilter
        self.sortFilter = sortFilter
        self.sortTypeFilter = sortTypeFilter
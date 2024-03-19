class customerDto:
    def __init__(self, id, address, contact_person, name, no_telp, daerah, master_list, last_invoice, last_complete, last_duedate, raport, last_order, last_count_days, raport_string,last_delivery,last_payment,debt, payment_details, debt_sort_first,debt_sort_last,payment_details_sort_first,payment_details_sort_last, master_list_order, location, status_id, delivery_date, delivery_status, driver_name):
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
        self.delivery_date = delivery_date
        self.delivery_status = delivery_status
        self.driver_name = driver_name

class customerFilterDto:
    def __init__(self, dateFilter, idFilter, nameFilter, addressFilter, daerahFilter, picFilter, phoneFilter, masterlistFilter, invoiceDateFilter, invoiceDateToFilter, dueDateFilter, dueDateToFilter, deliveryDateFilter, deliveryDateToFilter, completeDateFilter, completeDateToFilter, lastOrderFilter, paymentTypeFilter, paymentDetailsFilter, debtFilter, raportFilter, statusFilter, sortFilter, sortTypeFilter, deliverySheetDateFilter, deliverySheetDateToFilter, driverNameFilter):
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
        self.deliverySheetDateFilter = deliverySheetDateFilter
        self.deliverySheetDateToFilter = deliverySheetDateToFilter
        self.driverNameFilter = driverNameFilter

class customerMapFilterDto:
    def __init__(self, idFilter, nameFilter, addressFilter, daerahFilter, picFilter, phoneFilter, masterlistFilter, invoiceDateFilter, invoiceDateToFilter, dueDateFilter, dueDateToFilter, deliveryDateFilter, deliveryDateToFilter, completeDateFilter, completeDateToFilter, lastOrderFilter, paymentTypeFilter, paymentDetailsFilter, debtFilter, raportFilter, statusFilter,deliverySheetDateFilter, deliverySheetDateToFilter, driverNameFilter):
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
        self.statusFilter = statusFilter
        self.deliverySheetDateFilter = deliverySheetDateFilter
        self.deliverySheetDateToFilter = deliverySheetDateToFilter
        self.driverNameFilter = driverNameFilter

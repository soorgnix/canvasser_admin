class DBQueryIndex:
    class CustomerQuery:
        customer_id = 0
        customer_address = 1
        customer_contact_person = 2
        customer_name = 3
        customer_no_telp = 4
        customer_daerah = 5
        master_list_name = 6
        sales_order_id = 7
        sales_order_date = 8
        sales_order_delivery_date = 9
        sales_order_invoice_id = 10
        sales_order_invoice_date = 11
        sales_order_invoice_due_date = 12
        sales_order_invoice_date_completed = 13
        sales_order_total = 14
        sales_order_status_id = 15
        approval_status_name = 16
        payment_method_name = 17
        sales_order_invoice_invoice_number = 18
        customer_reference_code = 19
        delivery_date = 20
        delivery_status = 21
        driver_name = 22
        total_payment_amount = 23

    class ItemQuery:
        sales_order_detail_sales_order_id = 0
        sales_order_detail_id = 1
        item_name = 2
        sales_order_detail_quantity = 3
        sales_order_detail_price = 4

    class DebtQuery:
        customer_id = 0
        sales_order_id = 1
        sales_order_date = 2
        sales_order_delivery_date = 3
        sales_order_invoice_id = 4
        sales_order_invoice_date = 5
        sales_order_invoice_due_date = 6
        sales_order_invoice_total = 7
        payment_method_name = 8
        sales_order_invoice_invoice_number = 9
        total_payment_amount = 10
        debt = 11
  
    class PaymentDetailsQuery:
        customer_id = 0
        sales_order_id = 1
        sales_order_invoice_id = 2
        sales_order_invoice_date = 3
        sales_order_payment_date = 4
        sales_order_payment_amount = 5
        sales_order_payment_description = 6
        total_payment_amount = 7
    
    class InactiveCustomerQuery:
        customer_id = 0
        customer_address = 1
        customer_contact_person = 2
        customer_name = 3
        customer_no_telp = 4
        customer_daerah = 5
        master_list_name = 6
        customer_reference_code = 7  
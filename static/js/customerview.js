// Update the customer table based on the selected date
function updateCustomerList(selectedDate) {
    // Get the customer table element
    const customerTable = document.querySelector('table');
  
    // Clear the existing table rows
    customerTable.innerHTML = '';
  
    // Make an AJAX request to fetch the filtered customer data based on the selected date
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `/fetch_customers?selected_date=${selectedDate}`);
    xhr.onload = function() {
      if (xhr.status === 200) {
        const customers = JSON.parse(xhr.responseText);
  
        // Generate the table rows for each customer
        customers.forEach(function(customer) {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td><input type="checkbox" name="selected_items" value="${customer.id}"></td>
            <td>${customer.id}</td>
            <td>${customer.address}</td>
            <td>${customer.name}</td>
            <td>${customer.contact_person}</td>
            <td>${customer.no_telp}</td>
            <td>${customer.sub_district_id}</td>
          `;
          customerTable.appendChild(row);
        });
      } else {
        console.error('Error fetching customer data');
      }
    };
    xhr.send();
  }
  
  // Get the default selected date
  const defaultSelectedDate = new Date().toISOString().slice(0, 10);
  
  // Set the default selected date to the input field
  document.getElementById('selectedDate').value = defaultSelectedDate;
  
  // Update the customer list with the default selected date
  updateCustomerList(defaultSelectedDate);
  
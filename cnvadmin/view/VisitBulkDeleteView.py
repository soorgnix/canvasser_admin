from datetime import datetime, timedelta
from django.shortcuts import render
from firebase_admin import firestore

# Create a Firestore client
db = firestore.client()

def visit_bulk_delete(request):
    if request.method == 'POST':
        # Get the selected date from the form        
        valueDate = request.POST.get('dateFilter')

        selected_date = datetime.strptime(valueDate, '%Y-%m-%d')       
        selected_range_date = selected_date + timedelta(days=1)

        selected_user = request.POST.get('userFilter')
            
        docs = db.collection('visits').where('date', '>=', selected_date).where('date', '<', selected_range_date).stream()

        for doc in docs:
            if doc.get('user_id').lower() == selected_user.lower() or selected_user.lower() == 'all':
                doc_ref = db.collection('visits').document(doc.id)                
                doc_ref.delete()
            
    return render(request, 'cnvadmin/visit_bulk_delete.html')
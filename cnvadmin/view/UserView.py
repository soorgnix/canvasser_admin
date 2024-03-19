from django.shortcuts import render
from firebase_admin import firestore

from cnvadmin.dto.UsersDto import userFilterDto, userDto

# Create a Firestore client
db = firestore.client()

def user_list(request):   
    docs = db.collection('users').stream()

    users = []
    for doc in docs:
        user = userDto(
            id = doc.id,
            email=doc.get('email'),
            phone = doc.get('phone'),      
            deleted = doc.get('deletedFlag')
        )
        users.append(user)
    
    sorted_users = sorted(users, key=lambda x: x.email)

    if request.method == 'POST':
        email_filter = request.POST.get('emailFilter')
        if email_filter:
            sorted_users = [user for user in sorted_users if email_filter.lower() in user.email.lower()]

        deleted_filter = request.POST.get('deletedFilter')
        if deleted_filter == "True":
            sorted_users = [user for user in sorted_users if user.deleted]
        else:
            sorted_users = [user for user in sorted_users if not user.deleted]

    if request.method == 'POST':
        userFilter = userFilterDto(
            emailFilter=request.POST.get('emailFilter'),
            deletedFilter=request.POST.get('deletedFilter')
        )
    else:
        userFilter = userFilterDto(
            emailFilter='',
            deletedFilter='False'
        )

    return render(request, 'cnvadmin/user_list.html', {'users': sorted_users, 'userFilter':userFilter})

def user_edit(request):
    userId = request.GET.get('id')
   
    doc = db.collection('users').document(userId).get()

    user = userDto(
        id = doc.id,
        email = doc.get('email'),
        deleted = doc.get('deletedFlag'),
        phone = doc.get('phone')
    )
  
    return render(request, 'cnvadmin/user_edit.html', {'user': user})

def user_edit_execute(request):
    if request.method == 'POST':
        userId = request.POST.get('Id')
        deleted = request.POST.get('deleted')
        phone = request.POST.get('phone')             
        
        doc_ref = db.collection('users').document(userId)
        if request.POST.get('deleted') == "True":
            doc_ref.update({'deletedFlag': True, 'phone': phone})
        else:
            doc_ref.update({'deletedFlag': False, 'phone': phone})

        return render(request, 'cnvadmin\success.html')
    else:
        return render(request, 'cnvadmin\checkbox.html')

def user_add(request):
    return render(request, 'cnvadmin/user_add.html')

def user_add_execute(request):
    if request.method == 'POST':
        deleted = request.POST.get('deleted') == 'True'
        phone = request.POST.get('phone')             
        email = request.POST.get('email')             
        
        doc_ref = db.collection('users').document()
        doc_ref.set({'email': email, 'deletedFlag': deleted, 'phone': phone})

        return render(request, 'cnvadmin\success.html')
    else:
        return render(request, 'cnvadmin\checkbox.html')

"""
URL configuration for canvas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from cnvadmin import views
from cnvadmin.firestore import newcustomer_delete_execute, newcustomer_edit_execute, save_selected_items, set_location, visit_delete_execute, visit_edit_execute
from cnvadmin.view import ReportsView
from cnvadmin.view import VisitBulkDeleteView
from cnvadmin.view import UserView
from cnvadmin.view import VisitView
from cnvadmin.view import CustomerView
from cnvadmin.view import WhatsAppView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customer/', CustomerView.customer_list, name='customer_list'),
    path('customer_location/edit', CustomerView.customer_location_edit, name='customer_location_edit'),
    path('customer_location_edit_execute/', CustomerView.customer_location_edit_execute, name='customer_location_edit_execute'),
    path('customer_map/', CustomerView.customer_map, name='customer_map'),
    path('save_selected_items/', save_selected_items, name='save_selected_items'),
    path('set_location/', set_location, name='set_location'),
    path('visit/', views.visit_list, name='visit_list'),
    path('visit/edit', views.visit_edit, name='visit_edit'),
    path('visit_edit_execute/', visit_edit_execute, name='visit_edit_execute'),
    path('visit/delete', views.visit_delete, name='visit_delete'),
    path('visit_delete_execute/', visit_delete_execute, name='visit_delete_execute'),
    path('visit_bulk_delete/', VisitBulkDeleteView.visit_bulk_delete, name='visit_bulk_delete'),
    path('newcustomer/', views.newcustomer_list, name='newcustomer_list'),
    path('newcustomer/edit', views.newcustomer_edit, name='newcustomer_edit'),
    path('newcustomer_edit_execute/', newcustomer_edit_execute, name='newcustomer_edit_execute'),
    path('newcustomer/delete', views.newcustomer_delete, name='newcustomer_delete'),
    path('newcustomer_delete_execute/', newcustomer_delete_execute, name='newcustomer_delete_execute'),
    path('map/', VisitView.map_view, name='map'),
    path('newcustomer_map/', views.newcustomer_map_view, name='newcustomer_map'),
    path('reports/', ReportsView.reports, name='reports'),
    path('reports2/', ReportsView.reports2, name='reports2'),
    path('users/', UserView.user_list, name='user_list'),
    path('user/edit', UserView.user_edit, name='user_edit'),
    path('user_edit_execute', UserView.user_edit_execute, name='user_edit_execute'),
    path('user/add', UserView.user_add, name='user_add'),
    path('user_add_execute', UserView.user_add_execute, name='user_add_execute'),
    path('whatsapp/', WhatsAppView.whatsapp_view, name='whatsapp_view'),
    path('whatsapp_set_message', WhatsAppView.whatsapp_set_message, name='whatsapp_set_message'),
    path('whatsapp_execute', WhatsAppView.whatsapp_execute, name='whatsapp_execute')
]
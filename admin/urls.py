from django.urls import path
from . import views


urlpatterns = [
    path('request_service/<int:user_id>/<str:user_type>/<str:status_type>', views.RequestServiceListView.as_view(), name='dashboard'),
    path('client_request_service/<str:request_type>', views.ServiceRequestListView.as_view(), name='client_request_dashboard'),
    path('request_detail/<str:request_number>', views.RequestDetailUpdateView.as_view(), name='admin-request-detail'),
    # path('list', views.AdminListView.as_view(), name='list_of_admin'),
    path('client-list/', views.ClientListView.as_view(), name='list_of_client'),
    path('client-service-list/<pk>', views.ClientRequestServicesListView.as_view(), name='list_of_client_services'),
    path('client-folder-list/<pk>', views.FolderListView.as_view(), name='list_of_client_folders'),
    path('client-folder/<str:request_number>', views.FolderCreateView.as_view(), name='admin_service_folder_action'),
    path('complaints', views.ComplaintsListView.as_view(), name='client_complaints'),
    path('ws/chat', views.ChatView.as_view(), name='chat'),
    path('mark_messages_as_seen/<int:thread_id>/', views.mark_messages_as_seen, name='mark_messages_as_seen'),
    path('clear-session/<str:role>/', views.ClearSessionView.as_view(), name='clear_session'),

    #superadmin
    path('<str:user_type>/', views.SuperAdminClientEmployeeList.as_view(), name='user_employee_list'),
    path('client-form', views.ClientSignupView.as_view(), name='client_create_form'),
    path('employee-form', views.AdminSignupView.as_view(), name='employee_create_form'),
    path('client-update/<int:pk>/', views.ClientUpdateView.as_view(), name='client_update'),
    path('employee-update/<int:pk>/', views.AdminUpdateView.as_view(), name='employee_update'),
    path('delete_user/<str:user_type>/<int:pk>/', views.UserDeleteView.as_view(), name='delete_user'),   
    path('dashboard', views.DashboardView.as_view(), name='s_dashboard'),  
    path('pie_chart_dashboard', views.PiechartDashboard.as_view(), name='pie_chart_dashboard'),  
    path('manage-service', views.ManageServiceSubServiceView.as_view(), name='manage_services_subservices'),  

    path('invoice-list/<str:status>', views.InvoiceRecordListView.as_view(), name='invoice_list'),   
    path('invoice-preview/<pk>', views.InvoiceRecordPreview.as_view(), name='invoice_preview'), 
    path('invoice-record', views.InvoiceRecordCreateView.as_view(), name='invoicerecord_form'),  
    path('invoice-record/<pk>', views.InvoiceRecordUpdateView.as_view(), name='invoicerecord_update'),  
]

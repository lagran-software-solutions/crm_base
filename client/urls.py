from django.urls import path
from . import views


urlpatterns = [
    path('service-dashboard', views.ServiceListDashboard.as_view(), name='client_dashboard'),
    path('request-detail/<str:request_number>', views.RequestDetailView.as_view(), name='request-detail'),
    path('request', views.ClientRequestListView.as_view(), name='client_request'),
    path('folder', views.FolderListView.as_view(), name='client_folder'),
    path('folder_action', views.FolderCreateView.as_view(), name='folder_action'),
    path('service_folder_action/<str:request_number>', views.ServiceFolderCreateView.as_view(), name='service_folder_action'),
    path('file/<pk>/<slug>', views.FileUploadView.as_view(), name='file'),
    path('documents/<str:user_id>', views.ClientDocumentListView.as_view(), name='documents'),
    path('service_file/<pk>/<slug>', views.ServiceFileUploadView.as_view(), name='service_file'),
    path('notification/seen/<slug:slug>/', views.MarkNotificationAsSeenView.as_view(), name='mark_notification_seen'),
    path('service_request_chat/<str:request_number>', views.RequestServiceChatCreateView.as_view(), name='service_request_chat'),
    path('complaint', views.ComplaintView.as_view(), name='complaint'),
]

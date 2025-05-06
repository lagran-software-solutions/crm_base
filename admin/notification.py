from client.models import Notification
from django.urls import reverse


def file_upload_client_notification(folder, request_detail_url):
    Notification.objects.create(
        client=folder.client,
        message=f"Admin uploaded file in this folder number({folder.name})",
        url=request_detail_url,
        recipient_type='client'
    )


def file_upload_admin_notification(folder, request_detail_url):
    Notification.objects.create(
        recipient_type='admin',
        admin=folder.admin,
        message=f"Client uploaded file in this folder number({folder.name})",
        url=request_detail_url
    )


def create_new_message_notification(service, request_number, user):
    if user.is_admin:
        request_detail_url = reverse('request-detail', kwargs={'request_number': request_number})
        Notification.objects.create(
            client=service.user,
            message=f"A new message has been sent on this request ({request_number}).",
            url=request_detail_url,
            recipient_type='client'
        )
    else:
        request_detail_url = reverse('admin-request-detail', kwargs={'request_number': request_number})
        Notification.objects.create(
            admin=service.assigned_to_employee,
            message=f"A new message has been sent on this request ({request_number}).",
            url=request_detail_url,
            recipient_type='admin'
        )

# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Thread
from client.models import RequestService, RequestStatus
from django.utils.timezone import now
from threading import local


_request_user = local()

def set_request_user(user):
    _request_user.user = user

def get_request_user():
    return getattr(_request_user, 'user', None)


@receiver(post_save, sender=User)
def create_admin_threads(sender, instance, created, **kwargs):
    if created and instance.is_admin:
        existing_admins = User.objects.filter(is_admin=True)

        for admin in existing_admins:
            if admin != instance:
                Thread.objects.get_or_create(
                    first_person=instance,
                    second_person=admin
                )


@receiver(post_save, sender=RequestService)
def create_request_status(sender, instance, created, **kwargs):
    user = kwargs.get('user')
    
    if user:  
        employee = instance.assigned_to_employee
        if employee:
            RequestStatus.objects.create(
                request_number=instance,
                employee=employee,
                last_update=now(),
                status=instance.status,
                comment=f"Request updated by {user.first_name}" 
            )

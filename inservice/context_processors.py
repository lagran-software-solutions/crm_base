from . import models
from client.models import Notification
from admin.forms import FilterModelForm
from inservice.models import User, Thread,Footer,Team

def get_notifications(user):
    if user.is_admin:
        all_notification = Notification.objects.filter(admin__isnull=True, is_seen=False, recipient_type='admin')\
            .order_by('-created_at')
        notifications = Notification.objects.filter(admin=user, is_seen=False, recipient_type='admin')\
            .order_by('-created_at')
    else:
        all_notification = Notification.objects.filter(client__isnull=True, is_seen=False, recipient_type='client')\
            .order_by('-created_at')
        notifications = Notification.objects.filter(client=user, is_seen=False, recipient_type='client')\
            .order_by('-created_at')

    total_notifications_count = all_notification.count() + notifications.count()

    return {
        'all_notification': all_notification,
        'notifications': notifications,
        'total_notifications_count': total_notifications_count
    }


def inservice(request):
    user = request.user
    filter_form = FilterModelForm()
    try:
        seo = models.SEO.objects.get(page=request.path)
    except models.SEO.DoesNotExist:
        seo = None

    all_notification, notifications, total_notifications_count = None, None, 0
    total_unseen = 0
    if user.is_authenticated:
        try:
            user = User.objects.get(id=request.user.id)
            notification_data = get_notifications(user)
            all_notification = notification_data['all_notification']
            notifications = notification_data['notifications']
            total_notifications_count = notification_data['total_notifications_count']
            total_unseen = Thread.objects.total_unseen_messages(user)
        except User.DoesNotExist:
            user = None
            total_unseen = 0
            print("User does not exist.")
        except Exception as e:
            print(f"Error retrieving notifications for user {request.user.id}: {e}")

    return {
        'filter_form': filter_form,
        'address': models.Address.objects.first(),
        'banner': models.Banner.objects.all(),
        'footer': models.Footer.objects.all(),
        'seo': seo,
        'all_notification': all_notification,
        'notifications': notifications,
        'total_notifications_count': total_notifications_count,
        'crm_user': user,
        'total_unseen': total_unseen
        
    }


def footer_context(request):
    footer = Footer.objects.all()
    return {"footer": footer}



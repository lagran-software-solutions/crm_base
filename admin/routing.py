from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('crm_admin/ws/chat', consumers.ChatConsumer.as_asgi())
]
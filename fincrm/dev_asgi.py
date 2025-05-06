import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Set the default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincrm.dev_settings')

# Call setup to ensure the app registry is ready before imports
import django
django.setup()

# Now import your routing configurations
from admin.routing import websocket_urlpatterns

# Get the ASGI application
django_asgi_app = get_asgi_application()

# Define the application routing
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )
})

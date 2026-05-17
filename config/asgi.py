import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import app_modules.quiz.routing
from config.middleware import WSLogMiddleware, WSReconnectMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': WSReconnectMiddleware(
        WSLogMiddleware(
            AuthMiddlewareStack(
                URLRouter(
                    app_modules.quiz.routing.websocket_urlpatterns
                )
            )
        )
    ),
})
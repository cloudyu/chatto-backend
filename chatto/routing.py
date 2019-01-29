from channels.routing import ProtocolTypeRouter, URLRouter
import chatto.apps.ws.routing
from chatto.apps.ws.auth import AuthMiddleware
application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AuthMiddleware(
        URLRouter(
            chatto.apps.ws.routing.websocket_urlpatterns
        )
    ),
})

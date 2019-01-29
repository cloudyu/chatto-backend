from django.conf.urls import url

from . import players
websocket_urlpatterns = [
    url(r'^ws/(?P<id>[0-9A-Fa-f-]{36})$', players.PlayerConsumer),
]

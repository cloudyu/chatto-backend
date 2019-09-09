from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^((?P<id>[0-9A-Fa-f-]{36}))(/(?P<cid>[0-9A-Fa-f-]{36}))?', views.GameView.as_view()),
    url(r'^$', views.GamesView.as_view()),
]

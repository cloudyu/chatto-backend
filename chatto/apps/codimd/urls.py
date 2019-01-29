from . import views
from django.conf.urls import url
from rest_framework import routers

router = routers.SimpleRouter(trailing_slash=False)
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token

urlpatterns = [
    url(r'^token$', views.TokenView.as_view()),
    url(r'^profile$', views.ProfileView.as_view()),
    url(r'^((?P<noteId>.+))$', views.CodimdView.as_view()),
]
urlpatterns += router.urls

from chatto.apps.user import views
from django.conf.urls import url
from rest_framework import routers

router = routers.SimpleRouter(trailing_slash=False)
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token

urlpatterns = [
    url(r'^$', views.UserView.as_view()),
    url(r'^callback$', views.OauthView.as_view()),
    url(r'^oauth$', views.oauth_url),


#    url(r'^api-token-verify/', verify_jwt_token),
]
urlpatterns += router.urls

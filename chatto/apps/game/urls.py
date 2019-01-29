from . import views
from django.conf.urls import url

urlpatterns = [
    #url(r'^join(/(?P<id>[0-9A-Fa-f-]{36}))/?', views.ProjectView.as_view()),
    #url(r'^add(/(?P<id>[0-9A-Fa-f-]{36}))/?', views.ProjectView.as_view()),
    #url(r'^record/(?P<id>[0-9A-Fa-f-]{36})', views.RecordView.as_view()),
    #url(r'^attachment/(?P<id>[0-9A-Fa-f-]{36})', views.AttachmentView.as_view()),
    #url(r'^file/(?P<id>[0-9A-Fa-f-]{36})(?P<path>/?.*)', views.FileView.as_view()),
    url(r'^((?P<id>[0-9A-Fa-f-]{36}))(/(?P<cid>[0-9A-Fa-f-]{36}))?', views.GameView.as_view()),
    url(r'^$', views.GamesView.as_view()),
]

# -*- coding: utf-8
from django.conf.urls import *

urlpatterns = patterns('ajax_uploader',
    url(r'^info/$', 'views.info', name='jfu_info'),
    url(r'^upload/$', 'views.upload', name='jfu_upload'),
    url(r'^delete/(?P<pk>\d+)$', 'views.upload_delete', name='jfu_delete'),
)

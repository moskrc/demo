# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import subscribe, success, cancel, failure

urlpatterns = [
    url(r'^subscribe/(?P<plan_id>\d+)/$', subscribe, name='subscribe'),
    url(r'^subscribe/(?P<plan_id>\d+)/success/$', success, name='success'),
    url(r'^subscribe/(?P<plan_id>\d+)/failure/$', failure, name='failure'),
    url(r'^cancel_subscription/$', cancel, name='cancel_subscription'),
]

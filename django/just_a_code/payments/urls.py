# -*- coding: utf-8 -*-

from django.conf.urls import *

urlpatterns = patterns('payments.views',
    url(r'^$', 'index', name='payments_index'),
    url(r'^pay/$', 'pay', name='payments_pay'),
    url(r'^(?P<product_id>[0-9A-Za-z]+)/$', 'pay_product', name='payments_pay_product'),
)


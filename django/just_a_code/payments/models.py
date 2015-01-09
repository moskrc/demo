# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from catalog.models import Product
from model_utils.models import TimeStampedModel

PAYMENT = 1
PURCHASE = 2

OPERATION_TYPES = (
    (PAYMENT, u'Пополнение'),
    (PURCHASE, u'Списание')
)

REGULAR_SERVICE = 1

SERVICE_TYPES = (
    (REGULAR_SERVICE, u'Обычный показ'),
)

class Operation(TimeStampedModel):
    user = models.ForeignKey(User, related_name='payments')
    product = models.ForeignKey(Product, related_name='operations', blank=True, null=True)
    amount = models.DecimalField(u'Сумма', max_digits=10, decimal_places=2 )
    type = models.IntegerField(u'Вид операции', choices=OPERATION_TYPES)
    comment = models.TextField(u'Коментарий', max_length=2000, blank=True)
    days = models.IntegerField(u'Кол-во дней')
    service = models.IntegerField(u'Вид услуги', choices=SERVICE_TYPES)

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return u'%s %s' % (self.user, self.amount)

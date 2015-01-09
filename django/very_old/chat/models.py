# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from model_utils.models import TimeStampedModel
from services.models import Task

class Message(TimeStampedModel):
    task = models.ForeignKey(Task, verbose_name=u'Задача')
    user = models.ForeignKey(User, verbose_name=u'Пользователь')
    body = models.TextField(u'Текст',max_length=2048)
    is_new = models.BooleanField(u'Непрочитанное',default=True)

    def __unicode__(self):
        return u"%s" % self.body

    class Meta:
        ordering = ("created",)
        verbose_name = u'Сообщение'
        verbose_name_plural = u'Сообщения'

# -*- coding: utf-8 -*-

from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from model_utils.models import TimeStampedModel


class Chapter(MPTTModel):
    name = models.CharField(u'Название', max_length=255)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children')
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Раздел'
        verbose_name_plural = u'Разделы'

    class MPTTMeta:
        order_insertion_by = ['name']

    def get_active_questions(self):
        return self.questions.filter(is_active=True)


class Question(TimeStampedModel):
    chapter = TreeForeignKey(Chapter, related_name='question')
    question = models.CharField(u'Вопрос', max_length=255)
    answer = models.TextField(u'Ответ')
    is_active = models.BooleanField(u'Отображать на сайте', default=True)
    is_for_registered_users = models.BooleanField(u'Только для зарегистрированных', default=False)
    collapsed = models.BooleanField(u'Отображать свернутым', default=True)

    class Meta:
        verbose_name = 'Вопрос / Ответ'
        verbose_name_plural = 'Вопросы и ответы'
        ordering = ['id']

    def __unicode__(self):
        return self.question


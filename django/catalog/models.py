#coding=utf8
from datetime import datetime
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django_extensions.db.models import TimeStampedModel
from common.utils import make_uniq_key

class ActiveItemManager(models.Manager):
    def get_queryset(self):
        return super(ActiveItemManager, self).get_queryset().filter(is_active=True, site=Site.objects.get_current())


class Item(TimeStampedModel):
    title = models.CharField(u'Название', max_length=255, help_text=u'Краткое описание вакансии')
    description = models.TextField(u'Полное описание')
    email = models.EmailField(u'Контактный E-mail', help_text=u'Только для получения анкет, не публикуется на сайте')
    salary = models.CharField(u'Заработная плата', max_length=255, help_text=u'Фиксированная сумма или диапазон, может оставаться пустым, не забывайте указывать знак валюты - это важно! ')
    on_site = models.BooleanField(u'Это работа только в офисе', default=False)
    city = models.CharField(u'Город', max_length=255, blank=True, null=True, help_text=u'В каком городе находится офис')
    employer_name = models.CharField(u'Название', max_length=255, blank=True, null=True, help_text=u'Название вашей компании или стартапа')
    employer_description = models.TextField(u'Описание', blank=True, null=True, help_text=u'Ваше краткое описание')
    employer_website = models.URLField(u'Сайт', blank=True, null=True)
    secret_key = models.CharField(max_length=255, blank=True)
    not_sended = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    site = models.ForeignKey(Site)

    objects = models.Manager()
    active_objects = ActiveItemManager()


    def __unicode__(self):
        return self.title

    class Meta:
        pass

@receiver(pre_save, sender=Item)
def make_secret_key(sender, instance=None, **kwargs):
    if not instance.pk:
        instance.secret_key = make_uniq_key()[:4]

@receiver(post_save, sender=Item)
def send_info(sender, instance=None, created=False, **kwargs):
    if created:
        c = {
            'site': Site.objects.get_current(),
            'item': instance,
        }

        subject = render_to_string('catalog/email/item_subject.txt', c)
        html_body = render_to_string('catalog/email/item_body.html', c)
        text_body = strip_tags(html_body)

        msg = EmailMultiAlternatives(subject, text_body, None, instance.email.split(','))
        msg.attach_alternative(html_body, "text/html")
        msg.send()


class Application(TimeStampedModel):
    item = models.ForeignKey(Item)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    about = models.TextField(max_length=2048)

    def __unicode__(self):
        return self.name

    class Meta:
        pass


@receiver(post_save, sender=Application)
def send_application(sender, instance=None, created=False, **kwargs):
    if created:
        c = {
            'site': Site.objects.get_current(),
            'application': instance,
        }

        subject = render_to_string('catalog/email/application_subject.txt', c)
        html_body = render_to_string('catalog/email/application_body.html', c)
        text_body = strip_tags(html_body)

        msg = EmailMultiAlternatives(subject, text_body, instance.email, instance.item.email.split(','))
        msg.attach_alternative(html_body, "text/html")
        msg.send()

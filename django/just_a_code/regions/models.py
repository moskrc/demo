# -*- coding: utf-8
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django_geoip.models import GeoLocationFacade, Region
from model_utils.models import TimeStampedModel
from yandex_geo import geocode

class GeoLocation(GeoLocationFacade):
    """ Location is almost equivalent of geographic City.
        Major difference is that only locations
        from this model are returned by high-level API, so you can
        narrow down the list of cities you wish to display on your site.
    """
    name = models.CharField(u'Название', max_length=100)
    region = models.OneToOneField(Region, related_name='my_custom_location', verbose_name=u'Регион')
    is_default = models.BooleanField(u'По умолчанию', default=False)

    lat = models.FloatField(u'Широта', default=0, blank=True, null=True)
    lng = models.FloatField(u'Долгота', default=0, blank=True, null=True)
    zoom = models.IntegerField(u'Приближение',default=13)
    biggest_city = models.CharField(u'Центр. город', max_length=255)

    metro = models.BooleanField(u'Есть метро', default=False)
    subdomain = models.CharField(u'Поддомен', max_length=255, blank=True, null=True)
    weight = models.IntegerField(u'Вес', default=0, help_text=u'Чем меньше число тем выше в списке')

    description = models.TextField(u'Описание', max_length=2048, blank=True, null=True, help_text=u'Отображается внизу главной страницы')

    seo_title = models.CharField(u'SEO заголовок', max_length=255, blank=True, null=True)
    seo_keywords = models.CharField(u'SEO мета ключевые слова', max_length=255, blank=True, null=True)
    seo_description = models.CharField(u'SEO мета описание', max_length=255, blank=True, null=True)


    @classmethod
    def get_by_ip_range(cls, ip_range):
        """ IpRange has one to many relationship with Country, Region and City.
   Here we exploit the later relationship."""
        if ip_range:
            return ip_range.region.my_custom_location
        else:
            raise ObjectDoesNotExist

    @classmethod
    def get_default_location(cls):
        return cls.objects.get(is_default=True)

    @classmethod
    def get_available_locations(cls):
        return cls.objects.all()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['weight', 'name']

    def get_url(self):
        if self.subdomain and self.subdomain != '':
            return 'http://%s.%s/' % (self.subdomain, Site.objects.get_current().domain)
        else:
            return 'http://%s/' % (Site.objects.get_current().domain, )



def set_lat_lng(instance, sender, *args, **kwargs):
    if not instance.lng or not instance.lat:
        instance.lng, instance.lat = geocode('', instance.biggest_city)


models.signals.pre_save.connect(set_lat_lng, sender=GeoLocation)

# -*- coding: utf-8
import os
import datetime
from django.contrib.auth.models import User

from django.db import models
from django.contrib.sites.models import Site
from django.db.models import permalink, Q
from django.db.models.signals import pre_save
from easy_thumbnails.fields import ThumbnailerImageField
from mptt.models import MPTTModel
from pytils.translit import slugify
from dict.models import Dict
from django_hstore import hstore


from model_utils.models import TimeStampedModel
from regions.models import GeoLocation

WALKING = 1
TRANSPORT = 2

METRO_DIST_TYPE = (
    (WALKING, u'Пешком'),
    (TRANSPORT, u'На транспорте'),
)

DEAL_PRICE_TYPE = [(1,'Объект'), (2, 'Сотка'),(2, 'Кв. метр')]
DEAL_PRICE_PERIOD = [(1,'Месяц'), (2, 'Год')]


FIELD_TYPE = (
    ('BooleanField', u'Да/Нет'),
    ('CharField', u'Строка'),
    ('TextField', u'Текст'),
    ('ChoiceField', u'Выбор из списка'),
)


class DealType(models.Model):
    """
    Вид сделки
    """
    name = models.CharField(u'Название', max_length=255)
    show_commission_field = models.BooleanField(u'Отображать комиссию агента', default=False)
    show_pledge_field = models.BooleanField(u'Отображать залог собственника', default=False)
    show_period_field = models.BooleanField(u'Отображать поля выбора периода', default=False)
    show_price_field = models.BooleanField(u'Отображать поле ввода стоимости', default=True)
    slug = models.SlugField(unique=True, help_text=u'Не редактировать это поле без согласования с программистом')

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = u'Тип сделки'
        verbose_name_plural = u'Типы сделок'


class FieldSet(models.Model):
    """
    Набор полей
    """
    name = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, blank=True, null=True)
    weight = models.IntegerField(u'Сортировка', blank=True, null=True, default=0, help_text=u'Чем меньше число тем выше строка в списке')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Набор полей'
        verbose_name_plural = u'Наборы полей'
        ordering = ['weight',]


class Field(models.Model):
    """
    Поле с названием и типом (например: Браузер, тип=Одиночный выбор)
    """
    name = models.CharField(u'Название', max_length=255)
    type = models.CharField(u'Тип', choices=FIELD_TYPE, default='CharField', max_length=255)
    additional_info = models.BooleanField(u'Отобржать строчку для описания', default=False)
    field_set = models.ForeignKey(FieldSet, verbose_name=u'Набор полей')
    css_class = models.CharField(u'CSS класс', max_length=255, blank=True, null=True, default='input-xxlarge')
    code = models.CharField(max_length=255, unique=True, help_text=u'Не редактировать это поле без согласования с программистом')

    def __unicode__(self):
        return u'%s (%s) | %s' % (self.name, self.get_type_display(), self.field_set.name)

    class Meta:
        verbose_name = u'Поле'
        verbose_name_plural = u'Поля'
        ordering = ['field_set']



class CatetegoryTypeFieldValue(models.Model):
    """
    Вышеописанное поле привязанное к категории и его значение
    """
    category = models.ForeignKey('Category', related_name='fields', verbose_name=u'Категория')
    field = models.ForeignKey(Field)
    required = models.BooleanField(u'Обязательно для заполнения', blank=True, default=False)

    value_bool = models.BooleanField(blank=True, default=False)
    value_text = models.CharField(max_length=255, blank=True, null=True)
    value_choice = models.ManyToManyField(Dict, blank=True, null=True, related_name='choices')
    comment = models.TextField(blank=True, null=True)
    deal_types = models.ManyToManyField(DealType, verbose_name=u'Отображать при следующих сделках')

    weight = models.IntegerField(u'Сортировка', blank=True, null=True, default=0, help_text=u'Чем меньше число тем выше строка в списке')

    def __unicode__(self):
        return u"%s - %s" % (self.category.name, self.field.name)

    class Meta:
        verbose_name = u'Значение поля в категории'
        verbose_name_plural = u'Значения полей в категориях'


def category_upload_to(instance, filename):
    return os.path.join('categories', 'small_images', str(instance.id), filename)


class Category(MPTTModel):
    """
    Категория объекта
    """
    parent = models.ForeignKey('self', blank=True, null=True, related_name='childrens')
    name = models.CharField(max_length=255)
    show_additional_price_options = models.BooleanField(u'Отображать доп. параметры стоимости', default=False)
    deal_types = models.ManyToManyField(DealType, verbose_name=u'Отображать при следующих сделках')
    slug = models.SlugField(unique=True, help_text=u'Не редактировать это поле без согласования с программистом')
    small_image = ThumbnailerImageField(u'Изображение маленькое', blank=True, null=True, upload_to=category_upload_to, help_text=u'Для главной')
    show_on_main = models.BooleanField(u'Отображать на главной', default=False, help_text=u'Отображать на главной странице в виде картинки')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Тип объекта'
        verbose_name_plural = u'Типы объектов'

    def get_fields(self):
        fields = []

        ancestors_cats = self.get_ancestors(include_self=True)
        for c in ancestors_cats:
            fields.extend(c.fields.all())

        return fields

    @permalink
    def get_absolute_url(self):
        return ('view_region_by_object_type', (), {
            'category_slug': self.slug,
            })


def product_upload_to(instance, filename):
    return os.path.join('users', str(instance.user.id), 'products', str(instance.id), filename)


class ApprovedManager(hstore.Manager):
    def get_query_set(self):
        return super(ApprovedManager, self).get_query_set().filter(is_approved=True, paid_until__gte=datetime.date.today())


class NotApprovedManager(hstore.Manager):
    def get_query_set(self):
        return super(NotApprovedManager, self).get_query_set().filter(is_approved=False)

class NotProlongedManager(hstore.Manager):
    def get_query_set(self):
        return super(NotProlongedManager, self).get_query_set().filter(is_approved=True, paid_until__lt=datetime.date.today())


class NotPaidManager(hstore.Manager):
    def get_query_set(self):
        return super(NotPaidManager, self).get_query_set().filter(paid_until__lt=datetime.date.today()).exclude(deal_type__slug='demand')

class Product(TimeStampedModel):
    user = models.ForeignKey(User)
    deal_type = models.ForeignKey(DealType, verbose_name=u'Вид сделки')
    category = models.ForeignKey(Category, verbose_name=u'Категория', related_name='products')
    slug = models.CharField(max_length=255, blank=True, null=True)

    title = models.CharField(u'Наименование', max_length=255)
    description = models.TextField(u'Описание', blank=True, max_length=1024)
    data = hstore.DictionaryField(db_index=True)
    site = models.ForeignKey(Site)

    is_approved = models.BooleanField(u'Проверено', default=False)
    paid_until = models.DateField(u'Оплачено до', blank=True, default=datetime.date.today())

    objects = hstore.Manager()
    approved_objects = ApprovedManager()
    not_approved_objects = NotApprovedManager()
    not_paid_objects = NotPaidManager()
    not_prolonged_objects = NotProlongedManager()

    class Meta:
        verbose_name = u'Объект'
        verbose_name_plural = u'Объекты'

    def __unicode__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return ('view_product', (), {'city': self.locations.all()[0].region.subdomain,
                                     'slug': self.slug,
                                     'product_id': self.id})

    def get_main_image(self):
        try:
            return self.images.all()[0]
        except:
            return None

    def get_price(self):
        try:
            return self.prices.all()[0].price_str()
        except:
            return None

    def get_latest_price(self):
        try:
            return self.prices.all()[0]
        except:
            return None

    def get_latest_location(self):
        try:
            return self.locations.all()[0]
        except:
            return None


    def photos_count(self):
        return self.images.count()

    def videos_count(self):
        return 0

    def panoramas_count(self):
        return 0

    def is_unpaid(self):
        return not self.paid_until or self.paid_until < datetime.date.today()

    def days_remains(self):
        return (self.paid_until - datetime.date.today()).days

    def is_demand(self):
        return self.deal_type.slug == 'demand'

def make_slug(sender, instance, signal, *args, **kwargs):
    instance.slug = slugify(instance.title)

pre_save.connect(make_slug, sender=Product)


class Price(TimeStampedModel):
    """
    Цена продукта
    """
    product = models.ForeignKey(Product, related_name='prices')

    price = models.DecimalField(u'Стоимость', max_digits=12, decimal_places=0, blank=True, null=True)

    price_type = models.IntegerField(choices=DEAL_PRICE_TYPE, blank=True, null=True)
    price_period = models.IntegerField(choices=DEAL_PRICE_PERIOD, blank=True, null=True)

    commission = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)

    pledge = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)

    def price_str(self):
        return u"%s руб." % (self.price, )


class Location(TimeStampedModel):
    """
    Расположение продукта
    """
    product = models.ForeignKey(Product, related_name='locations')

    region = models.ForeignKey(GeoLocation)

    city = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    zoom_level = models.FloatField(blank=True, null=True)

    metro_available = models.BooleanField(default=False)

    metro = models.CharField(max_length=255, blank=True, null=True)
    metro_dist = models.CharField(max_length=255, blank=True, null=True)
    metro_dist_type = models.IntegerField(choices=METRO_DIST_TYPE, blank=True, null=True)

    metro_alt = models.CharField(max_length=255, blank=True, null=True)
    metro_alt_dist = models.CharField(max_length=255, blank=True, null=True)
    metro_alt_dist_type = models.IntegerField(choices=METRO_DIST_TYPE, blank=True, null=True)


def product_image_upload_to(instance, filename):
    return os.path.join('users', str(instance.product.user.id), 'products', str(instance.product.id), 'images', filename)


class ProductImage(TimeStampedModel):
    """
    Изображение продукта
    """
    product = models.ForeignKey(Product, related_name='images')
    image = models.ImageField(upload_to=product_image_upload_to)




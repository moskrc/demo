# -*- coding: utf-8
from django import template
from catalog.models import Product, Field

register = template.Library()

@register.filter
def products_count_in_work(user):
    return Product.approved_objects.filter(user=user).count()

@register.filter
def products_count_in_moderation(user):
    return Product.not_approved_objects.filter(user=user).count()

@register.filter
def products_count_in_unpaid(user):
    return Product.not_paid_objects.filter(user=user).count()

@register.filter
def products_count_in_old(user):
    return Product.not_prolonged_objects.filter(user=user).count()


@register.filter
def field(product, field_code):
    f = Field.objects.get(code=field_code)
    try:
        return product.data['field_%s' % f.id]
    except:
        return None


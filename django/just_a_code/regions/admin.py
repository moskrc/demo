# -*- coding: utf-8
from django.contrib import admin
from models import GeoLocation
from regions.forms import GeoLocationForm


class GeoLocationAdmin(admin.ModelAdmin):
    list_display = ['name','lat','lng','zoom','biggest_city','is_default','subdomain','weight'] #'metro'
    form = GeoLocationForm
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name',
                'subdomain',
                'is_default',
                'weight',
            ),
        }),
        ('Геолокация', {
            'classes': ('wide extrapretty',),
            'fields': (
                'region',
                'biggest_city',
                ('zoom', 'lat', 'lng', ),
                # 'metro',
            )
        }),
        ('Текст', {
            'classes': ('wide extrapretty',),
            'fields': (
                'description',
            )
        }),
        ('SEO', {
            'classes': ('wide extrapretty',),
            'fields': (
                'seo_title',
                'seo_description',
                'seo_keywords',
            )
        }),
    )





admin.site.register(GeoLocation, GeoLocationAdmin)


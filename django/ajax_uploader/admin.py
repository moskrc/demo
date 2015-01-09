# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from ajax_uploader.forms import UploadedFileForm
from models import UploadedFile
from django.contrib import admin


class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['image', 'get_image_thumb', 'get_size', 'confirmed', 'user', 'site', 'created']
    form = UploadedFileForm

    def get_image_thumb(self, instance):
        try:
            return '<img src="%s" width="100" height="100" />' % (instance.image.url)
        except Exception:
            return

    get_image_thumb.allow_tags = True

    def get_size(self, instance):
        try:
            return '%s Kb' % (instance.image.size / 1024)
        except Exception:
            return 'unknown'




admin.site.register(UploadedFile, UploadedFileAdmin)


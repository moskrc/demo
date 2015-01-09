# -*- coding: utf8 -*-

from django.contrib import admin
from models import Operation


class OperationAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'type', 'comment']

admin.site.register(Operation, OperationAdmin)

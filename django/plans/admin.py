# coding: utf-8
from .models import DataPlan
from django.contrib import admin


class DataPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'data', 'highlights', 'is_active']


admin.site.register(DataPlan, DataPlanAdmin)

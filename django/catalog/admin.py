from django.contrib import admin
from catalog.models import Item, Application


class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'email', 'salary', 'employer_name', 'city', 'on_site']

admin.site.register(Item, ItemAdmin)



class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'item', 'about',]

admin.site.register(Application, ApplicationAdmin)
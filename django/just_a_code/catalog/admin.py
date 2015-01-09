# -*- coding: utf-8
from django import forms
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from catalog.utils import product_was_approved_email
from models import Product, Category, Price, Field, CatetegoryTypeFieldValue, DealType, FieldSet, Location, ProductImage


class DealTypeAdmin(admin.ModelAdmin):
    list_display = [
            'name',
            'show_commission_field',
            'show_pledge_field',
            'show_period_field',
            'show_price_field',
            'slug',
            ]

admin.site.register(DealType, DealTypeAdmin)



class FieldAdminInline(admin.TabularInline):
    model = Field

class FieldSetAdmin(admin.ModelAdmin):
    inlines = [FieldAdminInline,]

admin.site.register(FieldSet, FieldSetAdmin)


class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'additional_info', 'field_set', 'code']
    list_filter = ['field_set', 'type',]
    search_fields = ['name', 'additional_info',]
    prepopulated_fields = {"code": ("name",)}

admin.site.register(Field, FieldAdmin)




# class CatetegoryTypeFieldValueForm(forms.ModelForm):
#
#     def __init__(self, *args, **kwargs):
#         super(CatetegoryTypeFieldValueForm,self).__init__(*args, **kwargs)
#
#         print args
#         print kwargs
#
#         if self.instance:
#             try:
#                 self.fields['field_set'].queryset = self.instance.category.field_sets.all()
#             except:
#                 pass
#
#
#     class Meta:
#         model = CatetegoryTypeFieldValue



class CatetegoryTypeFieldValueAdmin(admin.TabularInline):
    model = CatetegoryTypeFieldValue
    exclude = ['value_bool','value_text','comment']
    ordering = ['weight']

    # def get_formset(self, request, obj=None, **kwargs):
    #     return super(CatetegoryTypeFieldValueAdmin, self).get_formset(request, obj=None, form = CatetegoryTypeFieldValueForm)


class CategoryAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ['name', 'slug', ]
    inlines = [CatetegoryTypeFieldValueAdmin, ]
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Category, CategoryAdmin)

class ProductPriceInline(admin.TabularInline):
    model = Price

class ProductLocationInline(admin.TabularInline):
    model = Location

class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductPriceInline, ProductLocationInline, ProductImageInline]
    list_display = ['id', 'title', 'deal_type', 'category', 'user', 'is_approved', 'created', 'modified']
    list_filter = ('is_approved', 'deal_type', 'category')
    search_fields = ('title', 'description', 'user__email')

    def save_model(self, request, obj, form, change):
        if 'is_approved' in form.changed_data:
            if obj.is_approved:
                product_was_approved_email(obj)

        obj.save()

admin.site.register(Product, ProductAdmin)

# class PriceAdmin(admin.ModelAdmin):
#     pass
# admin.site.register(Price, PriceAdmin)






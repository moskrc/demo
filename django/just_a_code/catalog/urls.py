from django import forms
from django.conf.urls import url, patterns


from forms import FilesForm, DealTypeForm, LocationForm
from views import AddObjectWizard

named_contact_forms = (
    ('deal_type', DealTypeForm),
    ('location', LocationForm),
    ('object', forms.Form),
    ('files', FilesForm),
)

def it_not_demand(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('deal_type') or {}
    deal_type = cleaned_data.get('deal_type')
    if deal_type:
        return deal_type.slug != 'demand'

    return True


add_object_wizard = AddObjectWizard.as_view(named_contact_forms,
    url_name='add_object_step',
    done_step_name='finished',
    condition_dict={
        'deal_type': True,
        'location': it_not_demand,
        'object': it_not_demand,
        'files': it_not_demand
    }
)

urlpatterns = patterns('catalog.views',
    url(r'^add/(?P<step>.+)/$', add_object_wizard, name='add_object_step'),
    url(r'^add/$', add_object_wizard, name='add_object'),
    url(r'^get_sub_cats/(?P<category_id>\d+)/$', 'get_sub_cats'),

    url(r'^get_deal_type_info/(?P<deal_type_id>\d+)/$', 'get_deal_type_info'),
    url(r'^get_category_info/(?P<category_id>\d+)/$', 'get_category_info'),


    url(r'^my_items/$', 'my_products', name='my_products'),
    url(r'^(?P<product_id>\d+)/delete_item/$', 'delete_product', name='delete_product'),
    url(r'^(?P<product_id>\d+)/edit_item/$', 'edit_product', name='edit_product'),
    url(r'^(?P<product_id>\d+)/edit_demand/$', 'edit_demand', name='edit_demand'),
    url(r'^(?P<product_id>\d+)/edit_item/photos/$', 'edit_product_photos', name='edit_product_photos'),
    url(r'^(?P<product_id>\d+)/edit_item/map/$', 'edit_product_map', name='edit_product_map'),
    url(r'^(?P<product_id>\d+)/success/$', 'successfully_added', name='successfully_added'),
    url(r'^$', 'view_region', name='view_region'),
    url(r'^map/$', 'view_region_map', name='view_region_map'),
)


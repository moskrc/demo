# coding: utf-8

import os
from types import NoneType
import datetime
from dateutil.relativedelta import relativedelta
from robokassa.forms import RobokassaForm
from catalog.utils import new_product_email
from dict.models import Dict as MPTT_Dict, Dict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, render
from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView
from django.conf import settings

from annoying.decorators import ajax_request, JsonResponse

from catalog.forms import ImageForm, LocationForm, DynamicForm, PriceForm, DemandForm
from catalog.models import Category, Product, DealType, Price, Location, ProductImage, FieldSet
from payments.forms import ProductPaymentForm
from payments.models import REGULAR_SERVICE
from regions.models import GeoLocation


def prepare_for_hstore(src):
    str_dict = {}
    for k in src:
        if isinstance(src[k], unicode):
            str_dict[k] = unicode(src[k])
        elif isinstance(src[k], MPTT_Dict):
            str_dict[k] = str(src[k].id)
        elif isinstance(src[k], NoneType):
            str_dict[k] = unicode(src[k])
        else:
            # bool
            str_dict[k] = unicode(src[k])
    return str_dict



class AddObjectWizard(NamedUrlSessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'wizard'))

    def get_template_names(self):
        return ['catalog/add_object_wizard/step_{0}.html'.format(self.steps.current)]

    def done(self, form_list, **kwargs):

        deal_form = form_list[0].cleaned_data

        if deal_form['deal_type'].slug == 'demand':
            """
            Только для спроса
            """
            product = Product.objects.create(user=self.request.user,
                                             category=deal_form['category'],
                                             title=deal_form['title'],
                                             description=deal_form['description'],
                                             site=Site.objects.get_current(),
                                             deal_type=deal_form['deal_type'],
                                             data={'key_0':'val'}
            )

            Location.objects.create(product=product,
                                    region=deal_form['region'],
            )

        else:
            """
            Для всего остального
            """
            deal_form, location_form, dynamic_form, files_form = [form.cleaned_data for form in form_list]

            product = Product.objects.create(user=self.request.user,
                                             category=deal_form['category'],
                                             title=deal_form['title'],
                                             description=deal_form['description'],
                                             site=Site.objects.get_current(),
                                             deal_type=deal_form['deal_type'],
                                             data=prepare_for_hstore(dynamic_form)
            )

            Price.objects.create(product=product,
                                 price=deal_form['price'],

                                 price_type=deal_form['price_type'],
                                 price_period=deal_form['price_period'],

                                 commission=deal_form['commission'],
                                 pledge=deal_form['pledge'],
                                 )

            Location.objects.create(product=product,
                                    city=location_form['city'],
                                    metro_available=location_form['metro_available'],
                                    metro=location_form['metro'],
                                    metro_dist=location_form['metro_dist'],
                                    metro_dist_type=location_form['metro_dist_type'],
                                    metro_alt=location_form['metro_alt'],
                                    metro_alt_dist=location_form['metro_alt_dist'],
                                    metro_alt_dist_type=location_form['metro_alt_dist_type'],

                                    region=location_form['region'],
                                    lat=location_form['lat'],
                                    lng=location_form['lng'],
                                    zoom_level=location_form['zoom_level'],
                                    address=location_form['address']
            )

            for i in files_form:
                if i != {}:
                    ProductImage.objects.create(product=product, image=i['image'])

        new_product_email(product)

        messages.add_message(self.request, messages.INFO, u'Ваше объявление было успешно принято на модерацию.')
        return HttpResponseRedirect(reverse('successfully_added', kwargs={'product_id': product.id}))

    def get_form_kwargs(self, step=None):
        print '>>> get_form_kwargs %s' % step

        if step == 'object':
            category = self.get_cleaned_data_for_step('deal_type')['category']
            deal_type = self.get_cleaned_data_for_step('deal_type')['deal_type']

            self.form_list['object'] = DynamicForm

            return {'category': category, 'deal_type': deal_type}

        if step == 'files':
            self.form_list['files'] = formset_factory(ImageForm, extra=3)

        return {}

    def get_form_initial(self, step=None):
        print '>>> get_form_initial %s' % step

        if step == 'location' or step == 'deal_type':
            return {'region': self.request.location.id}

        return {}

    def process_step(self, form):
        print '>>> process_step %s' % self.steps.current

        if form.is_valid():
            print 'Form valid'
        else:
            print form.errors

        return self.get_form_step_data(form)



def get_sub_cats(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    return JsonResponse([[x.id, x.name] for x in category.get_children()])


@ajax_request
def get_category_info(request, category_id):
    cat = get_object_or_404(Category, pk=category_id)

    category_info = {
        'name': cat.name,
        'parent': cat.parent,
        'show_additional_price_options': cat.show_additional_price_options,
    }

    return {'info': category_info}


@ajax_request
def get_deal_type_info(request, deal_type_id):
    deal_type = get_object_or_404(DealType, pk=deal_type_id)

    deal_type_info = {
        'show_commission_field': deal_type.show_commission_field,
        'show_pledge_field': deal_type.show_pledge_field,
        'show_period_field': deal_type.show_period_field,
        'show_price_field': deal_type.show_price_field,
        'slug': deal_type.slug,
        'name': deal_type.name
    }

    return {'categories': [[x.id, x.name] for x in deal_type.category_set.all()], 'info': deal_type_info}


@login_required
def my_products(request):
    if request.GET.get('waiting', False):
        products = Product.not_approved_objects.filter(user=request.user).order_by('-id')
    elif request.GET.get('unpaid', False):
        products = Product.not_paid_objects.filter(user=request.user).order_by('-id')
    elif request.GET.get('not_prolonged', False):
        products = Product.not_prolonged_objects.filter(user=request.user).order_by('-id')
    else:
        products = Product.approved_objects.filter(user=request.user).order_by('-id')
    return render(request, 'catalog/my_products.html', {'products': products})


def view_product(request, city, product_id, slug):

    product = get_object_or_404(Product, pk=product_id)

    if product.user != request.user and not product.is_approved:
        raise Http404(u'Страница не найдена')


    data = []

    fields_ids = set()

    try:
        for i in product.data:
            if not 'additional' in i:
                fields_ids.add(i.split('_')[1])
    except:
        pass

    fsets = FieldSet.objects.filter(
        field__id__in=fields_ids).distinct()

    for fs in fsets:
        d = {'name': fs.name, 'values':[]}

        for f in product.category.fields.filter(field__field_set=fs, deal_types=product.deal_type).order_by('weight').distinct():
            try:
                data_p = {'name': f.field.name, 'type':f.field.type}

                val = product.data['field_%s' % f.field.id]

                if val == 'None':
                    val = None
                elif val == 'False':
                    val = False
                elif val == 'True':
                    val = True

                if f.field.type == 'ChoiceField' and val:
                    val = Dict.objects.get(pk=val).name

                data_p['value'] = val

                if f.field.additional_info:
                    data_p['additional'] = product.data['field_%s_additional' % f.field.id]

                if data_p['value'] or data_p['additional']:
                    d['values'].append(data_p)
            except Exception as e:
                print e
        if d['values']:
            data.append(d)

    return render(request, 'catalog/view_product.html', {'product': product, 'data': data})


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.user != product.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        product.delete()
        messages.info(request, u'Объявление было успешно удалено')
        return HttpResponseRedirect(reverse(my_products))

    return render(request, 'catalog/delete_product.html', {'product': product})


def prepare_data_for_edit(src):
    new_data = {}
    for k in src:
        if src[k] == 'None':
            new_data[k] = None
        elif src[k] == 'False':
            new_data[k] = False
        elif src[k] == 'True':
            new_data[k] = True
        else:
            new_data[k] = src[k]
    return new_data


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        object_form = DynamicForm(request.POST, category=product.category, deal_type=product.deal_type)
        price_form = PriceForm(request.POST, instance=product.get_latest_price())

        if object_form.is_valid() and price_form.is_valid():

            product.data = prepare_for_hstore(object_form.cleaned_data)
            product.title = price_form.cleaned_data['title']
            product.description = price_form.cleaned_data['description']
            product.save()

            price_form.save()

            messages.info(request, u'Объявление было успешно отредактировано')
            return HttpResponseRedirect(reverse(edit_product, kwargs={'product_id': product.id}))

    object_form = DynamicForm(category=product.category, deal_type=product.deal_type, initial=prepare_data_for_edit(product.data))
    price_form = PriceForm(instance=product.get_latest_price(), initial={'title': product.title, 'description': product.description})

    return render(request, 'catalog/edit_product.html', {'product': product, 'object_form': object_form, 'price_form': price_form})

@login_required
def edit_demand(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = DemandForm(request.POST, instance=product)

        if form.is_valid():
            p = form.save(commit=False)
            loc = p.get_latest_location()
            loc.region = form.cleaned_data['region']
            loc.save()
            p.save()

            messages.info(request, u'Объявление было успешно отредактировано')
            return HttpResponseRedirect(reverse(edit_demand, kwargs={'product_id': product.id}))

    form = DemandForm(instance=product, initial={'region':product.get_latest_location().region})

    return render(request, 'catalog/edit_demand.html', {'product': product, 'form': form})


@login_required
def edit_product_map(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = LocationForm(request.POST, instance=product.get_latest_location())

        if form.is_valid():
            form.save()
            messages.info(request, u'Объявление было успешно отредактировано')
            return HttpResponseRedirect(reverse(edit_product_map, kwargs={'product_id': product.id}))

    form = LocationForm(instance=product.get_latest_location())

    return render(request, 'catalog/edit_product_map.html', {'product': product, 'form': form})


@login_required
def edit_product_photos(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    #ProductImageFormSet = modelformset_factory(ProductImage, ImageForm, extra=3, can_delete=True)

    if request.method == 'POST':
        # # form = ProductImageFormSet(request.POST, request.FILES, queryset=product.images.all())
        #
        # if form.is_valid():
        #     #form.save()
        messages.info(request, u'Объявление было успешно отредактировано')
        return HttpResponseRedirect(reverse(edit_product_photos, kwargs={'product_id': product.id}))

    # form = ProductImageFormSet(queryset=product.images.all())

    return render(request, 'catalog/edit_product_photos.html', {'product': product})


def view_region(request, city=None, deal_type_slug=None, category_slug=None):
    subdomain = city if city is not None else 'msk'
    city = get_object_or_404(GeoLocation, subdomain=subdomain)

    deal_types = DealType.objects.all()
    price_from = request.GET.get('price_from', None)
    price_to = request.GET.get('price_to', None)

    products = Product.approved_objects.filter(locations__region=request.location).distinct()

    print deal_type_slug, category_slug
    if deal_type_slug:
        deal_type = get_object_or_404(DealType, slug=deal_type_slug)
        products = products.filter(deal_type=deal_type)
    else:
        deal_type = None

    if category_slug:
        category_slug = category_slug.split('/')[0]
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        category = None

    if price_from and price_to:
        products = products.filter(prices__price__lte=price_to).exclude(prices__price__lt=price_from)

    return render(request, 'catalog/view_region.html', {'products': products, 'deal_type': deal_type,
                                                        'category': category,
                                                        'price_from': price_from, 'price_to': price_to,
                                                        'deal_types': deal_types})


def view_region_map(request):
    products = Product.approved_objects.filter(locations__region=request.location).distinct()
    return render(request, 'catalog/view_region_map.html', {'products': products})


# def view_demand(request, category_slug=None):
#     categories_demand = Category.objects.filter(deal_types__slug='demand')
#
#     products = Product.approved_objects.filter(locations__region=request.location, deal_type__slug='demand').distinct()
#     return render(request, 'catalog/view_demand.html', {'products': products, 'categories': categories_demand})


@login_required
def successfully_added(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = ProductPaymentForm(request.POST, initial={'product': product})
        if form.is_valid():

            if not product.is_demand():
                r_form = RobokassaForm(initial={
                    'OutSum': form.cleaned_data['amount'],
                    'Desc': u'Оплата объявления #%s' % product.id,
                    'Email': product.user.email,

                    'user_id': product.user.id,
                    'product_id': product.id,
                    'days': int(form.cleaned_data['days']),
                    'service_id': REGULAR_SERVICE
                })

                return HttpResponseRedirect(r_form.get_redirect_url())
            else:
                date_from = datetime.date.today()
                date_to = date_from + relativedelta(days=int(form.cleaned_data['days']))
                product.paid_until = date_to
                product.save()
                return HttpResponseRedirect(reverse('my_products'))

    else:
        form = ProductPaymentForm(initial={'product': product, 'days': 10})

    return render(request, 'catalog/successfully_added.html', {'product': product, 'form': form})

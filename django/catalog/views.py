# coding=utf8
import json
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from catalog.forms import AddItemForm, ApplicationForm
from catalog.models import Item


def index(request):
    items = Item.active_objects.all().order_by('-id')
    return render(request, 'catalog/index.html', {'items': items})


def view(request, item_id):
    item = get_object_or_404(Item.active_objects, pk=item_id)
    return render(request, 'catalog/view.html', {'item': item})

@csrf_exempt
@require_POST
def feedback(request, item_id):
    item = get_object_or_404(Item.active_objects, pk=item_id)

    form = ApplicationForm(request.POST)
    if form.is_valid():
        if not form.cleaned_data['country']:
            new_feedback = form.save(commit=False)
            new_feedback.item = item
            new_feedback.save()

        return HttpResponse(json.dumps({'success': True, 'message': 'Success'}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'success': False, 'errors': form.errors}), content_type="application/json")

def add(request):
    if request.method == 'POST':
        form = AddItemForm(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.site = Site.objects.get_current()
            new_item.save()
            messages.add_message(request, messages.SUCCESS,
                                 u'Ваше объявление успешно добавлено! Письмо со ссылкой для редактирования или удаления отправлена вам на email.')
            return HttpResponseRedirect(reverse('catalog_view', kwargs={'item_id': new_item.pk}))
        else:
            messages.add_message(request, messages.WARNING, u'Исправьте пожалуйста ошибки выделенные красным цветом')
    else:
        form = AddItemForm()

    return render(request, 'catalog/add.html', {'form': form})


def edit(request, item_id, secret_key):
    item = get_object_or_404(Item.active_objects, pk=item_id)

    if item.secret_key != secret_key:
        return HttpResponseForbidden('Forbidden')

    if request.method == 'POST':
        form = AddItemForm(request.POST, instance=item)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.secret_key = item.secret_key
            new_item.save()

            messages.add_message(request, messages.SUCCESS,
                                 u'Ваше объявление успешно отредактировано!')
            return HttpResponseRedirect(
                reverse('catalog_edit', kwargs={'item_id': new_item.pk, 'secret_key': secret_key}))
        else:
            messages.add_message(request, messages.WARNING, u'Исправьте пожалуйста ошибки выделенные красным цветом')
    else:
        form = AddItemForm(instance=item)

    return render(request, 'catalog/edit.html', {'form': form, 'item': item})


def delete(request, item_id, secret_key):
    item = get_object_or_404(Item.active_objects, pk=item_id)

    if item.secret_key != secret_key:
        return HttpResponseForbidden('Forbidden')

    if request.method == 'POST':
        item.is_active = False
        item.save()
        messages.add_message(request, messages.SUCCESS, u'Ваше объявление успешно удалено!')
        return HttpResponseRedirect(reverse('catalog_index'))

    return render(request, 'catalog/delete.html', {'item': item})



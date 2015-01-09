# -*- coding: utf-8 -*-
from decimal import Decimal
import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from robokassa.forms import RobokassaForm
from robokassa.signals import result_received
from catalog.models import Product
from payments.forms import PaymentForm, ProductPaymentForm
from payments.models import Operation, PAYMENT, REGULAR_SERVICE


@login_required
def index(request):
    return render(request, 'payments/operation_list.html', {'object_list': Operation.objects.filter(user=request.user)})

@login_required
def pay(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            r_form = RobokassaForm(initial={
                'OutSum': form.cleaned_data['amount'],
                'Desc': u'Пополнение баланса',
                'Email': request.user.email,
                'user_id': request.user.id,
                'product_id': 0,
                'site_comment': '',

            })

            return HttpResponseRedirect(r_form.get_redirect_url())
    else:
        form = PaymentForm(initial={'amount': 100})

    return render(request, 'payments/pay.html', {'form': form})


@login_required
def pay_product(request, product_id):
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
                date_from, date_to = product_prolongation(product, int(form.cleaned_data['days']))
                messages.add_message(request, messages.INFO, u'Ваше объявление было успешно продлено на %s дней (с %s по %s).' % (int(form.cleaned_data['days']), date_from.strftime("%d.%m.%Y"), date_to.strftime("%d.%m.%Y")))

                return HttpResponseRedirect(reverse('my_products'))


    else:
        form = ProductPaymentForm(initial={'product': product, 'days': 10})

    return render(request, 'payments/pay_product.html', {'product': product, 'form': form})


def payment_received(sender, **kwargs):

    product = Product.objects.get(pk=kwargs['extra']['product_id'])

    date_from, date_to = product_prolongation(product, int(kwargs['extra']['days']))

    site_comment = u'Оплата объявления #%s с %s по %s (счет #%s)' % (
        product.id,
        date_from.strftime("%d.%m.%Y"),
        date_to.strftime("%d.%m.%Y"),
        kwargs['InvId']
    )

    Operation.objects.create(user_id=kwargs['extra']['user_id'],
                             product_id=kwargs['extra']['product_id'],
                             amount=kwargs['OutSum'],
                             type=PAYMENT,
                             comment=site_comment,
                             days=kwargs['extra']['days'],
                             service=kwargs['extra']['service_id'])

result_received.connect(payment_received)


def product_prolongation(product, days):

    if product.paid_until < datetime.date.today():
        # Просроченное объявление
        date_from = datetime.date.today()
    else:
        # Которое нужно продлить или сегодняшнее
        date_from = product.paid_until

    date_to = date_from + relativedelta(days=days)

    product.paid_until = date_to
    product.save()

    return date_from, date_to

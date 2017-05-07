# coding: utf-8

from datetime import datetime, timedelta

from django.views.generic import TemplateView, View
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import Http404
from django.utils.text import capfirst
from braces.views import LoginRequiredMixin
from payments.signals import payment_done
from paypal.pro.views import PayPalPro
from paypal.pro.models import PayPalNVP
from common.mixins import EmailMixin
from common import utils
from django.conf import settings

PRICE_TABLE = settings.PRODUCTS_TABLE


class BuyPackage(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        price_item = self.get_price_item(*args, **kwargs)

        description = 'Skyline Exchange Subscription - {title} - {cost}'.format(
            title=price_item['title'],
            cost=price_item['cost'])

        ppp = PayPalPro(item={
            'paymentrequest_0_amt': price_item['amount'],
            'custom': self.get_custom_descr(*args, **kwargs),
            'desc': description,
            'billingperiod': 'Month',
            'billingfrequency': '1',
            'cancelurl': request.build_absolute_uri(reverse('payments:paypal-cancel')),
            'returnurl': request.build_absolute_uri(reverse('payments:paypal-checkout'))})

        request.GET = dict(request.GET, express=True)

        return ppp(request)

    def get_price_item(self, *args, **kwargs):
        return PRICE_TABLE[int(kwargs.get('package'))]

    def get_custom_descr(self, *args, **kwargs):
        return int(kwargs.get('package'))


class BuyCustomPackage(BuyPackage):
    def get_price_item(self, *args, **kwargs):
        return {
            'title': _(u'Custom Plan'),
            'amount': int(kwargs.get('amount')),
            'cost': u'$%s/month' % int(kwargs.get('amount')),
            'features': []
        }

    def get_custom_descr(self, *args, **kwargs):
        price_item = self.get_price_item(*args, **kwargs)
        return 'custom_amount-%s' % price_item['amount']


class PayPalCheckout(LoginRequiredMixin, View):
    success_url = reverse_lazy('payments:paypal-success')

    def dispatch(self, request, *args, **kwargs):
        try:
            token = self.request.GET.get('token', None)
            if token is None:
                raise Http404()

            self.nvp = PayPalNVP.objects.get(token=token,
                                             user=request.user,
                                             method='SetExpressCheckout')
        except PayPalNVP.DoesNotExist:
            raise Http404()
        return super(PayPalCheckout, self).dispatch(request, *args, **kwargs)

    def payppal_handler(self, request, *args, **kwargs):
        self.request.session['token'] = self.request.GET['token']

        if 'custom_amount' in self.nvp.custom:
            amount = int(self.nvp.custom.split('-')[1])
            price_item = {
                'title': _(u'Custom Plan'),
                'amount': amount,
                'cost': u'$%s/month' % amount,
                'features': []
            }
            context = {'item': price_item}
        else:
            price_item = PRICE_TABLE[int(self.nvp.custom)]
            context = {'item': PRICE_TABLE[int(self.nvp.custom)]}

        description = 'Skyline Exchange Subscription - {title} - {cost}'.format(
            title=price_item['title'],
            cost=price_item['cost'])

        now = datetime.utcnow() + timedelta(minutes=1)

        ppp = PayPalPro(
            item={
                'amt': price_item['amount'],
                'desc': description,
                'custom': self.nvp.custom,
                'billingperiod': 'Month',
                'billingfrequency': '1',
                'profilestartdate': now.strftime("%Y-%m-%dT%H:%M:00Z"),
                'maxfailedpayments': '3'},
            confirm_template='payments/confirm_paypal.html',
            context=context,
            success_url=self.success_url)

        return ppp(request)

    def get(self, request, *args, **kwargs):
        return self.payppal_handler(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.payppal_handler(request, *args, **kwargs)


class PayPalCancel(LoginRequiredMixin, TemplateView):
    template_name = 'payments/paypal.html'

    def get_context_data(self, **kwargs):

        message = ' '.join([capfirst(item) for item in [
            _(u'your transaction has been cancelled and you have not been charged.'),
            _(u'please try again soon.')]])

        return dict(super(PayPalCancel, self).get_context_data(**kwargs), message=message)


class PayPalSuccess(LoginRequiredMixin, EmailMixin, TemplateView):
    template_name = 'payments/paypal.html'
    from_email = settings.FROM_EMAIL

    def dispatch(self, request, *args, **kwargs):
        try:
            token = request.session.get('token', None)

            if token is None:
                raise Http404()

            self.nvp = PayPalNVP.objects.get(token=token,
                                             user=request.user,
                                             method='CreateRecurringPaymentsProfile')

            request.session.clear()
        except PayPalNVP.DoesNotExist:
            raise Http404()

        return super(PayPalSuccess, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        message = '</br>'.join([capfirst(item) for item in [
            _(u'thank you for your subscription to Skyline Exchange!'),
            _(u'your billboards will go live within 48 hours from receiving your digital content.'),
            _(u'please send this text and image content to William Robertson.')]])

        if 'custom_amount' in self.nvp.custom:
            amount = int(self.nvp.custom.split('-')[1])
            item = {
                'title': _(u'Custom Plan'),
                'amount': amount,
                'cost': u'$%s/month' % amount,
                'features': []
            }
        else:
            item = PRICE_TABLE[int(self.nvp.custom)]

        payment_done.send(sender=self.__class__, item=item, user=self.request.user)

        utils.send_email("Thank you for subscribing to Skyline Exchange", "payments/email/user_subscription.html", {
            'name': self.nvp.user.first_name,
            'plan': item['title'],
            'amount': item['amount'],
        }, [self.request.user.email, ])

        for notify_email in ['moskrc@gmail.com', 'wrobertson@skylineexchange.com',]:
            utils.send_email("A credit card transaction", "payments/email/subscription_admin.html", {
                'name': self.nvp.user.first_name,
                'plan': item['title'],
                'amount': item['amount'],
                'email': self.nvp.user.email,
            }, [notify_email, ])

        return dict(super(PayPalSuccess, self).get_context_data(**kwargs), message=message)

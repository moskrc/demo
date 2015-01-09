# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from django import forms
from django.template.defaultfilters import safe
from catalog.models import Product
from site_config.models import SiteConfig


class PaymentForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, max_digits=10, label=u'Сумма')


class ProductPaymentForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.sc = SiteConfig.objects.get_current()
        super(ProductPaymentForm, self).__init__(*args, **kwargs)

        self.product = kwargs['initial']['product']

        if self.product.is_demand():
            self.fields['days'] = forms.ChoiceField(choices=self.get_choices(), label=u'Опубликовать на:')
        else:
            self.fields['days'] = forms.ChoiceField(choices=self.get_choices(), label=u'Оплатить на:')
        self.fields['tos'] = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=safe(u'Я ознакомлен с <a href="/agreement/">пользовательским соглашением</a>'),
                             error_messages={'required': u"Вы должны согласиться с пользовательским соглашением"})



    def get_choices(self):
        if self.product.is_demand():
            days = (
                (10, u'Десять дней'),
                (20, u'Двадцать дней'),
                (30, u'Тридцать дней'),
                (60, u'Шестьдесят дней'),
            )
        else:
            days = (
                (10, u'Десять дней - %s р.' % (self.sc.get('price_per_day') * 10)),
                (20, u'Двадцать дней - %s р.' % (self.sc.get('price_per_day') * 20)),
                (30, u'Тридцать дней - %s р.' % (self.sc.get('price_per_day') * 30)),
                (60, u'Шестьдесят дней - %s р.' % (self.sc.get('price_per_day') * 60)),
            )


        return days

    def clean(self):
        cleaned_data = super(ProductPaymentForm, self).clean()

        if self.product.is_demand():
            cleaned_data['amount'] = 0
        else:
            cleaned_data['amount'] = int(cleaned_data['days']) * self.sc.get('price_per_day')

        cleaned_data['date_from'] = datetime.date.today()
        cleaned_data['date_to'] = cleaned_data['date_from'] + relativedelta(days=int(cleaned_data['days']))

        return cleaned_data

from django import forms
from models import Item, Application
from nocaptcha_recaptcha import NoReCaptchaField


class AddItemForm(forms.ModelForm):
    # honeyspot
    country = forms.CharField(required=False)
    captcha = NoReCaptchaField()

    class Meta:
        model = Item
        exclude = ['secret_key', 'not_sended', 'is_active', 'site']


class ApplicationForm(forms.ModelForm):
    # honeyspot
    country = forms.CharField(required=False)

    class Meta:
        model = Application
        exclude = ['item',]

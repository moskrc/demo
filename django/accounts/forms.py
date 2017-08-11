# -*- coding: utf-8 -*-
from datetime import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field

User = get_user_model()


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'new_password1',
            'new_password2',
            FormActions(
                Submit('save', u'Submit', css_class='btn-primary'),
            )
        )


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'old_password',
            'new_password1',
            'new_password2',
            FormActions(
                Submit('save', u'Submit', css_class='btn-primary'),
            )
        )


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'email',
            FormActions(
                Submit('save', u'Submit', css_class='btn-primary'),
            )
        )


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label=u"Email", max_length=30)
    remember_me = forms.BooleanField(label=u'Remember Me', required=False, initial=True)

    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(request, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('username', id='login_username'),
            Field('password', id='login_password'),
            Field('remember_me',),
            FormActions(
                Submit('save', u'Login'),
            )
        )


class EnhancedRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput,
                               label=u'Create Password')
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label=u'Confirm Password')

    def __init__(self, *args, **kwargs):
        super(EnhancedRegistrationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'email',
            'password',
            'password1',
            HTML("""
                <div class="checkbox">
                    <label>
                        <input type="checkbox"> You have read &amp; agree to the
                        <a href="#">Terms of service</a>.
                    </label>
                </div>"""

            ),

            FormActions(
                Submit('save', u'Sign Up', css_class='button-red loaderBtn'),
            )
        )
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError(u"This email is already taken, chose an another one please.")
        return email


    def clean(self):
        if 'password' in self.cleaned_data and 'password1' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password1']:
                raise forms.ValidationError("The two password fields didn't match.")

        self.cleaned_data['last_login'] = datetime.now()

        return self.cleaned_data

    class Meta:
        model = User
        fields = ['email', 'password', ]


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'email', ]
        widgets = {
            'first_name': forms.TextInput({'placeholder': 'Your Name'})
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'first_name',
            'email',
            FormActions(
                Submit('save', u'Submit', css_class='btn-primary'),
            )
        )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk):
            raise forms.ValidationError(u"This email is already taken, chose an another one please.")
        return email


class CreateUserForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'email',
            'message',
            FormActions(
                Submit('save', u'Send Email', css_class='btn-primary'),
            )
        )

    class Meta:
        model = User
        fields = ['email', ]

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError(
                u"This email is already taken, chose an another one please.")
        return email


# coding: utf-8
from django import forms
from django.contrib.auth import get_user_model
from common.utils import is_power2
from core.models import Tournament

User = get_user_model()


class CreateNewTournamentForm(forms.ModelForm):
    start_date = forms.DateTimeField(input_formats=['%m/%d/%Y %I:%M %p', ], widget=forms.widgets.DateTimeInput(format="%m/%d/%Y %I:%M %p"))

    def clean_capacity(self):
        data = self.cleaned_data['capacity']
        if not is_power2(data):
            raise forms.ValidationError("Capacity must be a power of 2")
        return data

    def clean_custom_url(self):
        if self.cleaned_data['custom_url']:
            query = Tournament.objects.filter(custom_url__iexact=self.cleaned_data['custom_url'])

            if self.instance:
               query = query.exclude(pk=self.instance.id)

            if query:
                raise forms.ValidationError("This custom url is already in use. Please supply a different custom url.")

        return self.cleaned_data['custom_url']

    class Meta:
        model = Tournament
        fields = ['title', 'capacity', 'start_date', 'custom_url']


class JoinTournamentForm(forms.Form):
    nickname = forms.CharField(max_length=255)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        tournament = kwargs.pop('tournament')
        super(JoinTournamentForm, self).__init__(*args, **kwargs)

    def get_or_create_user(self, nickname, email, password):
        try:
            user = User.objects.get(username=nickname, email=email)

            print user, password
            if user.check_password(password):
                return user

            raise forms.ValidationError("Incorrect password!")
        except User.DoesNotExist as e:
            if User.objects.filter(username=nickname).exists():
                raise forms.ValidationError("This nickname is already taken")


            user = User.objects.create(username=nickname, email=email)
            user.set_password(password)
            user.save()
            return user

    def clean(self):
        data = super(JoinTournamentForm, self).clean()

        if not 'nickname' in data or not 'email' in data or not 'password' in data:
            return data

        data['user'] = self.get_or_create_user(data['nickname'], data['email'], data['password'])

        return data


class LeaveTournamentForm(JoinTournamentForm):
    def get_or_create_user(self, nickname, email, password):
        try:
            user = User.objects.get(username=nickname, email=email)

            if user.check_password(password):
                return user
        except User.DoesNotExist as e:
            raise forms.ValidationError("Unknown user!")

        raise forms.ValidationError("Incorrect password!")

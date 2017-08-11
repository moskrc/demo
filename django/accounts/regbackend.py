# coding: utf-8
from django.contrib import messages
import logging
from django.contrib.auth import get_user_model, login, authenticate
from django.urls import reverse
from registration import signals
from registration.backends.simple.views import RegistrationView
import datetime

User = get_user_model()

logger = logging.getLogger('project')

class CustomRegistrationView(RegistrationView):
    """
    A registration backend which implements the simplest possible
    workflow: a user supplies a username, email address and password
    (the bare minimum for a useful account), and is immediately signed
    up and logged in).

    """
    success_url = 'home'

    def get_success_url(self, user=None):
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        else:
            return reverse('home')

    def register(self, form):

        new_user = form.save(commit=False)
        new_user.last_login=datetime.datetime.now()
        new_user.set_password(form.cleaned_data['password1'])
        new_user.first_name = ''
        new_user.save()

        new_user = authenticate(
            email=getattr(new_user, 'email'),
            password=form.cleaned_data['password1']
        )


        login(self.request, new_user)
        messages.info(self.request, 'Welcome!', fail_silently=True)
        signals.user_registered.send(sender=self.__class__, user=new_user, request=self.request)
        return new_user

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        ctx = self.get_context_data(form=form)
        ctx.update({'next': self.request.GET.get('next', None)})
        return self.render_to_response(ctx)


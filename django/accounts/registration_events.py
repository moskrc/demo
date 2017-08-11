# coding: utf-8
from django.contrib import messages
from django.contrib.auth import user_logged_out

def logout_notifier(sender, request, user, **kwargs):
    messages.info(request, u'Your are logged out', fail_silently=True)

user_logged_out.connect(logout_notifier)
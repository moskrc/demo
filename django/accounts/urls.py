# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import login, password_change
from django.contrib.auth.views import password_change_done
from django.contrib.auth.views import logout
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_done
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_complete

from .forms import EnhancedRegistrationForm, CustomPasswordChangeForm
from .forms import LoginForm
from .forms import CustomPasswordResetForm
from .forms import CustomSetPasswordForm
from .regbackend import CustomRegistrationView
from .views import edit_profile, logged_in

urlpatterns = [

    url(r'^profile/$', edit_profile, name='profile'),

    url(r'^login/$', login,{'authentication_form': LoginForm,'extra_context': {'reg_form': EnhancedRegistrationForm(),'reset_form': PasswordResetForm()}},name='auth_login'),
    url(r'^logout/$', logout, {'next_page': reverse_lazy('home')},name='auth_logout'),
    url(r'^register/$',CustomRegistrationView.as_view(form_class=EnhancedRegistrationForm),name='auth_register'),
    url(r'^logged_in/$', logged_in, name='logged_in'),

    url(r'^password/change/$', password_change, {'password_change_form': CustomPasswordChangeForm}, name='auth_password_change'),
    url(r'^password/change/done/$', password_change_done, name='password_change_done'),
    url(r'^password/reset/$', password_reset, {'password_reset_form': CustomPasswordResetForm}, name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', password_reset_confirm, {'set_password_form': CustomSetPasswordForm, 'post_reset_redirect': reverse_lazy('auth_password_reset_complete')}, name='auth_password_reset_confirm'),
    url(r'^resetpassword/passwordsent/$', password_reset_done, name='password_reset_done'),
    url(r'^password_reset_complete/$', password_reset_complete, name='auth_password_reset_complete'),

]

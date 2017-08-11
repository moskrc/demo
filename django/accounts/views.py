# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UserProfileForm
from datetime import datetime
from django.conf import settings


@login_required
def edit_profile(request):
    if request.method == 'POST':

        form = UserProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            prof = form.save(commit=False)
            prof.save()
            messages.add_message(request, messages.INFO, u'Your profile was updated', fail_silently=True)
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = UserProfileForm(instance=request.user)



    return render(request, 'accounts/edit_profile.html', {'form': form, 'profile': request.user})


def logged_in(request):
    return HttpResponseRedirect(reverse('home'))

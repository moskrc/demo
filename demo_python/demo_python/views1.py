# coding: utf-8
from datetime import datetime
import logging
from common.utils import generate_password
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from accounts.forms import UserProfileForm, CreateUserForm
from invites.forms import InviteUserForm, TocForm
from invites.models import Invite
import hashlib
User = get_user_model()

logger = logging.getLogger(__name__)

@login_required
def invite(request):

    if request.method == 'POST':
        form = InviteUserForm(request.POST)
        if form.is_valid():
            logger.debug('Try to send invites for: ')

            for u in form.cleaned_data['new_users']:
                logger.debug(u['email'])
                new_user = User.objects.create(email=u['email'], username=u['username'], is_active=True, is_applicant=True)
                logger.debug('user was created')

                m = hashlib.md5()
                m.update(new_user.email.encode('utf8'))
                invite_key = m.hexdigest()

                Invite.objects.create(user=new_user, key=invite_key, created_by=request.user)

                logger.debug('invite was created')

                c = {
                    'site': Site.objects.get_current(),
                    'sent': datetime.now(),
                    'user': new_user,
                    'message': form.cleaned_data['message'],
                    'key': invite_key,
                }

                subject = render_to_string('invites/email/new_invite_subject.txt', c)
                html_body = render_to_string('invites/email/new_invite.html', c)
                text_body = strip_tags(html_body)

                msg = EmailMultiAlternatives(subject, text_body, None, [new_user.email,])
                msg.attach_alternative(html_body, "text/html")
                msg.send()

                logger.debug('Done')

            messages.add_message(request, messages.INFO, u'The invite as successfully created. Email has been sent.', fail_silently=True)

            return HttpResponseRedirect(request.path)

    else:
        form = InviteUserForm()

    return render(request, 'invites/create.html', {'form': form, })


def activate(request, invite_key):
    invite = get_object_or_404(Invite, key=invite_key, is_activated=False)
    new_user = invite.user

    if request.method == 'POST':
        form = TocForm(request.POST)
        if form.is_valid():

            generated_password = generate_password()
            new_user.set_password(generated_password)
            new_user.is_active = True
            new_user.save()

            invite.is_activated=True
            invite.save()

            c = {
                'site': Site.objects.get_current(),
                'sent': datetime.now(),
                'user': new_user,
                'generated_password': generated_password,
            }

            subject = render_to_string('invites/email/new_user_subject.txt', c)
            html_body = render_to_string('invites/email/new_user.html', c)
            text_body = strip_tags(html_body)

            msg = EmailMultiAlternatives(subject, text_body, None, [new_user.email,])
            msg.attach_alternative(html_body, "text/html")
            msg.send()

            messages.add_message(request, messages.INFO, u'Email with your credentials has been sent to your email', fail_silently=True)

            return HttpResponseRedirect(reverse('home'))

    else:
        form = TocForm()

    return render(request, 'invites/tos.html', {'form': form, })

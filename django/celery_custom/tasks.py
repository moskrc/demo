from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery import task

from webapp.utils import TaskStepManager

from webapp.steps import ip_address_reservation
from webapp.steps import dns_record_creation
from webapp.steps import os_installation
from webapp.steps import relocation_to_destination_vlan
from webapp.steps import reboot_for_changes_to_take_effect
from webapp.steps import connectivity_check
from webapp.steps import tic_entry_creation
from webapp.steps import cts_entry_creation
from webapp.steps import avamar_request_generation
from webapp.steps import scom_request_generation
from webapp.steps import final_checks_before_delivery
from webapp.steps import email_confirmation

User = get_user_model()

STEPS = [
    ('IP address reservation', ip_address_reservation),
    ('DNS record creation', dns_record_creation),
    ('OS installation', os_installation),
    ('Relocation to destination VLAN', relocation_to_destination_vlan),
    ('Reboot for changes to take effect', reboot_for_changes_to_take_effect),
    ('Connectivity check', connectivity_check),
    ('TIC entry creation', tic_entry_creation),
    ('CTS entry creation', cts_entry_creation),
    ('Avamar request generation', avamar_request_generation),
    ('SCOM discovery & installation', scom_request_generation),
    ('Final checks before delivery', final_checks_before_delivery),
    ('Email confirmation', email_confirmation),
]


@task
def create_server_foreman(network, user):
    # For local Django users
    if network.server.username == 'admin':
        request_user = 'valiyev'  # Valid user required for TIC, CTS etc.
    else:
        request_user = network.server.username

    tm = TaskStepManager(create_server_foreman, extra={'VERBOSE': False, 'request_user': request_user})

    tm.add_steps(STEPS)

    tm.start(network, user)

    send_notification_email(network, True)


def send_notification_email(network, is_success):
    user = User.objects.get(username=network.server.username)

    c = {
        'network': network,
        'user': user,
        'is_success': is_success
    }

    subject = render_to_string('demo/multiform/email/server_subject.txt', c)
    subject = "".join(subject.splitlines())
    html_body = render_to_string('demo/multiform/email/server_body.html', c)
    text_body = strip_tags(html_body)

    msg = EmailMultiAlternatives(subject, text_body, None, [user.email, ])
    msg.attach_alternative(html_body, "text/html")
    msg.send()
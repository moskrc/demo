from datetime import datetime
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from site_config.models import SiteConfig


def new_product_email(product):
    """
    Send notification to admin
    """
    sc = SiteConfig.objects.get_current()

    c = {
        'site': Site.objects.get_current(),
        'sended': datetime.now(),
        'product': product,
        'profile': product.user.get_profile(),
        }

    subject = render_to_string('catalog/email/new_product_subject.txt', c)
    html_body = render_to_string('catalog/email/new_product.html', c)
    text_body = strip_tags(html_body)

    msg = EmailMultiAlternatives(subject, text_body, None, sc.get('email').split(','))
    msg.attach_alternative(html_body, "text/html")
    msg.send()


def product_was_approved_email(product):
    """
    Send notification to user
    """
    sc = SiteConfig.objects.get_current()

    c = {
        'site': Site.objects.get_current(),
        'sended': datetime.now(),
        'product': product,
        'profile': product.user.get_profile(),
        }

    subject = render_to_string('catalog/email/product_was_approved_subject.txt', c)
    html_body = render_to_string('catalog/email/product_was_approved.html', c)
    text_body = strip_tags(html_body)

    msg = EmailMultiAlternatives(subject, text_body, None, [product.user.email,])
    msg.attach_alternative(html_body, "text/html")
    msg.send()


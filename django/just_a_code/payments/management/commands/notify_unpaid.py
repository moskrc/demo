# -*- coding: utf-8
import datetime
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from catalog.models import Product


class Command(BaseCommand):
    help = u"Отсылаем письма тем у кого приближается конец срока оплаты"

    def handle(self, *args, **options):
        now = datetime.date.today()
        end = now + datetime.timedelta(days=7)

        product_for_notify = Product.objects.filter(paid_until__range=[now, end])

        for p in product_for_notify:
            print 'Send notify for %s' % p
            self.send_product_notify_email(p)

    def send_product_notify_email(self, product):
        c = {
            'days_remains': (product.paid_until - datetime.date.today()).days,
            'site': Site.objects.get_current(),
            'sended': datetime.datetime.now(),
            'profile': product.user.get_profile(),
            'product': product
        }

        subject = "".join(render_to_string('payments/email/need_to_pay_subject.txt', c).splitlines())
        html_body = render_to_string('payments/email/need_to_pay.html', c)
        text_body = strip_tags(html_body)

        msg = EmailMultiAlternatives(subject, text_body, None, [product.user.email, ])
        msg.attach_alternative(html_body, "text/html")
        msg.send()



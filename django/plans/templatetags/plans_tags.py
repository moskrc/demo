# -*- coding: utf-8
from django.forms import CheckboxInput
from django import template
from plans.models import DataPlan
import stripe
from django.conf import settings
from datetime import datetime

stripe.api_key = settings.STRIPE_API_KEY


register = template.Library()


@register.filter
def get_comment_for_invoice(inv):
    for x in inv['lines']:
        return x['plan']['name']

@register.filter
def date_from_unixstamp(unixstamp):
    return datetime.fromtimestamp(unixstamp)

@register.filter
def cents_to_dollars(cents):
    return cents / 100

@register.inclusion_tag("plans/elements/render_data_plans.html", takes_context=True)
def render_data_plans(context):
    plans = DataPlan.objects.filter(is_active=True)
    return {'plans': plans, 'user': context.request.user}



@register.inclusion_tag("plans/elements/my_data_plan.html", takes_context=True)
def render_my_data_plan(context):

    if context.request.user.data_plan:
        subscription = stripe.Subscription.retrieve(context.request.user.stripe_subscription_id)
        next_payment_date = datetime.fromtimestamp(subscription['current_period_end'])
    else:
        next_payment_date = None

    return {'my_plan': context.request.user.data_plan, 'user': context.request.user, 'next_payment_date': next_payment_date}


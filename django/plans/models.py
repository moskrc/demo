# coding: utf-8
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


class DataPlan(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=4, decimal_places=2, help_text=u'Price per month. Warning: you cannot modify the price field after (stripe)!')
    data = JSONField(help_text=u'Data Plan Features')
    is_active = models.BooleanField(default=True)
    is_recommend = models.BooleanField(default=False, help_text='Highlight this data plan')
    highlights = ArrayField(models.CharField(max_length=32, blank=True), size=16, help_text=u'Data Plan Features in text')
    order = models.SmallIntegerField(default=0, help_text='Smaller at the first of list')

    def __str__(self):
        return self.title

    def generate_stripe_plan_id(self):
        return 'plan-%s' % self.pk

    class Meta:
        ordering = ['order',]


@receiver(post_save, sender=DataPlan, dispatch_uid="update_stripe")
def update_stripe(sender, instance, **kwargs):
    try:
        stripe.Plan.retrieve("plan-%s" % instance.pk)
    except Exception as e:
        stripe.Plan.create(
            amount=int(instance.price * 100), # in cents
            interval="month",
            name=instance.title,
            currency="usd",
            trial_period_days="14",
            id=instance.generate_stripe_plan_id())

    p = stripe.Plan.retrieve(instance.generate_stripe_plan_id())
    p.name = instance.title
    p.save()
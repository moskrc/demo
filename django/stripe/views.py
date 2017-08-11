# -*- coding: utf-8 -*-
import json
import stripe
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from plans.models import DataPlan

logger = logging.getLogger('payments')

stripe.api_key = settings.STRIPE_API_KEY


@csrf_exempt
@login_required
def subscribe(request, plan_id):
    plan = get_object_or_404(DataPlan, pk=plan_id)

    logger.debug('User %s open subscribe page for data plan %s' % (request.user, plan))

    if request.user.stripe_subscription_id:
        # check for the same subscription
        old_subscription = stripe.Subscription.retrieve(request.user.stripe_subscription_id)
        if old_subscription['plan']['id'] == plan.generate_stripe_plan_id():
            # it's the same dataplan
            logger.debug('The user has the same data plan before, redirecting to main page')
            messages.add_message(request, messages.INFO, u'You are already subscribed to the plan', fail_silently=True)
            return HttpResponseRedirect(reverse('home'))

    if request.is_ajax():
        if request.method == 'POST':

            try:
                token = json.loads(request.body.decode('utf-8'))
                token_id = token['token']['id']

                logger.debug('Token ID %s' % token_id)

                try:
                    # search for the customer in stripe
                    customer = stripe.Customer.retrieve(request.user.stripe_customer_id)
                    logger.debug('Customer has been founded in stripe (%s)' % request.user.stripe_customer_id)
                except stripe.error.InvalidRequestError:
                    logger.debug('The customer not found, lets create')
                    # customer doesn't exist, let's create the customer
                    customer = stripe.Customer.create(
                        description="Customer for msm_customer",
                        email=request.user.email,
                        source=token_id
                    )
                    request.user.stripe_customer_id = customer['id']
                    request.user.save()

                    logger.debug('New customer has been created, id is %s' % customer['id'])

                if request.user.stripe_subscription_id:
                    # cancel old subscription
                    logger.debug('The customer has an old subscription %s' % request.user.stripe_subscription_id)
                    old_subscription = stripe.Subscription.retrieve(request.user.stripe_subscription_id)
                    logger.debug('Delete it')
                    old_subscription.delete()

                logger.debug('Create a new subsctiption. User: %s, DataPlan: %s' % (
                request.user, plan.generate_stripe_plan_id()))
                # create a new subscription
                new_subsctiption = stripe.Subscription.create(
                    customer=request.user.stripe_customer_id,
                    plan=plan.generate_stripe_plan_id()
                )

                # update subscription in our db
                request.user.stripe_subscription_id = new_subsctiption['id']
                request.user.data_plan = plan
                request.user.save()

                logger.debug('Done')

                return JsonResponse({'success': True})
            except Exception as e:
                logger.error('An exception has been occurred %s' % str(e))
                return JsonResponse({'error': True, 'message': 'An error has been occurred'})

    return render(request, 'payments/subscribe.html', {'plan': plan, 'key': settings.STRIPE_PUBLISHARE_API_KEY})


@login_required
def success(request, plan_id):
    plan = get_object_or_404(DataPlan, pk=plan_id)
    messages.add_message(request, messages.INFO, u'You subscription has been successfully created', fail_silently=True)
    return render(request, 'payments/success.html', {'plan': plan})


@login_required
def failure(request, plan_id):
    plan = get_object_or_404(DataPlan, pk=plan_id)
    messages.add_message(request, messages.ERROR, u'An error has occurred', fail_silently=True)
    return render(request, 'payments/failure.html', {'plan': plan})


@login_required
def cancel(request):
    logger.debug('User %s want to cancel subscription')

    try:
        logger.debug('The customer has subscription %s' % request.user.stripe_subscription_id)
        subscription = stripe.Subscription.retrieve(request.user.stripe_subscription_id)
        logger.debug('Delete it')
        subscription.delete()
        request.user.stripe_subscription_id = ''
        request.user.data_plan = None
        request.user.save()
        logger.debug('Done')
        messages.add_message(request, messages.INFO, u'You subscription has been successfully cancelled',
                             fail_silently=True)
    except Exception as e:
        logger.debug('Error on cancel subscription')
        logger.error(e)
        messages.add_message(request, messages.ERROR,
                             u'We are really sorry. An error has occurred. We will fix it soon.', fail_silently=True)

    return HttpResponseRedirect(reverse('home'))

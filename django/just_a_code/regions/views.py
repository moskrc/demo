from django.shortcuts import get_object_or_404
from annoying.decorators import ajax_request
from regions.models import GeoLocation
from django.shortcuts import redirect
from django.core.urlresolvers import reverse


@ajax_request
def get_location_info(request, location_id):
    location = get_object_or_404(GeoLocation, pk=location_id)
    return {'lat': location.lat, 'lng': location.lng, 'zoom': location.zoom, 'metro': location.metro,
            'name': location.name, 'region_name': location.region.name}


def set_city(request, city_id):
    city = get_object_or_404(GeoLocation, pk=city_id)

    response = redirect(reverse('home', kwargs={'city': city.subdomain}))
    response.set_cookie('city_id', city.id, max_age=1000)
    return response

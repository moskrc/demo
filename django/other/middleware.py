from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SubDomainMiddleware(object):

    def process_request(self, request):
        scheme = "http" if not request.is_secure() else "https"
        path = request.get_full_path()
        domain = request.META.get(
            'HTTP_HOST') or request.META.get('SERVER_NAME')

        pieces = domain.split('.')
        subdomain = pieces[0]
        
        default_domain = Site.objects.get(id=settings.SITE_ID)

        logger.debug('Scheme {}, path {}, domain {}, pieces {}, subdomain {}, \
                     default doamin {}'.format(
            scheme, path, domain, pieces, subdomain, default_domain)
        )

        if domain in {default_domain.domain, "testserver", "localhost"}:
            return None

        route = '/instance/{}/wait/'.format(subdomain)

        logger.debug('Try redirect to {} of main domain'.format(route))

        redirect_url = "{0}://{1}{2}".format(scheme, default_domain.domain,
                                             route)

        logger.debug('Redirect to {}...'.format(redirect_url))

        return HttpResponseRedirect(redirect_url)

#coding=utf8
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from catalog.models import Item


class LatestEntriesFeed(Feed):
    current_site = Site.objects.get_current()
    title = u"%s: новые вакансии" % (current_site.name,)
    if current_site.name == 'djangojobbers.ru':
        description = u'Работа для талантливых Django программистов'

    if current_site.name == 'phpjobbers.ru':
        description = u'Работа для талантливых PHP программистов'

    link = "/"

    def items(self):
        return Item.objects.filter(site=self.current_site).order_by('-modified')[:50]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return reverse('catalog_view', args=[item.pk])
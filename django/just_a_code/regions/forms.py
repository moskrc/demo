from django.forms import ModelForm, Textarea
from django_markdown.widgets import MarkdownWidget
from regions.models import GeoLocation


class GeoLocationForm(ModelForm):

    class Meta:
        model = GeoLocation
        widgets = {
            'description': MarkdownWidget,
            'seo_description': Textarea
        }


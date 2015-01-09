from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from easy_thumbnails.files import get_thumbnailer


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            t = get_thumbnailer(value).get_thumbnail({'size': (128, 128)})
            output.append('<img src="{}">'.format(t.url))

        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

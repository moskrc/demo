import os
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from jfu.http import upload_receive, UploadResponse, JFUResponse

from models import UploadedFile
from sorl.thumbnail import get_thumbnail


def info(request):
    file_ids = request.GET.get('ids', [])

    files = []
    for id in file_ids.split(','):
        try:
            id = int(id)
            files.append(UploadedFile.objects.get(pk=id))
        except UploadedFile.DoesNotExist:
            pass
        except Exception:
            # todo: int('str')
            pass



    res = []

    for f in files:
        thumb_url = get_thumbnail(f.image, '100x100').url
        basename = os.path.basename(f.image.path)

        file_dict = {
            'id': f.pk,
            'name': basename,
            'size': f.image.size,

            'url': settings.MEDIA_URL + f.image.name,
            'thumbnailUrl': thumb_url,

            'deleteUrl': reverse('jfu_delete', kwargs={'pk': f.pk}),
            'deleteType': 'POST',
        }

        res.append(file_dict)



    return UploadResponse(request, res)

@require_POST
def upload(request):
    new_file = upload_receive(request)

    if request.user.is_authenticated():
        image_owner = request.user
    else:
        image_owner = None
    instance = UploadedFile(image=new_file, user=image_owner, site=Site.objects.get_current())

    instance.save()

    options = {'size': (100, 70), 'crop': True}
    thumb_url = get_thumbnail(instance.image, '100x100').url


    basename = os.path.basename(instance.image.path)

    file_dict = {
        'id': instance.pk,
        'name': basename,
        'size': new_file.size,

        'url': settings.MEDIA_URL + instance.image.name,
        'thumbnailUrl': thumb_url,

        'deleteUrl': reverse('jfu_delete', kwargs={'pk': instance.pk}),
        'deleteType': 'POST',
    }

    return UploadResponse(request, file_dict)


@require_POST
def upload_delete(request, pk):
    success = True
    # try:
    #     instance = UploadedFile.objects.get(pk=pk)
    #     os.unlink(instance.image.path)
    #     instance.delete()
    # except UploadedFile.DoesNotExist:
    #     success = False

    return JFUResponse(request, success)
# -*- encoding: utf-8 -*-
import os
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db import models
from django.dispatch import receiver
from django_extensions.db.models import TimeStampedModel
from django.db.models.signals import pre_delete

from easy_thumbnails.fields import ThumbnailerImageField
from utils import make_uniq_key

from django.conf import settings

User = settings.AUTH_USER_MODEL

def get_upload_path(instance, file_name):
    uniq_file_name = make_uniq_key()
    extension = file_name.split('.')[-1].lower()
    new_file_name = os.path.join('ajax-uploader', 'images', uniq_file_name[0], uniq_file_name[1], uniq_file_name[2],
                                 '%s.%s' % (uniq_file_name, extension))
    return new_file_name


class UploadedFile(TimeStampedModel):
    image = ThumbnailerImageField(upload_to=get_upload_path, resize_source=dict(size=(1024, 768)))
    confirmed = models.BooleanField(default=False)
    user = models.ForeignKey(User)
    site = models.ForeignKey(Site)

    def __unicode__(self):
        try:
            return self.image.file.name
        except Exception as e:
            return 'the file was deleted'

    class Meta():
        verbose_name = u'UploadedFile'
        verbose_name_plural = u'UploadedFiles'


@receiver(pre_delete, sender=UploadedFile)
def before_delete(sender, **kwargs):
    instance = kwargs['instance']
    instance.image.delete_thumbnails()

    try:
        os.unlink(instance.image.path)
    except OSError:
        pass

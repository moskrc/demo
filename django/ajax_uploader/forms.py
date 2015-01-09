from django import forms
from ajax_uploader.models import UploadedFile
from widgets import AdminImageWidget


class UploadedFileForm(forms.ModelForm):

    class Meta:
        model = UploadedFile
        exclude = ()
        widgets = {
            'image': AdminImageWidget,
        }



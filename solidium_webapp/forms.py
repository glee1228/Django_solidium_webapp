from django import forms

from .models import ImageUploadModel
from .models import ScriptModel

class UploadImageForm(forms.Form):
    title = forms.CharField(max_length=50)
    # file = forms.FileField()
    image = forms.ImageField()


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUploadModel
        fields = ('description', 'document')

# Form (일반 폼)
class ScriptForm(forms.Form):
    script_path = forms.CharField(max_length=50)

    def save(self, commit=True):
        post = ScriptModel(**self.cleaned_data)
        if commit:
            post.save()
        return post


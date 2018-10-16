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
from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
   class Meta:
       model = User
       fields = ['username', 'password']
       widgets = {
           'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '15자 이내로 입력 가능합니다.'}),
           'password': forms.PasswordInput(attrs={'class': 'form-control'}),
       }
       labels = {
           'username': 'username',
           'password': 'password'
       }

   # 글자수 제한
   def __init__(self, *args, **kwargs):
       super(UserForm, self).__init__(*args, **kwargs)
       self.fields['username'].widget.attrs['maxlength'] = 15


class LoginForm(forms.ModelForm):
   class Meta:
       model = User
       fields = ['username', 'password'] # 로그인 시에는 유저이름과 비밀번호만 입력 받는다.

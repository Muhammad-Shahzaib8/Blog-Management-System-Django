from django import forms
from .models import Blog

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)
    from django import forms
from .models import Blog


class BlogSubmitForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = [
            'title',
            'category',
            'tags',
            'featured_image',
            'short_description',
            'content',
        ]
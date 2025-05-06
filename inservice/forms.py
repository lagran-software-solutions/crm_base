from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.urls import reverse
from django import forms
from .models import Reachus,indexform,Service,SEO, ForgetPasswordRequest
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from django import forms
from .models import Reachus

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('mobile', 'email')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('mobile', 'email', 'is_admin')


class HomepageForm(forms.ModelForm):
    class Meta:
        model = indexform
        fields = ['name', 'email', 'message']


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = Reachus
        fields = ['name', 'email', 'message']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not re.match(r'^[A-Za-z\s]{3,}$', name):
            raise forms.ValidationError("Name should contain only letters and at least 3 characters.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Enter a valid email address.")
        return email


class SEOModelForm(forms.ModelForm):
    class Meta:
        model = SEO
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['page'] = forms.ChoiceField(choices=self.get_urls())
    
    def get_urls(self):

        PAGE_CHOICES = [
            ('/', 'Home'),
            ('/about', '/about'),
            ('/services', '/services'),
            ('/team', '/team'),
        ]
        services = Service.objects.only('slug')
        for service in services:
            url = reverse('service_details', kwargs={'slug': service.slug})
            PAGE_CHOICES.append((url, url))
        
        return PAGE_CHOICES


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        max_length=55, 
        widget=forms.TextInput(attrs={
            'maxlength': 55, 
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg', 
            'id': 'id_password',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Current Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label=_("New Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Enter a strong password."),
    )
    new_password2 = forms.CharField(
        label=_("Re-enter New Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'renewPassword'}),
        help_text=_("Enter the same password as above."),
    )

    def clean_new_password2(self):
        new_password2 = self.cleaned_data.get("new_password2")

        if len(new_password2) < 8: 
            raise ValidationError(_("Password must be at least 8 characters long."))
        
        if not any(char.isdigit() for char in new_password2):
            raise ValidationError(_("Password must contain at least one digit."))

        if not any(char.isalpha() for char in new_password2):
            raise ValidationError(_("Password must contain at least one letter."))

        if not any(char in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+'] for char in new_password2):
            raise ValidationError(_("Password must contain at least one special character."))

        if self.cleaned_data.get("new_password1") != new_password2:
            raise ValidationError(_("The two password fields didn’t match."))

        return new_password2


class ForgetPasswordForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        max_length=55, 
        widget=forms.TextInput(attrs={
            'maxlength': 55, 
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your name'
        })
    )
    email_or_mobile = forms.CharField(
        label="Email or Mobile",
        max_length=55, 
        widget=forms.TextInput(attrs={
            'maxlength': 55, 
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email or mobile'
        })
    )
    message = forms.CharField(
        label="Email or Mobile",
        max_length=55, 
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter Message',
            'rows': 3
        })
    )

    class Meta:
        model = ForgetPasswordRequest
        fields = '__all__'

from django import forms
from .models import RequestService, Service, SubService, ClientAdminFolder, ClientAdminFile, ServiceFile, \
                    ServiceRequestFolder, Complaint
from django.contrib.auth import get_user_model
import re


User = get_user_model()


class RequestServiceForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    sub_services = forms.ModelMultipleChoiceField(
        queryset=SubService.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = RequestService
        fields = ['services', 'sub_services']


class ClientAdminFolderForm(forms.ModelForm):

    class Meta:
        model = ClientAdminFolder
        fields = ('name', )


class ServiceRequestFolderForm(forms.ModelForm):

    class Meta:
        model = ServiceRequestFolder
        fields = ('name', )


class ClientAdminFileForm(forms.ModelForm):

    class Meta:
        model = ClientAdminFile
        fields = ('file', )


class ServiceFileForm(forms.ModelForm):

    class Meta:
        model = ServiceFile
        exclude = ('slug', 'folder')


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'profile_pic', 'about', 'address', 'mobile', 'email']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter name',
                'readonly': 'readonly', 
            }),
            'profile_pic': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'title': 'Upload new profile image',
            }),
            'about': forms.Textarea(attrs={
                'class': 'form-control', 
                'style': 'height: 100px',
                'placeholder': 'Tell us something about yourself...',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your address',
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your phone number',
                'readonly': 'readonly', 
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your email address',
                'readonly': 'readonly', 
            }),
        }


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_pic', 'about', 'address', 'mobile', 'email']
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your first name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your last name',
            }),
            'profile_pic': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'title': 'Upload new profile image',
            }),
            'about': forms.Textarea(attrs={
                'class': 'form-control', 
                'style': 'height: 100px',
                'placeholder': 'Tell us something about yourself...',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your address',
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your phone number',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your email address',
            }),
        }


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        exclude = ('user', )
        
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject',
                'required': True,  
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your message',
                'required': True, 
                'minlength': 10,   
            }),
        }


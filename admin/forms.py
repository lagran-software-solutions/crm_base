from django import forms
from client.models import RequestService, Service, SubService, InvoiceItem, Invoice, InvoiceRecord
from inservice.models import User
from django.contrib.auth.hashers import make_password


STATUS_CHOICES = [
    ('', 'All'),
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]


class DateInput(forms.DateInput):
    input_type = 'date'


class RequestServiceForm(forms.ModelForm):
    class Meta:
        model = RequestService
        fields = ['assigned_to_employee', 'date_of_completion', 'status']

        widgets = {
            'assigned_to_employee': forms.Select(attrs={'class': 'form-control'}), 
            'status': forms.Select(attrs={'class': 'form-control'}),
            'date_of_completion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to_employee'].required = True


class BaseAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name', 
            'last_name', 
            'email', 
            'mobile', 
            'employee_id', 
            'date_of_joining', 
            'date_of_birth', 
            'reporting_manager'
        ]

        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'maxlength': '150',
                    'pattern': '[a-zA-Z0-9 ]*', 
                    'oninput': "this.value = this.value.replace(/[^A-Za-z0-9 ]/g, '');" 
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'maxlength': '150',
                    'pattern': '[a-zA-Z0-9 ]*', 
                    'oninput': "this.value = this.value.replace(/[^A-Za-z0-9 ]/g, '');" 
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        field_attrs = {
            'username': 'Enter username',
            'first_name': 'Enter first name',
            'last_name': 'Enter last name',
            'email': 'Enter your email address',
            'mobile': 'Enter your mobile number',
            'employee_id': 'Enter employee ID',
            'date_of_joining': 'Enter date of joining',
            'date_of_birth': 'Enter date of birth',
            'reporting_manager': 'Enter reporting manager',
        }
        
        for field, placeholder in field_attrs.items():
            self.fields[field].widget.attrs.update({'placeholder': placeholder, 'class': 'form-control'})

        self.fields['date_of_joining'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['date_of_birth'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})

    
class AdminSignupForm(BaseAdminForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-control'}),
        label="Password",
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-control'}),
        label="Confirm Password",
        required=True
    )

    class Meta(BaseAdminForm.Meta):
        fields = BaseAdminForm.Meta.fields + ['password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password']) 
        if commit:
            user.save()
        return user


class UpdateAdminForm(BaseAdminForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a new password (optional)', 'class': 'form-control'}),
        label="New Password",
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password (optional)', 'class': 'form-control'}),
        label="Confirm New Password",
        required=False
    )

    class Meta(BaseAdminForm.Meta):
        fields = BaseAdminForm.Meta.fields + ['password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password or confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.password = make_password(password)
        if commit:
            user.save()
        return user


class BaseClientForm(forms.ModelForm): 
    class Meta:
        model = User
        fields = [
            'username',
            'entity_type',
            'name', 
            'registration', 
            'cin', 
            'llpin', 
            'firm_no', 
            'email', 
            'mobile',
            'legal_address', 
            'branch_address', 
            'pan', 
            'tan', 
            'pf_number', 
            'esi_number',
            'trade_license_number', 
            'rental_agreement', 
            'noc', 
            'pan_document', 
            'tan_document', 
            'incorporation_certificate', 
            'mom',
            'aoa',
            'other_documents',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'maxlength': '150',
                    'pattern': '[a-zA-Z0-9 ]*', 
                    'oninput': "this.value = this.value.replace(/[^A-Za-z0-9 ]/g, '');" 
                }
            )
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mom'].label = 'MOA' 
        self.fields['noc'].label = 'NOC'
        self.fields['aoa'].label = 'AOA'
        self.fields['pan'].label = 'PAN'
        self.fields['tan'].label = 'TAN'
        self.fields['cin'].label = 'CIN'
        self.fields['pf_number'].label = 'PF number'
        self.fields['pan_document'].label = 'PAN document'
        self.fields['tan_document'].label = 'TAN document'
        self.fields['esi_number'].label = 'ESI number'
        
        field_attrs = {
            'username': 'Enter username',
            'entity_type': 'Enter Entity type',
            'email': 'Enter email address',
            'mobile': 'Enter mobile number',
            'name': 'Enter name',
            'pan': 'Enter PAN number',
            'cin': 'Enter CIN number',
            'tan': 'Enter TAN number',
            'legal_address': 'Enter legal address',
            'branch_address': 'Enter branch address',
            'pf_number': 'Enter PF number',
            'esi_number': 'Enter ESI number',
            'trade_license_number': 'Enter trade license number',
            'rental_agreement': 'Upload rental agreement',
            'noc': 'Upload NOC document',
            'pan_document': 'Upload PAN document',
            'tan_document': 'Upload TAN document',
            'incorporation_certificate': 'Upload incorporation certificate',
            'mom': 'Upload MOA',
            'aoa': 'Upload AOA',
            'other_documents': 'Upload other documents',
            'llpin': 'Enter llpin', 
            'registration': 'Choose one option', 
            'firm_no': 'Enter firm no', 
        }
        
        for field, placeholder in field_attrs.items():
            self.fields[field].widget.attrs.update({'placeholder': placeholder, 'class': 'form-control'})


class ClientSignupForm(BaseClientForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-control'}),
        label="Password",
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-control'}),
        label="Confirm Password",
        required=True
    )

    class Meta(BaseClientForm.Meta):
        fields = BaseClientForm.Meta.fields + ['password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password']) 
        if commit:
            user.save()
        return user


class UpdateClientForm(BaseClientForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a new password (optional)', 'class': 'form-control'}),
        label="New Password",
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password (optional)', 'class': 'form-control'}),
        label="Confirm New Password",
        required=False
    )

    class Meta(BaseClientForm.Meta):
        fields = BaseClientForm.Meta.fields + ['password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password or confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.password = make_password(password)
        if commit:
            user.save()
        return user


class FilterModelForm(forms.Form):
    search_term = forms.CharField(
        max_length=100,
        required=False,
        label="Search Request, Service, or Sub-Service",
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter request number, Request Service, or Assigned To Employee',
                'id': 'id_admin_search_term',
                'class': 'form-control'
            }
        )
    )

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Start Date"
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="End Date"
    )

    @property
    def filters(self):
        data = self.cleaned_data
        filters_ = {}
        search_term = data.get('search_term', '').strip()

        if search_term:
            filters_['search_term'] = search_term

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date:
            filters_['start_date'] = start_date
        if end_date:
            filters_['end_date'] = end_date
        return filters_


class DashboardFilterForm(forms.Form):
    admin_start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'id': 'admin-start-date'}),
        label='Start Date'
    )
    admin_end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'id': 'admin-end-date'}),
        label='End Date'
    )
    client_start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'id': 'client-start-date'}),
        label='Start Date'
    )
    client_end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'id': 'client-end-date'}),
        label='End Date'
    )

    @property
    def filters(self):
        data = self.cleaned_data
        filters_ = {}
        if data.get('admin_start_date'):
            filters_['request_date__gte'] = data['admin_start_date']
        if data.get('admin_end_date'):
            filters_['request_date__lte'] = data['admin_end_date']
        if data.get('client_start_date'):
            filters_['request_date__gte'] = data['client_start_date']
        if data.get('client_end_date'):
            filters_['request_date__lte'] = data['client_end_date']
        return filters_

    @property
    def or_filters(self):
        # Assuming you might have additional fields to handle for OR conditions
        return {}


class ComplaintFilterForm(forms.Form):

    client_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter client name',
            'class': 'form-control'
        }),
    )
    complaint_from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'complaint_from_date'
        }),
    )
    complaint_to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'complaint_to_date'
        }),
    )


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service name',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class SubServiceForm(forms.ModelForm):
    class Meta:
        model = SubService
        fields = ['name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter sub-service name',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class AdminClientSearchForm(forms.Form):
    q = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'id': 'id_search_term',
            'class': 'form-control', 
            'placeholder': 'Search by username or name',
        }),
        label='' 
    )


class InvoiceForm(forms.ModelForm):
    invoice_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'invoice_date_id'
        }),
    )
    class Meta:
        model = Invoice
        fields = [
            'logo', 'from_name', 'from_business', 'from_gst', 'from_address', 
            'from_pan', 'from_email', 'to_name', 'to_business', 'to_gst',
            'to_address', 'to_pan', 'to_email', 'invoice_number',
            'invoice_date', 'bank_name', 'account_number', 'ifsc_code',
            'branch_name', 'mim_id', 'swift_id', 'additional_note'
        ]

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)

        self.fields['logo'].required = True
        self.fields['from_name'].required = True
        self.fields['from_business'].required = True
        self.fields['from_gst'].required = True
        self.fields['from_address'].required = True
        self.fields['from_pan'].required = True
        self.fields['from_email'].required = True
        self.fields['to_name'].required = True
        self.fields['to_business'].required = True
        self.fields['to_gst'].required = True
        self.fields['to_address'].required = True
        self.fields['to_pan'].required = True
        self.fields['to_email'].required = True
        self.fields['invoice_number'].required = True
        self.fields['invoice_date'].required = True
        self.fields['bank_name'].required = True
        self.fields['account_number'].required = True
        self.fields['ifsc_code'].required = True
        self.fields['branch_name'].required = True
        self.fields['mim_id'].required = True
        self.fields['swift_id'].required = True

        self.fields['logo'].widget.attrs.update({
            'class': 'form-control', 
            'accept': 'image/*',     
            'style': 'cursor: pointer;',      
        })

        self.fields['from_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
        self.fields['from_business'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your Business Name'
        })
        self.fields['from_gst'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your GST Number'
        })
        self.fields['from_address'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your Address'
        })
        self.fields['from_pan'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your PAN Number'
        })
        self.fields['from_email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'youremail@example.com'
        })
        self.fields['to_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Client Name'
        })
        self.fields['to_business'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Client Business Name'
        })
        self.fields['to_gst'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Client GST Number'
        })
        self.fields['to_address'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Client Address'
        })
        self.fields['to_pan'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Client PAN Number'
        })
        self.fields['to_email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'clientemail@example.com'
        })
        self.fields['invoice_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Invoice Number'
        })


        self.fields['invoice_date'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['bank_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Bank Name'
        })
        self.fields['account_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Account Number'
        })
        self.fields['ifsc_code'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter IFSC Code'
        })
        self.fields['branch_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Branch Name'
        })
        self.fields['mim_id'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter MIM ID'
        })
        self.fields['swift_id'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Swift ID'
        })
        self.fields['additional_note'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter any additional note (optional)'
        })


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'rate', 'gst', 'other_tax']


class InvoiceRecordForm(forms.ModelForm):
    invoice_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
    )

    class Meta:
        model = InvoiceRecord
        fields = [
            'logo', 'company_name', 'company_address', 'company_contact', 'invoice_date',
            'range_address', 'division', 'commissioner', 'reverse_charge', 'invoice_number',
            'receiver_name', 'receiver_address', 'place_of_supply', 'gstn',
            'state', 'state_code', 'total_amount_before_task', 'cgst', 'sgst',
            'igst', 'tax_amount', 'total_amount_after_task', 'total_in_words',
            'bank_account', 'ifsc', 'branch', 'qr_code', 'pan', 'tds_rate',
            'payment', 'gpay_phone', 'footer_content'
        ]

    def __init__(self, *args, **kwargs):
        super(InvoiceRecordForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.qr_code:
            self.fields['qr_code'].widget.attrs.update({
                'data-existing-file': self.instance.qr_code.url
            })

        for field_name, field in self.fields.items():
            field.required = True
            field.widget.attrs.update({'class': 'form-control'})

        self.fields['logo'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*',
            'style': 'cursor: pointer;',
        })

        if self.instance and self.instance.logo:
            self.fields['logo'].widget.attrs.update({
                'data-existing-file': self.instance.logo.url 
            })

        self.fields['company_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Company Name'
        })

        self.fields['invoice_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Invoice Number'
        })

        self.fields['company_address'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Company Address'
        })

        self.fields['company_contact'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter Company Contact Information'
        })

        for field in ['range_address', 'division', 'commissioner', 'receiver_name',
                      'receiver_address', 'place_of_supply', 'gstn', 'state',
                      'state_code', 'total_in_words', 'bank_account', 'ifsc',
                      'branch', 'payment', 'pan', 'tds_rate', 'gpay_phone', 'footer_content']:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.replace("_", " ").capitalize()}'
            })

        self.fields['reverse_charge'].widget.attrs.update({
            'class': 'form-select'
        })

        for field in ['total_amount_before_task', 'cgst', 'sgst', 'igst',
                      'tax_amount', 'total_amount_after_task']:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'type': 'number',
                'step': '0.01',
            })

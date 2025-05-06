from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import string
import random
import uuid
from django.utils.functional import cached_property
from django.db.models import Sum, F, FloatField
from tinymce.models import HTMLField


User = get_user_model()


STATUS_CHOICES = [
    ('empty', 'Empty'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]


STATUS_INVOICE_CHOICES = [
    ('empty', 'Empty'),
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('cancelled', 'Cancelled'),
]


class NameSlugModel(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.name = self.name.capitalize()
        if not self.slug:
            slug = slugify(self.name) + "-" + str(uuid.uuid4())
            self.slug = slug[:49]
        super(NameSlugModel, self).save(*args, **kwargs)


class Service(NameSlugModel):
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.name


class SubService(NameSlugModel):
    is_active = models.BooleanField(default=True)
    # provider = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_admin': True},
    #                              related_name="sub_service_provider")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="sub_service")

    class Meta:
        verbose_name = 'Sub Service'
        verbose_name_plural = 'Sub Services'

    def __str__(self):
        return self.name
    

class RequestServiceManager(models.Manager):
    
    def client_request_in_progress_count(self):
        return self.filter(status='in_progress', user__isnull=False).count()
    
    def client_request_completed_count(self):
        return self.filter(status='completed', user__isnull=False).count()
    
    def client_request_empty_count(self):
        return self.filter(status='empty', user__isnull=False).count()
    
    def client_request_cancelled_count(self):
        return self.filter(status='cancelled', user__isnull=False).count()
        

class RequestService(models.Model):
    request_number = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_admin': False}, null=True, blank=True,
                             related_name="user_request_service")
    services = models.ManyToManyField(Service)
    sub_services = models.ManyToManyField(SubService)
    assigned_to_employee = models.ForeignKey(User, on_delete=models.SET_NULL,
                                              limit_choices_to={'is_admin': True}, null=True, blank=True,
                                              related_name="assigned_employee")
    request_date = models.DateTimeField(auto_now_add=True)
    date_of_completion = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='empty')
    created_by_admin = models.BooleanField(default=False)

    objects = RequestServiceManager()

    def save(self, *args, **kwargs):
        if not self.request_number:
            if self.assigned_to_employee:
                prefix = 'TK-'
            else:
                prefix = 'RN-'

            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            self.request_number = prefix + suffix
        super(RequestService, self).save(*args, **kwargs)

    def __str__(self):
        return f"Request {self.request_number} by {self.user}"
    
    class Meta:
        ordering = ['-request_date'] 


class RequestServiceChat(models.Model):
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    service = models.ForeignKey(RequestService, on_delete=models.CASCADE, related_name='service_request_chat')
    admin = models.ForeignKey(User, limit_choices_to={'is_admin': True},
                              on_delete=models.CASCADE, null=True, blank=True, related_name='admin_service_request_chat')
    client = models.ForeignKey(User, limit_choices_to={'is_admin': False}, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='client_service_request_chat')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.service.request_number} - admin({self.admin}) - client({self.client})"
    
    class Meta:
        ordering = ['-created_at'] 


class ServiceRequestFolder(models.Model):
    name = models.CharField(max_length=255)
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    service = models.ForeignKey(RequestService, on_delete=models.CASCADE, related_name='service_request', null=True, blank=True)
    admin = models.ForeignKey(User, limit_choices_to={'is_admin': True},
                              on_delete=models.CASCADE, null=True, blank=True, related_name='admin_request_service_folder')
    client = models.ForeignKey(User, limit_choices_to={'is_admin': False}, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='client_request_service_folder')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at'] 
        

class ServiceFile(models.Model):
    folder = models.ForeignKey(ServiceRequestFolder, related_name='service_request_file', on_delete=models.CASCADE)
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    file = models.FileField(upload_to='file')
    admin = models.ForeignKey(User, limit_choices_to={'is_admin': True},
                              on_delete=models.CASCADE, null=True, blank=True, related_name='admin_file_upload')
    client = models.ForeignKey(User, limit_choices_to={'is_admin': False}, null=True, blank=True, on_delete=models.CASCADE,
                               related_name='client_file_upload')
    is_private = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.folder.name
    
    @cached_property
    def file_size(self):
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0
    
    class Meta:
        ordering = ['-uploaded_at'] 
    

class Folder(NameSlugModel):
    request_service = models.ForeignKey(RequestService, on_delete=models.CASCADE, related_name="folders")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Folder {self.name} for {self.request_service.request_number}"

    class Meta:
        ordering = ['-created_at'] 


class RequestStatus(models.Model):
    request_number = models.ForeignKey(RequestService, on_delete=models.CASCADE, related_name='request_status')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_request_status')
    last_update = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comment = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Request number: {self.request_number.request_number} and employee: {self.employee.first_name}"


class RequestFile(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="file")
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File {self.slug} in {self.folder.name} uploaded at {self.uploaded_at}"

    class Meta:
        ordering = ['-created_at'] 


class ClientAdminFolder(models.Model):
    name = models.CharField(max_length=255)
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    admin = models.ForeignKey(User, limit_choices_to={'is_admin': True},
                              on_delete=models.CASCADE, null=True, blank=True, related_name='admin_folder')
    client = models.ForeignKey(User, limit_choices_to={'is_admin': False}, on_delete=models.CASCADE,
                               related_name='client_folder')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at'] 


class ClientAdminFile(models.Model):
    folder = models.ForeignKey(ClientAdminFolder, related_name='folder_file', on_delete=models.CASCADE)
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    file = models.FileField(upload_to='file')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.folder.name
    
    @cached_property
    def file_size(self):
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0
    
    class Meta:
        ordering = ['-uploaded_at'] 


class ServiceRequestFile(models.Model):
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    service = models.ForeignKey(RequestService, on_delete=models.CASCADE, related_name='service_request_file')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_request_file_owner')
    file = models.FileField(upload_to='file')


class Notification(models.Model):
    RECIPIENT_CHOICES = [
        ('admin', 'Admin'),
        ('client', 'Client'),
        ('both', 'Both'),
    ]
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    admin = models.ForeignKey(User, limit_choices_to={'is_admin': True},
                              on_delete=models.CASCADE, null=True, blank=True, related_name='admin_notification')
    client = models.ForeignKey(User, limit_choices_to={'is_admin': False},
                              on_delete=models.CASCADE, null=True, blank=True, related_name='client_notification')
    message = models.TextField()
    url = models.URLField(max_length=200, null=True, blank=True)
    is_seen = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_CHOICES, default='client')

    def __str__(self):
        return f"{self.message} - {self.recipient_type}"

    class Meta:
        ordering = ['-created_at'] 


class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_admin': False})
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message} - {self.user.first_name}"

    class Meta:
        ordering = ['-created_at'] 


class InvoiceManager(models.Manager):
    def total_amount_by_status(self, status):
        return self.filter(status=status).aggregate(
            total_amount=Sum('items__amount')
        )['total_amount'] or 0.0

    def sub_amount_by_status(self, status):
        return self.filter(status=status).aggregate(
            sub_amount=Sum(F('items__amount') - F('items__total_tax'), output_field=FloatField())
        )['sub_amount'] or 0.0

    def total_paid_amount(self):
        return self.total_amount_by_status('paid')

    def total_cancelled_amount(self):
        return self.total_amount_by_status('cancelled')

    def total_pending_amount(self):
        return self.total_amount_by_status('pending')

    def total_empty_amount(self):
        return self.total_amount_by_status('empty')

    def sub_paid_amount(self):
        return self.sub_amount_by_status('paid')

    def sub_cancelled_amount(self):
        return self.sub_amount_by_status('cancelled')

    def sub_pending_amount(self):
        return self.sub_amount_by_status('pending')

    def sub_empty_amount(self):
        return self.sub_amount_by_status('empty')

    def total_amount(self):
        return self.aggregate(
            total_amount=Sum('items__amount')
        )['total_amount'] or 0.0

    def sub_amount(self):
        return self.aggregate(
            sub_amount=Sum(F('items__amount') - F('items__total_tax'), output_field=FloatField())
        )['sub_amount'] or 0.0

    def count_by_status(self, status):
        return self.filter(status=status).count()


class Invoice(models.Model):
    logo = models.ImageField(upload_to='invoice_logo', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_INVOICE_CHOICES, default='empty')
    from_name = models.CharField(max_length=255)
    from_business = models.CharField(max_length=255, blank=True, null=True)
    from_gst = models.CharField(max_length=100, blank=True, null=True)
    from_address = models.TextField(blank=True, null=True)
    from_pan = models.CharField(max_length=100, blank=True, null=True)
    from_email = models.EmailField(blank=True, null=True)
    to_name = models.CharField(max_length=255)
    to_business = models.CharField(max_length=255, blank=True, null=True)
    to_gst = models.CharField(max_length=100, blank=True, null=True)
    to_address = models.TextField(blank=True, null=True)
    to_pan = models.CharField(max_length=100, blank=True, null=True)
    to_email = models.EmailField(blank=True, null=True)
    invoice_number = models.CharField(max_length=100, unique=True)
    invoice_date = models.DateField()
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=50, blank=True, null=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    mim_id = models.CharField(max_length=100, blank=True, null=True)
    swift_id = models.CharField(max_length=100, blank=True, null=True)
    additional_note = models.TextField(blank=True, null=True)

    objects = InvoiceManager()
   

    def __str__(self):
        return self.invoice_number



    

class InvoiceRecordManager(models.Manager):
    def total_amount_by_status(self, status):
        return self.filter(status=status).aggregate(
            total_amount=Sum('invoice_items__amount')
        )['total_amount'] or 0.0

    def sub_amount_by_status(self, status):
        return self.filter(status=status).aggregate(
            sub_amount=Sum(('total_amount_after_task'), output_field=FloatField())
        )['sub_amount'] or 0.0

    def total_paid_amount(self):
        return self.total_amount_by_status('paid')

    def total_cancelled_amount(self):
        return self.total_amount_by_status('cancelled')

    def total_pending_amount(self):
        return self.total_amount_by_status('pending')

    def total_empty_amount(self):
        return self.total_amount_by_status('empty')

    def sub_paid_amount(self):
        return self.sub_amount_by_status('paid')

    def sub_cancelled_amount(self):
        return self.sub_amount_by_status('cancelled')

    def sub_pending_amount(self):
        return self.sub_amount_by_status('pending')

    def sub_empty_amount(self):
        return self.sub_amount_by_status('empty')

    def total_amount(self):
        return self.aggregate(
            total_amount=Sum('items__amount')
        )['total_amount'] or 0.0

    def sub_amount(self):
        return self.aggregate(
            sub_amount=Sum(('total_amount_after_task'), output_field=FloatField())
        )['sub_amount'] or 0.0

    def count_by_status(self, status):
        return self.filter(status=status).count()



class InvoiceRecord(models.Model):
    # Header fields
    logo = models.ImageField(upload_to='logos/')
    company_name = models.CharField(max_length=255)
    company_address = HTMLField()
    company_contact = HTMLField()
    invoice_date = models.DateField()
    invoice_number = models.CharField(max_length=200, unique=True)
    # Record details
    range_address = models.CharField(max_length=100)
    division = models.CharField(max_length=100)
    commissioner = models.CharField(max_length=100)
    reverse_charge = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    receiver_name = models.CharField(max_length=255)
    receiver_address = models.TextField()
    place_of_supply = models.CharField(max_length=100)
    gstn = models.CharField(max_length=50)
    state = models.CharField(max_length=100)
    state_code = models.CharField(max_length=10)

    # Total details
    total_amount_before_task = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    igst = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount_after_task = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_in_words = models.CharField(max_length=250)

    # Bank details
    bank_account = models.CharField(max_length=50)
    ifsc = models.CharField(max_length=15)
    branch = models.CharField(max_length=100)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    # Terms and conditions
    pan = models.CharField(max_length=50, null=True, blank=True)
    tds_rate = models.CharField(max_length=50, null=True, blank=True)
    payment = models.CharField(max_length=255, null=True, blank=True)
    gpay_phone = models.CharField(max_length=15)

    # Footer content
    footer_content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_INVOICE_CHOICES, default='empty')

    objects = InvoiceRecordManager()
    def __str__(self):
        return f"InvoiceRecord for {self.receiver_name} ({self.company_name})"


class InvoiceRecordItem(models.Model):
    invoice = models.ForeignKey(InvoiceRecord, on_delete=models.CASCADE, related_name='invoice_items')
    description = models.TextField()
    sac = models.CharField(max_length=50, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item: {self.description} (Invoice: {self.invoice.id}) {self.amount}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(InvoiceRecord, related_name="items", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    other_tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.description
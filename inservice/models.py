from tinymce.models import HTMLField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property

phone_validator = RegexValidator(r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$",
                                 "The phone number provided is invalid")


class CustomUserManager(BaseUserManager):
    
    def _create_user(self, username, mobile, email, password, **extra_fields):
        """
        Create and save a user with the given username, mobile, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        if not email:
            raise ValueError("The given email must be set")
        
        email = self.normalize_email(email)
        user = self.model(username=username, mobile=mobile, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, mobile, email=None, password=None, **extra_fields):
        """
        Create and return a regular user with username, mobile, email, and password.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, mobile, email, password, **extra_fields)

    def create_superuser(self, username, mobile=None, email=None, password=None, **extra_fields):
        """
        Create and return a superuser with username, mobile, email, and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        mobile = mobile or ''
        
        return self._create_user(username, mobile, email, password, **extra_fields)


class User(AbstractUser):
    ENTITY_TYPE_CHOICES = [
        ('company', 'Company'),
        ('llp', 'LLP'),
        ('partnership', 'Partnership'),
        ('sole_proprietor', 'Sole Proprietor'),
    ]
    REGISTRATION_FIELD_CHOICES = [
        ('llpin', 'LLPIN'),
        ('firm_no', 'Firm No'),
        ('cin', 'CIN'),
    ]
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    # username = None
    mobile = models.CharField(max_length=12, validators=[phone_validator])
    country_code = models.CharField(max_length=10, default='91')
    email = models.EmailField()
    profile_pic = models.ImageField(upload_to='user_profiles', null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)

    entity_type = models.CharField(
        max_length=20,
        choices=ENTITY_TYPE_CHOICES,
        default='company'
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    pan = models.CharField(max_length=10, null=True, blank=True)
    tan = models.CharField(max_length=10, null=True, blank=True)
    registration = models.CharField(
        max_length=10,
        choices=REGISTRATION_FIELD_CHOICES,
        default='cin'
    )
    llpin = models.CharField(max_length=8, blank=True, null=True)
    firm_no = models.CharField(max_length=15, blank=True, null=True)
    cin = models.CharField(max_length=21, null=True, blank=True)  
    legal_address = models.TextField(null=True, blank=True)
    branch_address = models.TextField(null=True, blank=True)
    pf_number = models.CharField(max_length=15, null=True, blank=True)
    esi_number = models.CharField(max_length=15, null=True, blank=True)
    trade_license_number = models.CharField(max_length=50, null=True, blank=True)

    # Document fields (you can modify the file field according to your requirements)
    rental_agreement = models.FileField(upload_to='documents/rental_agreement/', null=True, blank=True)
    noc = models.FileField(upload_to='documents/noc/', null=True, blank=True)
    pan_document = models.FileField(upload_to='documents/pan/', null=True, blank=True)
    tan_document = models.FileField(upload_to='documents/tan/', null=True, blank=True)
    incorporation_certificate = models.FileField(upload_to='documents/incorporation/', null=True, blank=True)
    mom = models.FileField(upload_to='documents/mom/', null=True, blank=True)
    aoa = models.FileField(upload_to='documents/aoa/', null=True, blank=True)
    other_documents = models.FileField(upload_to='documents/others/', null=True, blank=True)

    #admin
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    reporting_manager = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ["email"]
    # USERNAME_FIELD = 'mobile'

    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    def get_full_name(self):
        if not self.is_admin:
            return self.name
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        if not self.is_admin:
            return f"{self.name}"
        else:
            return f"{self.get_full_name()}"


class Homebanner(models.Model):
    title = models.CharField(max_length=150)
    subtitle1 = models.CharField(max_length=150)
    subtitle2 = models.CharField(max_length=150)
    subtitle3 = models.CharField(max_length=150)
    buttontext = models.CharField(max_length=150)
    image = models.ImageField(upload_to='homepages')

    def __str__(self):
        return self.title

class Elementor(models.Model):
    header = models.CharField(max_length=100)
    header_image = models.ImageField(upload_to='aboutus')
    title = HTMLField(null=True, blank=True)
    discription_image = models.ImageField(upload_to='aboutus')
    breif_discription = HTMLField(null=True, blank=True)
    detail_discription = HTMLField(null=True, blank=True)
    note = HTMLField(null=True, blank=True)
    button1 = models.CharField(max_length=50)
    button2 = models.CharField(max_length=50)
    #----------
    banner_title = models.CharField(max_length=150)
    gallery_header = HTMLField(null=True, blank=True)
    gallery_footer = HTMLField(null=True, blank=True)
    workflow_header = HTMLField(null=True, blank=True)
    services_header = models.CharField(max_length=100)
    services_title = models.CharField(max_length=150)

    def __str__(self):
        return self.title
    

class Aboutgallery(models.Model):
    description = models.TextField(null=True, blank=True)
    title=models.CharField(max_length=256,null=True,blank=True)
    image = models.ImageField(upload_to='about_gallery')
    
    def __str__(self):
        return self.title if self.title else "about gallery title"

class AboutHistory(models.Model):
    year = models.CharField(max_length=256,null=True, blank=True)
    title = models.CharField(max_length=256,null=True,blank=True)
    decription=models.TextField(blank=True,null=True)
    image=models.ImageField(upload_to='about')

    def __str__(self):
        return self.title if self.title else "about history title"

class OurSolution(models.Model):
    image = models.ImageField(upload_to='OurSolution')
    discription  = HTMLField(null=True, blank=True)
    button = models.CharField(max_length=150)

    def __str__(self):
        return self.button
    
    
class Workflow(models.Model):
    left_year =  models.IntegerField()
    left_name = models.CharField(max_length=150)
    left_discription  = HTMLField(null=True, blank=True)
    left_image = models.ImageField(upload_to='Workflow')
    right_year =  models.IntegerField()
    right_name = models.CharField(max_length=150)
    right_discription  = HTMLField(null=True, blank=True)
    right_image = models.ImageField(upload_to='Workflow')

    def __str__(self):
        return self.left_name

class Advertise(models.Model):
    discription = HTMLField(null=True, blank=True)
    button_a = models.CharField(max_length=150)
    button_b = models.CharField(max_length=150)

    def __str__(self):
        return self.discription
    

class Contact(models.Model):
    email=models.EmailField(max_length=256,blank=True,null=True)
    mobile_no=models.CharField(max_length=10,null=True,blank=True)
    whatsapp_no=models.CharField(max_length=10,null=True,blank=True)
    banner_image = models.ImageField(upload_to='contact',blank=True,null=True)
    def __str__(self):
        return self.email if self.email else "Contact"


class Footerform(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Reachus(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class indexform(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Banner(models.Model):
    image = models.ImageField(upload_to='banner')


class Service(models.Model):
    pageheader_image = models.ImageField(upload_to='services-homebanner')
    slug = models.SlugField(unique=True, max_length=155)
    title = models.CharField(max_length=100)
    smalldiscription =models.TextField()
    content = HTMLField()

    def __str__(self):
        return self.title
    

class Address(models.Model):
    left_discription = HTMLField()
    right_discription = HTMLField()
    email = models.CharField(max_length=150)
    phone = models.IntegerField()
    location_url = models.URLField(max_length=1000, blank=True, null=True)
    button = models.CharField(max_length=150)

    def __str__(self):
        return self.button


class Team(models.Model):
    CATEGORY_CHOICES = [
        ('core', 'Core'),
        ('technical', 'Technical'),
    ]

    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
       # default=CORE,
    )
    image = models.ImageField(upload_to='team')
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
   
    def __str__(self):
        return self.name
    

class SiteDocument(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    content = HTMLField()


class Management(models.Model):
    image = models.ImageField(upload_to='management')
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    facebook_link = models.CharField(max_length=530)
    twitter_link = models.CharField(max_length=530)
    linkedIn_link = models.CharField(max_length=530)
    google_link = models.CharField(max_length=530)

    def __str__(self):
        return self.name


class Footer(models.Model):
    title = models.CharField(max_length=75)
    discription = HTMLField(null=True, blank=True)
    service1 = models.CharField(max_length=155)
    service2 = models.CharField(max_length=155)
    service3 = models.CharField(max_length=155)
    service4 = models.CharField(max_length=155)
    contact = models.CharField(max_length=55)
    button = models.CharField(max_length=150)
    facebook_link = models.TextField()
    twitter_link = models.TextField()
    linkedIn_link = models.TextField()
    instagram_link = models.TextField()

    def __str__(self):
        return self.title

class HappyUser(models.Model):
    logo_title = models.CharField(max_length=256)
    logo = models.ImageField(upload_to="happyUser")

    def __str__(self):
        return self.logo_title

class OurService(models.Model):
    service_page = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='our_service_page')
    

class SEO(models.Model):
    page = models.CharField(max_length=150, unique=True)
    seo_title = models.CharField(max_length=60)
    seo_description = models.CharField(max_length=160)
    seo_keywords = models.TextField()

    def __str__(self):
        return self.page


class ForgetPasswordRequest(models.Model):
    name = models.CharField(max_length=150)
    email_or_mobile = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
            
    def __str__(self):
        return self.name
    

class ThreadManager(models.Manager): 
    def by_user(self, user):
        lookup = Q(first_person=user) | Q(second_person=user)
        return self.get_queryset().filter(lookup).distinct()
    
    def unseen_messages_count(self, user, thread):
        other_user = thread.first_person if thread.first_person == user else thread.second_person
        try:
            return thread.chatmessage_thread.filter(is_seen=False, user__in=[thread.first_person, thread.second_person]).exclude(user=other_user).count()
        except Exception as e:
            print(f"Error counting unseen messages for thread {thread.id}: {e}")
            return 0 

    def total_unseen_messages(self, user):
        if user.is_authenticated: 
            threads = self.by_user(user=user)
            total_unseen = 0

            for thread in threads:
                total_unseen += self.unseen_messages_count(user, thread)

            return total_unseen
        else:
            return 0 


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_admin': True}, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_admin': True}, null=True, blank=True, related_name='thread_second_person')
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.DateField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['first_person', 'second_person'], 
                name='unique_thread'
            ),
            models.UniqueConstraint(
                fields=['second_person', 'first_person'], 
                name='unique_thread_reversed'
            )
        ]

    def save(self, *args, **kwargs):
        if self.first_person and self.second_person and self.first_person.id > self.second_person.id:
            self.first_person, self.second_person = self.second_person, self.first_person
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Thread: {self.first_person.first_name if self.first_person else 'Unknown'} - {self.second_person.first_name if self.second_person else 'Unknown'}"
    


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}"
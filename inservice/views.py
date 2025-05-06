from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.views.generic import TemplateView, DetailView, CreateView, View, UpdateView
from itertools import zip_longest
from . import models
from django.contrib import messages
from .forms import ContactUsForm, HomepageForm, CustomLoginForm, CustomPasswordChangeForm, ForgetPasswordForm
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, PasswordChangeView
from client.forms import AdminProfileForm, ClientProfileForm
from inservice.mixins import UserLoginRequiredMixin
from django.urls import reverse
from django.shortcuts import render
from django.http import JsonResponse
from .forms import ContactUsForm
from django.http import JsonResponse
from .models import Reachus

User = get_user_model()


class FooterformCreateView(CreateView):
    queryset = models.Footerform.objects.all()
    fields = '__all__'

    def form_valid(self, form):
        form.save()
        return JsonResponse({"status": "OK"})

    def form_invalid(self, form):
        error_context = {}
        for field, errors in form.errors.items():
            error_context[field] = errors
        error_json = json.dumps(error_context)
        return JsonResponse({"errors": error_json}, status=400)

def reachus_view(request):
    if request.method == "POST":
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            subject = 'fincrmfin Form Submission'
            context = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'message': form.cleaned_data['message'],
            }
            message=form.cleaned_data['message']
            html_content = render_to_string('inservice/email.html', context)
            recipient_list = ['info@fincrmfin.com']
            from_email = 'info@fincrmfin.com'

            # Send the email
            email = EmailMultiAlternatives(subject, message, from_email, recipient_list)
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return JsonResponse({"message": "Thank you for reaching out!"}, status=200)
        else:
            return JsonResponse({"error": "Invalid data submitted"}, status=400)
    
    form = ContactUsForm()
    return render(request, "contact.html", {"form": form})


def subscribe_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        if Reachus.objects.filter(email=email).exists():
            return JsonResponse({"message": "Email already subscribed!"}, status=400)

        Reachus.objects.create(email=email, name="Subscriber", message="Newsletter subscription")
        return JsonResponse({"message": "Subscription successful!"})

    return JsonResponse({"message": "Invalid request"}, status=400)

class HomeFormView(CreateView):
    template_name = "inservice/index.html"
    form_class = HomepageForm
    model = models.indexform

    def form_valid(self, form):
        self.object = form.save()
        subject = 'fincrmfin Form Submission'
        context = {
            'name': self.object.name,
            'email': self.object.email,
            'message': self.object.message,
        }
        html_content = render_to_string('inservice/email.html', context)
        recipient_list = ['info@fincrmfin.com']
        from_email = 'info@fincrmfin.com'

        # Send the email
        email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return JsonResponse({"msg": "OK"}, status=200)

    def form_invalid(self, form):
        error = dict(form.errors.items())
        return JsonResponse({"error": error}, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_banner'] = models.Homebanner.objects.first()
        context['elementor'] = models.Elementor.objects.first()
        context['Aboutgallery'] = models.Aboutgallery.objects.first()
        context['OurSolution'] = models.OurSolution.objects.all()
        left_slide = models.Homebanner.objects.filter()
        right_slide = models.Homebanner.objects.filter()
        context['Homebanner'] = list(zip_longest(left_slide, right_slide))
        context['advertise'] = models.Advertise.objects.all()
        context['service_list'] = models.Service.objects.all()[:3]
        context['happy_users' ] = models.HappyUser.objects.all()
        context['contact' ] = models.Contact.objects.first()
        
        return context
    

def ServiceDetails(request):
    return render(request, "inservice/service-details.html")

class AboutView(TemplateView):
    template_name = "inservice/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['elementor'] = models.Elementor.objects.first()
        context['OurSolution'] = models.OurSolution.objects.all()
        context['workchart'] = models.Workflow.objects.all()
        context['management'] = models.Management.objects.all()
        context['contact'] = models.Contact.objects.first()
        context['Aboutgallery']=models.Aboutgallery.objects.last()
        context['About_history']=models.AboutHistory.objects.all()
        context['service_list'] = models.Service.objects.all()[:3]
        context['technical_team'] = models.Team.objects.filter(category='technical')
        return context


class ContactUsView(CreateView):
    template_name = "inservice/contact.html"
    form_class = ContactUsForm
    model = models.Reachus

    def form_valid(self, form):
        self.object = form.save()
        subject = 'fincrmfin Form Submission'
        context = {
            'name': self.object.name,
            'email': self.object.email,
            'message': self.object.message,
        }
        html_content = render_to_string('inservice/email.html', context)
        recipient_list = [ 'info@fincrmfin.com']
        from_email = 'info@fincrmfin.com'

        # Send the email
        email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return JsonResponse({"msg": "OK"}, status=200)

    def form_invalid(self, form):
        error = dict(form.errors.items())
        return JsonResponse({"error": error}, status=400)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['elementor'] = models.Elementor.objects.first()
        context['contact'] = models.Contact.objects.first()
        context['service_list'] = models.Service.objects.all()

        return context

class ServiceDetailView(DetailView):
    template_name = "inservice/ServiceDetails.html"
    model = models.Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['elementor'] = models.Elementor.objects.first()
        context['contact'] = models.Contact.objects.first()
        context['services'] = models.Service.objects.first()
        context['service_list'] = models.Service.objects.all()
        slug=self.kwargs.get('slug')
        context['service_page'] = models.Service.objects.get(slug=slug)
        return context


class TeamView(TemplateView):
    template_name = "inservice/team.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['elementor'] = models.Elementor.objects.first()
        context['core_team'] = models.Team.objects.filter(category='core')
        context['technical_team'] = models.Team.objects.filter(category='technical')
        context['service_list'] = models.Service.objects.all()

        return context


class ServiceView(TemplateView):
    template_name = "inservice/services.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['elementor'] = models.Elementor.objects.first()
        context['services'] = models.Service.objects.all()
        context['service_list'] = models.Service.objects.all()
        context['happy_users'] = models.HappyUser.objects.all()
        return context
    

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'signin.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if user.is_superuser:
            return redirect('s_dashboard')
        elif user.is_admin:
            return redirect('dashboard', user_id=0, user_type='all', status_type='all_request')
        else:
            return redirect('client_dashboard')


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        request.session.clear()
        logout(request)
        return redirect('login')


class AdminPanel(LoginRequiredMixin, TemplateView):
    template_name = 'adminpanel.html'
    
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context['custom_user'] = User.objects.exclude(id=self.request.user.id) \
                                             .filter(is_superuser=False, is_client=True)                       
        return context
    

class ProfileView(UserLoginRequiredMixin, UpdateView):
    template_name = 'profile.html'
    model = User
    success_url = reverse_lazy('profile')

    def get_form_class(self):
        if self.request.user.is_admin:
            return AdminProfileForm
        return ClientProfileForm
    
    def get_success_url(self):
        return reverse('profile', kwargs={'profile_type': 'overview'})
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been successfully updated!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_type'] = self.kwargs.get('profile_type')
        return context
    

class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'profile.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('login') 

    def form_valid(self, form):
        self.request.user = form.save()
        messages.success(self.request, 'Password changed successfully done')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_type'] = self.kwargs.get('profile_type')
        return context
    

class ForgetPasswordView(CreateView):
    form_class = ForgetPasswordForm
    template_name = 'forget_password.html'
    success_url = reverse_lazy('forget_password')

    def form_valid(self, form, *args, **kwargs):
        messages.success(self.request, 'Your Request has been successfully submited!')
        return super().form_valid(form)
    
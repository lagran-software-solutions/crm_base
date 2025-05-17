from django.views.generic import TemplateView, ListView, UpdateView, CreateView, View, DetailView, DeleteView
from inservice.mixins import AdminLoginRequiredMixin, AdminClientLoginRequiredMixin, AdminSuperAdminLoginRequiredMixin, SuperAdminLoginRequiredMixin, UserLoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from client.models import RequestService, ServiceRequestFolder, InvoiceRecord, InvoiceRecordItem, Notification, RequestServiceChat, Complaint, Service, SubService, RequestStatus, Invoice, InvoiceItem
from django.urls import reverse_lazy, reverse
from .forms import RequestServiceForm, ClientSignupForm, InvoiceRecordForm, InvoiceForm, UpdateClientForm, AdminSignupForm, ComplaintFilterForm, DashboardFilterForm, UpdateAdminForm, FilterModelForm, ServiceForm, SubServiceForm, AdminClientSearchForm
from client.forms import ServiceRequestFolderForm
from inservice.models import User
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.views.generic.edit import FormMixin 
from inservice.models import Thread, ChatMessage
from django.utils.timezone import localtime
import json
from django.contrib import messages
from django.db.models.functions import Concat
from django.db.models import Q, F, Value, Sum
from django.http import HttpResponseRedirect


class RequestServiceListView(AdminSuperAdminLoginRequiredMixin, FormMixin, ListView):
    model = RequestService
    form_class = FilterModelForm
    paginate_by = 30

    def get_template_names(self):
        if self.kwargs.get('status_type') == 'piechart_dashboard':
            return ["super_admin/piechart_dashboard.html"]
        return ["admin/all_request.html"]

    def get_queryset(self):
        queryset = RequestService.objects.select_related('user', 'assigned_to_employee').prefetch_related('services', 'sub_services').all()
        user_id = self.kwargs.get('user_id', 0)
        status_type = self.kwargs.get('status_type', 'all_request')
        user_type = self.kwargs.get('user_type', 'all')

        if user_type == 'client':
            if status_type in ['all_request', 'piechart_dashboard']:
                queryset = queryset.filter(user__isnull=False)
            elif status_type in ['in_progress', 'completed', 'empty', 'cancelled']:
                queryset = queryset.filter(status=status_type, user__isnull=False)
            elif status_type == 'my_works':
                queryset = queryset.filter(assigned_to_employee=self.request.user)
        elif user_type == 'admin':
            if status_type in ['all_request', 'piechart_dashboard']:
                queryset = queryset.filter(assigned_to_employee=user_id)
            else:
                queryset = queryset.filter(assigned_to_employee=user_id, status=status_type)
        elif user_type == 'all':
            if user_id != 0 and status_type != 'my_works':
                queryset = queryset.filter(user=user_id)
            elif status_type in ['in_progress', 'completed', 'empty', 'cancelled']:
                queryset = queryset.filter(status=status_type)
            elif status_type == 'my_works':
                queryset = queryset.filter(assigned_to_employee=self.request.user)
        return queryset

    def filter_queryset(self, queryset, search_term='', start_date=None, end_date=None):
        if search_term:
            queryset = queryset.annotate(
                employee_full_name=Concat(F('assigned_to_employee__first_name'), Value(' '), F('assigned_to_employee__last_name')),
                user_full_name=Concat(F('user__first_name'), Value(' '), F('user__last_name'))
            ).filter(
                Q(request_number__iexact=search_term) |
                Q(services__name__icontains=search_term) |
                Q(sub_services__name__icontains=search_term) |
                Q(employee_full_name__icontains=search_term) |
                Q(user_full_name__icontains=search_term)
            ).distinct()

        if start_date and end_date:
            queryset = queryset.filter(request_date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(request_date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(request_date__lte=end_date)

        return queryset

    def post(self, request, *args, **kwargs):
        filter_form = self.get_form()
        queryset = self.get_queryset()

        if filter_form.is_valid():
            filters = filter_form.filters
            search_term = filters.get('search_term', '')
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')

            queryset = self.filter_queryset(queryset, search_term, start_date, end_date)

            self.object_list = queryset
            context = self.get_context_data(filter_form=filter_form, search_term=search_term, start_date=start_date, end_date=end_date)
            return self.render_to_response(context)

        context = self.get_context_data(filter_form=filter_form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'object_list'):
            queryset = self.object_list
        else:
            queryset = self.get_queryset()

        status_type = self.kwargs.get('status_type', 'all_request')
        user_id = self.kwargs.get('user_id', 0)
        user_type = self.kwargs.get('user_type', 'all')

        context.update({
            'status_type': status_type,
            'user_id': user_id,
            'user_type': user_type,
            'all_request_count': queryset.count(),
            'in_progress_count': queryset.filter(status='in_progress').count(),
            'completed_count': queryset.filter(status='completed').count(),
            'empty_count': queryset.filter(status='empty').count(),
            'cancelled_count': queryset.filter(status='cancelled').count(),
        })
        
        return context


class PiechartDashboard(AdminSuperAdminLoginRequiredMixin, FormMixin, ListView):
    template_name = "super_admin/piechart_dashboard.html"
    model = RequestService
    form_class = FilterModelForm
    paginate_by = 30


class ServiceRequestListView(AdminSuperAdminLoginRequiredMixin, ListView):
    template_name = "admin/all_request.html"
    model = RequestService
    paginate_by = 30
    
    def get_queryset(self):
        queryset = super().get_queryset()

        request_type = self.kwargs.get('request_type')
        if request_type == 'my_request':
            return queryset.filter(assigned_to_employee=self.request.user)
        elif request_type == 'completed_request':
            return queryset.filter(assigned_to_employee=self.request.user, status='completed')
        elif request_type == 'my_works':
            return queryset.filter(assigned_to_employee=self.request.user, created_by_admin=True)

        return queryset 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_type'] = self.kwargs.get('status_type', 'all_request')
        context['user_id'] = self.kwargs.get('user_id', 0)
        context['user_type'] = self.kwargs.get('user_type', 'all')
        return context


class RequestDetailUpdateView(AdminSuperAdminLoginRequiredMixin, UpdateView):
    template_name = "admin/requestdetails.html"
    form_class = RequestServiceForm
    success_url = reverse_lazy('dashboard') 

    def get_success_url(self):
        return reverse('dashboard', kwargs={'user_id': 0, 'user_type': 'all', 'status_type': 'all_request'})
    
    def get_object(self, queryset=None):
        request_number = self.kwargs.get("request_number")
        return get_object_or_404(RequestService, request_number=request_number)

    def form_valid(self, form):
        service = form.save(commit=False)
        service.save() 

        from django.db.models.signals import post_save

        post_save.send(
            sender=RequestService,
            instance=service,
            created=False,
            user=self.request.user 
        )

        request_number = self.kwargs.get("request_number")
        request_detail_url = reverse('request-detail', kwargs={'request_number': self.kwargs.get('request_number')})
        Notification.objects.create(
            client=service.user,
            message=f"Some actions have been performed on this request-number({request_number})",
            url=request_detail_url,
            recipient_type='client'
        )

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = get_object_or_404(RequestService, request_number=self.kwargs.get("request_number"))
        messages = RequestServiceChat.objects.filter(service=service)
        grouped_message = {}

        for message in messages:
            message_date = message.created_at.date()
            if message_date not in grouped_message:
                grouped_message[message_date] = []
            
            grouped_message[message_date].append(message)
        context['discussion_messages'] = grouped_message
        context['status'] = RequestStatus.objects.filter(request_number=service)
        return context
    

class ClientListView(AdminLoginRequiredMixin, ListView):
    template_name = "admin/client_list.html"

    def get_queryset(self):
        queryset = RequestService.objects.filter(assigned_to_employee=self.request.user, created_by_admin=False)\
            .order_by('id').distinct('user')
        return queryset
    

class ClientRequestServicesListView(AdminSuperAdminLoginRequiredMixin, ListView):
    template_name = 'admin/client_service_request.html'
    paginate_by = 30

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        queryset = RequestService.objects.filter(user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.kwargs.get('pk')
        return context


class FolderListView(UserLoginRequiredMixin, ListView):
    template_name = "client/folders.html"

    def get_queryset(self, *args, **kwargs):
        response = ServiceRequestFolder.objects.filter(client=self.kwargs.get('pk'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_id'] = self.kwargs.get('pk')
        return context
    

class FolderCreateView(UserLoginRequiredMixin, TemplateView):
    template_name = "client/service_request_folders.html"

    def get_service_by_request_number(self, request_number):
        try:
            return RequestService.objects.get(request_number=request_number)
        except RequestService.DoesNotExist:
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request_number'] = self.kwargs.get("request_number")
        service = self.get_service_by_request_number(context['request_number'])
        try:
            context['folders'] = ServiceRequestFolder.objects.filter(service=service)
        except ServiceRequestFolder.DoesNotExist:
            context['folders'] = None
        context['form'] = ServiceRequestFolderForm()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'create':
            return self.create_folder(request)
        elif action == 'delete':
            return self.delete_folder(request)
        elif action == 'update':
            return self.update_folder(request)
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)

    def create_folder(self, request):
        form = ServiceRequestFolderForm(request.POST)
        if form.is_valid():
            request_number = self.kwargs.get("request_number")
            client = RequestService.objects.get(request_number=request_number).user
            service = self.get_service_by_request_number(request_number)
            if service:
                form.instance.service = service
                form.instance.admin = request.user
                form.instance.client = client
                form.save()
                data = {
                    'message': 'Folder has been created successfully',
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'error': 'Invalid request number or service does not exist'}, status=400)
        
        else:
            errors = {field: errors for field, errors in form.errors.items()}
            return JsonResponse({"errors": errors}, status=400)

    def delete_folder(self, request):
        folder_id = request.POST.get('folder_id')
        if not folder_id:
            return HttpResponseBadRequest("No folder ID provided.")
        
        folder = get_object_or_404(ServiceRequestFolder, id=folder_id)
        folder.delete()
        
        return JsonResponse({'message': 'Folder has been deleted successfully'})
    
    def update_folder(self, request):
        if request.method == 'POST':
            folder_id = request.POST.get('folder_id')
            if not folder_id:
                return HttpResponseBadRequest("No folder ID provided")

            form = ServiceRequestFolderForm(request.POST)
            if form.is_valid():
                folder = get_object_or_404(ServiceRequestFolder, id=folder_id)
                folder.name = form.cleaned_data['name']
                folder.save()
                return JsonResponse({'message': 'Folder updated successfully', 'responseCode': 200})
            else:
                return JsonResponse({'message': 'Invalid form data', 'responseCode': 400})


class ComplaintsListView(AdminSuperAdminLoginRequiredMixin, FormMixin, ListView):
    template_name = 'admin/complaint_list.html'
    model = Complaint
    paginate_by = 30
    form_class = ComplaintFilterForm

    def get_queryset(self):
        return Complaint.objects.all()

    def post(self, request, *args, **kwargs):
        filter_form = self.get_form(self.form_class)
        queryset = self.get_queryset() 

        if filter_form.is_valid():
            from_date = filter_form.cleaned_data.get('complaint_from_date')
            to_date = filter_form.cleaned_data.get('complaint_to_date')
            client_name = filter_form.cleaned_data.get('client_name')
            print("Client name (POST):", client_name)

            if from_date and to_date:
                queryset = queryset.filter(created_at__range=[from_date, to_date])
            elif from_date:
                queryset = queryset.filter(created_at__gte=from_date)
            elif to_date:
                queryset = queryset.filter(created_at__lte=to_date)

            if client_name:
                queryset = queryset.filter(user__first_name__icontains=client_name)

            self.object_list = queryset
        else:
            print("Form errors (POST):", filter_form.errors)

        context = self.get_context_data(filter_form=filter_form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.get_form(self.form_class)
        return context


class ChatView(AdminSuperAdminLoginRequiredMixin, TemplateView):
    template_name = 'admin/chat.html'

    def get_context_data(self, **kwargs):   
        context = super().get_context_data(**kwargs)
        threads = Thread.objects.by_user(user=self.request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
        chats = {}
        for thread in threads:
           
            if thread.first_person == self.request.user:
                
                user_name = thread.second_person.get_full_name()
                user_mobile = thread.second_person.mobile               
            else:                
                user_name = thread.first_person.get_full_name()
                user_mobile = thread.first_person.mobile                        
            chats_key = f"{user_name}-{user_mobile}"
            chats[chats_key] = [
                {
                    'text': chat.message,
                    'time': localtime(chat.timestamp).strftime("%I:%M %p"), 
                    'type': 'sent' if chat.user == self.request.user else 'received'
                }
                for chat in thread.chatmessage_thread.all()
            ]

            unseen_count = Thread.objects.unseen_messages_count(self.request.user, thread)
            thread.unseencount = unseen_count
            
        context['chats'] = json.dumps(chats)
        context['threads'] = threads 
        return context
    

def mark_messages_as_seen(request, thread_id):
    if request.method == "POST":
        user = request.user
        try:
            thread = Thread.objects.get(id=thread_id)
            other_user = thread.first_person if thread.first_person != user else thread.second_person
            ChatMessage.objects.filter(thread=thread, is_seen=False, user=other_user).update(is_seen=True)
            
            return JsonResponse({"success": True})
        except Thread.DoesNotExist:
            return JsonResponse({"success": False, "error": "Thread does not exist"})
    return JsonResponse({"success": False, "error": "Invalid request method"})


class SuperAdminClientEmployeeList(SuperAdminLoginRequiredMixin, ListView): 
    model = User
    paginate_by = 30

    def get_queryset(self):
        user_type = self.kwargs.get('user_type')
        queryset = User.objects.exclude(id=self.request.user.id)
        
        if user_type == 'client_list':
            queryset = queryset.filter(is_admin=False, is_superuser=False).order_by('-id')
        elif user_type == 'employee_list':
            queryset = queryset.filter(is_admin=True, is_superuser=False).order_by('-id')
        else:
            queryset = User.objects.none()

        form = self.get_search_form()
        if form.is_valid():
            search_query = form.cleaned_data.get('q')
            if search_query:
                queryset = queryset.filter(
                    Q(username__icontains=search_query) |
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query) |
                    Q(name__icontains=search_query)
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_type = self.kwargs.get('user_type')
        context['user_type'] = user_type
        context['admin_user_search_form'] = self.get_search_form() 
        return context

    def get_template_names(self):
        user_type = self.kwargs.get('user_type')
        if user_type == 'client_list':
            template_name = 'super_admin/client_list.html'
        elif user_type == 'employee_list':
            template_name = 'super_admin/admin_list.html'
        else:
            raise Http404("Invalid user type specified.")
        return template_name

    def post(self, request, *args, **kwargs):
        search_query = request.POST.get('q', '')
        url = f"{reverse('user_employee_list', kwargs={'user_type': self.kwargs.get('user_type')})}?q={search_query}"
        return HttpResponseRedirect(url)

    def get_search_form(self):
        return AdminClientSearchForm(self.request.GET or None)


class ClientSignupView(SuperAdminLoginRequiredMixin, CreateView):
    model = User
    form_class = ClientSignupForm
    success_url = reverse_lazy('user_employee_list', kwargs={'user_type': 'client_list'})
    template_name = 'super_admin/client_form.html'

    def form_valid(self, form):
        messages.success(self.request, "Account created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error in your signup form. Please correct the errors below.")
        return super().form_invalid(form)
    

class ClientUpdateView(SuperAdminLoginRequiredMixin, UpdateView):
    model = User
    form_class = UpdateClientForm
    template_name = 'super_admin/client_form.html'
    success_url = reverse_lazy('user_employee_list', kwargs={'user_type': 'client_list'})

    def form_valid(self, form):
        messages.success(self.request, "Account updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error in the form. Please correct the errors below.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), 'is_update': True}


class AdminSignupView(SuperAdminLoginRequiredMixin, CreateView):
    model = User
    form_class = AdminSignupForm
    success_url = reverse_lazy('user_employee_list', kwargs={'user_type': 'employee_list'})
    template_name = 'super_admin/admin_form.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_admin = True 
        user.save()
        messages.success(self.request, "Account created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error in your signup form. Please correct the errors below.")
        return super().form_invalid(form)
    

class AdminUpdateView(SuperAdminLoginRequiredMixin, UpdateView):
    model = User
    form_class = UpdateAdminForm
    template_name = 'super_admin/admin_form.html'
    success_url = reverse_lazy('user_employee_list', kwargs={'user_type': 'employee_list'})

    def form_valid(self, form):
        messages.success(self.request, "Account updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error in the form. Please correct the errors below.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), 'is_update': True}    


class UserDeleteView(SuperAdminLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user_type = kwargs.get('user_type')
        if user_type == 'client_list':
            success_url = reverse_lazy('user_employee_list', kwargs={'user_type': 'client_list'})
        elif user_type == 'employee_list':
            success_url = reverse_lazy('user_employee_list', kwargs={'user_type': 'employee_list'})
        else:
            success_url = reverse_lazy('user_employee_list', kwargs={'user_type': 'client_list'})
        
        try:
            user = User.objects.get(id=user_id)
            if user_type == 'employee_list':
                request_services = RequestService.objects.filter(assigned_to_employee=user, created_by_admin=True)
                request_services.delete()
            
            user.delete()
            messages.success(request, "User deleted successfully.")
        
        except User.DoesNotExist:
            messages.error(request, "User not found.")
        
        return redirect(success_url)


class ClearSessionView(View):
    def get(self, request, role=None, *args, **kwargs):
        if role == 'admin':
            request.session.pop('admin_start_date', None)
            request.session.pop('admin_end_date', None)
        elif role == 'client':
            request.session.pop('client_start_date', None)
            request.session.pop('client_end_date', None)
        
        return redirect('s_dashboard') 


class DashboardView(SuperAdminLoginRequiredMixin, FormMixin, ListView):
    template_name = 'super_admin/dashboard.html'
    model = RequestService
    form_class = DashboardFilterForm
    paginate_by = 10

    def get_queryset(self):
        return RequestService.objects.select_related('user', 'assigned_to_employee').prefetch_related('services', 'sub_services').all()

    def post(self, request, *args, **kwargs):
        filter_form = self.get_form(form_class=self.form_class)
        if filter_form.is_valid():
            filters = filter_form.cleaned_data
            admin_start_date = filters.get('admin_start_date')
            admin_end_date = filters.get('admin_end_date')
            client_start_date = filters.get('client_start_date')
            client_end_date = filters.get('client_end_date')

            queryset = self.get_queryset()
            admin_queryset = queryset  
            client_queryset = queryset 

            if admin_start_date and admin_end_date:
                admin_queryset = admin_queryset.filter(
                    request_date__range=[admin_start_date, admin_end_date]
                ).distinct()

            if client_start_date and client_end_date:
                client_queryset = client_queryset.filter(
                    request_date__range=[client_start_date, client_end_date],
                    user__is_admin=False 
                ).distinct()

            self.object_list = queryset 
            context = self.get_context_data(
                filter_form=filter_form,
                admin_queryset=admin_queryset,
                client_queryset=client_queryset
            )
            return self.render_to_response(context)
        else:
            context = self.get_context_data(filter_form=filter_form)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        admin_queryset = kwargs.get('admin_queryset', self.get_queryset())
        client_queryset = kwargs.get('client_queryset', self.get_queryset())

        context['client_status'] = self.get_client_status(client_queryset)
        context['admin_status'] = self.get_admin_status(admin_queryset)
        
        context['invoice_summary'] = {
            'paid': {
                'total': InvoiceRecord.objects.total_paid_amount(),
                'sub_total': InvoiceRecord.objects.sub_paid_amount(),
                'count': InvoiceRecord.objects.count_by_status('paid'),
            },
            'cancelled': {
                'total': InvoiceRecord.objects.total_cancelled_amount(),
                'sub_total': InvoiceRecord.objects.sub_cancelled_amount(),
                'count': InvoiceRecord.objects.count_by_status('cancelled'),
            },
            'pending': {
                'total': InvoiceRecord.objects.total_pending_amount(),
                'sub_total': InvoiceRecord.objects.sub_pending_amount(),
                'count': InvoiceRecord.objects.count_by_status('pending'),
            },
            'empty': {
                'total': InvoiceRecord.objects.total_empty_amount(),
                'sub_total': InvoiceRecord.objects.sub_empty_amount(),
                'count': InvoiceRecord.objects.count_by_status('empty'),
            },
            'overall': {
                'total': InvoiceRecord.objects.total_amount(),
                'sub_total': InvoiceRecord.objects.sub_amount(),
            },
        }

        return context

    def get_client_status(self, client_queryset):
        return {
            'in_progress': client_queryset.filter(status='in_progress', user__isnull=False).count() or 0,
            'completed': client_queryset.filter(status='completed', user__isnull=False).count() or 0,
            'empty': client_queryset.filter(status='empty', user__isnull=False).count() or 0,
            'cancelled': client_queryset.filter(status='cancelled', user__isnull=False).count() or 0,
        }

    def get_admin_status(self, admin_queryset):
        return {
            'in_progress': admin_queryset.filter(status='in_progress').count() or 0,
            'completed': admin_queryset.filter(status='completed').count() or 0,
            'empty': admin_queryset.filter(status='empty').count() or 0,
            'cancelled': admin_queryset.filter(status='cancelled').count() or 0,
        }


class ManageServiceSubServiceView(SuperAdminLoginRequiredMixin, TemplateView):
    template_name = 'super_admin/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = Service.objects.all()
        context["subservices"] = SubService.objects.all()
        context["service_form"] = ServiceForm()
        context["subservice_form"] = SubServiceForm()
        return context

    def post(self, request, *args, **kwargs):
        if "service_form" in request.POST:
            service_id = request.POST.get("servicemain_id") 
            if service_id:
                service = get_object_or_404(Service, id=service_id)
                form = ServiceForm(request.POST, instance=service)
            else:
                form = ServiceForm(request.POST)

            if form.is_valid():
                form.save()
                return redirect("manage_services_subservices")

            return self.render_to_response(self.get_context_data(service_form=form))

        elif "subservice_form" in request.POST:
            subservice_id = request.POST.get("subservice_id")
            service_id = request.POST.get("service_id")

            service = get_object_or_404(Service, id=service_id)

            if subservice_id: 
                subservice = get_object_or_404(SubService, id=subservice_id)
                form = SubServiceForm(request.POST, instance=subservice)
            else: 
                form = SubServiceForm(request.POST)

            if form.is_valid():
                subservice = form.save(commit=False)
                subservice.service = service
                subservice.save()
                return redirect("manage_services_subservices")
            else:
                context = self.get_context_data()
                context['subservice_form'] = form
                return self.render_to_response(context)

        elif "delete_service_id" in request.POST:
            service_id = request.POST.get("delete_service_id")
            service = get_object_or_404(Service, id=service_id)
            service.delete()
            return redirect("manage_services_subservices")

        elif "delete_subservice_id" in request.POST:
            subservice_id = request.POST.get("delete_subservice_id")
            subservice = get_object_or_404(SubService, id=subservice_id)
            subservice.delete()
            return redirect("manage_services_subservices")

        return self.render_to_response(self.get_context_data(error_message="Invalid form submission."))


class InvoiceRecordCreateView(SuperAdminLoginRequiredMixin, CreateView): 
    model = InvoiceRecord
    form_class = InvoiceRecordForm
    template_name = 'super_admin/invoicerecord_form.html'

    def get_initial(self):
        initial = super().get_initial()

        last_record = InvoiceRecord.objects.last()
        if last_record:

            initial.update({
                'company_name': last_record.company_name,
                'company_address': last_record.company_address,
                'company_contact': last_record.company_contact,
                'range_address': last_record.range_address,
                'division': last_record.division,
                'commissioner': last_record.commissioner,
                'gstn': last_record.gstn,
                'state': last_record.state,
                'state_code': last_record.state_code,
                'cgst': last_record.cgst,
                'sgst': last_record.sgst,
                'igst': last_record.igst,
                'pan': last_record.pan,
                'bank_account': last_record.bank_account,
                'ifsc': last_record.ifsc,
                'branch': last_record.branch,
                'tds_rate': last_record.tds_rate,
                'payment': last_record.payment,
                'gpay_phone': last_record.gpay_phone,
                'logo': last_record.logo,
                'qr_code': last_record.logo,
            })

        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        
        try:
            items = json.loads(self.request.POST.get('items', '[]'))
            for item in items:
                InvoiceRecordItem.objects.create(
                    invoice=self.object,
                    description=item.get('description', ''),
                    sac=item.get('sac', ''),
                    amount=item.get('amount', 0),
                )
            messages.success(self.request, "Invoice has been successfully created.")
        except json.JSONDecodeError:
            messages.error(self.request, "There was an error processing the item data. Please check the format.")
            return JsonResponse({'error': 'Invalid item data format'}, status=400)

        return response
    
    def get_success_url(self):
        return reverse('invoice_preview', kwargs={'pk': self.object.pk})


class InvoiceRecordUpdateView(SuperAdminLoginRequiredMixin, UpdateView):
    model = InvoiceRecord
    form_class = InvoiceRecordForm
    template_name = 'super_admin/invoicerecord_form.html'

    def serialize_items(self, items):
        return [
            {
                'id': item.id,
                'invoice_id': item.invoice_id,
                'description': item.description,
                'sac': item.sac,
                'amount': float(item.amount), 
            }
            for item in items
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.object.items.all()  
        context['items'] = [{'description': item.description, 'amount': item.amount} for item in items]
        context['invoice'] = get_object_or_404(InvoiceRecord, pk=self.kwargs.get('pk'))

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            items = json.loads(self.request.POST.get('items', '[]'))
            InvoiceRecordItem.objects.filter(invoice=self.object).delete()
            for item in items:
                InvoiceRecordItem.objects.create(
                    invoice=self.object,
                    description=item.get('description', ''),
                    sac=item.get('sac', ''),
                    amount=item.get('amount', 0),
                )
            messages.success(self.request, "Invoice have been successfully updated.")
        except json.JSONDecodeError:
            messages.error(self.request, "There was an error processing the item data. Please check the format.")
            return JsonResponse({'error': 'Invalid item data format'}, status=400)
        return response

    def get_success_url(self):
        return reverse('invoice_list', kwargs={'status': 'all'})
    

class InvoiceRecordListView(SuperAdminLoginRequiredMixin, ListView):
    model = InvoiceRecord
    template_name = 'super_admin/invoicerecord_list.html'

    def get_queryset(self):
        status = self.kwargs.get('status') 
        base_queryset = super().get_queryset()  
        
        if status and status != 'all':
            base_queryset = base_queryset.filter(status=status)

        return base_queryset.annotate(
            total_amount=Sum('items__amount'),
            total_discount=Sum('items__gst')
        )

    def post(self, request, *args, **kwargs):
        if 'selected_ids[]' in request.POST:
            selected_ids = request.POST.getlist('selected_ids[]')
            if selected_ids:
                try:
                    self.model.objects.filter(id__in=selected_ids).delete()
                    messages.success(request, "Selected invoices have been successfully deleted.")
                except Exception as e:
                    messages.error(request, f"Error deleting invoices: {e}")
            else:
                messages.error(request, "No invoices selected for deletion.")

        elif 'invoice_id' in request.POST and 'status' in request.POST:
            invoice_id = request.POST.get('invoice_id')
            new_status = request.POST.get('status')
            try:
                invoice = self.model.objects.get(id=invoice_id)
                if new_status:
                    invoice.status = new_status
                    invoice.save()
                    messages.success(request, "Invoice status updated successfully.")
                else:
                    messages.error(request, "Invalid status selected.")
            except self.model.DoesNotExist:
                messages.error(request, "Invoice not found.")
            except Exception as e:
                messages.error(request, f"Error updating invoice status: {e}")

        return redirect(reverse('invoice_list', kwargs={'status': 'all'}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.kwargs.get('status', 'all')
        return context


class InvoiceRecordListView(SuperAdminLoginRequiredMixin, ListView):
    model = InvoiceRecord
    template_name = 'super_admin/invoicerecord_list.html'

    def get_queryset(self):
        status = self.kwargs.get('status') 
        base_queryset = super().get_queryset()  
        
        if status and status != 'all':
            base_queryset = base_queryset.filter(status=status)

        return base_queryset.annotate(
            total_amount=Sum('items__amount')
        )

    def post(self, request, *args, **kwargs):
        if 'selected_ids[]' in request.POST:
            selected_ids = request.POST.getlist('selected_ids[]')
            if selected_ids:
                try:
                    self.model.objects.filter(id__in=selected_ids).delete()
                    messages.success(request, "Selected invoices have been successfully deleted.")
                except Exception as e:
                    messages.error(request, f"Error deleting invoices: {e}")
            else:
                messages.error(request, "No invoices selected for deletion.")

        elif 'invoice_id' in request.POST and 'status' in request.POST:
            invoice_id = request.POST.get('invoice_id')
            new_status = request.POST.get('status')
            try:
                invoice = self.model.objects.get(id=invoice_id)
                if new_status:
                    invoice.status = new_status
                    invoice.save()
                    messages.success(request, "Invoice status updated successfully.")
                else:
                    messages.error(request, "Invalid status selected.")
            except self.model.DoesNotExist:
                messages.error(request, "Invoice not found.")
            except Exception as e:
                messages.error(request, f"Error updating invoice status: {e}")

        return redirect(reverse('invoice_list', kwargs={'status': 'all'}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.kwargs.get('status', 'all')
        return context


class InvoiceRecordPreview(SuperAdminLoginRequiredMixin, DetailView):
    template_name = 'super_admin/invoice_preview.html'
    model = InvoiceRecord

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.object.items.all()
        context['items'] = items
        return context

from django.db.models.base import Model as Model
from django.shortcuts import redirect, reverse
from django.views.generic import TemplateView, ListView, View, DetailView, RedirectView, CreateView, UpdateView
from .models import *
from inservice.mixins import ClientLoginRequiredMixin, AdminClientLoginRequiredMixin, UserLoginRequiredMixin
from .forms import *
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from .models import Notification, RequestServiceChat
from admin.notification import file_upload_client_notification, file_upload_admin_notification, create_new_message_notification
from admin.forms import FilterModelForm
from django.db.models import Q
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.utils.functional import cached_property


class ServiceListDashboard(UserLoginRequiredMixin, ListView):
    template_name = "client/dashboard.html"
    form_class = RequestServiceForm

    def get_queryset(self):
        return Service.objects.prefetch_related("sub_service").all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            try:
                print('form valid: ')
                request_service = form.save(commit=False)
                if self.request.user.is_superuser:
                    request_service.created_by_admin = True
                elif self.request.user.is_admin:
                    request_service.assigned_to_employee = request.user
                    request_service.created_by_admin = True
                else:
                    request_service.user = request.user
                request_service.save()

                # Handle many-to-many relationships
                selected_services = request.POST.getlist('services')
                selected_sub_services = request.POST.getlist('sub_services')
                request_service.services.set(Service.objects.filter(id__in=selected_services))
                request_service.sub_services.set(SubService.objects.filter(id__in=selected_sub_services))

                service_request = RequestService.objects.get(request_number=request_service.request_number)
                if self.request.user.is_admin:
                    ServiceRequestFolder.objects.create(
                        name=request_service.request_number,
                        service=service_request,
                        admin=request.user
                    )
                    messages.success(request, "Service request successfully created and folder assigned.")
                    if self.request.user.is_superuser:
                        return redirect('dashboard', user_id=0, user_type='all', status_type='empty')
                    return redirect('client_request_dashboard', request_type='my_works')

                else:
                    ServiceRequestFolder.objects.create(
                        name=request_service.request_number,
                        service=service_request,
                        client=request.user
                    )
                    request_detail_url = reverse('admin-request-detail', kwargs={'request_number': request_service.request_number})
                    Notification.objects.create(
                        client=request.user,  
                        message=f"A new service request ({request_service.request_number}) has been submitted.",
                        url=request_detail_url,  
                        recipient_type='admin'
                    )
                    messages.success(request, "Your service request has been submitted successfully.")
                    return redirect('client_request')

            except Exception as e:
                messages.error(request, "An error occurred while processing your request")
                return redirect('client_dashboard')
        else:
            messages.error(request, "Form submission failed. Please correct the errors and try again.")
            return redirect('client_dashboard')
    

class RequestDetailView(ClientLoginRequiredMixin, DetailView):
    template_name = "client/requestdetails.html"
    model = RequestService

    def get_object(self):
        request_number = self.kwargs.get("request_number")
        return get_object_or_404(RequestService, request_number=request_number, user=self.request.user)

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

        return context
    

class ClientRequestListView(ClientLoginRequiredMixin, FormMixin, ListView):
    template_name = "client/request.html"
    model = RequestService
    form_class = FilterModelForm
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        return queryset

    def post(self, request, *args, **kwargs):
        filter_form = self.get_form(form_class=self.form_class) 
        if filter_form.is_valid():
            filters = filter_form.filters
            search_term = filters.get('search_term', '')
            queryset = self.get_queryset()

            if search_term:
                queryset = queryset.filter(
                    Q(request_number__iexact=search_term) | 
                    Q(services__name__icontains=search_term) |  
                    Q(sub_services__name__icontains=search_term)  |
                    Q(assigned_to_employee__first_name__icontains=search_term)
                ).distinct()

            self.object_list = queryset
            context = self.get_context_data(filter_form=filter_form, search_term=search_term)
            return self.render_to_response(context)
        else:
            context = self.get_context_data(filter_form=filter_form)
            return self.render_to_response(context)


class FolderListView(UserLoginRequiredMixin, ListView):
    template_name = "client/folders.html"

    def get_queryset(self):
        response = ServiceRequestFolder.objects.filter(client=self.request.user)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['client_id'] = self.request.user.id
        return context


class FolderCreateView(UserLoginRequiredMixin, TemplateView):
    template_name = "client/folders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folders'] = ServiceRequestFolder.objects.filter(client=self.request.user)
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
            if request.user.is_admin:
                client = get_object_or_404(User, id=request.POST.get('client_id'))
                form.instance.client = client
                form.instance.admin = request.user
            else:
                form.instance.client = request.user

            form.save()
            data = {
                'message': 'Folder has been created successfully',
            }
            return JsonResponse(data)
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
            

class ServiceFolderCreateView(ClientLoginRequiredMixin, TemplateView):
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

            service = self.get_service_by_request_number(request_number)
            if service:
                form.instance.service = service
                form.instance.client = request.user
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
        
        messages.success(request, 'Folder has been deleted successfully')
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


class ClientDocumentListView(UserLoginRequiredMixin, ListView):
    template_name = "client/client_documents.html"
    model = User

    def get_queryset(self, **kwargs):
        user_id = self.kwargs.get('user_id')
        queryset = super().get_queryset().filter(id=user_id)
        return queryset

    @cached_property
    def documents(self):
        user = self.get_queryset().first()
        if user:
            return [
                {'name': 'Rental Agreement', 'file': user.rental_agreement},
                {'name': 'NOC', 'file': user.noc},
                {'name': 'PAN Document', 'file': user.pan_document},
                {'name': 'TAN Document', 'file': user.tan_document},
                {'name': 'Incorporation Certificate', 'file': user.incorporation_certificate},
                {'name': 'MOM', 'file': user.mom},
                {'name': 'AOA', 'file': user.aoa},
                {'name': 'Other Documents', 'file': user.other_documents},
            ]
        return [] 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = [doc for doc in self.documents if doc['file']]
        return context


class FileUploadView(UserLoginRequiredMixin, TemplateView):
    template_name = "client/uploadmedia.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_id = self.kwargs.get('pk')
        context['form'] = ServiceFileForm()
        context['folder_id'] = folder_id
        context['files'] = ServiceFile.objects.filter(folder_id=folder_id)
        return context

    def post(self, request, *args, **kwargs):
        folder_id = self.kwargs.get('pk')
        folder_slug = self.kwargs.get('slug')
        
        if 'delete_file' in request.POST:
            file_id = request.POST.get('file_id')
            file_to_delete = get_object_or_404(ServiceFile, id=file_id)
            file_to_delete.delete()
            return redirect('file', pk=folder_id, slug=folder_slug)
        
        if 'toggle_private' in request.POST:
            file_id = request.POST.get('file_id')
            file_to_toggle = get_object_or_404(ServiceFile, id=file_id)
            file_to_toggle.is_private = not file_to_toggle.is_private
            file_to_toggle.save()
            return redirect('file', pk=folder_id, slug=folder_slug)
        
        folder = get_object_or_404(ServiceRequestFolder, id=folder_id)
        request_detail_url = reverse('file', kwargs={'pk': folder_id, 'slug': folder_slug})

        # Handle multiple file uploads
        files = request.FILES.getlist('file') 
        for file in files:
            form = ServiceFileForm(request.POST, {'file': file})
            if form.is_valid():
                if request.user.is_admin:
                    file_upload_client_notification(folder, request_detail_url)
                    form.instance.admin = request.user
                else:
                    file_upload_admin_notification(folder, request_detail_url)
                    form.instance.client = request.user
                form.instance.folder = folder
                form.save()
        
        return redirect('file', pk=folder_id, slug=folder_slug)


class ServiceFileUploadView(AdminClientLoginRequiredMixin, TemplateView):
    template_name = "client/upload_service_media.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_id = self.kwargs.get('pk')
        folder_slug = self.kwargs.get('slug')
        context['folder_slug'] = folder_slug
        context['form'] = ServiceFileForm()
        context['folder_id'] = folder_id
        context['files'] = ServiceFile.objects.filter(folder__id=folder_id, folder__slug=folder_slug)
        return context

    def post(self, request, *args, **kwargs):
        form = ServiceFileForm(request.POST, request.FILES)
        folder_id = self.kwargs.get('pk')
        folder_slug = self.kwargs.get('slug')
        
        if form.is_valid():
            folder = get_object_or_404(ServiceRequestFolder, id=folder_id)
            form.instance.folder = folder
            form.save()
            messages.success(request, 'File uploaded successfully.')
            return redirect('service_file', pk=folder_id, slug=folder_slug)
        else:
            messages.error(request, 'There was an error uploading the file.')
            return self.render_to_response(self.get_context_data(form=form))


class RequestServiceChatCreateView(UserLoginRequiredMixin, CreateView):
    template_name = 'service_request_chat.html'
    model = RequestServiceChat
    fields = ('message', )

    def form_valid(self, form, *args, **kwargs):
        chat = form.save(commit=False)
        service = get_object_or_404(RequestService, request_number=self.kwargs.get('request_number'))
        chat.service = service
        if self.request.user.is_admin:
            chat.admin = self.request.user
        else:
            chat.client = self.request.user
        create_new_message_notification(service, self.kwargs.get('request_number'), self.request.user)
        chat.save()
        return super().form_valid(form)
    
    def get_success_url(self, **kwargs): 
        if self.request.user.is_admin:
            url = reverse_lazy('admin-request-detail', kwargs = {'request_number': self.kwargs.get('request_number')})
        else:
            url = reverse_lazy('request-detail', kwargs = {'request_number': self.kwargs.get('request_number')})
        return url


class MarkNotificationAsSeenView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            notification = get_object_or_404(Notification, slug=kwargs['slug'])
        except Notification.DoesNotExist:
            return HttpResponseNotFound('<h1>Notification not found</h1>')
        notification.is_seen = True
        notification.save(update_fields=['is_seen'])

        if notification.url and is_valid_url(notification.url):
            return notification.url
        else:
            fallback_url = self.request.META.get('HTTP_REFERER', '/')
            return fallback_url

def is_valid_url(url):
    return True


class ClearSession(AdminClientLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            del request.session[kwargs["page_url"]]
        except KeyError:
            pass

        return redirect(kwargs["redirect_page"])
    

class ComplaintView(ClientLoginRequiredMixin, CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'client/complaint.html'
    success_url = reverse_lazy('complaint')

    def form_valid(self, form, *args, **kwargs):
        complaint = form.save(commit=False)
        complaint.user = User.objects.get(id=self.request.user.id)
        complaint.save()
        messages.success(self.request, 'Your Complaint has been successfully raised!')
        return super().form_valid(form)

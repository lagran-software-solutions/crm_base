from django.contrib import admin
from .models import Service, SubService, RequestService, ClientAdminFolder, ServiceRequestFolder, ServiceFile, \
Notification, RequestServiceChat, RequestStatus, Invoice, InvoiceItem, InvoiceRecord, InvoiceRecordItem

@admin.register(InvoiceRecord)
class InvoiceRecordAdmin(admin.ModelAdmin):
    list_display = [field.name for field in InvoiceRecord._meta.fields]

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display =['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(InvoiceRecordItem)
class InvoiceRecordItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in InvoiceRecordItem._meta.fields]

@admin.register(RequestService)
class ServiceAdmin(admin.ModelAdmin):
    list_display =['request_number']


@admin.register(SubService)
class SubServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'service', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

    def service_name(self, obj):
        return obj.service.name
    service_name.admin_order_field = 'service__name'
    service_name.short_description = 'Service'
    

admin.site.register(ClientAdminFolder)
admin.site.register(ServiceRequestFolder)
admin.site.register(ServiceFile)
admin.site.register(Notification)
admin.site.register(RequestServiceChat)
admin.site.register(RequestStatus)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1 
    fields = ('description', 'rate', 'gst', 'other_tax', 'total_tax', 'amount')
    readonly_fields = ('total_tax', 'amount') 

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'from_name', 'to_name', 'invoice_date')
    search_fields = ('invoice_number', 'from_name', 'to_name', 'from_business', 'to_business')
    list_filter = ('invoice_date',)
    date_hierarchy = 'invoice_date'
    #inlines = [InvoiceItemInline]
    fields = (
        'invoice_number', 'invoice_date', 
        'from_name', 'from_business'
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'rate', 'gst', 'other_tax', 'total_tax', 'amount', 'invoice')
    search_fields = ('description', 'invoice__invoice_number')
    list_filter = ('gst', 'other_tax')

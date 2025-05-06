from django.contrib import admin
from .models import *
from .forms import SEOModelForm
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm


User = get_user_model()

admin.site.register(Homebanner)
admin.site.register(Elementor)
admin.site.register(Aboutgallery)
admin.site.register(OurSolution)
admin.site.register(Advertise)
admin.site.register(Workflow)
admin.site.register(Service)
admin.site.register(Contact)
admin.site.register(Banner)
admin.site.register(Address)
admin.site.register(Management)
admin.site.register(Team)
admin.site.register(Reachus)
admin.site.register(indexform)
admin.site.register(Footerform)
admin.site.register(Footer)
admin.site.register(HappyUser)
admin.site.register(AboutHistory)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'mobile', 'first_name', 'last_name', 'email', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'mobile', 'first_name', 'last_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'mobile', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_admin'),
        }),
    )
    search_fields = ('username', 'mobile', 'email')
    ordering = ('mobile',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)


# @admin.register(File)
# class FileAdmin(admin.ModelAdmin):
#     list_display = ['uploaded_at', 'folder']


# @admin.register(Folder)
# class FolderAdmin(admin.ModelAdmin):
#     list_display = ['name', 'created_by', 'created_by_admin', 'created_at']
#     search_fields = ['name']


@admin.register(SEO)
class SEOAdmin(admin.ModelAdmin):
    list_display = ('page', )
    search_fields = ('page', )
    form = SEOModelForm
    
    
class SEOAdmin(admin.ModelAdmin):
    list_display = ( 'seo_title ', 'seo_description', 'seo_keywords')
    search_fields = ('seo_title',)
    

admin.site.register(ChatMessage)


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    fields = ['user', 'message', 'timestamp', 'is_seen']  
    readonly_fields = ['timestamp'] 
    extra = 0  

# Admin model for Thread
class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessageInline]  
    list_display = ['first_person', 'second_person', 'updated_at']
    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)

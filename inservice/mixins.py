from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import AccessMixin


class AdminLoginRequiredMixin(AccessMixin): 
    login_url = reverse_lazy('login')
    def dispatch(self, request, *args, **kwargs):
        print('2: ', request.user.is_admin)
        if not request.user.is_authenticated or not request.user.is_admin or request.user.is_superuser:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class ClientLoginRequiredMixin(AccessMixin):
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.is_admin or request.user.is_superuser:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class AdminClientLoginRequiredMixin(AccessMixin):
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.is_superuser:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class AdminSuperAdminLoginRequiredMixin(AccessMixin):
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or (not request.user.is_admin and not request.user.is_superuser):
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    

class SuperAdminLoginRequiredMixin(AccessMixin):
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and request.user.is_superuser:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    

class UserLoginRequiredMixin(AccessMixin):
    login_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
    

from django.urls import path
from . import views
from .sitemaps import HomeSitemap, AboutSitemap, ServiceSitemap, ContactSitemap, \
        TeamSitemap, TeamDetail
from django.contrib.sitemaps.views import sitemap


sitemaps = {
    'home': HomeSitemap,
    'about': AboutSitemap,
    'services': ServiceSitemap,
    'contact': ContactSitemap,
    'team': TeamSitemap,
    'team_detail': TeamDetail
}


urlpatterns = [
    # path("", views.HomeFormView.as_view(), name='home'),
    path("about",views.AboutView.as_view(), name='about'),
    path("footerform", views.FooterformCreateView.as_view(), name='footerform'),
    path("contact", views.ContactUsView.as_view(), name='contact'),
    path("homeform", views.HomeFormView.as_view(), name='homeform'),
    path("services", views.ServiceView.as_view(), name='services'),
    path("team", views.TeamView.as_view(), name='team'),
    path("service/<slug:slug>/", views.ServiceDetailView.as_view(), name="service_details"),
    path('servicedetails/', views.ServiceDetails, name='servicedetails'),
    path("team", views.TeamView.as_view(), name='team-details'),
    path("reachus/", views.reachus_view, name="reachus"),
    path('subscribe/', views.subscribe_email, name='subscribe'),
    # path('service/', Service.as_view(), name='service'),
    # path('servicedetails/', ServiceDetails.as_view(), name='servicedetails'),
    # path('signup/', Signup.as_view(), name='signup'),
    # path('forgot/', Forgot.as_view(), name='forgot'),
    # path('core/', Core.as_view(), name='core'),
    # path('contact/', Contact.as_view(), name='contact'),
    # path("submit-contact/",submit_contact_form, name="submit_contact_form"),
    # path("submit-contact/", SubmitContactForm.as_view(), name="contact_submit"),

    path("adminpanel",views.AdminPanel.as_view(), name='adminpanel'),
    path('', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/<str:profile_type>', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('forget-password/', views.ForgetPasswordView.as_view(), name='forget_password'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]


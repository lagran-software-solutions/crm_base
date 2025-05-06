from inservice.models import Service
from django.contrib import sitemaps
from django.urls import reverse


class HomeSitemap(sitemaps.Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)
    

class AboutSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['about']

    def location(self, item):
        return reverse(item)
    

class ContactSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['contact']

    def location(self, item):
        return reverse(item)
    

class TeamSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['team']

    def location(self, item):
        return reverse(item)
    

class TeamDetail(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['team-details']

    def location(self, item):
        return reverse(item)
    

class ServiceSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Service.objects.only('slug') 

    def location(self, obj):
        return f'/service/{obj.slug}'
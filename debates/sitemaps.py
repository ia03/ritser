from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Topic, Debate, Argument
from django.db.models import Q


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['index', 'about', 'rules', 'terms', 'privacy', 'cookies']

    def location(self, item):
        return reverse(item)


class TopicSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7
    
    def items(self):
        return Topic.objects.all()
    
    def lastmod(self, obj):
        return obj.edited_on


class DebateSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.4
    
    def items(self):
        return Debate.objects.filter(~Q(approvalstatus=3))
    
    def lastmod(self, obj):
        return obj.edited_on


class ArgumentSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.3
    
    def items(self):
        return Argument.objects.filter(~Q(approvalstatus=3))
    
    def lastmod(self, obj):
        return obj.edited_on
"""udebate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.contrib.sitemaps import views as smapviews
from debates.sitemaps import StaticViewSitemap, TopicSitemap, DebateSitemap, ArgumentSitemap
from accounts.sitemaps import UserSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'topic': TopicSitemap,
    'debate': DebateSitemap,
    'argument': ArgumentSitemap,
    'user': UserSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'favicon.ico',
        RedirectView.as_view(
            url=staticfiles_storage.url('debates/img/favicon.ico')),
        name="favicon"),
    # favicon for older browsers
    re_path(r'^', include('accounts.urls')),
    re_path(r'^accounts/', include('allauth.urls')),
    # path('signup', accounts.views.signup, name='signup'),
    re_path(r'^', include('debates.urls')),
    # sitemaps
    path('sitemap.xml',
         smapviews.index,
         {'sitemaps': sitemaps},
         name='sitemapindex'),
    path('sitemap-<section>.xml', smapviews.sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    re_path(
        r'^robots.txt$',
        TemplateView.as_view(template_name="robots.txt",
                             content_type="text/plain"),
        name="robots_file")
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

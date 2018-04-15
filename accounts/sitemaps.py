from django.contrib.sitemaps import Sitemap
from .models import User

class UserSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.2
    
    def items(self):
        return User.objects.filter(is_active=True)
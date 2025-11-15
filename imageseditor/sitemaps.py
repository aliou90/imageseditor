from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'resize', 'remove_bg']  # Ajoutez vos noms de vues ici

    def location(self, item):
        return reverse(item)

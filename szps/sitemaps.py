from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from news.models import NewsPost
from documents.models import Document


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["home", "news:list", "documents:list", "sponsors:list", "contact:contact"]

    def location(self, item):
        return reverse(item)


class NewsPostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return NewsPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

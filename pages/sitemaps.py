"""Sitemap generowana z bazy — nowe aktualności i opublikowane strony
trafiają do niej same, bez ręcznej edycji pliku XML."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article, StaticPage


class FixedPagesSitemap(Sitemap):
    protocol = "https"

    # (nazwa URL, changefreq, priority)
    PAGES = [
        ("pages:home", "weekly", 1.0),
        ("pages:article_list", "weekly", 0.8),
        ("board:list", "monthly", 0.7),
    ]

    def items(self):
        return self.PAGES

    def location(self, item):
        return reverse(item[0])

    def changefreq(self, item):
        return item[1]

    def priority(self, item):
        return item[2]


class ArticleSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Article.objects.filter(is_published=True)

    def location(self, obj):
        return reverse("pages:article_detail", args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at


class StaticPageSitemap(Sitemap):
    protocol = "https"
    changefreq = "yearly"
    priority = 0.4

    def items(self):
        return StaticPage.objects.filter(is_published=True)

    def location(self, obj):
        return reverse("pages:static_page", args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    "pages": FixedPagesSitemap,
    "articles": ArticleSitemap,
    "static": StaticPageSitemap,
}

from django.shortcuts import get_object_or_404, render

from .models import Article, StaticPage


def home(request):
    articles = Article.objects.filter(is_published=True)[:5]
    return render(request, "pages/home.html", {"articles": articles})


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, "pages/article_detail.html", {"article": article})


def static_page(request, slug):
    page = get_object_or_404(StaticPage, slug=slug, is_published=True)
    return render(request, "pages/static_page.html", {"page": page})

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from documents.models import Document, DocumentCategory

from .models import Article, StaticPage


def home(request):
    articles = Article.objects.filter(is_published=True)[:6]
    doc_categories = DocumentCategory.objects.prefetch_related(
        Prefetch(
            "documents",
            queryset=Document.objects.filter(is_published=True),
        )
    )
    return render(
        request,
        "pages/home.html",
        {
            "articles": articles,
            "doc_categories": doc_categories,
            "active_nav": "home",
        },
    )


def article_list(request):
    articles = Article.objects.filter(is_published=True)
    return render(
        request,
        "pages/article_list.html",
        {"articles": articles, "active_nav": "aktualnosci"},
    )


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, "pages/article_detail.html", {"article": article})


def static_page(request, slug):
    page = get_object_or_404(StaticPage, slug=slug, is_published=True)
    return render(request, "pages/static_page.html", {"page": page})

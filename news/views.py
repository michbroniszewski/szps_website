from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import NewsPost, NewsCategory
from documents.models import Document


def home(request):
    pinned = (
        NewsPost.objects.filter(is_published=True, is_pinned=True)
        .select_related("category")[:3]
    )
    latest = (
        NewsPost.objects.filter(is_published=True, is_pinned=False)
        .select_related("category")[:6]
    )
    featured_docs = (
        Document.objects.filter(is_active=True, is_featured=True)
        .select_related("category")[:6]
    )
    return render(request, "home.html", {
        "pinned": pinned,
        "latest": latest,
        "featured_docs": featured_docs,
    })


def news_list(request):
    category_slug = request.GET.get("kategoria")
    posts = NewsPost.objects.filter(is_published=True).select_related("category")
    categories = NewsCategory.objects.all()
    active_category = None
    if category_slug:
        active_category = get_object_or_404(NewsCategory, slug=category_slug)
        posts = posts.filter(category=active_category)
    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get("strona"))
    return render(request, "news/list.html", {
        "page_obj": page,
        "categories": categories,
        "active_category": active_category,
    })


def news_detail(request, slug):
    post = get_object_or_404(
        NewsPost.objects.select_related("category"),
        slug=slug,
        is_published=True,
    )
    related = (
        NewsPost.objects.filter(is_published=True, category=post.category)
        .exclude(pk=post.pk)
        .select_related("category")[:3]
    )
    return render(request, "news/detail.html", {"post": post, "related": related})

from django.shortcuts import render
from django.db.models import Q
from .models import Document, DocumentCategory


def document_list(request):
    query = request.GET.get("q", "")
    category_slug = request.GET.get("kategoria", "")
    documents = Document.objects.filter(is_active=True)
    categories = DocumentCategory.objects.all()
    active_category = None

    if query:
        documents = documents.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category_slug:
        try:
            active_category = DocumentCategory.objects.get(slug=category_slug)
            documents = documents.filter(category=active_category)
        except DocumentCategory.DoesNotExist:
            pass

    return render(request, "documents/list.html", {
        "documents": documents,
        "categories": categories,
        "active_category": active_category,
        "query": query,
    })

from django.shortcuts import render
from django.db.models import Q
from .models import Document, DocumentCategory


def document_list(request):
    query = request.GET.get("q", "")
    category_slug = request.GET.get("kategoria", "")
    base_qs = Document.objects.filter(is_active=True)
    categories = DocumentCategory.objects.all()
    active_category = None

    if query:
        base_qs = base_qs.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category_slug:
        try:
            active_category = DocumentCategory.objects.get(slug=category_slug)
            base_qs = base_qs.filter(category=active_category)
        except DocumentCategory.DoesNotExist:
            pass

    # Gdy filtrujemy — płaska lista wyników
    if query or active_category:
        return render(request, "documents/list.html", {
            "documents": base_qs,
            "categories": categories,
            "active_category": active_category,
            "query": query,
            "grouped": False,
        })

    # Widok domyślny — dokumenty pogrupowane po kategoriach
    grouped = []
    for cat in categories:
        docs = base_qs.filter(category=cat)
        if docs.exists():
            grouped.append({"category": cat, "documents": docs})

    uncategorized = base_qs.filter(category__isnull=True)
    if uncategorized.exists():
        grouped.append({"category": None, "documents": uncategorized})

    return render(request, "documents/list.html", {
        "grouped": True,
        "grouped_documents": grouped,
        "categories": categories,
        "active_category": None,
        "query": "",
    })

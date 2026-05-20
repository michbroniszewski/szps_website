from django.shortcuts import render
from django.db.models import Q
from .models import Document, DocumentCategory


def document_list(request):
    query = request.GET.get("q", "")
    category_slug = request.GET.get("kategoria", "")
    base_qs = Document.objects.filter(is_active=True).select_related("category")
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

    # Widok domyślny — dokumenty pogrupowane po kategoriach.
    # Jeden SELECT na całość; grupowanie w Pythonie zamiast N zapytań w pętli.
    all_docs = list(base_qs)
    grouped = []
    for cat in categories:
        docs = [d for d in all_docs if d.category_id == cat.pk]
        if docs:
            grouped.append({"category": cat, "documents": docs})

    uncategorized = [d for d in all_docs if d.category_id is None]
    if uncategorized:
        grouped.append({"category": None, "documents": uncategorized})

    return render(request, "documents/list.html", {
        "grouped": True,
        "grouped_documents": grouped,
        "categories": categories,
        "active_category": None,
        "query": "",
    })

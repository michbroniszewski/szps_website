from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase

from .models import Document, DocumentCategory


class DocumentCategoryTests(TestCase):
    def test_str_returns_name(self):
        cat = DocumentCategory.objects.create(name="Komunikaty", slug="komunikaty")
        self.assertEqual(str(cat), "Komunikaty")

    def test_category_with_document_cannot_be_deleted(self):
        cat = DocumentCategory.objects.create(name="Przepisy", slug="przepisy")
        Document.objects.create(
            title="Regulamin",
            category=cat,
            file=SimpleUploadedFile("r.pdf", b"%PDF-1.4"),
        )
        with self.assertRaises(ProtectedError):
            cat.delete()


class DocumentTests(TestCase):
    def test_published_at_is_set_automatically(self):
        cat = DocumentCategory.objects.create(name="Wytyczne", slug="wytyczne")
        doc = Document.objects.create(
            title="Poradnik",
            category=cat,
            file=SimpleUploadedFile("p.pdf", b"%PDF-1.4"),
        )
        self.assertIsNotNone(doc.published_at)

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase

from .models import Document, DocumentCategory


# Slugi z prefiksem "test-" żeby nie kolidować z kanonicznymi
# kategoriami zasianymi w migracji documents/0003.


class DocumentCategoryTests(TestCase):
    def test_str_returns_name(self):
        cat = DocumentCategory.objects.create(
            name="Test Komunikaty", slug="test-komunikaty"
        )
        self.assertEqual(str(cat), "Test Komunikaty")

    def test_category_with_document_cannot_be_deleted(self):
        cat = DocumentCategory.objects.create(
            name="Test Przepisy", slug="test-przepisy"
        )
        Document.objects.create(
            title="Regulamin",
            category=cat,
            file=SimpleUploadedFile("r.pdf", b"%PDF-1.4"),
        )
        with self.assertRaises(ProtectedError):
            cat.delete()


class DocumentTests(TestCase):
    def _cat(self):
        return DocumentCategory.objects.create(
            name="Wytyczne testowe", slug="test-wytyczne"
        )

    def test_published_at_is_set_automatically(self):
        doc = Document.objects.create(
            title="Poradnik",
            category=self._cat(),
            file=SimpleUploadedFile("p.pdf", b"%PDF-1.4"),
        )
        self.assertIsNotNone(doc.published_at)

    def test_get_href_prefers_uploaded_file(self):
        doc = Document.objects.create(
            title="Z pliku",
            category=self._cat(),
            file=SimpleUploadedFile("x.pdf", b"%PDF-1.4"),
            external_url="/static/dokumenty/inny.pdf",
        )
        # gdy jest plik, external_url jest ignorowany
        self.assertEqual(doc.get_href(), doc.file.url)
        self.assertNotEqual(doc.get_href(), "/static/dokumenty/inny.pdf")

    def test_get_href_falls_back_to_external_url(self):
        doc = Document.objects.create(
            title="Zewnętrzny",
            category=self._cat(),
            external_url="/static/dokumenty/przepisy.pdf",
        )
        self.assertEqual(doc.get_href(), "/static/dokumenty/przepisy.pdf")

    def test_clean_requires_file_or_url(self):
        doc = Document(title="Pusty", category=self._cat())
        with self.assertRaises(ValidationError):
            doc.clean()

    def test_clean_passes_with_external_url_only(self):
        doc = Document(
            title="OK",
            category=self._cat(),
            external_url="/static/dokumenty/x.pdf",
        )
        doc.clean()  # nie powinno rzucić

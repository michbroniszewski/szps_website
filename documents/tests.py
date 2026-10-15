from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase

from .models import Document, DocumentCategory


# Slugi z prefiksem "test-" żeby nie kolidować z kanonicznymi
# kategoriami zasianymi w migracji documents/0003.


class DocumentCategoryTests(TestCase):
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

    def test_get_href_prefers_uploaded_file(self):
        doc = Document.objects.create(
            title="Z pliku",
            category=self._cat(),
            file=SimpleUploadedFile("x.pdf", b"%PDF-1.4"),
            external_url="/static/dokumenty/inny.pdf",
        )
        # gdy jest plik, external_url jest ignorowany
        self.assertEqual(doc.get_href(), doc.file.url)

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

    def test_clean_accepts_local_path_and_http_url(self):
        cat = self._cat()
        for url in ("/static/dokumenty/x.pdf", "https://example.com/x.pdf"):
            Document(title="OK", category=cat, external_url=url).clean()  # nie rzuca

    def test_clean_rejects_unsafe_urls(self):
        cat = self._cat()
        for url in (
            "javascript:alert(1)",
            " JavaScript:alert(1)",
            "data:text/html,<script>",
            "//evil.example/x.pdf",
            "ftp://example.com/x.pdf",
            "dokumenty/x.pdf",
        ):
            doc = Document(title="Zły", category=cat, external_url=url)
            with self.assertRaises(ValidationError, msg=url):
                doc.clean()

    def test_get_href_hides_unsafe_legacy_url(self):
        doc = Document.objects.create(
            title="Stary wpis", category=self._cat(), external_url="javascript:alert(1)"
        )
        self.assertEqual(doc.get_href(), "")

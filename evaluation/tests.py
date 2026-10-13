import tempfile
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from . import sheet


def valid_post(**overrides):
    data = {
        "competition": "1ligam",
        "difficulty": "sredni",
        "teams": "Śląsk Katowice – Gwarek Zabrze",
        "match_date": "2026-10-03",
        "result": "3:1",
        "observer": "Jan Obserwator",
        "referee_name": "Anna Kowalska",
        "position": "r2",
        "comment": "",
    }
    for key, _label, _info in sheet.ELEMENTS:
        data[sheet.grade_field(key)] = "C"
        data[sheet.comment_field(key)] = ""
    data.update(overrides)
    return data


class EvaluationPageTests(TestCase):
    def setUp(self):
        self.url = reverse("evaluation:form")

    def test_page_renders_with_noindex(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        self.assertContains(response, '<meta name="robots" content="noindex, nofollow">')

    def test_page_is_not_linked_from_home(self):
        response = self.client.get(reverse("pages:home"))
        self.assertNotContains(response, self.url)

    def test_page_not_in_sitemap(self):
        response = self.client.get("/sitemap.xml")
        self.assertNotContains(response, self.url)

    def test_valid_post_returns_pdf(self):
        response = self.client.post(self.url, valid_post())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_missing_required_fields_rerenders_form(self):
        response = self.client.post(self.url, valid_post(observer="", referee_name="", position=""))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        self.assertTrue(response.context["form"].has_error("observer"))
        self.assertTrue(response.context["form"].has_error("referee_name"))
        self.assertTrue(response.context["form"].has_error("position"))

    def test_competition_must_come_from_list(self):
        response = self.client.post(self.url, valid_post(competition="PlusLiga"))
        self.assertTrue(response.context["form"].has_error("competition"))

    def test_page_lists_all_competitions_and_elements(self):
        response = self.client.get(self.url)
        for _value, label in sheet.COMPETITIONS:
            self.assertContains(response, label)
        for _key, label, _info in sheet.ELEMENTS:
            self.assertContains(response, label)

    def test_info_panels_render_position_specific_details(self):
        response = self.client.get(self.url)
        # Wspólne (organizacja) i zależne od pozycji (technika I / II).
        self.assertContains(response, "Przybycie na obiekt na co najmniej godzinę przed meczem")
        self.assertContains(response, "Brak obserwacji ukrytej sygnalizacji Sędziego II")
        self.assertContains(response, "Zajęcie przez Sędziego II optymalnej pozycji")
        self.assertContains(response, 'data-pos="r1"')
        self.assertContains(response, 'data-pos="r2"')

    def test_comment_possible_for_every_element(self):
        form = self.client.get(self.url).context["form"]
        for key, _label, _info in sheet.ELEMENTS:
            self.assertIn(sheet.comment_field(key), form.fields)

    def test_comment_on_c_grade_is_allowed(self):
        response = self.client.post(
            self.url, valid_post(c_technika="Dobra współpraca z sekretarzem.\nBez uwag.")
        )
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_non_c_grade_requires_comment(self):
        response = self.client.post(self.url, valid_post(g_relacje="E"))
        self.assertTrue(response.context["form"].has_error("c_relacje"))
        self.assertFalse(response.context["form"].has_error("c_technika"))
        self.assertFalse(response.context["form"].has_error("comment"))

    def test_non_c_grade_with_comment_is_valid(self):
        response = self.client.post(
            self.url, valid_post(g_relacje="E", c_relacje="Brak kontroli ławki gości.")
        )
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_send_button_visible_with_default_recipient(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'value="email"')
        self.assertContains(response, settings.CONTACT_RECIPIENT)

    @override_settings(EVALUATION_EMAIL_RECIPIENTS=["ws@example.com"])
    def test_email_action_sends_pdf(self):
        response = self.client.post(self.url, valid_post(action="email"))
        self.assertRedirects(response, self.url + "?wyslano=1")
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.to, ["ws@example.com"])
        self.assertEqual(msg.cc, [])
        self.assertIn("I Liga Śląska Mężczyzn", msg.body)
        self.assertIn("Anna Kowalska (Sędzia II)", msg.body)
        filename, content, mimetype = msg.attachments[0]
        self.assertEqual(mimetype, "application/pdf")
        self.assertTrue(content.startswith(b"%PDF"))

    def test_email_copy_goes_to_observer(self):
        self.client.post(self.url, valid_post(action="email", observer_email="obs@example.com"))
        msg = mail.outbox[0]
        self.assertEqual(msg.to, settings.EVALUATION_EMAIL_RECIPIENTS)
        self.assertEqual(msg.cc, ["obs@example.com"])
        self.assertEqual(msg.reply_to, ["obs@example.com"])

    def test_invalid_form_does_not_send(self):
        response = self.client.post(self.url, valid_post(action="email", observer=""))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)


class ExportHtmlCommandTests(TestCase):
    def test_export_writes_self_contained_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "arkusz.html"
            call_command("export_evaluation_html", output=str(out), stdout=StringIO())
            html = out.read_text(encoding="utf-8")
        self.assertIn("Wersja do przeglądu", html)
        self.assertIn(".ev-el__info", html)          # CSS wbudowany
        self.assertIn("refreshPosition", html)       # JS wbudowany
        self.assertIn("Przybycie na obiekt", html)   # rozwinięcia „i”
        self.assertNotIn('name="csrfmiddlewaretoken"', html)
        self.assertNotIn('value="email"', html)


class ResultDocumentTests(TestCase):
    """PDF to dokument wynikowy: tabela wyników + podsumowanie + opis."""

    def _cleaned(self, **overrides):
        from .forms import EvaluationForm
        form = EvaluationForm(valid_post(**overrides))
        self.assertTrue(form.is_valid(), form.errors)
        return form.cleaned_data

    def _summary_text(self, data):
        from .pdf import _styles, _summary
        return " ".join(p.text for p in _summary(data, _styles()))

    def test_summary_all_default(self):
        text = self._summary_text(self._cleaned())
        self.assertIn("C × 5", text)
        self.assertIn("Wszystkie elementy ocenione na poziomie wyjściowym", text)

    def test_summary_lists_elements_above_and_below(self):
        text = self._summary_text(self._cleaned(
            g_technika="B", c_technika="x", g_relacje="E", c_relacje="y",
        ))
        self.assertIn("Powyżej poziomu wyjściowego: Technika sędziowania (B)", text)
        self.assertIn("obszary do poprawy: Relacje z zespołami", text)
        self.assertIn("(E)", text)

    def test_filename_names_referee_and_date(self):
        from .pdf import pdf_filename
        self.assertEqual(
            pdf_filename(self._cleaned()),
            "protokol-obserwacji-2026-10-03-anna-kowalska.pdf",
        )

    def test_pdf_builds_with_long_comments(self):
        from .pdf import build_pdf
        long = ("Długi komentarz obserwatora. " * 200)[:4000]
        pdf = build_pdf(self._cleaned(comment=long, c_technika=long))
        self.assertTrue(pdf.startswith(b"%PDF"))

from django.core import mail
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

    def test_email_button_hidden_without_recipients(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, 'value="email"')

    def test_email_action_ignored_without_recipients(self):
        response = self.client.post(self.url, valid_post(action="email"))
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EVALUATION_EMAIL_RECIPIENTS=["ws@example.com"])
    def test_email_action_sends_pdf(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'value="email"')

        response = self.client.post(self.url, valid_post(action="email"))
        self.assertRedirects(response, self.url + "?wyslano=1")
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.to, ["ws@example.com"])
        self.assertIn("I Liga Śląska Mężczyzn", msg.body)
        self.assertIn("Anna Kowalska (Sędzia II)", msg.body)
        filename, content, mimetype = msg.attachments[0]
        self.assertEqual(mimetype, "application/pdf")
        self.assertTrue(content.startswith(b"%PDF"))

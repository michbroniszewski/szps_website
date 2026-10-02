from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from . import sheet


def valid_post(**overrides):
    data = {
        "competition": "II liga mężczyzn",
        "match_date": "2026-10-03",
        "teams": "Śląsk Katowice – Gwarek Zabrze",
        "result": "3:1",
        "observer": "Jan Obserwator",
        "difficulty": "sredni",
        "staff_info": "",
        "notes": "",
    }
    for ref in sheet.REFEREES:
        r = ref["key"]
        data.update({
            f"{r}_name": f"Sędzia {r}",
            f"{r}_impact": "bez_wplywu",
            f"{r}_experience": "duze",
            f"{r}_recommendation": "utrzymanie",
            f"{r}_overall": "dobra",
            f"{r}_summary": "Pewne prowadzenie meczu.",
            f"{r}_reasons": "",
        })
        for _group, items in ref["groups"]:
            for key, _label in items:
                data[sheet.grade_field(r, key)] = "C"
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
        response = self.client.post(self.url, valid_post(observer="", r1_name=""))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        self.assertTrue(response.context["form"].has_error("observer"))
        self.assertTrue(response.context["form"].has_error("r1_name"))

    def test_non_c_grade_requires_reasons(self):
        response = self.client.post(self.url, valid_post(r2_g_lawki="E"))
        self.assertTrue(response.context["form"].has_error("r2_reasons"))
        self.assertFalse(response.context["form"].has_error("r1_reasons"))

    def test_non_c_grade_with_reasons_is_valid(self):
        response = self.client.post(
            self.url, valid_post(r2_g_lawki="E", r2_reasons="Brak kontroli ławki gości.")
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
        filename, content, mimetype = msg.attachments[0]
        self.assertEqual(mimetype, "application/pdf")
        self.assertTrue(content.startswith(b"%PDF"))

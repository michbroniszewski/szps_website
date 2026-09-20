from django.test import TestCase
from django.urls import reverse

from .models import BoardMember


class BoardMemberModelTests(TestCase):
    def test_full_name_joins_first_and_last(self):
        member = BoardMember.objects.create(
            first_name="Jan", last_name="Kowalski", role="Przewodniczący"
        )
        self.assertEqual(member.full_name, "Jan Kowalski")
        self.assertEqual(str(member), "Jan Kowalski")


class BoardListViewTests(TestCase):
    def test_list_returns_200(self):
        response = self.client.get(reverse("board:list"))
        self.assertEqual(response.status_code, 200)

    def test_list_shows_only_active_members(self):
        BoardMember.objects.create(
            first_name="Anna", last_name="Aktywna", role="Członek", is_active=True
        )
        BoardMember.objects.create(
            first_name="Piotr", last_name="Nieaktywny", role="Członek", is_active=False
        )
        response = self.client.get(reverse("board:list"))
        rendered_ids = {m.id for m in response.context["members"]}
        active_ids = set(
            BoardMember.objects.filter(is_active=True).values_list("id", flat=True)
        )
        self.assertEqual(rendered_ids, active_ids)

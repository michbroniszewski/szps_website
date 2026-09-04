from django.db import migrations


MEMBERS = [
    ("Marek", "Lagierski", "Przewodniczący WS"),
    ("Marek", "Krupski", "Zastępca Przewodniczącego WS"),
    ("Wojciech", "Targosz", "Sekretarz WS · Komisja Organizacyjna"),
    ("Michał", "Broniszewski", "Członek WS · Komisja Szkolenia"),
    ("Mariusz", "Fiutek", "Członek WS · Komisja Obsad"),
    ("Piotr", "Paprzycki", "Członek WS · Komisja Obsad"),
    ("Katarzyna", "Sajdok-Iwańska", "Członek WS · Komisja Szkolenia"),
    ("Łukasz", "Szczepankiewicz", "Członek WS · Komisja Organizacyjna"),
    ("Włodzimierz", "Włodyka", "Członek WS · Komisja Organizacyjna"),
]


def seed_members(apps, schema_editor):
    BoardMember = apps.get_model("board", "BoardMember")
    for order, (first, last, role) in enumerate(MEMBERS, start=10):
        BoardMember.objects.update_or_create(
            first_name=first,
            last_name=last,
            defaults={"role": role, "order": order, "is_active": True},
        )


def unseed_members(apps, schema_editor):
    BoardMember = apps.get_model("board", "BoardMember")
    for first, last, _ in MEMBERS:
        BoardMember.objects.filter(first_name=first, last_name=last).delete()


class Migration(migrations.Migration):
    dependencies = [("board", "0001_initial")]

    operations = [migrations.RunPython(seed_members, unseed_members)]

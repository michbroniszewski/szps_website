"""Polityka prywatności: dopisanie ciasteczka ev_access (kod dostępu do
arkusza oceny). Zmienia treść tylko wtedy, gdy fragment z listą ciasteczek
jest nadal w wersji z migracji 0004 — ręcznych edycji w panelu nie ruszamy.
"""

from django.db import migrations

SLUG = "polityka-prywatnosci"

OLD = """  <li><code>sessionid</code> — tylko dla osób logujących się do panelu
  administracyjnego (ważne do 2 tygodni).</li>
</ul>"""

NEW = """  <li><code>sessionid</code> — tylko dla osób logujących się do panelu
  administracyjnego (ważne do 2 tygodni),</li>
  <li><code>ev_access</code> — tylko dla obserwatorów: potwierdza podanie
  kodu dostępu do arkusza oceny, aby nie trzeba było wpisywać go przy każdej
  wizycie (ważne do 180 dni).</li>
</ul>"""


def add_cookie(apps, schema_editor):
    StaticPage = apps.get_model("pages", "StaticPage")
    for page in StaticPage.objects.filter(slug=SLUG):
        if OLD in page.body:
            page.body = page.body.replace(OLD, NEW)
            page.save(update_fields=["body"])


def remove_cookie(apps, schema_editor):
    StaticPage = apps.get_model("pages", "StaticPage")
    for page in StaticPage.objects.filter(slug=SLUG):
        if NEW in page.body:
            page.body = page.body.replace(NEW, OLD)
            page.save(update_fields=["body"])


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0004_seed_privacy_policy"),
    ]

    operations = [
        migrations.RunPython(add_cookie, remove_cookie),
    ]

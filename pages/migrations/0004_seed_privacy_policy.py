"""Szkic polityki prywatności jako strona statyczna.

Zakładany jako NIEOPUBLIKOWANY — fragmenty oznaczone [DO UZUPEŁNIENIA]
wymagają decyzji Związku (administrator, okresy przechowywania). Po
uzupełnieniu w panelu wystarczy zaznaczyć „Opublikowana”; wtedy link
pojawi się w stopce i przy zgodzie w formularzu kontaktowym.

get_or_create: jeśli strona już istnieje (np. ktoś ją edytował), migracja
jej nie nadpisuje. Cofnięcie migracji niczego nie usuwa.
"""

from django.db import migrations

SLUG = "polityka-prywatnosci"

TODO = '<mark class="todo">[DO UZUPEŁNIENIA: {}]</mark>'

BODY = f"""
<p class="prose__meta">Ostatnia aktualizacja: {TODO.format("data publikacji")}</p>

<p>Niniejsza polityka opisuje, jakie dane osobowe przetwarzamy w związku
z korzystaniem ze strony <strong>sedziowie.szps.pl</strong> (dalej: „Strona”),
w jakim celu, na jakiej podstawie oraz jakie prawa Ci przysługują.</p>

<h2>1. Administrator danych</h2>
<p>Administratorem danych osobowych jest Śląski Związek Piłki Siatkowej
z siedzibą w Katowicach, ul. Bukowa 1A, 40-108 Katowice
{TODO.format("KRS / NIP Związku; potwierdzić, że administratorem jest Związek, a nie sam Wydział")}.</p>
<p>W sprawach dotyczących danych osobowych możesz kontaktować się z nami pod
adresem <a href="mailto:ws@szps.pl">ws@szps.pl</a>
{TODO.format("dane kontaktowe Inspektora Ochrony Danych, jeśli został wyznaczony — w przeciwnym razie usunąć ten dopisek")}.</p>

<h2>2. Jakie dane przetwarzamy i w jakim celu</h2>

<h3>Formularz kontaktowy</h3>
<p>Gdy wysyłasz wiadomość przez formularz kontaktowy, przetwarzamy podane
przez Ciebie: imię i nazwisko, adres e-mail, wybrany temat i treść wiadomości.
Dane wykorzystujemy wyłącznie, aby odpowiedzieć na Twoją wiadomość i prowadzić
dalszą korespondencję.</p>
<ul>
  <li><strong>Podstawa prawna:</strong> Twoja zgoda (art. 6 ust. 1 lit. a RODO),
  wyrażana przez zaznaczenie pola zgody pod formularzem. Zgodę możesz wycofać
  w każdej chwili, pisząc na <a href="mailto:ws@szps.pl">ws@szps.pl</a>;
  wycofanie nie wpływa na zgodność z prawem wcześniejszego przetwarzania.</li>
  <li><strong>Okres przechowywania:</strong>
  {TODO.format("np. do 12 miesięcy od zakończenia korespondencji")}.</li>
</ul>

<h3>Arkusz oceny sędziego</h3>
<p>Wydział udostępnia obserwatorom formularz oceny sędziego. Przetwarzamy
w nim: imię i nazwisko obserwatora i (opcjonalnie) jego adres e-mail,
imię i nazwisko ocenianego sędziego, dane meczu oraz wystawione oceny
i komentarze. Dane służą do oceny i szkolenia sędziów oraz prowadzenia
dokumentacji Wydziału.</p>
<ul>
  <li><strong>Podstawa prawna:</strong> prawnie uzasadniony interes
  administratora (art. 6 ust. 1 lit. f RODO) — realizacja zadań statutowych
  związanych z obsadą, oceną i szkoleniem sędziów
  {TODO.format("potwierdzić podstawę prawną z Zarządem / statutem Związku")}.</li>
  <li><strong>Okres przechowywania:</strong>
  {TODO.format("np. przez okres posiadania uprawnień sędziowskich i 5 lat po ich wygaśnięciu")}.</li>
</ul>

<h3>Logi serwera</h3>
<p>Serwer, na którym działa Strona, automatycznie zapisuje podstawowe
informacje o połączeniach (m.in. adres IP, datę i godzinę, adres
odwiedzanej podstrony, typ przeglądarki). Dane te służą wyłącznie
zapewnieniu bezpieczeństwa i prawidłowego działania Strony (art. 6 ust. 1
lit. f RODO) i nie są łączone z innymi danymi.</p>

<h2>3. Odbiorcy danych</h2>
<p>Dane mogą być przekazywane wyłącznie podmiotom, które świadczą na naszą
rzecz usługi techniczne, w szczególności dostawcy hostingu i poczty
elektronicznej (MyDevil.net), na podstawie umowy powierzenia przetwarzania
danych {TODO.format("potwierdzić zawarcie umowy powierzenia z MyDevil.net")}.
Nie sprzedajemy danych ani nie przekazujemy ich w celach marketingowych.
Nie przekazujemy danych poza Europejski Obszar Gospodarczy
{TODO.format("potwierdzić — np. czy skrzynka ws@szps.pl nie jest przekierowana do usług poza EOG")}.</p>

<h2>4. Pliki cookies i pamięć przeglądarki</h2>
<p>Strona <strong>nie używa</strong> cookies analitycznych, reklamowych ani
narzędzi śledzących (np. Google Analytics, piksel Facebooka). Fonty są
udostępniane z naszego serwera, a nie z serwisów zewnętrznych.</p>
<p>Używamy wyłącznie plików niezbędnych do działania Strony, na które
zgoda nie jest wymagana:</p>
<ul>
  <li><code>csrftoken</code> — zabezpieczenie formularzy przed nadużyciami
  (ważne do 1 roku),</li>
  <li><code>messages</code> — jednorazowe komunikaty po wysłaniu formularza
  (usuwane po wyświetleniu),</li>
  <li><code>sessionid</code> — tylko dla osób logujących się do panelu
  administracyjnego (ważne do 2 tygodni).</li>
</ul>
<p>Arkusz oceny zapisuje wersję roboczą odpowiedzi w pamięci Twojej
przeglądarki (<code>localStorage</code>), aby odświeżenie strony nie
kasowało wpisanych danych. Te informacje nie są wysyłane na serwer, dopóki
sam nie pobierzesz lub nie wyślesz arkusza, i możesz je usunąć przyciskiem
„Wyczyść formularz”.</p>

<h2>5. Linki do serwisów zewnętrznych</h2>
<p>Strona zawiera odnośniki do serwisów zewnętrznych, m.in. Facebooka,
Map Google i systemu obsad <em>system.szps.pl</em>. Po przejściu do nich
obowiązują polityki prywatności ich operatorów. Sama Strona nie ładuje
treści z tych serwisów.</p>

<h2>6. Twoje prawa</h2>
<p>W związku z przetwarzaniem danych masz prawo do:</p>
<ul>
  <li>dostępu do swoich danych i otrzymania ich kopii,</li>
  <li>sprostowania (poprawienia) danych,</li>
  <li>usunięcia danych,</li>
  <li>ograniczenia przetwarzania,</li>
  <li>wniesienia sprzeciwu wobec przetwarzania opartego na prawnie
  uzasadnionym interesie,</li>
  <li>przenoszenia danych przetwarzanych na podstawie zgody,</li>
  <li>wycofania zgody w dowolnym momencie.</li>
</ul>
<p>Aby skorzystać z tych praw, napisz na <a href="mailto:ws@szps.pl">ws@szps.pl</a>.
Przysługuje Ci także prawo wniesienia skargi do Prezesa Urzędu Ochrony Danych
Osobowych (ul. Stawki 2, 00-193 Warszawa, <em>uodo.gov.pl</em>).</p>

<h2>7. Dobrowolność podania danych</h2>
<p>Podanie danych jest dobrowolne, ale niezbędne do wysłania wiadomości przez
formularz kontaktowy lub wypełnienia arkusza oceny. Nie podejmujemy decyzji
w sposób zautomatyzowany ani nie profilujemy użytkowników.</p>

<h2>8. Zmiany polityki</h2>
<p>Polityka może być aktualizowana, np. w razie zmian na Stronie lub
w przepisach. Aktualna wersja jest zawsze dostępna na tej podstronie.</p>
""".strip()


def seed_policy(apps, schema_editor):
    StaticPage = apps.get_model("pages", "StaticPage")
    StaticPage.objects.get_or_create(
        slug=SLUG,
        defaults={
            "title": "Polityka prywatności",
            "body": BODY,
            "is_published": False,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0003_seed_initial_articles"),
    ]

    operations = [
        migrations.RunPython(seed_policy, migrations.RunPython.noop),
    ]

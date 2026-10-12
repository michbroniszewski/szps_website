/* Arkusz ewaluacyjny — wersja robocza w localStorage + podpowiedzi. */
(function(){
  'use strict';

  const form = document.getElementById('evForm');
  if (!form) return;

  // v2: arkusz jednego sędziego (inne nazwy pól niż w pierwszej wersji).
  const KEY = 'szps-arkusz-ewaluacyjny-v2';
  const SKIP = new Set(['csrfmiddlewaretoken', 'action']);

  const read = () => {
    const data = {};
    for (const [name, value] of new FormData(form)) {
      if (!SKIP.has(name)) data[name] = value;
    }
    return data;
  };

  const save = () => {
    try { localStorage.setItem(KEY, JSON.stringify(read())); } catch (e) {}
  };

  const restore = () => {
    let data;
    try { data = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {}
    if (!data) return;
    for (const [name, value] of Object.entries(data)) {
      form.querySelectorAll(`[name="${CSS.escape(name)}"]`).forEach(el => {
        if (el.type === 'radio') el.checked = el.value === value;
        else el.value = value;
      });
    }
  };

  // Ocena inna niż C → komentarz przy tym elemencie jest wymagany.
  const refreshComments = () => {
    form.querySelectorAll('.ev-el').forEach(el => {
      const nonC = el.querySelector('input[name^="g_"]:checked:not([value="C"])');
      el.querySelector('.ev-el__comment').classList.toggle('needed', !!nonC);
    });
  };

  // Pozycja sędziego decyduje, które rozwinięcia „i” są widoczne.
  const refreshPosition = () => {
    const pos = form.querySelector('input[name="position"]:checked');
    if (pos) form.dataset.position = pos.value;
    else delete form.dataset.position;
  };

  const refresh = () => { refreshComments(); refreshPosition(); };

  form.querySelectorAll('.ev-el__info').forEach(btn => {
    btn.addEventListener('click', () => {
      const panel = document.getElementById(btn.getAttribute('aria-controls'));
      const open = btn.getAttribute('aria-expanded') !== 'true';
      btn.setAttribute('aria-expanded', open);
      panel.hidden = !open;
    });
  });

  if (new URLSearchParams(location.search).has('wyslano')) {
    try { localStorage.removeItem(KEY); } catch (e) {}
  }

  // Po błędzie walidacji formularz ma już dane z serwera — nie nadpisujemy.
  if (form.dataset.bound !== '1') restore();
  refresh();

  form.addEventListener('input', () => { save(); refresh(); });
  form.addEventListener('change', () => { save(); refresh(); });

  document.getElementById('evReset').addEventListener('click', () => {
    if (!confirm('Wyczyścić wszystkie odpowiedzi?')) return;
    try { localStorage.removeItem(KEY); } catch (e) {}
    window.location.href = window.location.pathname;
  });

  // Wysyłka: potwierdzenie i blokada przycisku, żeby nie wysłać dwa razy.
  // (Pobranie PDF nie przeładowuje strony, więc tamtego przycisku nie blokujemy.)
  const send = document.getElementById('evSend');
  if (send) {
    form.addEventListener('submit', (e) => {
      if (e.submitter !== send) return;
      if (!confirm('Wysłać arkusz do Wydziału Sędziowskiego?')) { e.preventDefault(); return; }
      // Zablokowany przycisk nie trafia do POST — przekazujemy akcję ukrytym polem.
      const action = document.createElement('input');
      action.type = 'hidden'; action.name = 'action'; action.value = 'email';
      form.appendChild(action);
      setTimeout(() => { send.disabled = true; send.textContent = 'Wysyłanie…'; });
    });
  }

  const errors = document.getElementById('ev-errors');
  if (errors) {
    const first = form.querySelector('.invalid');
    (first || errors).scrollIntoView({block: 'start'});
  }
})();

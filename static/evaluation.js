/* Arkusz ewaluacyjny — wersja robocza w localStorage + podpowiedzi. */
(function(){
  'use strict';

  const form = document.getElementById('evForm');
  if (!form) return;

  const KEY = 'szps-arkusz-ewaluacyjny';
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

  // Ocena inna niż C → pole „Przyczyny” danego sędziego jest wymagane.
  const refreshReasons = () => {
    form.querySelectorAll('[data-referee]').forEach(card => {
      const r = card.dataset.referee;
      const nonC = card.querySelector(`input[name^="${r}_g_"]:checked:not([value="C"])`);
      const reasons = card.querySelector('.ev-reasons');
      if (reasons) reasons.classList.toggle('needed', !!nonC);
    });
  };

  if (new URLSearchParams(location.search).has('wyslano')) {
    try { localStorage.removeItem(KEY); } catch (e) {}
  }

  // Po błędzie walidacji formularz ma już dane z serwera — nie nadpisujemy.
  if (form.dataset.bound !== '1') restore();
  refreshReasons();

  form.addEventListener('input', () => { save(); refreshReasons(); });
  form.addEventListener('change', () => { save(); refreshReasons(); });

  document.getElementById('evReset').addEventListener('click', () => {
    if (!confirm('Wyczyścić wszystkie odpowiedzi?')) return;
    try { localStorage.removeItem(KEY); } catch (e) {}
    window.location.href = window.location.pathname;
  });

  const errors = document.getElementById('ev-errors');
  if (errors) {
    const first = form.querySelector('.invalid');
    (first || errors).scrollIntoView({block: 'start'});
  }
})();

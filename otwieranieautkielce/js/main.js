(function () {
  var b = document.querySelector('.burger'), m = document.getElementById('menu');
  if (b && m) b.addEventListener('click', function () {
    var open = m.classList.toggle('open'); b.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  var q = document.getElementById('szukaj');
  if (q) q.addEventListener('input', function () {
    var v = q.value.trim().toLowerCase(), any = false;
    document.querySelectorAll('.cat-sec').forEach(function (sec) {
      var shown = 0;
      sec.querySelectorAll('.acard').forEach(function (c) {
        var ok = !v || (c.dataset.q + ' ' + c.textContent.toLowerCase()).indexOf(v) >= 0;
        c.hidden = !ok; if (ok) shown++;
      });
      sec.hidden = shown === 0; if (shown) any = true;
    });
    var nr = document.querySelector('.no-results'); if (nr) nr.hidden = any;
  });
  var f = document.getElementById('kontakt-form');
  if (!f) return;
  var via = 'sms';
  f.querySelectorAll('button[name=via]').forEach(function (btn) { btn.addEventListener('click', function () { via = btn.value; }); });
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(f);
    var txt = 'Dzień dobry, ' + d.get('imie') + ' (tel. ' + d.get('tel') + ').\nUsługa: ' + d.get('usluga') +
      (d.get('auto') ? '\nAuto: ' + d.get('auto') : '') + (d.get('gdzie') ? '\nMiejsce: ' + d.get('gdzie') : '') + '\n' + d.get('opis');
    if (via === 'mail' && f.dataset.mail) {
      location.href = 'mailto:' + f.dataset.mail + '?subject=' + encodeURIComponent('Zapytanie: ' + d.get('usluga')) + '&body=' + encodeURIComponent(txt);
    } else {
      location.href = 'sms:' + f.dataset.tel + '?&body=' + encodeURIComponent(txt);
    }
  });
})();

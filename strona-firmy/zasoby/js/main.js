(function () {
  var b = document.querySelector('.burger'), m = document.getElementById('menu');
  if (b && m) b.addEventListener('click', function () {
    var open = m.classList.toggle('open'); b.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  var f = document.getElementById('kontakt-form');
  if (!f) return;
  var via = 'sms';
  f.querySelectorAll('button[name=via]').forEach(function (btn) { btn.addEventListener('click', function () { via = btn.value; }); });
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(f);
    var txt = 'Dzień dobry, ' + d.get('imie') + ' (tel. ' + d.get('tel') + ').\nUsługa: ' + d.get('usluga') +
      (d.get('auto') ? '\nAuto: ' + d.get('auto') : '') + '\n' + d.get('opis');
    if (via === 'mail') {
      var mail = f.dataset.mail;
      if (!mail) { alert('Adres e-mail nie jest jeszcze ustawiony. Wyślij SMS lub zadzwoń.'); return; }
      location.href = 'mailto:' + mail + '?subject=' + encodeURIComponent('Zapytanie: ' + d.get('usluga')) + '&body=' + encodeURIComponent(txt);
    } else {
      location.href = 'sms:' + f.dataset.tel + '?&body=' + encodeURIComponent(txt);
    }
  });
})();

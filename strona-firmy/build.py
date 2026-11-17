# Generator strony. Uzycie: python3 build.py  ->  gotowa strona w folderze public/
# Dane firmy (nazwa, telefon, adres...) wpisz w pliku dane.json i uruchom ponownie.
import json, os, re, html, shutil, datetime, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'public')
D = json.load(open(os.path.join(ROOT, 'dane.json'), encoding='utf-8'))
import tresci as T

def is_ph(v): return isinstance(v, str) and v.strip().startswith('[')
def esc(s): return html.escape(str(s), quote=True)
def val(k):
    v = D.get(k, '')
    return f'<span class="ph" title="Uzupełnij w pliku dane.json">{esc(v)}</span>' if is_ph(v) else esc(v)
def plain(k): return str(D.get(k, ''))

_ic = {}
def icon(name, cls='ico'):
    if name not in _ic:
        s = open(os.path.join(ROOT, 'ikony', name + '.svg'), encoding='utf-8').read()
        inner = re.search(r'<svg[^>]*>(.*)</svg>', s, re.S).group(1).strip()
        _ic[name] = re.sub(r'\s+', ' ', inner)
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_ic[name]}</svg>')

def tokens(s, r):
    rep = {
        '%%NAZWA%%': val('nazwa'), '%%TEL%%': val('telefon'), '%%EMAIL%%': val('email'), '%%MIASTO%%': val('miasto'),
        '%%OBSZAR%%': val('obszar'), '%%KROTKA%%': val('nazwa_krotka') if D.get('nazwa_krotka') else val('nazwa'), '%%PODTYTUL%%': val('podtytul'), '%%ADRES%%': val('adres'), '%%GODZ%%': val('godziny'), '%%NIP%%': val('nip'),
        '%%TELHREF%%': 'tel:' + esc(plain('telefon_link')), '%%SMSHREF%%': 'sms:' + esc(plain('telefon_link')),
        '%%MAILHREF%%': 'mailto:' + ('' if is_ph(plain('email')) else esc(plain('email'))),
        '%%GOOGLE%%': esc(plain('google')), '%%R%%': r, '%%ROK%%': str(datetime.date.today().year),
    }
    for k, v in rep.items(): s = s.replace(k, v)
    for key in ('email', 'nip', 'adres', 'kod'):
        if not str(D.get(key, '')).strip():
            s = re.sub(r'<(\w+)[^>]*data-need="' + key + r'"[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'%%IC:([a-z-]+)%%', lambda m: icon(m.group(1)), s)
    def icx(m):
        icon(m.group(1))
        return (f'<svg x="{m.group(2)}" y="{m.group(3)}" width="{m.group(4)}" height="{m.group(4)}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{m.group(5)}" stroke-linecap="round" stroke-linejoin="round">{_ic[m.group(1)]}</svg>')
    s = re.sub(r'%%ICX:([a-z-]+):([\d.]+):([\d.]+):([\d.]+):([\d.]+)%%', icx, s)
    return s

def strip_tags(s): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()
def plain_tokens(s):  # do tytulow i meta: bez znacznikow
    return strip_tags(tokens(s, ''))

NAV = [('index.html', 'Start'), ('uslugi.html', 'Usługi'), ('poradnik.html', 'Poradnik'), ('kontakt.html', 'Kontakt')]

def local_business():
    d = {'@context': 'https://schema.org', '@type': ['Locksmith', 'AutomotiveBusiness'], 'name': plain('nazwa'),
         'telephone': plain('telefon_link'), 'areaServed': plain('obszar'),
         'description': 'Awaryjne otwieranie samochodów, mieszkań i domów, programowanie kluczy samochodowych, '
                        'naprawa i programowanie sterowników, diagnostyka i czyszczenie filtrów DPF.'}
    if plain('ulica') and not is_ph(plain('ulica')):
        d['address'] = {'@type': 'PostalAddress', 'streetAddress': plain('ulica'), 'addressLocality': plain('miasto'),
                        'addressRegion': 'świętokrzyskie', 'addressCountry': 'PL'}
        if plain('kod'): d['address']['postalCode'] = plain('kod')
    if isinstance(D.get('geo'), list): d['geo'] = {'@type': 'GeoCoordinates', 'latitude': D['geo'][0], 'longitude': D['geo'][1]}
    if 'całą dobę' in plain('godziny').lower():
        d['openingHoursSpecification'] = [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 'opens': '00:00', 'closes': '23:59'}]
    d['hasMap'] = 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(plain('nazwa') + ' ' + plain('adres'))
    if not is_ph(plain('email')): d['email'] = plain('email')
    if not is_ph(plain('domena')): d['url'] = plain('domena').rstrip('/') + '/'
    if plain('google') and not is_ph(plain('google')): d['sameAs'] = [plain('google')]
    return d

def faq_schema(faqs):
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': plain_tokens(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain_tokens(a)}} for q, a in faqs]}

def faq_html(faqs):
    return '<div class="faq">' + ''.join(
        f'<details><summary>{q}<span class="plus" aria-hidden="true"></span></summary><div class="ans">{a}</div></details>' for q, a in faqs) + '</div>'

PAGES = []
def page(path, title, desc, body, schemas=(), active=None, crumbs=None):
    depth = path.count('/'); r = '../' * depth
    canon = '' if is_ph(plain('domena')) else f'<link rel="canonical" href="{esc(plain("domena").rstrip("/"))}/{path}">'
    nav = ''.join(f'<a href="%%R%%{h}"{" aria-current=\"page\"" if active == h else ""}>{t}</a>' for h, t in NAV)
    sch = ''.join('<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False) + '</script>'
                  for s in [local_business(), *schemas])
    bc = ''
    if crumbs:
        bc = '<nav class="crumbs wrap" aria-label="Okruszki"><a href="%%R%%index.html">Start</a>' + ''.join(
            f' <span aria-hidden="true">›</span> <a href="%%R%%{h}">{t}</a>' if h else f' <span aria-hidden="true">›</span> <span>{t}</span>'
            for h, t in crumbs) + '</nav>'
    full_title = plain_tokens(title)
    doc = f'''<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(plain_tokens(desc))}">
<meta name="theme-color" content="#0d1726">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(plain_tokens(desc))}">
<meta property="og:locale" content="pl_PL">
{canon}
<link rel="icon" href="%%R%%favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="%%R%%css/style.css">
{sch}
</head>
<body>
<a class="skip" href="#tresc">Przejdź do treści</a>
<header class="top">
  <div class="wrap top-in">
    <a class="logo" href="%%R%%index.html" aria-label="Strona główna">
      <span class="logo-mark">%%IC:key-round%%</span>
      <span class="logo-txt">%%KROTKA%%<small>%%PODTYTUL%%</small></span>
    </a>
    <nav class="menu" id="menu" aria-label="Menu główne">{nav}</nav>
    <a class="btn btn-call top-call" href="%%TELHREF%%">%%IC:phone%%<span>%%TEL%%</span></a>
    <button class="burger" aria-controls="menu" aria-expanded="false" aria-label="Otwórz menu">%%IC:menu%%</button>
  </div>
</header>
{bc}
<main id="tresc">
{body}
</main>
<footer class="foot">
  <div class="wrap foot-grid">
    <div>
      <p class="foot-name">%%NAZWA%%</p>
      <p>Awaryjne otwieranie aut i mieszkań, programowanie kluczy, sterowniki, filtry DPF.</p>
      <p>%%IC:map-pin%% Działamy: %%OBSZAR%%</p>
      <p>%%IC:clock%% %%GODZ%%</p>
    </div>
    <div>
      <p class="foot-h">Usługi</p>
      <ul>{''.join(f'<li><a href="%%R%%{s["slug"]}.html">{s["short"]}</a></li>' for s in T.USLUGI)}</ul>
    </div>
    <div>
      <p class="foot-h">Poradnik</p>
      <ul>{''.join(f'<li><a href="%%R%%poradnik/{a["slug"]}.html">{a["short"]}</a></li>' for a in T.ARTYKULY[:6])}</ul>
    </div>
    <div>
      <p class="foot-h">Kontakt</p>
      <p><a class="foot-tel" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a></p>
      <p data-need="email"><a href="%%MAILHREF%%">%%IC:mail%% %%EMAIL%%</a></p>
      <p><a href="%%GOOGLE%%" rel="noopener" target="_blank">%%IC:star%% Opinie w Google</a></p>
    </div>
  </div>
  <div class="wrap foot-bottom">
    <span>© %%ROK%% %%NAZWA%%</span>
    <a href="%%R%%polityka-prywatnosci.html">Polityka prywatności</a>
  </div>
</footer>
<div class="callbar">
  <a class="btn btn-call" href="%%TELHREF%%">%%IC:phone%% Zadzwoń teraz</a>
  <a class="btn btn-ghost" href="%%SMSHREF%%">%%IC:message-square%% SMS</a>
</div>
<script src="%%R%%js/main.js" defer></script>
</body>
</html>
'''
    out = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(tokens(doc, r))
    PAGES.append(path)

def cta_band(h='Potrzebujesz pomocy teraz?', p='Zadzwoń – powiemy, ile to potrwa i ile będzie kosztować, zanim wyjedziemy.'):
    return f'''<section class="band"><div class="wrap band-in">
<div><h2>{h}</h2><p>{p}</p></div>
<div class="band-btns"><a class="btn btn-call btn-big" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a>
<a class="btn btn-ghost" href="%%SMSHREF%%">%%IC:message-square%% Wyślij SMS</a></div>
</div></section>'''

def steps_html(steps):
    return '<ol class="steps">' + ''.join(f'<li><span class="num">{i + 1}</span><div><h3>{t}</h3><p>{d}</p></div></li>'
                                         for i, (t, d) in enumerate(steps)) + '</ol>'

def article_card(a, r='%%R%%'):
    return (f'<a class="acard" href="{r}poradnik/{a["slug"]}.html"><span class="acard-ic">%%IC:{a["icon"]}%%</span>'
            f'<span class="acard-cat">{a["cat"]}</span><h3>{a["title"]}</h3><p>{a["lead"]}</p>'
            f'<span class="more">Czytaj {a["min"]} min %%IC:chevron-right%%</span></a>')

def service_card(s):
    return (f'<a class="scard" href="%%R%%{s["slug"]}.html"><span class="scard-ic">%%IC:{s["icon"]}%%</span>'
            f'<h3>{s["short"]}</h3><p>{s["card"]}</p><span class="more">Szczegóły %%IC:chevron-right%%</span></a>')

# ---------------- strony ----------------
def build():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    for sub in ('css', 'js'):
        shutil.copytree(os.path.join(ROOT, 'zasoby', sub), os.path.join(OUT, sub))
    shutil.copy(os.path.join(ROOT, 'zasoby', 'favicon.svg'), OUT)

    # START
    body = f'''
<section class="hero"><div class="wrap hero-in">
  <div class="hero-txt">
    <p class="badge">%%IC:siren%%<span>Pogotowie zamkowe i samochodowe · %%OBSZAR%%</span></p>
    <h1>Zatrzaśnięte drzwi? Zgubione kluczyki? <em>Przyjedziemy i otworzymy.</em></h1>
    <p class="lead">Awaryjne otwieranie samochodów, mieszkań i domów, dorabianie i programowanie kluczyków, naprawa sterowników
    oraz diagnostyka filtrów DPF. Cenę podajemy przez telefon, zanim wyjedziemy.</p>
    <div class="hero-btns"><a class="btn btn-call btn-big" href="%%TELHREF%%">%%IC:phone%% Zadzwoń: %%TEL%%</a>
    <a class="btn btn-ghost" href="#uslugi">Zobacz usługi</a></div>
    <ul class="ticks">
      <li>%%IC:check%% Dojazd do klienta</li><li>%%IC:check%% Cena ustalona przed pracą</li>
      <li>%%IC:check%% Bez zbędnych zniszczeń</li><li>%%IC:check%% Paragon lub faktura</li>
    </ul>
  </div>
  <div class="hero-art" aria-hidden="true">{T.HERO_SVG}</div>
</div></section>

<section class="trust"><div class="wrap trust-grid">
  <div>%%IC:timer%%<h3>Szybki dojazd</h3><p>Ruszamy od razu po rozmowie i mówimy, kiedy będziemy.</p></div>
  <div>%%IC:user-check%%<h3>Weryfikacja właściciela</h3><p>Otwieramy tylko po potwierdzeniu, że masz prawo do auta lub lokalu.</p></div>
  <div>%%IC:shield-check%%<h3>Delikatne metody</h3><p>Specjalistyczne narzędzia zamiast łomu – dbamy o zamek i lakier.</p></div>
  <div>%%IC:receipt-text%%<h3>Uczciwa cena</h3><p>Cenę znasz przed rozpoczęciem pracy. Bez niespodzianek na końcu.</p></div>
</div></section>

<section class="sec" id="uslugi"><div class="wrap">
  <p class="eyebrow">Usługi</p><h2>W czym pomagamy</h2>
  <div class="sgrid">{''.join(service_card(s) for s in T.USLUGI)}</div>
</div></section>

<section class="sec alt"><div class="wrap">
  <p class="eyebrow">Jak działamy</p><h2>Od telefonu do otwartych drzwi</h2>
  {steps_html(T.KROKI_OGOLNE)}
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-head"><div><p class="eyebrow">Poradnik</p><h2>Zanim zadzwonisz – przeczytaj</h2></div>
  <a class="btn btn-line" href="%%R%%poradnik.html">Wszystkie porady %%IC:chevron-right%%</a></div>
  <div class="agrid">{''.join(article_card(a) for a in T.ARTYKULY[:3])}</div>
</div></section>

<section class="sec alt"><div class="wrap narrow">
  <p class="eyebrow">Pytania</p><h2>Najczęstsze pytania</h2>
  {faq_html(T.FAQ_START)}
</div></section>
{cta_band()}
'''
    page('index.html', '%%NAZWA%% – awaryjne otwieranie aut i mieszkań, programowanie kluczy | %%MIASTO%%',
         'Awaryjne otwieranie samochodów, mieszkań i domów, programowanie kluczyków, naprawa sterowników i filtry DPF. %%OBSZAR%%. Zadzwoń: %%TEL%%.',
         body, [faq_schema(T.FAQ_START)], active='index.html')

    # USLUGI (zbiorcza)
    body = f'''<section class="phero"><div class="wrap"><p class="eyebrow">Usługi</p><h1>Nasze usługi</h1>
<p class="lead">Otwieramy, dorabiamy, programujemy i naprawiamy. Wybierz usługę, aby zobaczyć szczegóły, przebieg i odpowiedzi na pytania.</p></div></section>
<section class="sec"><div class="wrap"><div class="sgrid">{''.join(service_card(s) for s in T.USLUGI)}</div></div></section>{cta_band()}'''
    page('uslugi.html', 'Usługi – %%NAZWA%%', 'Awaryjne otwieranie aut i mieszkań, programowanie kluczy, sterowniki, filtry DPF – %%OBSZAR%%.',
         body, active='uslugi.html', crumbs=[(None, 'Usługi')])

    # POSZCZEGOLNE USLUGI
    for s in T.USLUGI:
        rel = [a for a in T.ARTYKULY if a['slug'] in s['related']]
        body = f'''<section class="phero"><div class="wrap phero-in">
<div><p class="eyebrow">%%IC:{s["icon"]}%% Usługa</p><h1>{s["title"]}</h1><p class="lead">{s["lead"]}</p>
<div class="hero-btns"><a class="btn btn-call btn-big" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a>
<a class="btn btn-ghost" href="%%SMSHREF%%">%%IC:message-square%% SMS</a></div></div></div></section>
<section class="sec"><div class="wrap cols">
  <div><h2>W czym pomożemy</h2><ul class="checklist">{''.join(f'<li>%%IC:check%%<span>{i}</span></li>' for i in s["items"])}</ul></div>
  <div><h2>Co przygotować</h2><ul class="checklist doc">{''.join(f'<li>%%IC:user-check%%<span>{i}</span></li>' for i in s["prepare"])}</ul>
  <div class="note">%%IC:circle-alert%%<p>{s["note"]}</p></div></div>
</div></section>
<section class="sec alt"><div class="wrap"><h2>Jak to wygląda</h2>{steps_html(s["steps"])}</div></section>
<section class="sec"><div class="wrap narrow"><h2>Pytania i odpowiedzi</h2>{faq_html(s["faq"])}</div></section>
<section class="sec alt"><div class="wrap"><h2>Przydatne porady</h2><div class="agrid">{''.join(article_card(a) for a in rel)}</div></div></section>
{cta_band()}'''
        page(f'{s["slug"]}.html', f'{s["title"]} – %%MIASTO%% | %%NAZWA%%', s['desc'], body, [faq_schema(s['faq'])],
             active='uslugi.html', crumbs=[('uslugi.html', 'Usługi'), (None, s['short'])])

    # PORADNIK
    cats = []
    for a in T.ARTYKULY:
        if a['cat'] not in cats: cats.append(a['cat'])
    body = f'''<section class="phero"><div class="wrap"><p class="eyebrow">%%IC:book-open%% Poradnik</p><h1>Poradnik: zamki, kluczyki i elektronika auta</h1>
<p class="lead">Praktyczne porady na sytuacje awaryjne i na co dzień: co zrobić, gdy drzwi się zatrzasną, jak nie stracić auta przez keyless,
jak rozpoznać awarię sterownika i jak dbać o filtr DPF.</p>
<div class="chips">{''.join(f'<a class="chip" href="#{T.slugify(c)}">{c}</a>' for c in cats)}</div></div></section>'''
    for c in cats:
        body += (f'<section class="sec" id="{T.slugify(c)}"><div class="wrap"><h2>{c}</h2><div class="agrid">'
                 + ''.join(article_card(a) for a in T.ARTYKULY if a['cat'] == c) + '</div></div></section>')
    body += cta_band('Sytuacja awaryjna?', 'Poradnik poczeka – zadzwoń, a pomożemy od razu.')
    page('poradnik.html', 'Poradnik – otwieranie awaryjne, kluczyki, sterowniki, DPF | %%NAZWA%%',
         'Porady: zatrzaśnięte kluczyki i drzwi, zgubione klucze, kradzież na walizkę, awarie sterowników, filtr DPF.',
         body, active='poradnik.html', crumbs=[(None, 'Poradnik')])

    for i, a in enumerate(T.ARTYKULY):
        others = [x for x in T.ARTYKULY if x['slug'] != a['slug'] and x['cat'] == a['cat']][:2]
        others += [x for x in T.ARTYKULY if x['slug'] != a['slug'] and x not in others][:3 - len(others)]
        srv = next(s for s in T.USLUGI if s['slug'] == a['service'])
        art_schema = {'@context': 'https://schema.org', '@type': 'Article', 'headline': strip_tags(a['title']),
                      'description': strip_tags(a['lead']), 'inLanguage': 'pl', 'author': {'@type': 'Organization', 'name': plain('nazwa')}}
        body = f'''<article class="art">
<header class="phero"><div class="wrap narrow"><p class="eyebrow">%%IC:{a["icon"]}%% {a["cat"]} · {a["min"]} min czytania</p>
<h1>{a["title"]}</h1><p class="lead">{a["lead"]}</p></div></header>
<div class="wrap narrow art-body">
{a["body"]}
<aside class="art-cta"><div><p class="art-cta-h">{srv["title"]}</p><p>Potrzebujesz pomocy na miejscu? Zadzwoń – podamy cenę i czas dojazdu.</p></div>
<div class="band-btns"><a class="btn btn-call" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a><a class="btn btn-line" href="%%R%%{srv["slug"]}.html">O usłudze</a></div></aside>
</div></article>
<section class="sec alt"><div class="wrap"><h2>Czytaj dalej</h2><div class="agrid">{''.join(article_card(x) for x in others)}</div></div></section>'''
        page(f'poradnik/{a["slug"]}.html', f'{a["title"]} | Poradnik %%NAZWA%%', a['lead'], body, [art_schema],
             active='poradnik.html', crumbs=[('poradnik.html', 'Poradnik'), (None, a['short'])])

    # KONTAKT
    adres = plain('adres')
    mapa = ('<div class="map-ph">%%IC:map-pin%%<p>Tu pojawi się mapa po wpisaniu adresu w pliku <code>dane.json</code>.</p></div>' if is_ph(adres) else
            f'<iframe class="map" title="Mapa dojazdu" loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
            f'src="https://www.google.com/maps?q={html.escape(urllib.parse.quote(plain("nazwa") + ", " + adres))}&amp;output=embed"></iframe>')
    body = f'''<section class="phero"><div class="wrap"><p class="eyebrow">%%IC:phone%% Kontakt</p><h1>Kontakt</h1>
<p class="lead">W sytuacji awaryjnej najszybciej będzie telefonicznie. W innych sprawach napisz SMS albo wiadomość – oddzwonimy.</p></div></section>
<section class="sec"><div class="wrap cols">
<div class="contact-card">
  <a class="big-tel" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a>
  <ul class="clist">
    <li>%%IC:message-square%%<span><a href="%%SMSHREF%%">Wyślij SMS</a></span></li>
    <li data-need="email">%%IC:mail%%<span><a href="%%MAILHREF%%">%%EMAIL%%</a></span></li>
    <li>%%IC:map-pin%%<span>%%ADRES%%<br><small>Obszar działania: %%OBSZAR%%</small></span></li>
    <li>%%IC:clock%%<span>%%GODZ%%</span></li>
    <li>%%IC:star%%<span><a href="%%GOOGLE%%" target="_blank" rel="noopener">Nasza wizytówka i opinie w Google</a></span></li>
    <li data-need="nip">%%IC:receipt-text%%<span>NIP: %%NIP%%</span></li>
  </ul>
  {mapa}
</div>
<div>
  <h2>Napisz do nas</h2>
  <p class="muted">Formularz przygotuje wiadomość w Twojej aplikacji SMS lub poczcie – nic nie jest wysyłane na serwer.</p>
  <form class="form" id="kontakt-form" data-tel="{esc(plain('telefon_link'))}" data-mail="{'' if is_ph(plain('email')) else esc(plain('email'))}">
    <label>Imię<input name="imie" autocomplete="given-name" required></label>
    <label>Telefon do kontaktu<input name="tel" type="tel" autocomplete="tel" required></label>
    <label>Usługa<select name="usluga">{''.join(f'<option>{s["short"]}</option>' for s in T.USLUGI)}<option>Inne</option></select></label>
    <label>Marka, model i rok auta (jeśli dotyczy)<input name="auto"></label>
    <label>Opis sytuacji<textarea name="opis" rows="4" required></textarea></label>
    <div class="form-btns"><button class="btn btn-call" type="submit" name="via" value="sms">%%IC:message-square%% Wyślij SMS</button>
    <button data-need="email" class="btn btn-line" type="submit" name="via" value="mail">%%IC:mail%% Wyślij e-mail</button></div>
  </form>
</div>
</div></section>'''
    page('kontakt.html', 'Kontakt – %%NAZWA%% | %%MIASTO%%', 'Zadzwoń: %%TEL%%. Awaryjne otwieranie, programowanie kluczy, sterowniki. %%OBSZAR%%.',
         body, active='kontakt.html', crumbs=[(None, 'Kontakt')])

    # POLITYKA, 404
    page('polityka-prywatnosci.html', 'Polityka prywatności – %%NAZWA%%', 'Zasady przetwarzania danych na stronie %%NAZWA%%.',
         f'<section class="phero"><div class="wrap narrow"><h1>Polityka prywatności</h1></div></section><div class="wrap narrow art-body">{T.POLITYKA}</div>',
         crumbs=[(None, 'Polityka prywatności')])
    page('404.html', 'Nie znaleziono strony – %%NAZWA%%', 'Strona nie istnieje.',
         '<section class="phero"><div class="wrap narrow"><h1>Ups, tej strony nie ma</h1><p class="lead">Ale drzwi otworzymy. Wróć na '
         '<a href="%%R%%index.html">stronę główną</a> albo zadzwoń: <a href="%%TELHREF%%">%%TEL%%</a>.</p></div></section>')

    # sitemap, robots
    dom = plain('domena').strip('[]').rstrip('/')
    today = datetime.date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{dom}/{"" if p == "index.html" else p}</loc><lastmod>{today}</lastmod></url>\n' for p in PAGES if p != '404.html') + '</urlset>\n'
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(sm)
    open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {dom}/sitemap.xml\n')
    todo = [k for k, v in D.items() if is_ph(v)]
    print(f'Gotowe: {len(PAGES)} stron w folderze public/.')
    if todo: print('Do uzupełnienia w dane.json:', ', '.join(todo))
    if is_ph(plain('domena')) or 'twoja-domena' in dom: print('Uwaga: wpisz adres domeny (pole "domena"), żeby sitemap.xml miała poprawne adresy.')

if __name__ == '__main__':
    build()

# Generator strony. Uzycie: python3 build.py  ->  gotowa strona w folderze public/
# Dane firmy (nazwa, telefon, adres...) wpisz w pliku dane.json i uruchom ponownie.
import json, os, re, html, shutil, datetime, urllib.parse

import sys
ROOT = os.path.dirname(os.path.abspath(__file__))
PODGLAD = '--podglad' in sys.argv  # wersja do akceptacji: noindex
OUT = sys.argv[sys.argv.index('--podglad') + 1] if PODGLAD else os.path.join(ROOT, 'public')
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


# ---------------- tresci z plikow JSON (tresci/*) ----------------
def _load_dir(sub):
    d = os.path.join(ROOT, 'tresci', sub); out = []
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith('.json'):
                try: out.append(json.load(open(os.path.join(d, f), encoding='utf-8')))
                except Exception as e: print('BŁĄD w pliku', sub + '/' + f, e)
    return out

def _merge(defaults, extra):
    by = {x['slug']: dict(x) for x in defaults}
    for x in extra: by[x['slug']] = {**by.get(x['slug'], {}), **x}
    items = list(by.values())
    items.sort(key=lambda x: (x.get('order', 500), x['slug']))
    return items

_REG = json.load(open(os.path.join(ROOT, 'zasoby', 'img', 'rejestr.json'), encoding='utf-8')) if os.path.exists(os.path.join(ROOT, 'zasoby', 'img', 'rejestr.json')) else {}
def _img(kind, items):
    for x in items:
        if 'image' not in x and f"{kind}/{x['slug']}" in _REG: x['image'] = _REG[f"{kind}/{x['slug']}"]
    return items
SERV = _img('uslugi', _merge(T.USLUGI, _load_dir('uslugi')))
ARTS = _img('poradnik', _merge(T.ARTYKULY, _load_dir('poradnik')))
TOWNS = sorted(_load_dir('miejscowosci'), key=lambda x: (x.get('order', 500), x['slug']))
STRONY = {x['slug']: x for x in _load_dir('strony')}
MARKI = sorted(_load_dir('marki'), key=lambda x: (x.get('order', 500), x['slug']))
HOME = STRONY.get('index', {})
AREA = STRONY.get('obszar-dzialania')
for s in SERV:
    s.setdefault('meta_title', s['title'] + ' – %%MIASTO%%'); s.setdefault('meta_description', s.get('desc', s['lead']))
    s.setdefault('sections', []); s.setdefault('related', [])
for a in ARTS:
    a.setdefault('meta_title', a['title']); a.setdefault('meta_description', a['lead']); a.setdefault('faq', [])
    a['min'] = max(2, round(len(strip_tags(a['body']).split()) / 200))
SLUG_A = {a['slug'] for a in ARTS}

def boxes(h):  # ramki porad: tip / warn / note z ikona
    ic = {'tip': 'lightbulb', 'warn': 'triangle-alert', 'note': 'circle-alert'}
    def rep(m):
        inner = m.group(2)
        if inner.lstrip().startswith('%%IC:') or inner.lstrip().startswith('<svg'): return m.group(0)
        return f'<div class="{m.group(1)}">%%IC:{ic[m.group(1)]}%%<div>{inner}</div></div>'
    return re.sub(r'<div class="(tip|warn|note)">(.*?)</div>', rep, h, flags=re.S)

def with_toc(body):
    heads = []
    def rep(m):
        t = strip_tags(m.group(1)); hid = T.slugify(t)[:60] or f'sekcja-{len(heads)+1}'
        heads.append((hid, t)); return f'<h2 id="{hid}">{m.group(1)}</h2>'
    body = re.sub(r'<h2>(.*?)</h2>', rep, body)
    toc = ''
    if len(heads) >= 3:
        toc = ('<nav class="toc" aria-label="Spis treści"><p class="toc-h">Spis treści</p><ol>'
               + ''.join(f'<li><a href="#{h}">{esc(t)}</a></li>' for h, t in heads) + '</ol></nav>')
    return toc, body

def sections_html(sections):
    return ''.join(f'<section class="sec{" alt" if i % 2 else ""}"><div class="wrap narrow prose"><h2>{x["h2"]}</h2>{boxes(x["html"])}</div></section>'
                   for i, x in enumerate(sections))

def breadcrumb_schema(path, crumbs):
    dom = plain('domena').strip('[]').rstrip('/')
    items = [{'@type': 'ListItem', 'position': 1, 'name': 'Start', 'item': dom + '/'}]
    for i, (h, t) in enumerate(crumbs):
        it = {'@type': 'ListItem', 'position': i + 2, 'name': strip_tags(t)}
        it['item'] = dom + '/' + (h or path)
        items.append(it)
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': items}

PAGES = []; META = []
def page(path, title, desc, body, schemas=(), active=None, crumbs=None, image=None):
    depth = path.count('/'); r = '../' * depth
    canon = '' if is_ph(plain('domena')) else f'<link rel="canonical" href="{esc(plain("domena").rstrip("/"))}/{"" if path == "index.html" else path}">'
    nav = ''.join(f'<a href="%%R%%{h}"{" aria-current=\"page\"" if active == h else ""}>{t}</a>' for h, t in NAV)
    schemas = list(schemas)
    if crumbs: schemas.append(breadcrumb_schema(path, crumbs))
    sch = ''.join('<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False) + '</script>'
                  for s in [local_business(), *schemas])
    bc = ''
    if crumbs:
        bc = '<nav class="crumbs wrap" aria-label="Okruszki"><a href="%%R%%index.html">Start</a>' + ''.join(
            f' <span aria-hidden="true">›</span> <a href="%%R%%{h}">{t}</a>' if h else f' <span aria-hidden="true">›</span> <span>{t}</span>'
            for h, t in crumbs) + '</nav>'
    full_title = plain_tokens(title); full_desc = plain_tokens(desc)
    META.append((path, full_title, full_desc))
    area_links = ''.join(f'<li><a href="%%R%%{t["slug"]}.html">{t["name"]}</a></li>' for t in TOWNS[:10])
    if AREA: area_links += '<li><a href="%%R%%obszar-dzialania.html">Cały obszar działania</a></li>'
    doc = f'''<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(full_desc)}">
<meta name="theme-color" content="#0d1726">
{'<meta name="robots" content="noindex, nofollow">' if PODGLAD else ''}
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(full_desc)}">
<meta property="og:locale" content="pl_PL">
{f'<meta property="og:image" content="{esc(plain("domena").rstrip("/"))}/{image}">' if image and not is_ph(plain("domena")) else ''}
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
      <p>%%IC:map-pin%% %%ADRES%%</p>
      <p>%%IC:clock%% %%GODZ%%</p>
      <p><a class="foot-tel" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a></p>
      <p data-need="email"><a href="%%MAILHREF%%">%%IC:mail%% %%EMAIL%%</a></p>
      <p><a href="%%GOOGLE%%" rel="noopener" target="_blank">%%IC:star%% Opinie w Google</a></p>
      {'<p><a href="%%R%%o-nas.html">%%IC:user-check%% O nas</a></p>' if 'o-nas' in STRONY else ''}
    </div>
    <div>
      <p class="foot-h">Usługi</p>
      <ul>{''.join(f'<li><a href="%%R%%{s["slug"]}.html">{s["short"]}</a></li>' for s in SERV)}{'<li><a href="%%R%%marki.html">Kluczyki do marek ›</a></li>' if MARKI else ''}</ul>
    </div>
    <div>
      <p class="foot-h">Kielce i okolice</p>
      <ul>{area_links or '<li>%%OBSZAR%%</li>'}</ul>
    </div>
    <div>
      <p class="foot-h">Poradnik</p>
      <ul>{''.join(f'<li><a href="%%R%%poradnik/{a["slug"]}.html">{a["short"]}</a></li>' for a in ARTS[:8])}
      <li><a href="%%R%%poradnik.html">Wszystkie porady ›</a></li></ul>
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

def article_card(a):
    return (f'<a class="acard" href="%%R%%poradnik/{a["slug"]}.html" data-q="{esc((strip_tags(a["title"]) + " " + a.get("cat", "") + " " + " ".join(a.get("keywords", []))).lower())}">'
            + (f'<span class="acard-img"><img src="%%R%%{a["image"]["thumb"]}" alt="" width="480" height="270" loading="lazy" decoding="async"></span>' if a.get('image') else f'<span class="acard-ic">%%IC:{a.get("icon", "book-open")}%%</span>') +
            f''
            f'<span class="acard-cat">{a["cat"]}</span><h3>{a["title"]}</h3><p>{a["lead"]}</p>'
            f'<span class="more">Czytaj · {a["min"]} min %%IC:chevron-right%%</span></a>')

def service_card(s):
    top = (f'<span class="acard-img"><img src="%%R%%{s["image"]["thumb"]}" alt="" width="480" height="270" loading="lazy" decoding="async"></span>' if s.get('image') else '')
    return (f'<a class="scard" href="%%R%%{s["slug"]}.html">{top}<span class="scard-ic">%%IC:{s["icon"]}%%</span>'
            f'<h3>{s["short"]}</h3><p>{s["card"]}</p><span class="more">Szczegóły %%IC:chevron-right%%</span></a>')

def brand_chips(exclude=None):
    if not MARKI: return ''
    return '<div class="town-chips">' + ''.join(f'<a class="tchip" href="%%R%%{m["slug"]}.html">%%IC:key-round%% {m["brand"]}</a>' for m in MARKI if m['slug'] != exclude) + \
           '<a class="tchip all" href="%%R%%marki.html">Wszystkie marki ›</a></div>'

def town_chips():
    if not TOWNS: return ''
    return '<div class="town-chips">' + ''.join(f'<a class="tchip" href="%%R%%{t["slug"]}.html">%%IC:map-pin%% {t["name"]}</a>' for t in TOWNS) + \
           ('<a class="tchip all" href="%%R%%obszar-dzialania.html">Cały obszar ›</a>' if AREA else '') + '</div>'

# ---------------- strony ----------------
def build():
    global NAV
    NAV = [('index.html', 'Start'), ('uslugi.html', 'Usługi')] + ([('obszar-dzialania.html', 'Kielce i okolice')] if AREA else []) + \
          [('poradnik.html', 'Poradnik')] + ([('o-nas.html', 'O nas')] if 'o-nas' in STRONY else []) + [('kontakt.html', 'Kontakt')]
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    for sub in ('css', 'js'):
        shutil.copytree(os.path.join(ROOT, 'zasoby', sub), os.path.join(OUT, sub))
    shutil.copy(os.path.join(ROOT, 'zasoby', 'favicon.svg'), OUT)
    if os.path.isdir(os.path.join(ROOT, 'zasoby', 'img')): shutil.copytree(os.path.join(ROOT, 'zasoby', 'img'), os.path.join(OUT, 'img'), ignore=shutil.ignore_patterns('rejestr.json'))
    shutil.copy(os.path.join(ROOT, 'zasoby', '.htaccess'), OUT)

    # START
    H = HOME
    hero_h1 = H.get('hero_h1', 'Zatrzaśnięte drzwi? Zgubione kluczyki? <em>Przyjedziemy i otworzymy.</em>')
    hero_lead = H.get('hero_lead', 'Awaryjne otwieranie samochodów, mieszkań i domów, dorabianie i programowanie kluczyków, naprawa sterowników oraz diagnostyka filtrów DPF. Cenę podajemy przez telefon, zanim wyjedziemy.')
    faq_start = H.get('faq', T.FAQ_START)
    featured = [a for a in ARTS if a.get('featured')] or ARTS
    area_block = ''
    if TOWNS or H.get('area_html'):
        area_block = f'''<section class="sec"><div class="wrap">
  <p class="eyebrow">%%IC:map-pin%% Obszar działania</p><h2>{H.get('area_h2', 'Kielce i okolice')}</h2>
  <div class="prose wide">{H.get('area_html', '')}</div>{town_chips()}
</div></section>'''
    body = f'''
<section class="hero"><div class="wrap hero-in">
  <div class="hero-txt">
    <p class="badge">%%IC:siren%%<span>{H.get('badge', 'Pogotowie zamkowe i samochodowe 24h · %%OBSZAR%%')}</span></p>
    <h1>{hero_h1}</h1>
    <p class="lead">{hero_lead}</p>
    <div class="hero-btns"><a class="btn btn-call btn-big" href="%%TELHREF%%">%%IC:phone%% Zadzwoń: %%TEL%%</a>
    <a class="btn btn-ghost" href="#uslugi">Zobacz usługi</a></div>
    <ul class="ticks">{''.join(f'<li>%%IC:check%% {x}</li>' for x in H.get('ticks', ['Czynne całą dobę', 'Cena ustalona przed pracą', 'Dojazd do klienta', 'Paragon lub faktura']))}</ul>
  </div>
  <div class="hero-art" aria-hidden="true">{T.HERO_SVG}</div>
</div></section>

<section class="trust"><div class="wrap trust-grid">
  <div>%%IC:timer%%<h3>Całą dobę</h3><p>Działamy 24 godziny na dobę, 7 dni w tygodniu – także w nocy i w święta.</p></div>
  <div>%%IC:user-check%%<h3>Weryfikacja właściciela</h3><p>Otwieramy tylko po potwierdzeniu, że masz prawo do auta lub lokalu.</p></div>
  <div>%%IC:shield-check%%<h3>Delikatne metody</h3><p>Specjalistyczne narzędzia zamiast łomu – dbamy o zamek i lakier.</p></div>
  <div>%%IC:receipt-text%%<h3>Uczciwa cena</h3><p>Cenę znasz przed rozpoczęciem pracy. Bez niespodzianek na końcu.</p></div>
</div></section>

<section class="sec" id="uslugi"><div class="wrap">
  <p class="eyebrow">Usługi</p><h2>{H.get('services_h2', 'W czym pomagamy')}</h2>
  <div class="sgrid">{''.join(service_card(s) for s in SERV)}</div>
</div></section>

{f'<section class="sec"><div class="wrap"><p class="eyebrow">%%IC:key-round%% Marki</p><h2>{H.get("brands_h2", "Kluczyki do popularnych marek")}</h2><p class="lead">{H.get("brands_lead", "Dorabiamy i kodujemy kluczyki do aut wielu popularnych marek. Wybierz swoją markę – opisaliśmy typowe kluczyki i problemy.")}</p>{brand_chips()}</div></section>' if MARKI else ''}
<section class="sec alt"><div class="wrap">
  <p class="eyebrow">Jak działamy</p><h2>Od telefonu do otwartych drzwi</h2>
  {steps_html(T.KROKI_OGOLNE)}
</div></section>
{area_block}
{f'<section class="sec about"><div class="wrap about-in"><div class="about-ic">%%IC:user-check%%</div><div class="prose wide"><p class="eyebrow">Kim jestem</p>{H["about_html"]}' + ('<p><a class="btn btn-line" href="%%R%%o-nas.html">Więcej o mnie i o tym, jak pracuję %%IC:chevron-right%%</a></p>' if 'o-nas' in STRONY else '') + '</div></div></section>' if H.get('about_html') else ''}
<section class="sec alt"><div class="wrap">
  <div class="sec-head"><div><p class="eyebrow">Poradnik</p><h2>Zanim zadzwonisz – przeczytaj</h2></div>
  <a class="btn btn-line" href="%%R%%poradnik.html">Wszystkie porady ({len(ARTS)}) %%IC:chevron-right%%</a></div>
  <div class="agrid">{''.join(article_card(a) for a in featured[:6])}</div>
</div></section>
{sections_html(H.get('sections', []))}
<section class="sec alt"><div class="wrap narrow">
  <p class="eyebrow">Pytania</p><h2>Najczęstsze pytania</h2>
  {faq_html(faq_start)}
</div></section>
{cta_band()}
'''
    page('index.html', H.get('meta_title', '%%NAZWA%% | %%MIASTO%%'),
         H.get('meta_description', 'Awaryjne otwieranie samochodów, mieszkań i domów, programowanie kluczyków – %%OBSZAR%%. Tel. %%TEL%%.'),
         body, [faq_schema(faq_start)], active='index.html')

    # USLUGI (zbiorcza)
    U = STRONY.get('uslugi', {})
    body = f'''<section class="phero"><div class="wrap"><p class="eyebrow">Usługi</p><h1>{U.get('h1', 'Nasze usługi')}</h1>
<p class="lead">{U.get('lead', 'Otwieramy, dorabiamy, programujemy i naprawiamy. Wybierz usługę, aby zobaczyć szczegóły.')}</p></div></section>
<section class="sec"><div class="wrap"><div class="sgrid">{''.join(service_card(s) for s in SERV)}</div></div></section>
{sections_html(U.get('sections', []))}{cta_band()}'''
    page('uslugi.html', U.get('meta_title', 'Usługi – %%NAZWA%%'), U.get('meta_description', 'Usługi: otwieranie aut i mieszkań, programowanie kluczy, sterowniki, DPF – %%OBSZAR%%.'),
         body, active='uslugi.html', crumbs=[(None, 'Usługi')])

    # POSZCZEGOLNE USLUGI
    for s in SERV:
        rel = [a for a in ARTS if a['slug'] in s['related']] or [a for a in ARTS if a.get('service') == s['slug']][:3]
        others = [a for a in ARTS if a.get('service') == s['slug'] and a not in rel]
        body = f'''<section class="phero"><div class="wrap phero-in">
<div><p class="eyebrow">%%IC:{s["icon"]}%% Usługa · %%MIASTO%% i okolice</p><h1>{s["title"]}</h1><p class="lead">{s["lead"]}</p>
<div class="hero-btns"><a class="btn btn-call btn-big" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a>
<a class="btn btn-ghost" href="%%SMSHREF%%">%%IC:message-square%% SMS</a></div></div>
{f'<figure class="phero-img"><img src="%%R%%{s["image"]["src"]}" alt="{esc(s["image"]["alt"])}" width="1200" height="675" fetchpriority="high"></figure>' if s.get('image') else ''}</div></section>
<section class="sec"><div class="wrap cols">
  <div><h2>W czym pomożemy</h2><ul class="checklist">{''.join(f'<li>%%IC:check%%<span>{i}</span></li>' for i in s["items"])}</ul></div>
  <div><h2>Co przygotować</h2><ul class="checklist doc">{''.join(f'<li>%%IC:user-check%%<span>{i}</span></li>' for i in s["prepare"])}</ul>
  <div class="note">%%IC:circle-alert%%<p>{s["note"]}</p></div></div>
</div></section>
<section class="sec alt"><div class="wrap"><h2>Jak to wygląda</h2>{steps_html(s["steps"])}</div></section>
{sections_html(s["sections"])}
<section class="sec"><div class="wrap narrow"><h2>Pytania i odpowiedzi</h2>{faq_html(s["faq"])}</div></section>
{f'<section class="sec"><div class="wrap"><h2>Kluczyki do popularnych marek</h2>{brand_chips()}</div></section>' if MARKI and s['slug'] in ('programowanie-kluczy', 'utrata-wszystkich-kluczykow', 'otwieranie-samochodow', 'sterowniki') else ''}
{f'<section class="sec alt"><div class="wrap"><h2>Działamy w Kielcach i okolicach</h2>{town_chips()}</div></section>' if TOWNS else ''}
<section class="sec"><div class="wrap"><h2>Przydatne porady</h2><div class="agrid">{''.join(article_card(a) for a in (rel + others)[:6])}</div></div></section>
{cta_band()}'''
        page(f'{s["slug"]}.html', s['meta_title'], s['meta_description'], body, [faq_schema(s['faq'])], image=(s.get('image') or {}).get('src'),
             active='uslugi.html', crumbs=[('uslugi.html', 'Usługi'), (None, s['short'])])

    # OBSZAR DZIALANIA + MIEJSCOWOSCI
    if AREA:
        body = f'''<section class="phero"><div class="wrap"><p class="eyebrow">%%IC:map-pin%% Obszar działania</p><h1>{AREA['h1']}</h1>
<p class="lead">{AREA['lead']}</p>{town_chips()}</div></section>
{sections_html(AREA.get('sections', []))}
{f'<section class="sec"><div class="wrap narrow"><h2>Pytania i odpowiedzi</h2>{faq_html(AREA["faq"])}</div></section>' if AREA.get('faq') else ''}
{cta_band()}'''
        page('obszar-dzialania.html', AREA['meta_title'], AREA['meta_description'], body,
             [faq_schema(AREA['faq'])] if AREA.get('faq') else [], active='obszar-dzialania.html', crumbs=[(None, 'Kielce i okolice')])
    for t in TOWNS:
        body = f'''<section class="phero"><div class="wrap phero-in"><div><p class="eyebrow">%%IC:map-pin%% {t["name"]}</p><h1>{t["h1"]}</h1>
<p class="lead">{t["lead"]}</p>
<div class="hero-btns"><a class="btn btn-call btn-big" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a>
<a class="btn btn-ghost" href="%%SMSHREF%%">%%IC:message-square%% SMS</a></div></div></div></section>
{sections_html(t.get('sections', []))}
<section class="sec"><div class="wrap"><h2>Usługi w miejscowości {t["name"]}</h2><div class="sgrid">{''.join(service_card(s) for s in SERV)}</div></div></section>
{f'<section class="sec alt"><div class="wrap narrow"><h2>Pytania i odpowiedzi</h2>{faq_html(t["faq"])}</div></section>' if t.get('faq') else ''}
<section class="sec"><div class="wrap"><h2>Inne miejscowości</h2>{town_chips()}</div></section>
{cta_band()}'''
        page(f'{t["slug"]}.html', t['meta_title'], t['meta_description'], body,
             [faq_schema(t['faq'])] if t.get('faq') else [], active='obszar-dzialania.html',
             crumbs=[('obszar-dzialania.html', 'Kielce i okolice') if AREA else (None, 'Obszar'), (None, t['name'])])

    # MARKI
    if MARKI:
        M = STRONY.get('marki', {})
        cards = ''.join(f'<a class="scard" href="%%R%%{m["slug"]}.html"><span class="scard-ic">%%IC:key-round%%</span><h3>{m["brand"]}</h3><p>{m.get("card", "")}</p><span class="more">Szczegóły %%IC:chevron-right%%</span></a>' for m in MARKI)
        body = f'''<section class="phero"><div class="wrap"><p class="eyebrow">%%IC:key-round%% Marki</p><h1>{M.get('h1', 'Kluczyki samochodowe do popularnych marek – Kielce')}</h1>
<p class="lead">{M.get('lead', 'Dorabianie i kodowanie kluczyków, utrata wszystkich kluczyków i awaryjne otwieranie aut wielu marek. Możliwość wykonania kluczyka sprawdzamy po numerze VIN.')}</p></div></section>
<section class="sec"><div class="wrap"><div class="sgrid">{cards}</div></div></section>
{sections_html(M.get('sections', []))}
<section class="sec"><div class="wrap narrow"><p class="muted small">Nazwy marek służą wyłącznie do opisu, do jakich aut wykonujemy usługi. Nie jesteśmy autoryzowanym serwisem żadnej z tych marek.</p></div></section>
{cta_band()}'''
        page('marki.html', M.get('meta_title', 'Kluczyki samochodowe do popularnych marek – Kielce'),
             M.get('meta_description', 'Dorabianie i kodowanie kluczyków do aut popularnych marek: Toyota, BMW, Volkswagen, Skoda i inne. Kielce i okolice, całą dobę.'),
             body, active='uslugi.html', crumbs=[('uslugi.html', 'Usługi'), (None, 'Marki')])
        key_serv = [s for s in SERV if s['slug'] in ('programowanie-kluczy', 'utrata-wszystkich-kluczykow', 'otwieranie-samochodow', 'sterowniki', 'kodowanie-ford-mazda')]
        for m in MARKI:
            sv = [s for s in key_serv if s['slug'] != 'kodowanie-ford-mazda' or m['slug'] in ('kluczyki-ford', 'kluczyki-mazda')]
            rel = [a for a in ARTS if a['slug'] in m.get('related', [])]
            body = f'''<section class="phero"><div class="wrap phero-in"><div><p class="eyebrow">%%IC:key-round%% {m["brand"]} · %%MIASTO%% i okolice</p><h1>{m["h1"]}</h1>
<p class="lead">{m["lead"]}</p>
<div class="hero-btns"><a class="btn btn-call btn-big" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a>
<a class="btn btn-ghost" href="%%SMSHREF%%">%%IC:message-square%% SMS</a></div></div></div></section>
{sections_html(m.get('sections', []))}
<section class="sec"><div class="wrap"><h2>Usługi dla aut {m["brand"]}</h2><div class="sgrid">{''.join(service_card(s) for s in sv)}</div></div></section>
{f'<section class="sec alt"><div class="wrap narrow"><h2>Pytania i odpowiedzi</h2>{faq_html(m["faq"])}</div></section>' if m.get('faq') else ''}
{f'<section class="sec"><div class="wrap"><h2>Przydatne porady</h2><div class="agrid">{"".join(article_card(a) for a in rel[:3])}</div></div></section>' if rel else ''}
<section class="sec alt"><div class="wrap"><h2>Inne marki</h2>{brand_chips(m['slug'])}
<p class="muted small">Nazwa marki {m["brand"]} służy wyłącznie do opisu, do jakich aut wykonujemy usługi. Nie jesteśmy autoryzowanym serwisem tej marki.</p></div></section>
{cta_band()}'''
            page(f'{m["slug"]}.html', m['meta_title'], m['meta_description'], body, [faq_schema(m['faq'])] if m.get('faq') else [],
                 active='uslugi.html', crumbs=[('uslugi.html', 'Usługi'), ('marki.html', 'Marki'), (None, m['brand'])])

    # STRONY OGOLNE (o-nas, cennik i inne z tresci/strony)
    for slug, G in STRONY.items():
        if slug in ('index', 'uslugi', 'poradnik', 'obszar-dzialania', 'marki'): continue
        body = f'''<section class="phero"><div class="wrap"><p class="eyebrow">{G.get('eyebrow', '')}</p><h1>{G['h1']}</h1><p class="lead">{G['lead']}</p>
<div class="hero-btns"><a class="btn btn-call btn-big" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a></div></div></section>
{sections_html(G.get('sections', []))}
{f'<section class="sec"><div class="wrap narrow"><h2>Pytania i odpowiedzi</h2>{faq_html(G["faq"])}</div></section>' if G.get('faq') else ''}
{cta_band()}'''
        page(f'{slug}.html', G['meta_title'], G['meta_description'], body, [faq_schema(G['faq'])] if G.get('faq') else [],
             active=f'{slug}.html', crumbs=[(None, G.get('crumb', strip_tags(G['h1'])[:40]))])

    # PORADNIK
    cats = []
    for a in ARTS:
        if a['cat'] not in cats: cats.append(a['cat'])
    P = STRONY.get('poradnik', {})
    body = f'''<section class="phero"><div class="wrap"><p class="eyebrow">%%IC:book-open%% Poradnik · {len(ARTS)} porad</p><h1>{P.get('h1', 'Poradnik: zamki, kluczyki i elektronika auta')}</h1>
<p class="lead">{P.get('lead', 'Praktyczne porady na sytuacje awaryjne i na co dzień.')}</p>
<label class="search">%%IC:book-open%%<input id="szukaj" type="search" placeholder="Szukaj w poradniku, np. zgubione kluczyki" aria-label="Szukaj w poradniku"></label>
<div class="chips">{''.join(f'<a class="chip" href="#{T.slugify(c)}">{c}</a>' for c in cats)}</div></div></section>'''
    for c in cats:
        body += (f'<section class="sec cat-sec" id="{T.slugify(c)}"><div class="wrap"><h2>{c}</h2><div class="agrid">'
                 + ''.join(article_card(a) for a in ARTS if a['cat'] == c) + '</div></div></section>')
    body += '<p class="wrap no-results" hidden>Brak porad pasujących do wyszukiwania. Zadzwoń – doradzimy przez telefon.</p>'
    body += sections_html(P.get('sections', []))
    body += cta_band('Sytuacja awaryjna?', 'Poradnik poczeka – zadzwoń, a pomożemy od razu.')
    page('poradnik.html', P.get('meta_title', 'Poradnik – otwieranie awaryjne, kluczyki, sterowniki | %%MIASTO%%'),
         P.get('meta_description', 'Porady: zatrzaśnięte kluczyki i drzwi, zgubione klucze, kradzież na walizkę, awarie sterowników, filtr DPF.'),
         body, active='poradnik.html', crumbs=[(None, 'Poradnik')])

    for a in ARTS:
        rel = [x for x in ARTS if x['slug'] in a.get('related', []) and x['slug'] != a['slug']]
        rel += [x for x in ARTS if x['slug'] != a['slug'] and x['cat'] == a['cat'] and x not in rel]
        rel += [x for x in ARTS if x['slug'] != a['slug'] and x not in rel]
        srv = next((s for s in SERV if s['slug'] == a.get('service')), SERV[0])
        toc, body_html = with_toc(boxes(a['body']))
        art_schema = {'@context': 'https://schema.org', '@type': 'Article', 'headline': strip_tags(a['title']),
                      'description': strip_tags(a['lead']), 'inLanguage': 'pl', 'author': {'@type': 'Organization', 'name': plain('nazwa')},
                      'publisher': {'@type': 'Organization', 'name': plain('nazwa')}}
        if a.get('date'): art_schema['datePublished'] = a['date']
        if a.get('image') and not is_ph(plain('domena')): art_schema['image'] = plain('domena').rstrip('/') + '/' + a['image']['src']
        faq_part = f'<h2 id="pytania">Pytania i odpowiedzi</h2>{faq_html(a["faq"])}' if a['faq'] else ''
        body = f'''<article class="art">
<header class="phero"><div class="wrap narrow"><p class="eyebrow">%%IC:{a.get("icon", "book-open")}%% {a["cat"]} · {a["min"]} min czytania</p>
<h1>{a["title"]}</h1><p class="lead">{a["lead"]}</p></div></header>
<div class="wrap narrow art-body prose">
{f'<figure class="art-img"><img src="%%R%%{a["image"]["src"]}" alt="{esc(a["image"]["alt"])}" width="1200" height="675" fetchpriority="high"></figure>' if a.get('image') else ''}
{toc}
{body_html}
{faq_part}
<aside class="art-cta"><div><p class="art-cta-h">{srv["title"]} – %%MIASTO%% i okolice</p><p>Potrzebujesz pomocy na miejscu? Zadzwoń – podamy cenę i czas dojazdu. %%GODZ%%.</p></div>
<div class="band-btns"><a class="btn btn-call" href="%%TELHREF%%">%%IC:phone%% %%TEL%%</a><a class="btn btn-line" href="%%R%%{srv["slug"]}.html">O usłudze</a></div></aside>
</div></article>
<section class="sec alt"><div class="wrap"><h2>Czytaj dalej</h2><div class="agrid">{''.join(article_card(x) for x in rel[:3])}</div></div></section>'''
        schemas = [art_schema] + ([faq_schema(a['faq'])] if a['faq'] else [])
        page(f'poradnik/{a["slug"]}.html', a['meta_title'], a['meta_description'], body, schemas, image=(a.get('image') or {}).get('src'),
             active='poradnik.html', crumbs=[('poradnik.html', 'Poradnik'), (None, a['short'])])

    # KONTAKT
    adres = plain('adres')
    mapa = ('<div class="map-ph">%%IC:map-pin%%<p>Tu pojawi się mapa po wpisaniu adresu w pliku <code>dane.json</code>.</p></div>' if is_ph(adres) or not adres else
            f'<iframe class="map" title="Mapa dojazdu" loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
            f'src="https://www.google.com/maps?q={html.escape(urllib.parse.quote(plain("nazwa") + ", " + adres))}&amp;output=embed"></iframe>')
    body = f'''<section class="phero"><div class="wrap"><p class="eyebrow">%%IC:phone%% Kontakt</p><h1>Kontakt – %%MIASTO%% i okolice</h1>
<p class="lead">W sytuacji awaryjnej najszybciej będzie telefonicznie – odbieramy całą dobę. W innych sprawach napisz SMS – oddzwonimy.</p></div></section>
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
  <p class="muted">Formularz przygotuje wiadomość w Twojej aplikacji SMS – nic nie jest wysyłane na serwer.</p>
  <form class="form" id="kontakt-form" data-tel="{esc(plain('telefon_link'))}" data-mail="{'' if is_ph(plain('email')) else esc(plain('email'))}">
    <label>Imię<input name="imie" autocomplete="given-name" required></label>
    <label>Telefon do kontaktu<input name="tel" type="tel" autocomplete="tel" required></label>
    <label>Usługa<select name="usluga">{''.join(f'<option>{s["short"]}</option>' for s in SERV)}<option>Inne</option></select></label>
    <label>Marka, model i rok auta (jeśli dotyczy)<input name="auto"></label>
    <label>Gdzie jesteś (miejscowość, ulica)<input name="gdzie"></label>
    <label>Opis sytuacji<textarea name="opis" rows="4" required></textarea></label>
    <div class="form-btns"><button class="btn btn-call" type="submit" name="via" value="sms">%%IC:message-square%% Wyślij SMS</button>
    <button data-need="email" class="btn btn-line" type="submit" name="via" value="mail">%%IC:mail%% Wyślij e-mail</button></div>
  </form>
</div>
</div></section>'''
    page('kontakt.html', 'Kontakt – %%KROTKA%% %%MIASTO%% | tel. %%TEL%%', 'Zadzwoń całą dobę: %%TEL%%. %%ADRES%%. Awaryjne otwieranie, dorabianie kluczy samochodowych – %%OBSZAR%%.',
         body, active='kontakt.html', crumbs=[(None, 'Kontakt')])

    # POLITYKA, 404
    page('polityka-prywatnosci.html', 'Polityka prywatności – %%KROTKA%%', 'Zasady przetwarzania danych osobowych na stronie.',
         f'<section class="phero"><div class="wrap narrow"><h1>Polityka prywatności</h1></div></section><div class="wrap narrow art-body prose">{T.POLITYKA}</div>',
         crumbs=[(None, 'Polityka prywatności')])
    page('404.html', 'Nie znaleziono strony – %%KROTKA%%', 'Strona nie istnieje.',
         '<section class="phero"><div class="wrap narrow"><h1>Ups, tej strony nie ma</h1><p class="lead">Ale drzwi otworzymy. Wróć na '
         '<a href="%%R%%index.html">stronę główną</a> albo zadzwoń: <a href="%%TELHREF%%">%%TEL%%</a>.</p></div></section>')

    # sitemap, robots
    dom = plain('domena').strip('[]').rstrip('/')
    today = datetime.date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
        f'  <url><loc>{dom}/{"" if p == "index.html" else p}</loc><lastmod>{today}</lastmod></url>\n' for p in PAGES if p != '404.html') + '</urlset>\n'
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(sm)
    open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {dom}/sitemap.xml\n')
    qa()
    todo = [k for k, v in D.items() if is_ph(v)]
    print(f'Gotowe: {len(PAGES)} stron w folderze public/ ({len(ARTS)} artykułów, {len(SERV)} usług, {len(TOWNS)} miejscowości).')
    if todo: print('Do uzupełnienia w dane.json:', ', '.join(todo))

BANNED = ['najtańsz', 'gwarantujemy', 'gwarancja dojazdu', 'zawsze bez', '100%', 'bez żadnych uszkodzeń', 'w 15 minut', 'w 10 minut',
          'korekta licznika', 'cofanie licznika', 'wycinanie dpf', 'usuwanie dpf', 'usunięcie dpf w', 'lorem', 'TODO', '[[', 'najlepszy w kielcach']

def qa():
    warns = []
    titles = {}; descs = {}
    for path, t, d in META:
        if path == '404.html': continue
        if len(t) > 65: warns.append(f'{path}: tytuł ma {len(t)} znaków (>65)')
        if len(d) > 165: warns.append(f'{path}: opis ma {len(d)} znaków (>165)')
        if len(d) < 70: warns.append(f'{path}: opis krótki ({len(d)} znaków)')
        titles.setdefault(t, []).append(path); descs.setdefault(d, []).append(path)
    for t, ps in titles.items():
        if len(ps) > 1: warns.append(f'powtórzony tytuł "{t}": {ps}')
    for d, ps in descs.items():
        if len(ps) > 1: warns.append(f'powtórzony opis: {ps}')
    for p in PAGES:
        f = os.path.join(OUT, p); s = open(f, encoding='utf-8').read()
        if '%%' in s: warns.append(f'{p}: niezamieniony znacznik')
        for h in re.findall(r'(?:href|src)="([^"#:?]+)(?:[#?][^"]*)?"', s):
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), h))): warns.append(f'{p}: zły link {h}')
        low = strip_tags(re.sub(r'<script.*?</script>', '', s, flags=re.S)).lower()
        for b in BANNED:
            if b.lower() in low: warns.append(f'{p}: ryzykowna fraza "{b}"')
        if s.count('<h1') > 1: warns.append(f'{p}: więcej niż jedno H1')
    for a in ARTS:
        n = len(strip_tags(a['body']).split())
        if n < 450: warns.append(f'poradnik/{a["slug"]}: tylko {n} słów')
    print(f'Kontrola jakości: {len(warns)} uwag')
    for w in warns[:80]: print('  -', w)

if __name__ == '__main__':
    build()

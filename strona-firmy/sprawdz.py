# Sprawdza pliki tresci (bez budowania strony). Uzycie: python3 sprawdz.py [slug ...]
import json, os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import tresci as T

ICONS = {f[:-4] for f in os.listdir(os.path.join(ROOT, 'ikony')) if f.endswith('.svg')}
SERVICES = {s['slug'] for s in T.USLUGI} | {'utrata-wszystkich-kluczykow'} | {f[:-5] for f in os.listdir(os.path.join(ROOT, 'tresci', 'uslugi')) if f.endswith('.json')}
PLAN = json.load(open(os.path.join(ROOT, 'tresci', 'plan_poradnika.json'), encoding='utf-8')) if os.path.exists(os.path.join(ROOT, 'tresci', 'plan_poradnika.json')) else []
ARTICLES = {a['slug'] for a in T.ARTYKULY} | {a['slug'] for a in PLAN} | {f[:-5] for f in os.listdir(os.path.join(ROOT, 'tresci', 'poradnik')) if f.endswith('.json')}
TOWNS = {f[:-5] for f in os.listdir(os.path.join(ROOT, 'tresci', 'miejscowosci')) if f.endswith('.json')}
PAGES = {'index', 'uslugi', 'poradnik', 'kontakt', 'obszar-dzialania', 'polityka-prywatnosci', 'o-nas', 'checiny', 'morawica', 'maslow', 'piekoszow'} | SERVICES | TOWNS
BANNED = ['najtańsz', 'gwarantujemy', 'gwarancja dojazdu', 'zawsze bez', '100%', 'bez żadnych uszkodzeń', 'w 15 minut', 'w 10 minut', 'w 20 minut',
          'korekta licznika', 'cofanie licznika', 'wycinanie dpf', 'usuwanie dpf', 'lorem', 'todo', 'najlepszy w kielcach', 'najszybszy', 'numer 1', 'nr 1',
          'wieloletnie doświadczenie', 'lat doświadczenia', 'certyfikowan', 'wszystkie marki', 'każdą markę', 'każdy model']
ALLOWED_TAGS = {'h2', 'h3', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'div', 'br'}

def words(h): return len(re.sub(r'<[^>]+>', ' ', h).split())

def check_article(a, fname):
    e = []
    req = ['slug', 'cat', 'icon', 'title', 'short', 'meta_title', 'meta_description', 'lead', 'keywords', 'service', 'related', 'body', 'faq']
    for k in req:
        if k not in a: e.append(f'brak pola {k}')
    if e: return e
    if a['slug'] + '.json' != os.path.basename(fname): e.append('slug nie zgadza się z nazwą pliku')
    if a['icon'] not in ICONS: e.append(f'nieznana ikona {a["icon"]} (dostępne: {", ".join(sorted(ICONS))})')
    if a['service'] not in SERVICES: e.append(f'nieznana usługa {a["service"]}')
    if len(a['meta_title']) > 60: e.append(f'meta_title {len(a["meta_title"])} zn. (max 60)')
    if not 110 <= len(a['meta_description']) <= 158: e.append(f'meta_description {len(a["meta_description"])} zn. (110-158)')
    if len(a['short']) > 34: e.append(f'short {len(a["short"])} zn. (max 34)')
    if len(re.sub(r'<[^>]+>', '', a['title'])) > 80: e.append('title za długi (max 80)')
    n = words(a['body'])
    if n < 650: e.append(f'treść ma {n} słów (min 650)')
    if a['body'].count('<h2>') < 3: e.append('za mało sekcji <h2> (min 3)')
    if '<h1' in a['body']: e.append('H1 w treści – niedozwolone')
    for t in set(re.findall(r'</?([a-z0-9]+)', a['body'])):
        if t not in ALLOWED_TAGS: e.append(f'niedozwolony znacznik <{t}>')
    for href in re.findall(r'href="([^"]+)"', a['body']):
        m = re.fullmatch(r'%%R%%(?:poradnik/)?([a-z0-9-]+)\.html(#[a-z0-9-]+)?', href)
        if href.startswith('%%TELHREF%%') or href.startswith('%%SMSHREF%%'): continue
        if not m: e.append(f'link w złym formacie: {href} (użyj %%R%%slug.html lub %%R%%poradnik/slug.html)'); continue
        slug = m.group(1)
        if '/poradnik/' in href or href.startswith('%%R%%poradnik/'):
            if slug not in ARTICLES: e.append(f'link do nieistniejącego artykułu {slug}')
        elif slug not in PAGES: e.append(f'link do nieistniejącej strony {slug}')
    for r in a['related']:
        if r not in ARTICLES: e.append(f'related: nieznany artykuł {r}')
    if not 3 <= len(a['faq']) <= 6: e.append('faq: 3-6 pytań')
    low = (a['body'] + ' ' + json.dumps(a['faq'], ensure_ascii=False) + ' ' + a['lead'] + ' ' + a['meta_description']).lower()
    for b in BANNED:
        if b in low: e.append(f'ryzykowna fraza: "{b}"')
    if low.count('kielc') > 4: e.append(f'"Kielce" użyte {low.count("kielc")} razy (max 4 – bez upychania)')
    return e

def check_links(h, e):
    for href in re.findall(r'href="([^"]+)"', h):
        if href.startswith('%%TELHREF%%') or href.startswith('%%SMSHREF%%') or href.startswith('%%GOOGLE%%'): continue
        m = re.fullmatch(r'%%R%%(?:poradnik/)?([a-z0-9-]+)\.html(#[a-z0-9-]+)?', href)
        if not m: e.append(f'link w złym formacie: {href}'); continue
        if href.startswith('%%R%%poradnik/'):
            if m.group(1) not in ARTICLES: e.append(f'link do nieistniejącego artykułu {m.group(1)}')
        elif m.group(1) not in PAGES: e.append(f'link do nieistniejącej strony {m.group(1)}')

def check_page(kind, a, fname):
    e = []
    req = {'uslugi': ['slug', 'icon', 'short', 'title', 'meta_title', 'meta_description', 'card', 'lead', 'items', 'prepare', 'note', 'steps', 'sections', 'faq', 'related'],
           'miejscowosci': ['slug', 'name', 'h1', 'meta_title', 'meta_description', 'lead', 'sections', 'faq'],
           'strony': ['slug', 'meta_title', 'meta_description']}[kind]
    for k in req:
        if k not in a: e.append(f'brak pola {k}')
    if e: return e
    if a['slug'] + '.json' != os.path.basename(fname): e.append('slug nie zgadza się z nazwą pliku')
    if len(a['meta_title']) > 60: e.append(f'meta_title {len(a["meta_title"])} zn. (max 60)')
    if not 110 <= len(a['meta_description']) <= 158: e.append(f'meta_description {len(a["meta_description"])} zn. (110-158)')
    if kind == 'uslugi':
        if a['icon'] not in ICONS: e.append(f'nieznana ikona {a["icon"]}')
        if len(a['steps']) != 4: e.append('steps: dokładnie 4 kroki')
        if len(a['items']) < 4: e.append('items: min 4')
        for r in a['related']:
            if r not in ARTICLES: e.append(f'related: nieznany artykuł {r}')
    secs = a.get('sections', [])
    html_all = ' '.join(x.get('html', '') for x in secs) + ' ' + ' '.join(str(a.get(k, '')) for k in ('area_html', 'about_html', 'lead', 'hero_lead'))
    n = words(' '.join(x.get('html', '') for x in secs))
    mins = {'uslugi': 350, 'miejscowosci': 450, 'strony': 0}[kind]
    if n < mins: e.append(f'sekcje mają {n} słów (min {mins})')
    for x in secs:
        if 'h2' not in x or 'html' not in x: e.append('sekcja bez h2/html')
        for t in set(re.findall(r'</?([a-z0-9]+)', x.get('html', ''))):
            if t not in ALLOWED_TAGS: e.append(f'niedozwolony znacznik <{t}>')
        if '<h2' in x.get('html', ''): e.append('H2 wewnątrz html sekcji – użyj osobnej sekcji lub H3')
    check_links(html_all, e)
    faq = a.get('faq', [])
    if kind != 'strony' and not 3 <= len(faq) <= 8: e.append('faq: 3-8 pytań')
    low = (json.dumps(a, ensure_ascii=False)).lower()
    for b in BANNED:
        if b in low: e.append(f'ryzykowna fraza: "{b}"')
    return e

def main_pages():
    total = 0
    for kind in ('uslugi', 'miejscowosci', 'strony'):
        d = os.path.join(ROOT, 'tresci', kind)
        for f in sorted(x for x in os.listdir(d) if x.endswith('.json')):
            try: a = json.load(open(os.path.join(d, f), encoding='utf-8'))
            except Exception as ex: print(f'{kind}/{f}: BŁĄD JSON: {ex}'); total += 1; continue
            e = check_page(kind, a, f)
            n = words(' '.join(x.get('html', '') for x in a.get('sections', [])))
            print(f'{kind}/{f}: ' + ('OK' if not e else 'PROBLEMY: ' + '; '.join(e)) + f'  ({n} słów w sekcjach)')
            total += len(e)
    print('Łącznie problemów:', total)

def main():
    if sys.argv[1:2] == ['--strony']: return main_pages()
    d = os.path.join(ROOT, 'tresci', 'poradnik')
    files = sorted(f for f in os.listdir(d) if f.endswith('.json'))
    want = set(sys.argv[1:])
    total = 0
    for f in files:
        if want and f[:-5] not in want: continue
        try: a = json.load(open(os.path.join(d, f), encoding='utf-8'))
        except Exception as ex: print(f'{f}: BŁĄD JSON: {ex}'); total += 1; continue
        e = check_article(a, f)
        print(f'{f}: ' + ('OK' if not e else 'PROBLEMY: ' + '; '.join(e)) + f'  ({words(a.get("body", ""))} słów)')
        total += len(e)
    print('Łącznie problemów:', total)

if __name__ == '__main__':
    main()

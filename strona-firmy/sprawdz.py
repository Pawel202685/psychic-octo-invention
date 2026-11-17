# Sprawdza pliki tresci (bez budowania strony). Uzycie: python3 sprawdz.py [slug ...]
import json, os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import tresci as T

ICONS = {f[:-4] for f in os.listdir(os.path.join(ROOT, 'ikony')) if f.endswith('.svg')}
SERVICES = {s['slug'] for s in T.USLUGI} | {f[:-5] for f in os.listdir(os.path.join(ROOT, 'tresci', 'uslugi')) if f.endswith('.json')}
PLAN = json.load(open(os.path.join(ROOT, 'tresci', 'plan_poradnika.json'), encoding='utf-8')) if os.path.exists(os.path.join(ROOT, 'tresci', 'plan_poradnika.json')) else []
ARTICLES = {a['slug'] for a in T.ARTYKULY} | {a['slug'] for a in PLAN} | {f[:-5] for f in os.listdir(os.path.join(ROOT, 'tresci', 'poradnik')) if f.endswith('.json')}
TOWNS = {f[:-5] for f in os.listdir(os.path.join(ROOT, 'tresci', 'miejscowosci')) if f.endswith('.json')}
PAGES = {'index', 'uslugi', 'poradnik', 'kontakt', 'obszar-dzialania', 'polityka-prywatnosci'} | SERVICES | TOWNS
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

def main():
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

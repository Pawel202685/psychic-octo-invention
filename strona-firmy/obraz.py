# Pobiera zdjecie (np. ze stocku), kadruje 16:9, zapisuje 1200x675 + miniature 480x270 i wpisuje "image" do pliku JSON tresci.
# Uzycie: python3 obraz.py <rodzaj: poradnik|uslugi> <slug> <url-lub-plik> "<alt po polsku>" [fokus_x 0-1] [fokus_y 0-1] [id_stocku]
import sys, os, json, io, urllib.request
from PIL import Image, ImageOps
ROOT = os.path.dirname(os.path.abspath(__file__))
kind, slug, src, alt = sys.argv[1:5]
fx = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
fy = float(sys.argv[6]) if len(sys.argv) > 6 else 0.5
sid = sys.argv[7] if len(sys.argv) > 7 else ''
jf = os.path.join(ROOT, 'tresci', kind, slug + '.json')
assert os.path.exists(jf), f'brak pliku {jf}'
data = open(src, 'rb').read() if os.path.exists(src) else urllib.request.urlopen(src, timeout=120).read()
im = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert('RGB')
W, H = im.size; r = 16 / 9
if W / H > r: cw, ch = int(H * r), H
else: cw, ch = W, int(W / r)
x0 = int(min(max(fx * W - cw / 2, 0), W - cw)); y0 = int(min(max(fy * H - ch / 2, 0), H - ch))
im = im.crop((x0, y0, x0 + cw, y0 + ch))
out = os.path.join(ROOT, 'zasoby', 'img'); os.makedirs(out, exist_ok=True)
im.resize((1200, 675), Image.LANCZOS).save(os.path.join(out, slug + '.jpg'), quality=78, optimize=True, progressive=True)
im.resize((480, 270), Image.LANCZOS).save(os.path.join(out, slug + '-m.jpg'), quality=74, optimize=True, progressive=True)
d = json.load(open(jf, encoding='utf-8'))
d['image'] = {'src': f'img/{slug}.jpg', 'thumb': f'img/{slug}-m.jpg', 'alt': alt, 'w': 1200, 'h': 675, 'source': 'Freepik (licencja Premium)', 'stock_id': sid}
json.dump(d, open(jf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
reg = os.path.join(ROOT, 'zasoby', 'img', 'rejestr.json')
R = json.load(open(reg, encoding='utf-8')) if os.path.exists(reg) else {}
R[f'{kind}/{slug}'] = d['image']
json.dump(R, open(reg, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('OK', slug, os.path.getsize(os.path.join(out, slug + '.jpg')) // 1024, 'KB')

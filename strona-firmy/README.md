# Strona firmy: awaryjne otwieranie, klucze, sterowniki, DPF

Gotowa strona internetowa (20 podstron) z poradnikiem dla klientów.

- **Strona główna**: usługi, przebieg współpracy, porady i najczęstsze pytania.
- **5 stron usług**:
  - otwieranie samochodów,
  - otwieranie mieszkań i domów,
  - programowanie kluczy,
  - sterowniki i immobilizery,
  - filtry DPF.
- **Poradnik: 9 artykułów**, m.in.:
  - zatrzaśnięte kluczyki,
  - zgubione klucze,
  - keyless i kradzież „na walizkę”,
  - awaria sterownika,
  - jak dbać o filtr DPF.
- **Kontakt**: telefon, SMS, e-mail, mapa i formularz, który przygotowuje wiadomość SMS lub e-mail.
- **Polityka prywatności**, strona 404, `sitemap.xml` i `robots.txt`.
- Strona działa na telefonach i ma przycisk „Zadzwoń teraz” zawsze na dole ekranu.
- Ma dane strukturalne dla Google: firma, pytania i artykuły.
- Nie używa ciasteczek ani zewnętrznych czcionek.

## 1. Wpisz dane firmy

Otwórz plik `dane.json` i zamień teksty w nawiasach kwadratowych na prawdziwe dane:

| Pole | Co wpisać |
|---|---|
| `nazwa` | nazwa firmy |
| `telefon` | numer w wersji do wyświetlenia, np. `600 123 456` |
| `telefon_link` | ten sam numer z kierunkowym, bez spacji, np. `+48600123456` |
| `email` | adres e-mail |
| `miasto`, `obszar` | miasto i obszar działania, np. `Rzeszów i okolice do 30 km` |
| `adres` | adres firmy (pojawi się mapa na stronie Kontakt) |
| `godziny` | godziny pracy, np. `Całą dobę, 7 dni w tygodniu` |
| `nip` | NIP |
| `google` | link do wizytówki Google (już wpisany) |
| `domena` | adres strony, np. `https://www.twoja-firma.pl` |

Dopóki pole nie jest uzupełnione, na stronie jest podświetlone na żółto.

## 2. Zbuduj stronę

```
python3 build.py
```

Gotowe pliki trafiają do folderu `public/`. Teksty usług i poradnika są w pliku `tresci.py`, a wygląd w `zasoby/css/style.css`.

## 3. Opublikuj

Wgraj **zawartość** folderu `public/` na serwer, np. przez FTP do folderu `public_html` u dostawcy hostingu. Strona to zwykłe pliki HTML i nie potrzebuje bazy danych ani PHP.

## Ikony

Ikony pochodzą z zestawu Lucide (licencja ISC, w pliku `ikony/LICENSE-lucide.txt`).

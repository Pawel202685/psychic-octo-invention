# Tresci strony: uslugi, poradnik, FAQ, polityka prywatnosci.
# Znaczniki %%TEL%%, %%NAZWA%%, %%OBSZAR%% itd. sa zamieniane na dane z pliku dane.json.
import re, unicodedata

def slugify(s):
    s = unicodedata.normalize('NFKD', s.replace('ł', 'l').replace('Ł', 'L')).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

# ilustracja w naglowku strony glownej: %%ICX:nazwa:x:y:rozmiar:grubosc%%
HERO_SVG = '''<svg viewBox="0 0 440 440" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="g1" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffb020" stop-opacity=".35"/><stop offset="1" stop-color="#ffb020" stop-opacity="0"/></radialGradient>
<linearGradient id="g2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1d3354"/><stop offset="1" stop-color="#0f1c30"/></linearGradient></defs>
<circle cx="220" cy="220" r="210" fill="url(#g1)"/>
<circle cx="220" cy="220" r="150" fill="url(#g2)" stroke="#ffb020" stroke-opacity=".5" stroke-width="2"/>
<circle cx="220" cy="220" r="178" fill="none" stroke="#ffffff" stroke-opacity=".12" stroke-dasharray="4 10"/>
<g color="#ffcd5c">%%ICX:key-round:124:124:192:1.3%%</g>
<g><circle cx="78" cy="96" r="50" fill="#132239" stroke="#ffb020" stroke-width="2"/><g color="#ffffff">%%ICX:car:50:68:56:1.6%%</g></g>
<g><circle cx="368" cy="128" r="44" fill="#132239" stroke="#ffb020" stroke-width="2"/><g color="#ffffff">%%ICX:house:344:104:48:1.6%%</g></g>
<g><circle cx="358" cy="330" r="46" fill="#132239" stroke="#ffb020" stroke-width="2"/><g color="#ffffff">%%ICX:cpu:333:305:50:1.6%%</g></g>
<g><circle cx="96" cy="340" r="42" fill="#132239" stroke="#ffb020" stroke-width="2"/><g color="#ffffff">%%ICX:lock-open:74:318:44:1.7%%</g></g>
</svg>'''

KROKI_OGOLNE = [
    ('Zadzwoń', 'Opisz krótko sytuację: co się stało, gdzie jesteś, jaki to samochód albo jakie drzwi.'),
    ('Poznaj cenę', 'Podamy orientacyjną cenę i czas dojazdu. Decydujesz spokojnie, bez presji.'),
    ('Weryfikacja', 'Na miejscu potwierdzamy, że masz prawo do auta lub lokalu – to chroni Ciebie.'),
    ('Gotowe', 'Otwieramy lub programujemy, sprawdzamy działanie i wystawiamy dowód zakupu.'),
]

FAQ_START = [
    ('Jak szybko przyjedziecie?', 'To zależy od miejsca i pory. Czas dojazdu podajemy podczas rozmowy telefonicznej. Obszar działania: %%OBSZAR%%.'),
    ('Ile kosztuje awaryjne otwarcie?', 'Cena zależy od rodzaju zamka lub modelu auta, pory dnia i odległości. Podajemy ją przez telefon, zanim wyjedziemy – bez dopisywania kosztów na końcu.'),
    ('Czy otwarcie uszkodzi zamek albo samochód?', 'W większości przypadków otwieramy bez śladów, specjalistycznymi narzędziami. Jeśli w danej sytuacji jest ryzyko uszkodzenia (np. wkładka o wysokiej klasie bezpieczeństwa), uprzedzamy o tym przed rozpoczęciem pracy.'),
    ('Jak sprawdzacie, że auto lub mieszkanie jest moje?', 'Prosimy o dowód osobisty oraz dowód rejestracyjny auta albo dokument potwierdzający prawo do lokalu. Jeśli dokumenty są w środku, pokazujesz je zaraz po otwarciu, zanim zakończymy zlecenie.'),
    ('Zgubiłem wszystkie kluczyki. Czy da się dorobić nowy?', 'Tak, w wielu modelach kluczyk dorabiamy i programujemy na miejscu, przy samochodzie. Przy okazji usuwamy zgubione kluczyki z pamięci auta, żeby nikt nie mógł ich użyć.'),
    ('Kiedy pracujecie?', '%%GODZ%%. W sytuacji awaryjnej po prostu zadzwoń: <a href="%%TELHREF%%">%%TEL%%</a>.'),
]

USLUGI = [
dict(slug='otwieranie-samochodow', icon='car', short='Otwieranie samochodów',
     title='Awaryjne otwieranie samochodów',
     card='Kluczyki zatrzaśnięte w aucie lub bagażniku, rozładowany akumulator, zablokowany zamek.',
     desc='Awaryjne otwieranie samochodów – kluczyki zamknięte w aucie, rozładowany akumulator, zablokowany zamek. %%OBSZAR%%. Tel. %%TEL%%.',
     lead='Kluczyki zostały w środku, akumulator padł, a zamek nie reaguje? Przyjeżdżamy na miejsce i otwieramy auto, dbając o zamek, lakier i uszczelki.',
     items=['Kluczyki zatrzaśnięte w kabinie lub w bagażniku',
            'Rozładowany akumulator – centralny zamek nie reaguje na pilota',
            'Zamarznięty, zablokowany lub uszkodzony zamek',
            'Złamany kluczyk w zamku lub stacyjce – wyjęcie ułamanej części',
            'Dziecko lub zwierzę w zamkniętym aucie – zgłoszenie traktujemy jako pilne (przy zagrożeniu życia dzwoń najpierw na 112)'],
     prepare=['Dowód osobisty',
              'Dowód rejestracyjny auta – jeśli jest w środku, pokażesz go zaraz po otwarciu',
              'Marka, model i rok produkcji – pomogą nam dobrać narzędzia i podać cenę'],
     note='Nie otwieramy samochodu bez potwierdzenia, że masz do niego prawo. To chroni Ciebie i Twoje auto.',
     steps=[('Telefon', 'Mówisz, gdzie stoi auto, jaki to model i gdzie zostały kluczyki.'),
            ('Cena i dojazd', 'Podajemy orientacyjną cenę i czas przyjazdu.'),
            ('Otwarcie', 'Otwieramy auto specjalistycznymi narzędziami, bez łomu i bez wybijania szyby.'),
            ('Kontrola', 'Sprawdzamy dokumenty oraz to, czy zamki i szyby działają poprawnie.')],
     faq=[('Ile trwa otwarcie samochodu?', 'Samo otwarcie zwykle trwa od kilku do kilkudziesięciu minut – zależy od modelu i jego zabezpieczeń.'),
          ('Czy po otwarciu zostaną ślady?', 'W większości przypadków nie. Jeśli przy danym modelu istnieje ryzyko, mówimy o tym przed rozpoczęciem.'),
          ('Co, jeśli dokumenty auta są w środku?', 'Nic nie szkodzi – po otwarciu pokazujesz dowód rejestracyjny i dowód osobisty, a my porównujemy dane.'),
          ('Czy otworzycie bagażnik, gdy auto jest otwarte?', 'Tak, pomagamy także wtedy, gdy kluczyki zostały w zamkniętym bagażniku.')],
     related=['zatrzasniete-kluczyki-w-aucie', 'pilot-od-auta-nie-dziala', 'jak-wybrac-uczciwego-slusarza']),
dict(slug='otwieranie-mieszkan-i-domow', icon='house', short='Otwieranie mieszkań i domów',
     title='Awaryjne otwieranie mieszkań i domów',
     card='Zatrzaśnięte drzwi, zgubione klucze, zacięty zamek. Na miejscu wymienimy też wkładkę.',
     desc='Awaryjne otwieranie drzwi mieszkań i domów, wymiana wkładek i zamków. %%OBSZAR%%. Tel. %%TEL%%.',
     lead='Drzwi się zatrzasnęły, klucze zginęły albo zamek się zaciął? Otwieramy drzwi mieszkań, domów, furtek i garaży – w miarę możliwości bez niszczenia zamka.',
     items=['Drzwi zatrzaśnięte, klucz został w środku',
            'Zgubione lub skradzione klucze – otwarcie i wymiana wkładki',
            'Zacięty zamek, klucz nie chce się obrócić',
            'Złamany klucz w zamku',
            'Wymiana wkładek i zamków, montaż lepszych zabezpieczeń',
            'Furtki, bramy, garaże i kłódki'],
     prepare=['Dowód osobisty z adresem lokalu albo inny dokument potwierdzający prawo do niego (np. umowa najmu)',
              'Jeśli dokumenty są w środku – pokażesz je zaraz po otwarciu',
              'W razie wątpliwości otwarcie odbywa się w obecności zarządcy budynku lub policji'],
     note='Jeśli klucze zginęły razem z dokumentami albo ktoś mógł poznać Twój adres, wymień wkładkę jeszcze tego samego dnia.',
     steps=[('Telefon', 'Mówisz, gdzie jesteś i jaki masz zamek (jeśli wiesz) – np. drzwi w bloku, drzwi zewnętrzne, furtka.'),
            ('Cena i dojazd', 'Podajemy orientacyjną cenę otwarcia i ewentualnej nowej wkładki.'),
            ('Weryfikacja i otwarcie', 'Potwierdzamy Twoje prawo do lokalu i otwieramy drzwi.'),
            ('Wymiana (jeśli trzeba)', 'Montujemy nową wkładkę i przekazujemy komplet kluczy.')],
     faq=[('Czy da się otworzyć drzwi bez niszczenia zamka?', 'Często tak – zależy to od rodzaju zamka i klasy wkładki. Przy wkładkach o wysokiej klasie bezpieczeństwa bywa konieczne ich usunięcie – wtedy od razu montujemy nową.'),
          ('Kto może zlecić otwarcie mieszkania?', 'Właściciel, najemca lub inna osoba, która ma prawo do lokalu i może to potwierdzić.'),
          ('Czy zatrzaśnięte drzwi to to samo co zamknięte na klucz?', 'Nie. Drzwi zatrzaśnięte tylko na zapadkę zwykle łatwiej otworzyć bez uszkodzeń niż drzwi zamknięte na klucz.'),
          ('Czy dostanę paragon lub fakturę?', 'Tak, za każdą usługę wystawiamy dowód zakupu.')],
     related=['zatrzasniete-drzwi-zgubione-klucze', 'jak-wybrac-uczciwego-slusarza']),
dict(slug='programowanie-kluczy', icon='key-round', short='Programowanie kluczy',
     title='Dorabianie i programowanie kluczyków samochodowych',
     card='Zapasowy kluczyk, utrata wszystkich kluczyków, piloty, karty i systemy keyless.',
     desc='Dorabianie i programowanie kluczyków samochodowych, także gdy zgubiłeś wszystkie. Piloty, keyless, immobilizer. %%OBSZAR%%.',
     lead='Dorabiamy i programujemy kluczyki samochodowe – również wtedy, gdy zgubiłeś wszystkie. W wielu modelach robimy to na miejscu, przy aucie.',
     items=['Zapasowy kluczyk z chipem immobilizera',
            'Utrata wszystkich kluczyków – nowy kluczyk od zera',
            'Piloty, kluczyki składane, karty i kluczyki keyless',
            'Usunięcie zgubionych kluczyków z pamięci auta',
            'Naprawa pilota: nowa obudowa, przyciski, bateria',
            'Synchronizacja pilota z centralnym zamkiem'],
     prepare=['Dowód rejestracyjny i dowód osobisty – dane muszą się zgadzać',
              'Wszystkie posiadane kluczyki do tego auta (żeby pozostały w pamięci)',
              'Numer VIN, marka, model i rok produkcji – do wyceny przez telefon'],
     note='Kupiłeś używane auto? Przy programowaniu możemy usunąć z pamięci kluczyki, których nie masz – poprzedni posiadacz nie uruchomi już samochodu.',
     steps=[('Dane auta', 'Podajesz markę, model, rok i VIN – sprawdzamy, jaki kluczyk jest potrzebny.'),
            ('Wycena', 'Mówimy, ile to kosztuje i ile potrwa.'),
            ('Przygotowanie', 'Przygotowujemy kluczyk i nacinamy grot.'),
            ('Programowanie', 'Programujemy kluczyk w aucie i sprawdzamy wszystkie funkcje.')],
     faq=[('Czy to wyjdzie taniej niż w serwisie dealerskim?', 'Często tak i zwykle szybciej, ale zależy to od modelu. Cenę podajemy przed wykonaniem usługi.'),
          ('Nie mam żadnego kluczyka. Czy to możliwe?', 'W wielu modelach tak. Potrzebne będą dokumenty auta i dowód osobisty.'),
          ('Czy zgubiony kluczyk nadal będzie otwierał auto?', 'Nie, jeśli usuniemy go z pamięci samochodu podczas programowania – i zalecamy to zrobić.'),
          ('Kupiłem kluczyk w internecie. Zaprogramujecie go?', 'Czasem tak, ale tanie zamienniki często mają zły chip lub częstotliwość. Zanim kupisz, zadzwoń – sprawdzimy numer części.')],
     related=['zgubione-wszystkie-kluczyki-do-auta', 'zapasowy-kluczyk-do-auta', 'keyless-kradziez-na-walizke']),
dict(slug='sterowniki', icon='cpu', short='Sterowniki i immobilizery',
     title='Naprawa i programowanie sterowników',
     card='Sterowniki silnika (ECU), immobilizery i moduły elektroniki – diagnostyka, naprawa, adaptacja.',
     desc='Diagnostyka, naprawa i programowanie sterowników silnika (ECU) i immobilizerów. Auto kręci, ale nie odpala? %%OBSZAR%%.',
     lead='Auto kręci, ale nie odpala? Po wymianie sterownika samochód „nie widzi” kluczyka? Diagnozujemy, naprawiamy i programujemy sterowniki silnika, immobilizery i moduły elektroniki.',
     items=['Diagnostyka komputerowa i odczyt błędów',
            'Naprawa sterowników silnika (ECU) po zalaniu, przepięciu lub awarii',
            'Adaptacja używanego sterownika do Twojego auta',
            'Problemy z immobilizerem – auto kręci, ale nie zapala',
            'Moduły komfortu i elektroniki nadwozia, które nie rozpoznają kluczyka',
            'Kopia zapasowa danych sterownika przed naprawą'],
     prepare=['Opis objawów: kiedy się zaczęło, co poprzedziło awarię (np. zalanie, wymiana akumulatora)',
              'Dowód rejestracyjny',
              'Jeśli kupiłeś używany sterownik – jego numery z naklejki'],
     note='Nie kupuj używanego sterownika „w ciemno”. Najpierw zadzwoń – sprawdzimy, czy numer części i oprogramowania pasuje do Twojego auta.',
     steps=[('Opis objawów', 'Mówisz, co się dzieje z autem – to pozwala wstępnie ocenić problem.'),
            ('Diagnostyka', 'Sprawdzamy zasilanie, połączenia i komunikację ze sterownikami.'),
            ('Wycena', 'Proponujemy rozwiązanie: naprawę, adaptację lub wymianę – z ceną przed pracą.'),
            ('Naprawa i test', 'Naprawiamy lub programujemy i sprawdzamy auto po uruchomieniu.')],
     faq=[('Czy sterownik da się naprawić zamiast kupować nowy?', 'Często tak – naprawa bywa wyraźnie tańsza niż nowy sterownik. Po diagnostyce powiemy, co się opłaca.'),
          ('Kupiłem używany sterownik. Czy zadziała w moim aucie?', 'Zwykle wymaga adaptacji do Twojego auta i kluczyków. Ważne, żeby numer części się zgadzał.'),
          ('Czy auto trzeba holować?', 'Nie zawsze. Część prac wykonujemy na miejscu – zapytaj przez telefon.'),
          ('Co może uszkodzić sterownik?', 'Najczęściej wilgoć, przepięcia (np. przy uruchamianiu „na kable”) i uszkodzone przewody lub złącza.')],
     related=['awaria-sterownika-objawy', 'zgubione-wszystkie-kluczyki-do-auta', 'filtr-dpf-jak-dbac']),
dict(slug='filtry-dpf', icon='filter', short='Filtry DPF',
     title='Filtry DPF – diagnostyka, regeneracja i czyszczenie',
     card='Kontrolka DPF, spadek mocy, tryb awaryjny – diagnostyka, regeneracja serwisowa, czyszczenie.',
     desc='Diagnostyka, regeneracja serwisowa i czyszczenie filtrów cząstek stałych DPF/FAP. Kontrolka DPF, tryb awaryjny. %%OBSZAR%%.',
     lead='Zaświeciła się kontrolka DPF, auto straciło moc albo przeszło w tryb awaryjny? Sprawdzamy, co się dzieje z filtrem cząstek stałych i usuwamy przyczynę zapychania.',
     items=['Diagnostyka filtra: stopień zapełnienia, czujniki, błędy',
            'Wymuszona regeneracja serwisowa komputerem',
            'Czyszczenie filtra DPF/FAP',
            'Wymiana czujnika różnicy ciśnień i czujników temperatury',
            'Szukanie przyczyny: wtryski, zawór EGR, turbosprężarka, termostat',
            'Porady, jak jeździć, żeby filtr wytrzymał dłużej'],
     prepare=['Opis objawów i komunikatów na desce rozdzielczej',
              'Informacja, jak zwykle jeździsz (miasto czy trasa)',
              'Historia napraw – jeśli coś już było robione przy filtrze'],
     note='Zapchany filtr to często skutek innej usterki. Sama regeneracja bez usunięcia przyczyny pomaga tylko na chwilę.',
     steps=[('Opis objawów', 'Mówisz, co pokazuje auto i kiedy pojawiły się problemy.'),
            ('Diagnostyka', 'Odczytujemy parametry filtra i błędy, sprawdzamy czujniki.'),
            ('Rozwiązanie', 'Regeneracja serwisowa, czyszczenie lub naprawa przyczyny – z ceną przed pracą.'),
            ('Kontrola', 'Sprawdzamy parametry po naprawie i podpowiadamy, jak dbać o filtr.')],
     faq=[('Jak poznać, że filtr DPF jest zapchany?', 'Typowe objawy to kontrolka DPF, spadek mocy, tryb awaryjny, częste regeneracje i wyższe spalanie.'),
          ('Czy wystarczy pojeździć w trasie?', 'Przy lekkim zapełnieniu często tak. Gdy filtr jest mocno zapchany, potrzebna jest regeneracja serwisowa lub czyszczenie.'),
          ('Czy czyszczenie jest lepsze niż nowy filtr?', 'Jeśli filtr nie jest uszkodzony mechanicznie, czyszczenie zwykle wystarcza i kosztuje znacznie mniej niż nowy.'),
          ('Jaki olej do auta z DPF?', 'Taki, jaki zaleca producent – zwykle o niskiej zawartości popiołów (low SAPS). Zły olej przyspiesza zapychanie filtra.')],
     related=['filtr-dpf-jak-dbac', 'awaria-sterownika-objawy']),
]

def tip(t, ic='lightbulb'): return f'<div class="tip">%%IC:{ic}%%<p>{t}</p></div>'
def warn(t): return f'<div class="warn">%%IC:triangle-alert%%<p>{t}</p></div>'

ARTYKULY = [
dict(slug='zatrzasniete-kluczyki-w-aucie', icon='car', cat='Samochód', min=4, service='otwieranie-samochodow',
     short='Kluczyki zamknięte w aucie',
     title='Kluczyki zatrzaśnięte w aucie – co zrobić krok po kroku',
     lead='Drzwi trzasnęły, a kluczyki zostały na siedzeniu? To jedna z najczęstszych sytuacji awaryjnych. Podpowiadamy, co sprawdzić, czego nie robić i jak szybko odzyskać dostęp do auta.',
     body=f'''
<h2>1. Najpierw sprawdź, kto jest w środku</h2>
<p>Jeśli w zamkniętym aucie zostało dziecko lub zwierzę, a jest gorąco albo widzisz, że dzieje się coś złego – <strong>dzwoń od razu na 112</strong>. Przy zagrożeniu życia liczy się każda minuta, a służby mogą wybić szybę. Gdy nie ma bezpośredniego zagrożenia, zadzwoń do nas i od razu powiedz, kto jest w aucie – takie zgłoszenia traktujemy jako pilne.</p>
<h2>2. Obejdź auto dookoła</h2>
<p>Sprawdź wszystkie drzwi, bagażnik i klapę wlewu. Zdarza się, że jedne drzwi nie zostały zablokowane. Pamiętaj też, że wiele aut zamyka się samo, jeśli po otwarciu pilotem żadne drzwi nie zostaną otwarte w ciągu kilkudziesięciu sekund.</p>
<h2>3. Zapasowy kluczyk i aplikacja producenta</h2>
<ul>
<li><strong>Zapasowy kluczyk</strong> – czy ktoś może go przywieźć? Często to najtańsze rozwiązanie, jeśli dom jest blisko.</li>
<li><strong>Aplikacja w telefonie</strong> – wiele nowszych aut można otworzyć zdalnie przez aplikację producenta, jeśli usługa była wcześniej aktywowana.</li>
<li><strong>Assistance</strong> – sprawdź, czy Twoja polisa lub pakiet serwisowy nie obejmuje pomocy w takiej sytuacji.</li>
</ul>
<h2>4. Czego nie robić</h2>
<ul>
<li>Nie wsuwaj drutu ani wieszaka między szybę a uszczelkę. W drzwiach są przewody, mechanizm szyby i czujniki – łatwo o kosztowną usterkę.</li>
<li>Nie podważaj drzwi ani zamka śrubokrętem – zniszczysz lakier, uszczelkę albo zamek.</li>
<li>Nie wybijaj szyby, jeśli nie ma zagrożenia życia. Wymiana szyby i sprzątanie odłamków kosztują więcej niż otwarcie auta.</li>
</ul>
<h2>5. Zadzwoń po pomoc – co przygotować</h2>
<p>Przy zgłoszeniu podaj markę, model i rok auta, dokładne miejsce oraz to, gdzie leżą kluczyki (kabina czy bagażnik). Przygotuj dowód osobisty – jeśli dowód rejestracyjny jest w aucie, pokażesz go po otwarciu.</p>
{tip('Wyrób sobie nawyk: kluczyk w dłoni, zanim zamkniesz drzwi. A zapasowy kluczyk trzymaj w domu – nigdy w samochodzie.')}
<h2>Jak uniknąć tej sytuacji w przyszłości</h2>
<ul>
<li>Miej zapasowy kluczyk i daj znać bliskiej osobie, gdzie leży.</li>
<li>Wymieniaj baterię w pilocie, zanim całkiem się wyczerpie – słabnący zasięg to pierwszy sygnał.</li>
<li>Sprawdź w instrukcji, jak działa automatyczne ryglowanie w Twoim aucie.</li>
</ul>'''),
dict(slug='zatrzasniete-drzwi-zgubione-klucze', icon='door-closed', cat='Dom i mieszkanie', min=4, service='otwieranie-mieszkan-i-domow',
     short='Zatrzaśnięte drzwi, zgubione klucze',
     title='Zatrzaśnięte drzwi lub zgubione klucze do mieszkania – poradnik',
     lead='Wyszedłeś na chwilę, drzwi się zatrzasnęły, a klucze zostały w środku? Albo zgubiłeś cały pęk? Oto jak działać rozsądnie i bezpiecznie – i kiedy od razu wymienić wkładkę.',
     body=f'''
<h2>Najpierw: kto ma zapasowy klucz?</h2>
<p>Zanim wezwiesz pomoc, pomyśl, kto może mieć zapasowy komplet: domownicy, rodzina, zaufany sąsiad. Jeśli wynajmujesz mieszkanie – właściciel lub zarządca. Czasem to kwestia kilku telefonów.</p>
<h2>Zatrzaśnięte czy zamknięte na klucz?</h2>
<p>To ważna różnica. Drzwi <strong>zatrzaśnięte</strong> (tylko na zapadkę) zwykle łatwiej otworzyć bez uszkodzeń. Drzwi <strong>zamknięte na klucz</strong> – zależnie od rodzaju zamka i klasy wkładki – mogą wymagać więcej pracy, a przy najlepszych zabezpieczeniach czasem trzeba wkładkę usunąć i założyć nową. Dobry fachowiec powie Ci to przed rozpoczęciem.</p>
<h2>Klucze zgubione lub skradzione? Wymień wkładkę</h2>
<p>Jeśli klucze zginęły razem z portfelem, dokumentami lub czymś, co zdradza Twój adres – <strong>wymień wkładkę jeszcze tego samego dnia</strong>. Nawet jeśli klucze „pewnie leżą gdzieś w domu”, zrób to, gdy nie masz pewności. Nowa wkładka kosztuje mniej niż skutki włamania.</p>
<h2>Czego nie robić</h2>
<ul>
<li>Nie wchodź przez balkon ani okno – upadek z wysokości to realne ryzyko.</li>
<li>Nie wierć zamka samodzielnie i nie podważaj drzwi – uszkodzisz ościeżnicę, a naprawa będzie droga.</li>
<li>Nie zostawiaj otwartego mieszkania bez opieki po otwarciu, jeśli zamek trzeba wymienić.</li>
</ul>
<h2>Co przygotować dla ślusarza</h2>
<p>Uczciwy ślusarz zawsze sprawdzi, czy masz prawo do lokalu. Przygotuj dowód osobisty z adresem, umowę najmu albo inny dokument. Jeśli dokumenty zostały w środku, pokażesz je zaraz po otwarciu. W razie wątpliwości otwarcie może odbyć się w obecności zarządcy budynku lub policji.</p>
{tip('Przy wymianie wkładki zapytaj o jej klasę i atesty. Wkładka z wyższą klasą i kartą kodową utrudnia dorobienie klucza bez Twojej wiedzy.')}
<h2>Po otwarciu</h2>
<ul>
<li>Sprawdź, czy zamek działa płynnie z obu stron.</li>
<li>Zrób zapasowy klucz i zostaw go u zaufanej osoby.</li>
<li>Poproś o paragon lub fakturę – to Twoja gwarancja.</li>
</ul>'''),
dict(slug='keyless-kradziez-na-walizke', icon='radio', cat='Bezpieczeństwo', min=4, service='programowanie-kluczy',
     short='Keyless i kradzież na walizkę',
     title='Keyless i kradzież „na walizkę” – jak chronić auto',
     lead='Systemy bezkluczykowe są wygodne, ale złodzieje potrafią przedłużyć sygnał kluczyka leżącego w domu i odjechać autem. Oto proste sposoby, żeby skutecznie utrudnić im zadanie.',
     body=f'''
<h2>Na czym polega ta metoda</h2>
<p>Auto z systemem keyless otwiera się i uruchamia, gdy „wyczuje” kluczyk w pobliżu. Złodzieje używają urządzeń, które przechwytują sygnał kluczyka – na przykład leżącego przy drzwiach wejściowych – i przekazują go do auta. Samochód „myśli”, że właściciel stoi obok. Cała kradzież może trwać krótko i nie zostawia śladów włamania.</p>
<h2>Proste i skuteczne zabezpieczenia</h2>
<ul>
<li><strong>Etui blokujące sygnał</strong> (tzw. klatka Faradaya) lub metalowe pudełko. Przetestuj je: z kluczykiem w etui stań przy aucie – nie powinno się otworzyć.</li>
<li><strong>Kluczyk z dala od drzwi i okien.</strong> Nie zostawiaj go w przedpokoju tuż przy wejściu.</li>
<li><strong>Wyłącz keyless lub uśpij kluczyk</strong>, jeśli Twoje auto na to pozwala – sprawdź w instrukcji lub ustawieniach samochodu.</li>
<li><strong>Blokada mechaniczna</strong> kierownicy lub pedałów – widoczna z zewnątrz, zniechęca już na starcie.</li>
<li><strong>Dodatkowe zabezpieczenie elektroniczne</strong> – niezależny immobilizer lub lokalizator GPS.</li>
<li><strong>Zabezpieczenie gniazda diagnostycznego</strong> – utrudnia dodanie nowego kluczyka do auta.</li>
</ul>
<h2>Wiesz, ile kluczyków zna Twoje auto?</h2>
<p>Po zakupie używanego samochodu warto sprawdzić, ile kluczyków jest zapisanych w jego pamięci. Jeśli więcej niż masz – te nieznane można usunąć. Dzięki temu nikt nie uruchomi auta „starym” kluczykiem.</p>
{tip('Najlepiej działa kilka warstw naraz: etui na kluczyk, blokada mechaniczna i dodatkowe zabezpieczenie elektroniczne.', 'shield-check')}
<h2>Gdy kluczyk zginie</h2>
<p>Zgubiony lub skradziony kluczyk keyless jak najszybciej usuń z pamięci auta. Pomożemy zaprogramować nowy komplet i wykasować ten, którego nie masz.</p>'''),
dict(slug='zgubione-wszystkie-kluczyki-do-auta', icon='key-round', cat='Samochód', min=4, service='programowanie-kluczy',
     short='Zgubione wszystkie kluczyki',
     title='Zgubione wszystkie kluczyki do auta – co teraz?',
     lead='Kluczyk przepadł, a zapasowego nie ma? Nowoczesny kluczyk to nie tylko kawałek metalu – ma chip immobilizera, który trzeba zaprogramować do auta. Wyjaśniamy, jak to działa i co przygotować.',
     body=f'''
<h2>Dlaczego nie wystarczy „dorobić klucza”</h2>
<p>W prawie każdym aucie z ostatnich dwudziestu kilku lat w kluczyku jest chip (transponder). Immobilizer pozwala uruchomić silnik tylko wtedy, gdy rozpozna zapisany w pamięci kluczyk. Dlatego sam nacięty grot otworzy drzwi, ale nie odpali auta – nowy kluczyk trzeba zaprogramować.</p>
<h2>Jakie masz możliwości</h2>
<ul>
<li><strong>Serwis dealerski</strong> – często oznacza zamówienie kluczyka, holowanie auta i czekanie.</li>
<li><strong>Mobilny specjalista</strong> – w wielu modelach kluczyk można przygotować i zaprogramować na miejscu, przy aucie. To zwykle szybsze, a często także tańsze.</li>
</ul>
<h2>Co przygotować</h2>
<ul>
<li>Dowód rejestracyjny i dowód osobisty – dane właściciela muszą się zgadzać.</li>
<li>Numer VIN (jest w dowodzie rejestracyjnym) – pozwala dobrać właściwy kluczyk.</li>
<li>Informację, jaki był kluczyk: zwykły, składany, karta, keyless.</li>
</ul>
<h2>Co ze zgubionym kluczykiem?</h2>
<p>Podczas programowania warto <strong>usunąć zgubiony kluczyk z pamięci auta</strong>. Jeśli ktoś go znajdzie, nie uruchomi Twojego samochodu. Jeśli kluczyk został skradziony razem z dokumentami, zgłoś to także na policję.</p>
{warn('Uważaj na ogłoszenia z bardzo niską ceną „za dorobienie kluczyka”. Zapytaj, czy cena obejmuje kluczyk, nacięcie grota i programowanie.')}
<h2>Po wszystkim: zrób zapasowy</h2>
<p>Gdy masz już działający kluczyk, od razu dorób drugi. Kopia, gdy jeden kluczyk działa, jest zwykle prostsza i tańsza niż ponowna sytuacja „zero kluczyków”.</p>'''),
dict(slug='zapasowy-kluczyk-do-auta', icon='key-square', cat='Samochód', min=3, service='programowanie-kluczy',
     short='Zapasowy kluczyk',
     title='Zapasowy kluczyk do auta – dlaczego warto go mieć',
     lead='Kupiłeś auto z jednym kluczykiem? To częste przy używanych samochodach. Dorobienie zapasowego, gdy masz działający klucz, jest prostsze i tańsze niż awaria, gdy zgubisz jedyny.',
     body=f'''
<h2>Ile kosztuje brak zapasowego kluczyka</h2>
<p>Gdy jedyny kluczyk zginie, dochodzą koszty dojazdu, otwarcia auta i programowania od zera – a czasem także holowania i dni bez samochodu. Zapasowy kluczyk zrobiony „na spokojnie” to zwykle ułamek tej kwoty.</p>
<h2>Ubezpieczenie AC a komplet kluczyków</h2>
<p>Sprawdź warunki swojej polisy AC. Wiele z nich wymaga, by po kradzieży auta oddać ubezpieczycielowi wszystkie kluczyki. Brak kompletu może skomplikować wypłatę odszkodowania.</p>
<h2>Kupujesz używane auto?</h2>
<ul>
<li>Zapytaj, ile kluczyków wydano do auta i ile dostajesz.</li>
<li>Rozważ usunięcie z pamięci auta kluczyków, których nie masz – i zaprogramowanie nowego zapasowego.</li>
</ul>
<h2>Jak przechowywać zapasowy kluczyk</h2>
<ul>
<li>W domu, w stałym miejscu – nigdy w samochodzie.</li>
<li>Nie przy kluczyku głównym (nie zgub obu naraz).</li>
<li>Kluczyk keyless – w etui blokującym sygnał lub metalowym pudełku.</li>
</ul>
{tip('Bateria w zapasowym kluczyku też się rozładowuje. Raz na rok sprawdź, czy pilot nadal działa.', 'battery-low')}'''),
dict(slug='pilot-od-auta-nie-dziala', icon='battery-low', cat='Samochód', min=4, service='programowanie-kluczy',
     short='Pilot od auta nie działa',
     title='Pilot od auta nie działa – 6 najczęstszych przyczyn',
     lead='Auto nie reaguje na pilota? Zanim wpadniesz w panikę, sprawdź kilka prostych rzeczy. Wiele usterek da się usunąć w kilka minut.',
     body=f'''
<h2>1. Rozładowana bateria w pilocie</h2>
<p>Najczęstsza przyczyna. Pierwszy objaw to malejący zasięg – trzeba podchodzić coraz bliżej. Typ baterii jest zwykle nadrukowany na starej (np. CR2032). Przy wymianie zwróć uwagę na biegunowość i kup baterię dobrej marki.</p>
<h2>2. Rozładowany akumulator w aucie</h2>
<p>Jeśli auto nie reaguje i nie mrugają kierunkowskazy, problem może leżeć po stronie samochodu. Większość pilotów ma <strong>ukryty grot awaryjny</strong>, a zamek bywa schowany pod osłoną na klamce – sprawdź w instrukcji auta, jak się do niego dostać.</p>
<h2>3. Zakłócenia radiowe</h2>
<p>W pobliżu nadajników, stacji bazowych czy niektórych urządzeń pilot może działać gorzej. Podejdź bliżej albo spróbuj z drugiej strony auta.</p>
<h2>4. Utrata synchronizacji</h2>
<p>W niektórych modelach po wymianie baterii pilot trzeba ponownie zsynchronizować z autem. Procedura bywa opisana w instrukcji – a jeśli nie, zrobi to specjalista.</p>
<h2>5. Uszkodzony pilot</h2>
<p>Wytarte przyciski, pęknięta obudowa, zalanie czy upadek mogą uszkodzić elektronikę. Często wystarczy nowa obudowa lub naprawa mikroprzełączników – bez kupowania całego kluczyka.</p>
<h2>6. Usterka w samochodzie</h2>
<p>Jeśli żaden kluczyk nie działa, przyczyna może być w aucie: odbiornik, moduł centralnego zamka albo silniczek zamka. Tu potrzebna jest diagnostyka.</p>
{tip('Zanim pilot zawiedzie, sprawdź w instrukcji, gdzie jest grot awaryjny i zamek w drzwiach. W stresie trudniej to znaleźć.')}'''),
dict(slug='jak-wybrac-uczciwego-slusarza', icon='shield-check', cat='Bezpieczeństwo', min=3, service='otwieranie-mieszkan-i-domow',
     short='Jak wybrać uczciwego ślusarza',
     title='Jak wybrać uczciwego ślusarza i nie dać się oszukać',
     lead='W stresie łatwo zgodzić się na wszystko. Kilka prostych zasad chroni przed zawyżonym rachunkiem i niepotrzebnym niszczeniem zamka.',
     body=f'''
<h2>1. Pytaj o cenę przed przyjazdem</h2>
<p>Poproś o orientacyjną cenę przez telefon i zapytaj, co obejmuje: dojazd, otwarcie, ewentualną nową wkładkę. Uczciwa firma nie ma z tym problemu.</p>
<h2>2. Uważaj na ogłoszenia „od 49 zł”</h2>
<p>Bardzo niska cena w reklamie często rośnie na miejscu – o „dopłatę nocną”, „trudny zamek” i „specjalne narzędzia”. Zapytaj wprost o cenę końcową w Twojej sytuacji.</p>
<h2>3. Sprawdź firmę</h2>
<ul>
<li>Opinie w Google i prawdziwe zdjęcia z realizacji.</li>
<li>Nazwa firmy, adres i NIP – a nie tylko anonimowy numer telefonu.</li>
<li>Paragon lub faktura za usługę.</li>
</ul>
<h2>4. Nie zgadzaj się od razu na rozwiercanie</h2>
<p>Jeśli ślusarz od razu chce wiercić, zapytaj dlaczego i czy jest inna możliwość. Wiele zamków da się otworzyć bez niszczenia. Czasem usunięcie wkładki jest konieczne – ale powinieneś wiedzieć o tym przed rozpoczęciem pracy.</p>
<h2>5. Weryfikacja tożsamości to dobry znak</h2>
<p>Fachowiec, który prosi o dokumenty, chroni także Ciebie. Ten, który otworzy każde drzwi bez pytania, mógłby równie dobrze otworzyć Twoje – komuś innemu.</p>
{tip('Zapisz numer sprawdzonej firmy w telefonie już dziś. W sytuacji awaryjnej nie będziesz musiał szukać w pośpiechu.', 'smartphone')}'''),
dict(slug='awaria-sterownika-objawy', icon='cpu', cat='Elektronika i DPF', min=4, service='sterowniki',
     short='Awaria sterownika – objawy',
     title='Awaria sterownika silnika lub immobilizera – objawy i co dalej',
     lead='Auto kręci, ale nie odpala? Miga kontrolka immobilizera, a komputer diagnostyczny nie widzi sterownika? To mogą być objawy usterki elektroniki. Wyjaśniamy, co je powoduje i jakie są rozwiązania.',
     body=f'''
<h2>Typowe objawy</h2>
<ul>
<li>Rozrusznik kręci, ale silnik nie zapala.</li>
<li>Miga lub świeci kontrolka kluczyka albo immobilizera.</li>
<li>Brak komunikacji ze sterownikiem podczas diagnostyki.</li>
<li>Tryb awaryjny, przypadkowe błędy, gaśnięcie silnika.</li>
<li>Problemy, które pojawiły się po zalaniu, uruchamianiu „na kable” lub wymianie akumulatora.</li>
</ul>
<h2>Najczęstsze przyczyny</h2>
<p>Sterowniki psują się najczęściej przez wilgoć i korozję, przepięcia oraz uszkodzone przewody i złącza. Często winny nie jest sam sterownik, tylko zasilanie, masa albo wtyczka – a to tańsza naprawa.</p>
<h2>Co możesz sprawdzić sam</h2>
<ul>
<li>Stan akumulatora – zbyt niskie napięcie potrafi dawać dziwne objawy.</li>
<li>Bezpieczniki opisane w instrukcji auta.</li>
<li>Drugi kluczyk – jeśli z nim auto odpala, problem jest w kluczyku, a nie w sterowniku.</li>
</ul>
<h2>Jakie są rozwiązania</h2>
<ul>
<li><strong>Naprawa sterownika</strong> – często wyraźnie tańsza niż nowy.</li>
<li><strong>Używany sterownik z adaptacją</strong> – musi zostać dopasowany do Twojego auta i kluczyków.</li>
<li><strong>Nowy sterownik</strong> – z kodowaniem do auta.</li>
</ul>
{warn('Nie kupuj używanego sterownika „w ciemno”. Numer części i oprogramowania musi pasować do Twojego auta – zadzwoń, zanim kupisz.')}
{tip('Przy uruchamianiu auta „na kable” zawsze podłączaj przewody we właściwej kolejności i nie rozłączaj ich przy pracującym silniku – to częsta przyczyna przepięć.', 'battery-low')}'''),
dict(slug='filtr-dpf-jak-dbac', icon='filter', cat='Elektronika i DPF', min=4, service='filtry-dpf',
     short='Filtr DPF – jak dbać',
     title='Filtr DPF – jak dbać, kiedy czyścić i czego unikać',
     lead='Filtr cząstek stałych zatrzymuje sadzę ze spalin silnika Diesla. Gdy się zapcha, auto traci moc i przechodzi w tryb awaryjny. Kilka nawyków wyraźnie wydłuża jego życie.',
     body=f'''
<h2>Jak działa filtr DPF</h2>
<p>Filtr zbiera sadzę, a co jakiś czas ją wypala – to tak zwana regeneracja. Najlepiej przebiega podczas dłuższej jazdy ze stałą prędkością, gdy spaliny są gorące. W krótkich, miejskich trasach regeneracja często nie ma szans się zakończyć.</p>
<h2>Objawy zapchanego filtra</h2>
<ul>
<li>Kontrolka DPF lub komunikat na desce rozdzielczej.</li>
<li>Spadek mocy, tryb awaryjny.</li>
<li>Częste regeneracje: podwyższone obroty na postoju, pracujący wentylator po wyłączeniu silnika, wyższe spalanie.</li>
</ul>
<h2>Jak dbać o filtr</h2>
<ul>
<li>Regularnie jedź dłuższą trasą poza miastem – zwłaszcza gdy na co dzień jeździsz krótko.</li>
<li>Nie przerywaj regeneracji, jeśli wiesz, że trwa – dokończ jazdę, jeśli to możliwe.</li>
<li>Używaj oleju zalecanego przez producenta (zwykle low SAPS).</li>
<li>Dbaj o sprawność wtrysków, zaworu EGR, turbosprężarki i termostatu – ich usterki zwiększają ilość sadzy.</li>
</ul>
<h2>Co, gdy filtr jest już zapchany</h2>
<ol>
<li><strong>Diagnostyka</strong> – odczyt zapełnienia, błędów i pracy czujników.</li>
<li><strong>Regeneracja serwisowa</strong> – wymuszona komputerem.</li>
<li><strong>Czyszczenie filtra</strong> – gdy regeneracja nie wystarcza.</li>
<li><strong>Wymiana</strong> – dopiero gdy filtr jest uszkodzony.</li>
</ol>
{warn('Samochód bez wymaganego filtra DPF nie spełnia warunków technicznych. Usunięcie filtra z auta jeżdżącego po drogach publicznych grozi niezaliczonym przeglądem i mandatem.')}'''),
]

POLITYKA = '''
<h2>Administrator danych</h2>
<p>Administratorem danych osobowych jest %%NAZWA%%, %%ADRES%%, NIP: %%NIP%%. Kontakt: <a href="%%TELHREF%%">%%TEL%%</a>, <a href="%%MAILHREF%%">%%EMAIL%%</a>.</p>
<h2>Jakie dane przetwarzamy</h2>
<p>Strona nie zawiera formularzy wysyłających dane na serwer. Formularz kontaktowy tylko przygotowuje wiadomość, którą sam wysyłasz SMS-em lub e-mailem ze swojego telefonu lub komputera. Przetwarzamy dane, które nam w ten sposób przekażesz (np. imię, numer telefonu, opis sytuacji), oraz dane podane podczas rozmowy telefonicznej.</p>
<h2>Cel i podstawa</h2>
<p>Dane przetwarzamy, aby odpowiedzieć na Twoje zapytanie i wykonać usługę (art. 6 ust. 1 lit. b RODO), a także w celu wystawienia dokumentów sprzedaży i rozliczeń wymaganych przepisami (art. 6 ust. 1 lit. c RODO).</p>
<h2>Jak długo</h2>
<p>Dane z zapytań przechowujemy do czasu ich obsłużenia, a dokumenty księgowe – przez okres wymagany przepisami.</p>
<h2>Pliki cookies i usługi zewnętrzne</h2>
<p>Strona nie używa plików cookies ani narzędzi analitycznych. Na stronie Kontakt może być wyświetlana mapa Google – po jej załadowaniu Google może przetwarzać dane techniczne (np. adres IP) zgodnie z własną polityką prywatności. Dostawca hostingu może zapisywać standardowe logi serwera.</p>
<h2>Twoje prawa</h2>
<p>Masz prawo do dostępu do swoich danych, ich sprostowania, usunięcia, ograniczenia przetwarzania i wniesienia sprzeciwu, a także prawo do skargi do Prezesa Urzędu Ochrony Danych Osobowych.</p>
'''

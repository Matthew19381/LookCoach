# LookCoach — Plan działania 2026-11-01

> Źródło: przegląd całego systemu 2026-11-01 (kod LookCoach + kontrakt huba
> `System-Glowny/docs/INTEGRACJA-MODULOW.md` + odbiorcy w ForgeBody i Diecie).
> Poprzedni plan (zamknięty): `decisions/ACTION_PLAN_2026-08-09_wykonane_2026-08-23.md`.
>
> **Decyzje właściciela (2026-11-01):**
> - D1. Skóra i linia włosów analizowane ze zdjęcia **z przodu** (nie z „back”).
> - D2. System jest **jednoosobowy** (`user_id = 1` z huba) — bez kont i logowania,
>   ale API ma być dostępne tylko lokalnie / dla huba.
> - D3. Dane mają być **wymieniane między modułami** tak, żeby plan był dopasowany
>   do celów: LookCoach nie liczy sam snu/stresu/żywienia „na oko”, tylko bierze je
>   z modułów-źródeł i wysyła swoje potrzeby do ForgeBody / Diety.
> - D4. Język interfejsu: **polski**.
> - D5. Najpierw plan (ten plik), potem realizacja wg kolejności faz.
> - D6 (2026-11-02). Zmiany w hubie, ForgeBody i Diecie wolno robić — na gałęziach `claude/...`,
>   bez merge do master (merge decyduje właściciel).
> - D7. Bez HEIC (tylko JPEG/PNG/WEBP; przeglądarka konwertuje zdjęcia z iPhone'a).
> - D8. Podgląd fryzury/zarostu na własnym zdjęciu (generowanie obrazu) — **tak, jako opcja**.
> - D9. Kolorystyka ubrań — **tak, jako `[HIPOTEZA]`**.
> - D10. „Do projektu zostanie dodane AI” = **asystent AI wewnątrz LookCoach** (Faza 8).
>
> Zasady, które obowiązują w każdym punkcie: **LC-9** (zero liczbowych ocen
> atrakcyjności), **LC-1** (rct/meta muszą mieć PMID/DOI, reszta oznaczona
> `[HIPOTEZA]` / „porada stylistyczna”), **LC-4** (LookCoach nie układa treningów
> ani diet — wysyła potrzeby), **LC-8** (Health Safety Layer przed każdą rekomendacją).
>
> Każdy punkt: co zrobić → pliki → kryterium akceptacji. Odhaczać dopiero po
> spełnieniu kryterium, nie po napisaniu kodu.

---

## Stan wyjściowy (zmierzony 2026-11-01)

| Element | Wynik |
|---|---|
| Testy backend | 335 ✅ (CLAUDE.md mówi 225 — nieaktualne) |
| Testy frontend | 93 ✅ (CLAUDE.md mówi 85) |
| `vite build` | ✅ |
| `verify_evidence_db` | ✅ 29 wpisów, 9 rct/meta ze źródłem |
| `npm ci` | ❌ `package-lock.json` niezgodny z `package.json` |
| `pip install -r requirements.txt` na Pythonie 3.13 | ❌ `pillow==10.3.0` nie buduje się (Docker 3.12 działa) |
| CI | ❌ brak |

---

## FAZA 0 — Higiena i powtarzalność (blokuje resztę)

- [x] **0.1 Zsynchronizuj `package-lock.json`.**
  Pliki: `code/frontend/package-lock.json`.
  Kryterium: `npm ci` w czystym katalogu kończy się sukcesem.
- [x] **0.2 Podnieś `pillow` do wersji z kołami dla 3.12 i 3.13** (np. `pillow>=11,<12`).
  [WYKONANE 2026-11-02: pillow 11.3.0 + sqlalchemy 2.0.36 — 2.0.29 też nie działał na 3.13]
  Pliki: `code/backend/requirements.txt`.
  Kryterium: `pip install -r requirements.txt` działa na 3.12 i 3.13; testy zielone.
- [x] **0.3 `.gitignore` dla danych wrażliwych uruchamianych z `code/`.**
  Dopisz `code/uploads/`, `uploads/`, `.cache/`, `code/.cache/`, `code/backend/.cache/`.
  Kryterium: po uploadzie zdjęcia i analizie `git status` jest czysty.
- [x] **0.4 Ujednolić ścieżki `uploads/` i `.cache/`** — kotwiczyć do katalogu
  backendu (jak `database.py`), nie do CWD.
  Pliki: `main.py`, `routers/photos.py`, `services/gemini_vision.py`.
  Kryterium: start z `code/` i z `code/backend/` zapisuje do tego samego katalogu.
  [WYKONANE 2026-11-02: `backend/paths.py`; przy okazji naprawia Dockera — zdjęcia lądowały w
  `/app/uploads`, poza wolumenem `/app/backend/uploads`, i znikały z kontenerem]
- [x] **0.5 CI (GitHub Actions)**: pytest + vitest + `verify_evidence_db` + `ruff`
  + `vite build` na każdy push/PR.
  Pliki: `.github/workflows/ci.yml`.
  Kryterium: zielony przebieg na gałęzi.
- [x] **0.6 Aktualizacja dokumentacji stanu**: liczby testów w `CLAUDE.md`,
  stopka `TASKS.md`, zamknięcie/archiwizacja `IMPROVEMENTS.md` (→ `decisions/IMPROVEMENTS_2026-06_archiwum.md`) (z czerwca, większość
  zrobiona), `memory/projects/Wyglad.md` (React 18, 7 routerów — nieaktualne).
  Kryterium: brak sprzeczności z kodem (sprawdzone ręcznie).

---

## FAZA 1 — Usunięcie atrap i naruszeń LC-1 / LC-9 (krytyczne)

- [x] **1.1 Usuń zmyślony wykres „Look Score”.**
  `code/frontend/src/pages/ProgressTracker.jsx:46` — `50 + i * 5` rośnie o 5 pkt
  przy każdym zdjęciu niezależnie od analizy.
  Zastąp **jakościową osią czasu** (pkt 4.3). Do tego czasu — sekcja usunięta.
  Kryterium: w UI brak słowa „Score” w kontekście wyglądu; test vitest to pilnuje.
- [x] **1.2 Usuń `delta_score` z `/progress/compare`** (zawsze `0.0`).
  Pliki: `routers/progress.py`, `ProgressTracker.jsx`.
  Kryterium: odpowiedź bez pola liczbowego; test.
- [x] **1.3 Rekomendacje z prawdziwej analizy.** `routers/recommendations.py:16`
  używa pustego `user_analysis`. Wydziel funkcję `load_latest_analysis(db, user_id)`
  (logika z `routers/analysis.py:get_latest_analysis`) i użyj jej w rekomendacjach,
  Confidence, Posture, Video Learning, Aesthetic Training.
  Pliki: nowy `services/analysis_store.py`, routery j.w.
  Kryterium: test — analiza z `focus_areas=[skincare high]` zmienia kolejność rekomendacji.
  [WYKONANE 2026-11-02: `services/analysis_store.py`; ponadto: dźwignia (lever) wnosi
  skórę/włosy do rekomendacji, ROI sortuje w obrębie priorytetu, EvidenceEngine nie mutuje
  już globalnego `EVIDENCE_DB`; strona Postawy i Wideo też miały atrapy — usunięte,
  nowy `GET /posture/assessment`; analiza sylwetki bez `v_taper_score`]
- [x] **1.4 Confidence bez atrapy.** `routers/confidence.py:12` `dummy_analysis` →
  dane z 1.3; przy braku analizy komunikat „najpierw zrób zdjęcia”.
  Kryterium: test na brak analizy i na realną analizę.
- [x] **1.5 Usuń `/confidence/attractiveness-impact`.** Liczba „do 20%” bez źródła
  (LC-1) i procent atrakcyjności (LC-9).
  Pliki: `services/confidence_presence.py:161`, router, `api/client.js`,
  `ConfidencePresence.jsx`, testy.
  Kryterium: `grep -ri attractiveness_boost code/` puste.
- [x] **1.6 Event Mode oznaczony jako `[HIPOTEZA]`** — backend zwraca
  `evidence_level: "hipoteza"` + ostrzeżenie; UI pokazuje baner.
  (CLAUDE.md twierdzi, że już jest — nie jest.)
  Kryterium: test backend + vitest na baner.
  [WYKONANE 2026-11-02: + filtr LC-8 (nerki → bez wody/sodu); naprawione pole `emergency_day_of`]
- [x] **1.7 Wyniki „X/100” w Sen / Stres / Żywienie** → kategorie
  (`dobry / do poprawy / wymaga uwagi`) z listą czynników; patrz też Faza 3
  (dane mają przychodzić z modułów-źródeł).
  Pliki: `services/sleep_engine.py`, `stress_engine.py`, `nutrition_looks.py`,
  odpowiednie strony.
  Kryterium: żadna strona nie renderuje `/100`.
  [WYKONANE 2026-11-02: `services/lifestyle_status.py`; przy okazji naprawione porównanie godzin
  snu jako tekstu. Dane z modułów-źródeł — Faza 3.8]
- [x] **1.8 `integrations/output` zwraca zawsze pustą listę** — usunąć albo zwracać
  realne rekomendacje (po 1.3). [USUNIĘTE 2026-11-02 — nikt go nie wołał, także hub]
- [x] **1.9 Placeholder `_recompose_plan`** w `services/feedback_loop.py:313` —
  dokończyć (ROIEngine na realnych danych) albo usunąć ścieżkę z API.
  [WYKONANE 2026-11-02: protokoły to rutyny, nie wpisy EVIDENCE_DB — wybór 3 najlepiej
  utrzymywanych protokołów opisany uczciwie; usunięty też udawany `POST /thresholds`]

---

## FAZA 2 — Bezpieczeństwo i prywatność zdjęć (D2: jeden użytkownik, ale dane wrażliwe)

- [x] **2.1 Walidacja uploadu**: dozwolone tylko JPEG/PNG/WEBP/HEIC (sprawdzane
  przez Pillow, nie po nazwie), limit rozmiaru (np. 15 MB), nazwa pliku generowana
  przez serwer z rozszerzeniem wg faktycznego formatu, usunięcie EXIF (GPS).
  Pliki: `routers/photos.py`.
  Kryterium: testy — `.html` odrzucony, 20 MB odrzucony, EXIF GPS usunięty.
  [WYKONANE 2026-11-02: `services/photo_storage.py`; HEIC pominięty (D7); orientacja z EXIF
  zachowana przed usunięciem metadanych]
- [x] **2.2 Nasłuch tylko lokalny / w sieci Dockera** (`--host 127.0.0.1` w dev,
  dokumentacja w `docs/DEPLOYMENT.md`). [WYKONANE: Docker `127.0.0.1:8010`, Ollama też;
  frontend w LAN świadomie (telefon) — opisane]
- [x] **2.3 Wspólna weryfikacja `X-Module-Key`** (`hmac.compare_digest`) jako
  dependency; podpiąć też pod `POST /api/v1/directives` (dziś bez autoryzacji).
  **Uwaga:** hub w `broadcast_directive` nie wysyła nagłówka — wymaga zmiany
  po stronie huba (H-4). Do tego czasu: akceptuj bez klucza tylko z `127.0.0.1`.
  [WYKONANE: `backend/security.py`; zły klucz odrzucany także z localhost]
- [x] **2.4 Kaskadowe usuwanie**: `DELETE /photos/{id}` usuwa też `analyses`
  i wpis z `.cache`. Migracja Alembic (`ondelete="CASCADE"`).
  Kryterium: test — po usunięciu brak osieroconych wierszy.
  [WYKONANE: kaskada ORM (SQLite nie egzekwuje FK) + sprzątanie sierot przy starcie
  (`init_db` nie uruchamia Alembica, więc migracja danych by się nie wykonała)]
- [x] **2.5 Eksport i trwałe usunięcie wszystkich danych** (`GET /api/v1/data/export`
  → ZIP, `DELETE /api/v1/data` z potwierdzeniem). UI: Ustawienia → Prywatność.
  [WYKONANE: `services/data_privacy.py` (generycznie po tabelach z `user_id`), strona Prywatność]
- [x] **2.6 Obsługa błędu analizy bez wycieku wyjątku** (`analysis.py` zwraca
  `str(e)` do klienta) → log + komunikat ogólny.

---

## FAZA 3 — Wymiana danych z ekosystemem (D3) — **najważniejsza dla celów**

### Stan faktyczny (zweryfikowany w kodzie trzech repo, 2026-11-01)

| Przepływ | Stan | Problem |
|---|---|---|
| LookCoach → hub: `protocol_done/skipped` | ✅ działa (Consistency Tracker) | brak kolejki/retry — event ginie przy wyłączonym hubie |
| LookCoach → hub: `state_observation` | ❌ funkcja istnieje, **nikt jej nie wywołuje** | — |
| LookCoach → ForgeBody: `aesthetic_priority` | ❌ `publish_aesthetic_priority_directive` **nigdzie nie wywoływana** | 1) hub nie ma reguły, która z eventu zrobi dyrektywę; 2) `broadcast_directive` wysyła do **wszystkich** modułów, bez adresata; 3) payload niezgodny: LookCoach wysyła `priority_area: str`, ForgeBody czyta `payload.muscle_groups: list` (zagnieżdżone `payload`), a hub spłaszcza pola do top-level |
| LookCoach → Dieta: `nutrition_needs` | ❌ funkcja nigdzie nie wywoływana | Dieta przyjmuje tylko `survival_mode/priority/quiet_hours` — nie ma czym odebrać sodu/nabiału |
| Hub → LookCoach: dyrektywy | ✅ `survival_mode`, `quiet_hours` | `priority` zapisywana, ale **nigdzie nie używana**; `quiet_hours` też nie |
| Inne moduły → LookCoach: dane (waga, obwody, sen, stres, sód) | ❌ brak | `POST /integrations/event` przyjmuje stary format (`source_module/payload`, nie `module/data`) i tylko zapisuje — nic nie czyta tych eventów |
| LookCoach → hub: plan dnia (`suggested_items`) | ✅ rutyny pielęgnacji | brak przypomnienia o sesji zdjęć kontrolnych |

### 3A. Po stronie LookCoach

- [x] **3.1 Kolejka wychodząca + retry + idempotencja** (wzorzec
  `LinguaAI/backend/services/sync_service.py`): tabela `outbox_events`, wysyłka
  w tle, `client_event_id`, ponawianie z backoffem. Kontrakt huba wymaga, żeby
  błąd sieci nie blokował UX i nie gubił eventów.
  Kryterium: test — hub niedostępny → event czeka → hub wraca → event wysłany raz.
  [WYKONANE 2026-11-02: `models/outbox.py`, `services/outbox.py`, worker co 60 s w `main.lifespan`]
- [x] **3.2 Mapa „analiza → potrzeby treningowe”** (`services/goal_router.py`):
  z `body.missing_muscles`, `body.asymmetries`, `posture_notes` oraz celów profilu
  wylicz `muscle_groups` w nazwach z mapy ForgeBody (`side_delts`, `upper_chest`,
  `rear_delts`, `lats_width`, …) + `duration_weeks` + `reason` + `evidence_id`.
  Kryterium: testy jednostkowe mapowania (np. „forward head posture” → `rear_delts`
  + korekta postawy jako akcesoria, nie własny plan).
- [x] **3.3 Wysyłka `aesthetic_priority` po zakończonej analizie ciała**
  (i przy zmianie celów) — w formacie uzgodnionym w H-1:
  `{"directive":"aesthetic_priority","target_module":"forge-body","payload":{"muscle_groups":[…],"duration_weeks":4,"reason":"…"}}`.
  Bez duplikatów: wysyłka tylko gdy zestaw się zmienił.
  Kryterium: test integracyjny z mockiem huba; event widoczny w hubie.
- [x] **3.4 Mapa „analiza → potrzeby żywieniowe”** — tylko pozycje z dowodami:
  - obrzęk twarzy (`swelling medium/high`) → limit sodu (`sodium_limit_mg`) + nawodnienie;
  - trądzik (`problems: acne`) → dieta o niskim ładunku glikemicznym
    (RCT: Smith 2007, PMID 17616769 — ZWERYFIKOWANE na PubMed 2026-11-02, wpis `nutrition_005`;
    zastrzeżenie: efekt częściowo przez spadek masy ciała);
    nabiał → tylko jako `[HIPOTEZA]` (badania obserwacyjne);
  - przerzedzenie włosów → **nie** suplementy na ślepo; sugestia badań
    (ferrytyna, wit. D) jako `[HIPOTEZA]` + disclaimer.
  Kryterium: każda pozycja ma `evidence_id` lub flagę hipotezy; test.
  [WYKONANE: `services/goal_router.py`; włosy/badania krwi — odłożone do 4.x jako hipoteza]
- [x] **3.5 Wysyłka `nutrition_needs` do Diety** (format z H-2), z Health Safety
  (choroba nerek → brak zaleceń dot. białka/wody).
- [x] **3.6 `state_observation` po analizie** — jakościowe obserwacje
  (obrzęk, stan skóry, linia włosów) do huba, bez liczb, dla korelacji w hubie
  i dla Mentalności.
- [x] **3.7 Konsumpcja dyrektywy `priority`** — jeśli hub ustawi priorytet
  (np. `skincare`), rekomendacje i plan dnia stawiają ten obszar na górze.
  `quiet_hours` → brak przypomnień w tych godzinach.
  Kryterium: testy.
  [WYKONANE 2026-11-02: `priority` → kategoria na samej górze rekomendacji. `quiet_hours` jest
  zapisywane, a zastosowanie wejdzie z powiadomieniami (5.5) — dziś LookCoach nic nie wysyła]
- [ ] **3.8 Klient danych z innych modułów** (`services/ecosystem_client.py`):
  odczyt z huba `GET /api/v1/integrations/events?module=…&event_type=…&since=…`
  (sprawdzić wymagania `get_read_user` — H-5):
  - ForgeBody `measurement_logged` (waga, % tłuszczu, talia) i `workout_completed`
    → zakładka „Ciało” pokazuje trend pomiarów (liczby pomiarowe, nie ocena),
  - Dieta `weight_logged`, `meal_logged` (sód dzienny) → korelacja z obrzękiem,
  - Mentalność / Affect `affect_logged` (sen, stres) → zastępuje ręczne ankiety
    w Sen/Stres (pkt 1.7, INT-4 z TASKS).
  Fallback: gdy hub niedostępny — ostatnie dane z lokalnego cache, w UI „dane z …”.
- [x] **3.9 Napraw schemat `POST /integrations/event`** na kontrakt 1.2
  (`module`, `data`), zachowując zgodność wstecz; odbiór eventów zasila 3.8.
- [x] **3.10 Plan dnia**: pozycja „Zdjęcia kontrolne” co 14–28 dni
  (`complete_on: ["state_observation:observation_type=photo_session"]`),
  nie częściej (wspiera LC-9 — przeciw kompulsywnemu skanowaniu).
- [ ] **3.11 LC-4: usuń własne plany treningowe i jadłospisy.**
  `services/aesthetic_training.py:generate_plan` (serie/powtórzenia) oraz
  `services/nutrition_looks.py:get_meal_plan` dublują ForgeBody i Dietę.
  Zostaw edukację „dlaczego”, a przycisk „Wyślij do ForgeBody / Diety” uruchamia 3.3 / 3.5.
  Kryterium: brak endpointów generujących serie/powtórzenia i jadłospisy.
- [ ] **3.12 Panel „Połączenia” w UI**: status huba, ostatnio wysłane dyrektywy
  i odpowiedź modułów, ostatnie dane pobrane z ForgeBody/Diety/Mentalności.

### 3B. Zmiany po stronie innych repo (do zrobienia w ich sesjach — tu tylko śledzenie)

> Stan 2026-11-02: H-1..H-5 zrobione na gałęziach `claude/lookcoach-integracja` w repo
> System-Glowny, ForgeBody i Dieta (wypchnięte, **bez merge** — D6). Hub: event
> `module_directive` (kontrakt §1.5). Do merge: najpierw hub, potem ForgeBody/Dieta, na końcu
> ta gałąź LookCoach (działa też bez nich — eventy czekają w kolejce lub hub odpowie 422,
> co oznacza je jako `failed`).

- [x] **H-1 (System-Glowny)**: dyrektywy z adresatem — `target_module` w payloadzie
  `broadcast_directive` (wysyłka tylko do wskazanego modułu) + reguła
  „event `aesthetic_priority_directive` od lookcoach → dyrektywa `aesthetic_priority`
  do forge-body”, z zachowaniem zagnieżdżonego `payload`.
- [x] **H-2 (System-Glowny + Dieta)**: nowa dyrektywa `nutrition_needs`
  (`sodium_limit_mg`, `low_glycemic`, `hydration_ml`, `reason`, `evidence_id`);
  Dieta: dopisać do `KNOWN` w `backend/routers/directives.py`, model stanu,
  użycie w planie posiłków (limit sodu w doborze produktów — pole `sodium_mg` już istnieje).
- [x] **H-3 (ForgeBody)**: poprawka mapy w `routers/directives.py`
  (`"quads_special populations_"` to literówka) — oraz `rear_delts` → „rear delts”, czego nie
  ma w żadnym splicie; teraz test pilnuje zgodności ze SPLITS.
- [ ] **H-3b (ForgeBody)**: `aesthetic_priority` tylko DOKŁADA grupy do `focus_muscles`
  (nigdy nie zdejmuje) i ignoruje `duration_weeks`. Potrzebne: zapamiętanie, które grupy dodał
  LookCoach (nowa kolumna/tabela + migracja), zastępowanie zestawu i wygasanie po N tyg.
- [ ] **H-2b (Dieta)**: liczenie sodu w dzienniku posiłków i uwzględnianie `nutrition_needs`
  (limit sodu, niski ładunek glikemiczny) przy układaniu planu; dziś potrzeby są tylko zapisane
  i widoczne w `GET /directives/{user_id}`.
- [x] **H-4 (System-Glowny)**: `broadcast_directive` wysyła `X-Module-Key`
  (moduły mogą wtedy wymagać klucza na `/directives`).
- [x] **H-5 (System-Glowny)**: odczyt eventów innych modułów kluczem modułu
  (dziś `GET /integrations/events` wymaga `get_read_user`) — albo nowy endpoint
  „dane dla modułu” z białą listą typów eventów.
- [ ] **H-6 (Mentalność)**: przyjmowanie `state_observation` z LookCoach
  (sygnał częstotliwości skanowania — pkt 5.6).

---

## FAZA 4 — Analiza: nowe parametry wyglądu (D1) i jakość zdjęć

Wspólne wymaganie dla 4.x: wynik **wyłącznie kategoryczny/opisowy**, rekomendacja
z poziomem dowodów (`rct/meta/obs/ekspert/hipoteza` albo „porada stylistyczna”),
każda zmiana promptu = test na kształt JSON + test na brak liczb ocen.

- [ ] **4.0 Nowe mapowanie zdjęć (D1).**
  - przód → twarz + **skóra** + **linia włosów** + **brwi** + **zarost**,
  - bok → sylwetka, postawa, profil (podbródek/szyja),
  - tył → plecy/postawa od tyłu + **czubek głowy (gęstość włosów)**.
  Pliki: `routers/analysis.py`, `services/gemini_vision.py`, `PhotoUpload.jsx`
  (instrukcje kadrowania), migracja jeśli trzeba nowych kolumn (`brows_data`,
  `beard_data`, `style_data` w `analyses` albo jedna kolumna JSON `extras`).
  Kryterium: test — zdjęcie przód zapisuje `skin` i `hair.hairline`; tył `hair.crown`.
- [ ] **4.1 Brwi.** Prompt: kształt (prosty/łukowaty/opadający), gęstość
  (rzadkie/średnie/gęste), symetria (symetryczne/lekka/wyraźna asymetria),
  zarośnięcie środka. Rekomendacje: pielęgnacja/regulacja „tylko nadmiar”,
  konsultacja ze stylistą; serum (bimatoprost — tylko na receptę, high-risk
  disclaimer). Poziom: porada stylistyczna + ewentualne źródła dla bimatoprostu.
- [ ] **4.2 Fryzura.** Wejście: kształt twarzy (owalna/okrągła/kwadratowa/
  podłużna/serce — jako opis, `[HIPOTEZA]`, brak twardych dowodów), typ włosa
  (prosty/falowany/kręcony), gęstość i linia włosów (z 4.0), **czas na stylizację**
  i **ograniczenia** (praca, sport) z profilu. Wynik: 3 propozycje fryzur z opisem
  „dlaczego” + „co powiedzieć fryzjerowi” + produkty do stylizacji.
  Opcjonalnie później: podgląd fryzury na zdjęciu (generacja obrazu) — osobna decyzja.
- [ ] **4.3 Zarost.** Prompt: gęstość (brak/rzadki/średni/pełny), równomierność
  (łaty), linia policzka/szyi. Rekomendacje: styl brody do konturu żuchwy
  (porada stylistyczna), linia szyi, pielęgnacja (olejek, trymer);
  minoxidil na brodę → `[obs/małe RCT]` + Health Safety (choroba serca, ciąża partnerki
  nie dotyczy — tylko kontakt), disclaimer obowiązkowy.
- [ ] **4.4 Budowa ciała.** Jakościowo ze zdjęć (proporcje ramiona/talia:
  „wąskie/zrównoważone/szerokie”, postawa) **+ pomiary z ForgeBody (3.8)**.
  Zero somatotypów i ocen; wynik zasila 3.2 (`muscle_groups` dla ForgeBody)
  i 3.4 (żywienie dla Diety). Kryterium: test — brak liczb poza pomiarami użytkownika.
- [ ] **4.5 Okolica oczu** (cienie, opuchnięcie) → powiązanie ze snem (3.8)
  i sodem (Dieta) — tylko korelacja jakościowa.
- [ ] **4.6 Uśmiech/zęby** (przebarwienia: brak/lekkie/wyraźne) → higiena,
  wybielanie (dowody dla nadtlenku karbamidu — zweryfikować PMID), dentysta.
- [ ] **4.7 Okulary i oprawki** (jeśli nosi): propozycje kształtu oprawek do kształtu
  twarzy — porada stylistyczna.
- [ ] **4.8 Dopasowanie ubioru do sylwetki** (fit, długości, kroje) — porada
  stylistyczna; kolorystyka („typ urody”) jako osobna sekcja oznaczona `[HIPOTEZA]` (D9).
- [ ] **4.9 Kontrola jakości zdjęcia przed analizą** (lokalnie, Pillow): ostrość
  (wariancja Laplasjanu), ekspozycja (histogram), rozdzielczość, wykrycie twarzy
  dla „przód”. Zła jakość → komunikat „zrób ponownie: …”, analiza nie startuje.
  Kryterium: testy na rozmyte/ciemne obrazy.
- [ ] **4.10 Nakładka-szablon w aparacie** (PWA, `getUserMedia`): sylwetka/owal
  do ustawienia kadru + przypomnienie o tym samym świetle i odległości.
- [ ] **4.11 Wybór modelu AI zgodny z dokumentacją**: domyślnie `AI_SERVICE=gemini`
  (dziś `openrouter`), lub zaktualizować CLAUDE.md — decyzja przy realizacji;
  klucz cache zależny od modelu i wersji promptu (dziś `prompt[:50]`).
- [ ] **4.13 Podgląd fryzury/zarostu na własnym zdjęciu (D8)** — opcjonalny przycisk przy
  propozycjach z 4.2/4.3; model generowania obrazu przez OpenRouter/Gemini; wynik tylko
  w pamięci/na żądanie (nie zapisywany jako „po”), ostrzeżenie LC-9 („to wizualizacja, nie
  cel do porównywania”), informacja o koszcie przed wygenerowaniem, limit dzienny.
- [ ] **4.12 Profil celów**: formularz celów (co chcę poprawić: skóra/włosy/
  sylwetka/styl, termin, ile czasu dziennie). Cele trafiają do rekomendacji,
  do `goal_router` (3.2/3.4) i do huba (`priority`).

---

## FAZA 5 — Postęp i motywacja (bez scoringu)

- [ ] **5.1 Jakościowa oś czasu** (zastępuje „Look Score”): dla każdej sesji
  zdjęć etykiety stanu (obrzęk, skóra, linia włosów, brwi, zarost, postawa)
  i zmiana słowna względem poprzedniej („obrzęk: średni → niski”).
- [ ] **5.2 Porównanie przed/po**: suwak lub obok siebie, automatyczne wyrównanie
  (twarz/sylwetka), różnice w obserwacjach słownych.
- [ ] **5.3 Correlation Engine (jakościowy)**: „w tygodniach ze snem < 6 h obrzęk
  częściej średni”, „przy sodzie > limitu …” — dane z 3.8; komunikaty tylko
  przy wystarczającej liczbie obserwacji, z zastrzeżeniem „korelacja ≠ przyczyna”.
- [ ] **5.4 Dashboard „Dziś”** jako strona startowa: 3 akcje na dziś
  (rutyna, protokół, ewentualnie zdjęcia kontrolne), stan dyrektyw huba
  (survival/priority), ostatnie dane z innych modułów.
- [ ] **5.5 Przypomnienia PWA (push)** — rano/wieczór skincare, zdjęcia co 2–4 tyg.;
  respektują `quiet_hours` (3.7) i `survival_mode`.
- [ ] **5.6 Detektor kompulsywnego skanowania** (otwarte E-3 z TASKS): > N analiz
  w tygodniu lub wielokrotne zdjęcia tego samego dnia → miękki komunikat, limit,
  `state_observation` do Mentalności (H-6).
- [ ] **5.7 Skaner kosmetyków — kod kreskowy** (Open Beauty Facts) + ostrzeżenia
  z Health Safety (ciąża, alergie) obok istniejącego skanu składu.

---

## FAZA 6 — UX i język (D4)

- [ ] **6.1 Cały interfejs po polsku** (15 stron + Layout + komunikaty błędów API
  pokazywane w UI). Teksty w jednym pliku `src/i18n/pl.js`, żeby łatwo poprawiać.
  Kryterium: vitest — brak angielskich etykiet nawigacji.
- [ ] **6.2 Nawigacja w 4 grupach**: *Analiza* (Zdjęcia, Wyniki, Postęp),
  *Plan* (Dziś, Rekomendacje, Pielęgnacja, Regularność), *Styl życia*
  (Sen, Stres, Żywienie, Postawa), *Więcej* (Eksperymenty, Wideo, Event Mode,
  Pewność siebie, Połączenia, Prywatność). Menu mobilne (hamburger / dolny pasek).
- [ ] **6.3 Stany puste i błędy**: każda strona bez danych mówi, co zrobić dalej
  (np. „Zrób zdjęcia z przodu, żeby zobaczyć analizę skóry”).
- [ ] **6.4 Dostępność**: kontrast, etykiety `aria`, obsługa klawiaturą.

---

## FAZA 7 — Jakość techniczna (ciągła)

- [ ] **7.1 Type hints w routerach i serwisach** + `mypy` w CI (stopniowo).
- [ ] **7.2 `.pre-commit-config.yaml`** (ruff, ruff-format, trailing whitespace).
- [ ] **7.3 `logging` zamiast `print`** w `main.py`, `gemini_vision.py`, `local_llm.py`.
- [ ] **7.4 Wersja API spójna** (`main.py` mówi `0.2.0`, TASKS `v0.3.0`).
- [ ] **7.5 `datetime.utcnow()` → `datetime.now(UTC)`** (ostrzeżenia w testach).
- [ ] **7.8 Alembic rozjechany z modelami**: tabele `adherence_logs`, `protocol_adherence`,
  `consistency_metrics`, `directive_states`, `skin_reactions`, `skincare_products`,
  `ingredient_usage`, `outbox_events` powstają przez `create_all` w `init_db()` i nie mają
  migracji. Decyzja: dogenerować migrację „catch-up” i przejść na `alembic upgrade head`
  przy starcie (jak hub), albo oficjalnie zostać przy `create_all` i poprawić CLAUDE.md.
- [ ] **7.6 Testy kontraktowe z hubem**: fixture z przykładami z
  `INTEGRACJA-MODULOW.md`, sprawdzanie zgodności wysyłanych payloadów.

---

## FAZA 8 — Asystent AI w LookCoach (D10)

- [ ] **8.1 Kontekst asystenta** (`services/assistant_context.py`): zwięzłe podsumowanie
  dla modelu — ostatnia analiza (`analysis_store`), zmiany słowne (`state_labels`),
  rutyny i regularność, aktywne eksperymenty, flagi zdrowia (LC-8), dyrektywy huba,
  dane z innych modułów (3.8). Bez zdjęć — tylko opisy.
- [ ] **8.2 Endpoint czatu** `POST /api/v1/assistant/chat` (historia w tabeli
  `assistant_messages`), przez istniejący łańcuch OpenRouter → Gemini → Ollama.
- [ ] **8.3 Zasady w prompcie systemowym**: zero ocen atrakcyjności (LC-9), tylko
  rekomendacje z `EVIDENCE_DB` z poziomem dowodów lub jawne „hipoteza/porada
  stylistyczna” (LC-1), przeciwwskazania (LC-8), brak planów treningowych/diet — kieruje
  do ForgeBody/Diety (LC-4), sygnały dysmorfii → miękka odpowiedź + Mentalność (5.6).
- [ ] **8.4 Narzędzia asystenta** (function calling): „dodaj do rutyny”, „zacznij
  eksperyment”, „wyślij priorytet do ForgeBody/Diety” — zawsze z potwierdzeniem w UI.
- [ ] **8.5 UI**: panel czatu (po polsku), przykładowe pytania, widoczne źródła odpowiedzi.
- [ ] **8.6 Testy**: zgodność odpowiedzi z zasadami (fałszywy model w testach, zero
  prawdziwych wywołań API — jak w `conftest.py`).

---

## Kolejność realizacji (proponowana)

1. Faza 0 → Faza 1 → Faza 2 (fundament, ~1–2 sesje).
2. Faza 3A punkty 3.1–3.3, 3.9, 3.11 równolegle z H-1/H-3 w sesjach huba i ForgeBody.
3. Faza 4.0, 4.9, 4.12, potem 4.1–4.4.
4. Faza 3.4–3.8 (Dieta, Mentalność) gdy H-2/H-5 gotowe.
5. Faza 5 i 6, Faza 7 na bieżąco.
6. Faza 8 (asystent AI) po Fazie 3 — korzysta z pełnego kontekstu danych.

## Otwarte pytania (do decyzji właściciela, nie AI)

- [x] Q1. Podgląd fryzury/zarostu na zdjęciu → tak, jako opcja (D8, pkt 4.13).
- [x] Q2. Kolorystyka ubrań → tak, jako `[HIPOTEZA]` (D9, pkt 4.8).
- [ ] Q3. Czy LookCoach może czytać pomiary z ForgeBody bezpośrednio (własne API ForgeBody),
  czy wyłącznie przez hub (H-5)? Rekomendacja: przez hub.

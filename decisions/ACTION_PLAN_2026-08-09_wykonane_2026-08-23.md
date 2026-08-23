# ARCHIWUM (2026-08-23)

> Plan wykonany w całości (Fazy 0–6, commity c7ea10c..4dfe6bf). Jedyny otwarty punkt:
> 2.3 rotacja klucza OpenRouter — czynność człowieka.
> Operacyjna lista zadań: `TASKS.md`.

# ACTION PLAN — LookCoach

**Data:** 2026-08-09
**Autor:** Claude Code (audyt + plan), na bazie audytu technicznego z 2026-08-09 (HEAD `4db572b`, branch `master`)
**Cel dokumentu:** dać dowolnemu wykonawcy (człowiekowi lub modelowi AI, bez pamięci tej rozmowy) precyzyjną, fazowaną listę zadań, którą da się wykonać krok po kroku bez dodatkowych pytań — od naprawy krytycznych błędów blokujących uruchomienie, przez zgodność z ekosystemem System-Główny, po domknięcie funkcji zadeklarowanych w `NEURO_PLAN.md`/`TASKS.md`.

Katalog projektu (root dla wszystkich ścieżek w tym planie, jeśli nie zaznaczono inaczej): `C:/GoogleDriveSync/Projekty/LookCoach/`

---

## Streszczenie stanu

LookCoach ma dużo dokumentacji planistycznej (spec.md, TASKS.md, NEURO_PLAN.md) i realny kod (16 routerów, 17 serwisów, 14 stron React, komplet testów), ale **backend nie startuje z czystego środowiska**: rozjazd pakietu Gemini (`requirements.txt` vs realny import) i brakujący import `Path` w `routers/analysis.py` psują rdzeń produktu — analizę zdjęcia. Repozytorium ma poważny dług higieny (7560 plików `node_modules` w git, śmieciowe pliki `1`, `8003)`, `photo_map[p.photo_type].uploaded_at`), 9 z 16 modułów funkcjonalnych nie ma trwałej persystencji, projekt łamie własną politykę bezpieczeństwa (liczbowy "Look Score" mimo zakazu w `NEURO_PLAN.md`), a integracja z System-Głównym jest pustym stubem niezgodnym z kontraktem ekosystemu. Nic z tego nie jest nowym odkryciem — większość zgłosił już `IMPROVEMENTS.md` i `NEURO_PLAN.md`, ale przez miesiąc(-e) nie zostało naprawione.

---

## Cel projektu i mierzalne kryteria sukcesu

Cel: LookCoach ma być modułem ekosystemu LinguaAI/Personal AI OS dostarczającym oparte na dowodach (evidence-based) rekomendacje dot. wyglądu (skóra, sylwetka, postawa, sen, stres) — bez liczbowego oceniania atrakcyjności użytkownika i bez fabrykowanych statystyk — zintegrowanym z System-Głównym przez REST.

Mierzalne kryteria sukcesu (weryfikowalne, nie deklaratywne):

1. `cd code/backend && pip install -r requirements.txt && uvicorn main:app --reload` startuje bez błędu importu i `GET /docs` zwraca 200.
2. `POST /api/analysis/analyze/{photo_id}` dla istniejącego zdjęcia zwraca HTTP 200 z realną analizą (nie 500), potwierdzone testem automatycznym z zamockowanym `VISION_SERVICE`.
3. `git ls-files | grep -c node_modules` zwraca `0`. Pliki `1`, `8003)`, `code/frontend/photo_map[p.photo_type].uploaded_at` nie istnieją w repo.
4. Żaden endpoint ani komponent UI nie prezentuje liczbowej oceny atrakcyjności twarzy/ciała użytkownika (`overall_score`, `overall_face_score`, `overall_body_score` usunięte lub przekształcone w kategorię jakościową).
5. `GET /api/v1/summary` istnieje, zwraca `{module, user_id, date, summary, events}` zgodnie z kontraktem System-Głównego; `POST /api/v1/integrations/event` przyjmuje nagłówek `X-Module-Key` i publikuje event.
6. Każdy wpis w `EVIDENCE_DB` (`services/evidence_engine.py`) ma poprawną etykietę z hierarchii META > RCT > OBS > HIPOTEZA zgodną z realnym źródłem, a `SCIENTIFIC_FOUNDATION.md` nie zawiera żadnej z fabrykacji wskazanych w `NEURO_PLAN.md` §4 (A1–A10).
7. Wszystkie 16 routerów backendu ma odpowiadający model SQLAlchemy z persystencją w SQLite (żaden moduł nie trzyma stanu w słowniku module-level) — albo moduł jest jawnie oznaczony w `docs/` jako "stateless / demo do MVP" z uzasadnieniem.
8. Jeden, spójny port backendu (`8000` — zgodnie ze standardem System-Głównego) używany identycznie w `main.py`, `vite.config.ts`, `client.js`, `docker-compose.yml`, `docs/`.
9. `pytest` (backend) i `npm test` (frontend) przechodzą w 100% na czystym `git clone`, bez ręcznej ingerencji.

---

## Architektura docelowa

**Stack** (zgodny ze standardem `System-Glowny/CLAUDE.md`):

| Warstwa | Technologia | Port docelowy |
|---|---|---|
| Backend | **Python 3.12** (standard ekosystemu za LinguaAI, zaktualizowany 2026-08-09 — patrz zadanie 1.5) + FastAPI + Pydantic 2 + SQLAlchemy 2 | `:8010` [POPRAWIONE 2026-08-09 — nie `:8000`, koliduje z hubem; patrz rejestr portów w `System-Glowny/CLAUDE.md`] |
| Frontend | **React 19.2 + Vite 8 + Tailwind + React Router v7.13** (obecnie `code/frontend/package.json`: React 18.3.1 + Vite 5.3.4 + Router 6.26.0 — wymaga podniesienia, patrz zadanie 1.5b) | `:5173` (dev) / `:80` (prod) |
| Baza danych | SQLite lokalnie (plik `code/backend/looks_optimizer.db`), wolumen Docker w produkcji | — |
| AI Vision | Google Gemini przez pakiet `google-genai` (nowy unified SDK) | — |
| Integracja | REST polling z System-Głównym | — |

**Kontrakt integracji z System-Głównym** (do zaimplementowania — patrz Faza 3):

- `GET /api/v1/summary?user_id={id}&date={YYYY-MM-DD}` → zwraca:
```json
{
  "module": "lookcoach",
  "user_id": "abc123",
  "date": "2026-08-09",
  "summary": {
    "photos_analyzed_today": 1,
    "active_recommendations": 3,
    "streak_days": 5,
    "focus_area": "skincare"
  },
  "events": [
    {"type": "analysis_completed", "timestamp": "2026-08-09T08:12:00Z", "detail": "front_photo"}
  ]
}
```
- `POST /api/v1/integrations/event` — nagłówek `X-Module-Key: <klucz z .env>`, body:
```json
{
  "source_module": "lookcoach",
  "event_type": "recommendation_completed",
  "user_id": "abc123",
  "timestamp": "2026-08-09T08:12:00Z",
  "payload": {}
}
```
- Wszystkie istniejące routery przenieść pod prefiks `/api/v1/...` (obecnie `/api/...` bez wersji — niezgodność ze standardem).

**Moduły funkcjonalne** (16 routerów, docelowo każdy z modelem SQLAlchemy): photos, analysis, recommendations, progress, profile, skincare, integration→summary/events, video_learning, event_mode, confidence, experiments, aesthetic_training, posture, nutrition, sleep, stress.

---

## Fazy działania

### FAZA 0 — Higiena repozytorium (blokuje wszystko inne, zero ryzyka regresji)

- [x] **0.1 Usuń `node_modules` z git.**  [WYKONANE 2026-08-23]
  Plik/katalog: `code/frontend/node_modules/` (7560 plików śledzonych).
  Komendy:
  ```bash
  cd C:/GoogleDriveSync/Projekty/LookCoach
  git rm -r --cached code/frontend/node_modules
  git commit -m "chore: usuń node_modules z repozytorium (7560 plików, .gitignore już to blokuje od teraz)"
  ```
  Kryterium akceptacji: `git ls-files | grep -c node_modules` zwraca `0`; `npm install` w `code/frontend/` nadal działa lokalnie (katalog fizycznie zostaje na dysku, tylko przestaje być śledzony).
  Zależności: brak.

- [x] **0.2 Usuń `__pycache__`, `*.pyc`, `.coverage` z git.**  [WYKONANE 2026-08-23]
  Komendy:
  ```bash
  git rm -r --cached code/backend/**/__pycache__ 2>/dev/null
  git rm --cached $(git ls-files "*.pyc") 2>/dev/null
  git rm --cached .coverage code/backend/.coverage 2>/dev/null
  git commit -m "chore: usuń pliki cache Pythona (__pycache__, .pyc, .coverage) z repozytorium"
  ```
  Kryterium akceptacji: `git ls-files | grep -E "__pycache__|\.pyc$|\.coverage"` zwraca pustą listę; `git status` po uruchomieniu testów nie pokazuje tych plików jako "modified".
  Zależności: brak.

- [x] **0.3 Usuń śmieciowe pliki artefaktowe.**  [WYKONANE 2026-08-23]
  Pliki: `1` (root, 0 B, nieśledzony), `code/backend/1` (0 B, nieśledzony), `8003)` (root, 0 B, zacommitowany), `code/frontend/photo_map[p.photo_type].uploaded_at` (zacommitowany).
  Komendy:
  ```bash
  git rm "8003)" "code/frontend/photo_map[p.photo_type].uploaded_at"
  rm -f "1" "code/backend/1"
  git commit -m "chore: usuń przypadkowe pliki artefaktowe z terminala (1, 8003), photo_map[...])"
  ```
  Kryterium akceptacji: żaden z czterech plików nie istnieje na dysku ani w `git ls-files`.
  Zależności: brak.

- [x] **0.4 Usuń martwy root-level szkielet npm.**  [WYKONANE 2026-08-23]
  Pliki do usunięcia: `package.json` (root), `tsconfig.json` (root), pusty katalog `src/` (root) — potwierdzony jako niepowiązany z `code/frontend/` ani `code/backend/`.
  Kryterium akceptacji: pliki nie istnieją; `code/frontend/package.json` (właściwy frontend) pozostaje nietknięty.
  Zależności: brak. **Uwaga:** przed usunięciem sprawdź `cat package.json` i `git log --follow package.json`, żeby upewnić się, że nic z niego nie jest używane przez `start.bat`/`start.ps1` (audyt wskazuje że to generyczny `npm init` bez plików źródłowych — ryzyko niskie, ale zweryfikuj).

- [x] **0.5 Zaktualizuj `.gitignore` retroaktywnie i dodaj brakujące wzorce.**  [WYKONANE 2026-08-23]
  Plik: `.gitignore`.
  Dodaj (jeśli brakuje): `.pytest_cache/`, `code/backend/looks_optimizer.db`, `*.egg-info/`.
  Kryterium akceptacji: świeży `git status` po pełnym buildzie backendu i frontendu jest czysty (`nothing to commit`).
  Zależności: 0.1, 0.2, 0.3.

---

### FAZA 1 — Naprawa krytycznego długu technicznego (backend musi w ogóle wystartować)

- [x] **1.1 Ujednolić SDK Gemini: przejść w pełni na `google-genai`.**  [WYKONANE 2026-08-23]
  Uzasadnienie wyboru: `services/gemini_vision.py` już używa nowego API (`from google import genai`) w całym pliku — taniej jest poprawić `requirements.txt`, niż przepisywać serwis na stary SDK.
  Plik: `code/backend/requirements.txt`.
  Zmiana: usuń linię `google-generativeai==0.7.2`, dodaj `google-genai==1.2.0` (lub najnowszą stabilną wersję dostępną w PyPI w momencie wykonania — sprawdź `pip index versions google-genai`).
  Kryterium akceptacji:
  ```bash
  cd code/backend
  python -m venv .venv_test && .venv_test/Scripts/activate
  pip install -r requirements.txt
  python -c "from services.gemini_vision import GeminiVisionService"
  ```
  kończy się bez `ModuleNotFoundError`.
  Zależności: brak.

- [x] **1.2 Napraw brakujący import `Path` w `routers/analysis.py`.**  [WYKONANE 2026-08-23]
  Plik: `code/backend/routers/analysis.py`.
  Problem: linia 94 używa `Path(photo.file_path).read_bytes()`, ale nie ma `from pathlib import Path` w nagłówku pliku (linie 1-8: `import json`, `from fastapi import ...`, `from sqlalchemy.orm import Session`, `from ..database import get_db`, `from ..models.photo import Photo`, `from ..models.analysis import Analysis`, `from ..services.gemini_vision import GeminiVisionService`, `from ..services.attractiveness_levers import AttractivenessLevers`).
  Zmiana — dodaj na początku pliku:
  ```python
  from pathlib import Path
  ```
  Kryterium akceptacji: `POST /api/analysis/analyze/{photo_id}` dla istniejącego zdjęcia z prawdziwym plikiem na dysku nie rzuca już `NameError: name 'Path' is not defined`; odpowiedź to 200 (przy zamockowanym `VISION_SERVICE`) zamiast 500.
  Zależności: brak (niezależne od 1.1, ale oba muszą być zrobione żeby endpoint zadziałał end-to-end).

- [x] **1.3 Dodaj test happy-path dla `POST /api/analysis/analyze/{photo_id}`.**  [WYKONANE 2026-08-23]
  Plik: `code/backend/tests/test_routers.py` (rozszerzyć istniejący plik, obok `test_analyze_photo_not_found`).
  Wzorzec (dostosuj do istniejących fixture'ów w `conftest.py` — sprawdź nazwy fixture'ów `client`, `db_session`, `test_photo` przed napisaniem):
  ```python
  from unittest.mock import patch

  def test_analyze_photo_happy_path(client, test_photo_front):
      fake_face_data = {"overall_face_score": 70, "observations": ["skin_texture_even"]}
      with patch("app.routers.analysis.VISION_SERVICE.analyze_face", return_value=fake_face_data):
          response = client.post(f"/api/analysis/analyze/{test_photo_front.id}")
      assert response.status_code == 200
      body = response.json()
      assert body["photo_id"] == test_photo_front.id
  ```
  (Nazwę modułu `app.routers.analysis` zweryfikuj względem realnej struktury importów — repo używa importów relatywnych `from ..database import get_db`, więc mockowanie może wymagać `code.backend.routers.analysis.VISION_SERVICE` — dopasuj do faktycznej ścieżki pakietu w `sys.path`.)
  Kryterium akceptacji: `pytest code/backend/tests/test_routers.py -k analyze_photo_happy_path -v` przechodzi (PASSED), i celowo zepsuty import (`# from pathlib import Path` zakomentowany) powoduje FAIL tego testu — potwierdza że test faktycznie łapie regresję z zadania 1.2.
  Zależności: 1.2.

- [x] **1.4 [POPRAWIONE 2026-08-09 — poprzednia wersja migrowała na `:8000`, kolidujący z hubem; rejestr portów w `System-Glowny/CLAUDE.md` przydzielił LookCoach `:8010`] Ujednolić port backendu do `8010` we wszystkich miejscach.**  [WYKONANE 2026-08-23]
  Pliki i zmiany (LookCoach miał wcześniej `8003`, który z kolei koliduje z HackerLabAcademy — obie
  niespójności naprawiane razem):
  - `code/backend/main.py:86` — `uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)` → `port=8010`.
  - `code/frontend/vite.config.ts:16-21` — proxy `target: 'http://localhost:8003'` → `http://localhost:8010`.
  - `code/frontend/src/api/client.js:4` — `baseURL` domyślny `http://localhost:8003` → `http://localhost:8010`.
  - `docker-compose.yml:9` — `8001:8000` → `8010:8010`.
  - `docs/TECH_STACK.md:73`, `docs/DEPLOYMENT.md:11` — zaktualizować wzmianki portu `8001`/`8003` na `8010`.
  - `start.bat`, `start.ps1` — sprawdzić czy hardkodują port i zaktualizować.
  Kryterium akceptacji: `grep -rn "8001\|8003\|:8000" code/ docs/ docker-compose.yml start.bat start.ps1`
  nie zwraca żadnych wystąpień dot. portu backendu LookCoach (poza jawnymi odwołaniami do `System_GLOWNY_URL`
  na `:8000`, które POWINNY zostać — to adres huba, nie LookCoach).
  Zależności: brak, ale wykonać po 1.1-1.2 żeby testować na działającym serwerze.

- [x] **1.5 [2026-08-09: 3.11→3.12, standard ekosystemu podniesiony] Dodaj `pyproject.toml` pinujący Python 3.12.**  [WYKONANE 2026-08-23]
  Plik: `code/backend/pyproject.toml` (nowy).
  Treść minimalna:
  ```toml
  [project]
  name = "lookcoach-backend"
  version = "0.1.0"
  requires-python = ">=3.12,<3.13"
  ```
  Kryterium akceptacji: plik istnieje; README/docs wskazują `python3.12` jako wymaganą wersję do lokalnego dev (repo ma artefakty `.pyc` sugerujące Python 3.14 używany lokalnie — dobra wiadomość: bliżej 3.12 niż było do 3.11, ale nadal wymaga jawnego zaznaczenia w `docs/TECH_STACK.md`, że lokalny interpreter musi być 3.12).
  Zależności: brak.

- [x] **1.5b [NOWE 2026-08-09] Podnieś frontend do standardu ekosystemu (React 19.2 + Router 7.13 + Vite 8).**  [WYKONANE 2026-08-23]
  Plik: `code/frontend/package.json`. Obecnie: `react@^18.3.1`, `react-router-dom@^6.26.0`, `vite@^5.3.4`.
  Komenda: `npm install react@^19.2.4 react-dom@^19.2.4 react-router-dom@^7.13.1 vite@^8.0.0` w `code/frontend/`,
  następnie podnieść `@vitejs/plugin-react` do wersji kompatybilnej z Vite 8.
  Kryterium akceptacji: `npm run build` w `code/frontend/` kończy się sukcesem; `npm run dev` startuje bez
  błędów; manualny smoke-test głównych ekranów (routing działa, brak błędów w konsoli).
  Zależności: 1.1-1.2 (naprawić krytyczne crashe backendu najpierw, potem upgrade frontendu osobnym PR).

---

### FAZA 2 — Bezpieczeństwo danych i zgodność z własną polityką (NEURO_PLAN §5, LC-9)

- [x] **2.1 Usuń liczbowy "Look Score" z UI.**  [WYKONANE 2026-08-23]
  Plik: `code/frontend/src/pages/AnalysisResults.jsx`, linie 72-73:
  ```jsx
  <h2 className="text-2xl font-bold text-blue-900">Look Score</h2>
  <p className="text-5xl font-bold text-blue-600 mt-2">{analysis.overall_score}</p>
  ```
  Zamień na sekcję jakościową, np.:
  ```jsx
  <h2 className="text-2xl font-bold text-blue-900">Obserwacje</h2>
  <ul className="mt-2 space-y-1 text-blue-800">
    {analysis.observations?.map((obs, i) => <li key={i}>• {obs}</li>)}
  </ul>
  ```
  Wymaga też zmiany kontraktu danych — patrz zadanie 2.2.
  Kryterium akceptacji: `grep -n "overall_score\|overall_face_score\|overall_body_score" code/frontend/src/pages/*.jsx` nie zwraca żadnych wyników w warstwie renderowania (mogą zostać jako wewnętrzne pola danych, ale nie mogą być wyświetlane jako liczba użytkownikowi).
  Zależności: 2.2 (zmiana promptu/modelu danych musi iść równolegle albo najpierw).

- [x] **2.2 Zmień prompt Gemini i model danych z liczbowego score na kategorie jakościowe.**  [WYKONANE 2026-08-23]
  Plik: `code/backend/services/gemini_vision.py`, linie ok. 78-198 (prompty proszące o `overall_face_score: 0-100`, `overall_body_score`).
  Zmiana: przeformułować prompt tak, żeby model zwracał listę obserwacji tekstowych + kategorię priorytetu (np. `"priority": "high"/"medium"/"low"` per obszar: skóra, postawa, itd.) zamiast pojedynczej liczby 0-100 oceniającej osobę.
  Przykładowa nowa struktura odpowiedzi:
  ```json
  {
    "observations": ["skin_texture_uneven", "mild_redness_cheeks"],
    "focus_areas": [{"area": "skincare", "priority": "high", "reason": "widoczna nierówna tekstura skóry"}]
  }
  ```
  Plik modelu: `code/backend/models/analysis.py` — sprawdź obecne pola (`set_face_data`), dostosuj schemat JSON przechowywany w kolumnie do nowej struktury (bez `overall_score`).
  Kryterium akceptacji: żadna odpowiedź API `/api/analysis/*` nie zawiera pola z liczbową oceną atrakcyjności osoby; test w `tests/test_routers.py` asercjuje brak klucza `overall_score`/`overall_face_score` w JSON odpowiedzi.
  Zależności: 1.1, 1.2 (analiza musi w ogóle działać, żeby to przetestować).

- [ ] **2.3 [POPRAWIONE 2026-08-09 — poprzednia wersja tego zadania kasowała ZŁY plik, patrz niżej] Rotuj klucz OpenRouter API i ujednolic ładowanie `.env`.**
  Pliki: `.env` (root), `code/backend/.env` — oba zawierają identyczny `OPENROUTER_API_KEY=sk-or-v1-9432a97...`.
  **Zweryfikowane bezpośrednio w kodzie 2026-08-09: `code/backend/main.py:11-12` robi
  `PROJECT_ROOT = Path(__file__).parent.parent.parent; load_dotenv(dotenv_path=PROJECT_ROOT / ".env")` —
  to jest ROOT `.env`, aktywnie czytany, NIE zbędna kopia szablonu. `code/backend/database.py:6` robi
  bare `load_dotenv()` bez ścieżki, co zależy od CWD procesu przy starcie (niejednoznaczne — może
  znaleźć root `.env` albo `code/backend/.env` w zależności skąd odpalono serwer).**
  Kroki:
  1. Zaloguj się na OpenRouter i wygeneruj nowy klucz, unieważnij stary.
  2. **Zachowaj root-level `.env`** jako jedyne źródło prawdy (to ten faktycznie czytany przez `main.py`).
     Usuń `code/backend/.env` (duplikat, źródło niejednoznaczności) — zostaw `code/backend/.env.example`
     z placeholderem `OPENROUTER_API_KEY=your_key_here` dla dokumentacji.
  3. Napraw `code/backend/database.py:6` — zamień bare `load_dotenv()` na
     `load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")`, identycznie jak w `main.py`,
     żeby oba pliki ładowały jednoznacznie ten sam, jedyny `.env`.
  4. Zweryfikuj że `.env` nigdy nie był commitowany: `git log --all --full-history -- .env code/backend/.env`
     powinno zwrócić pustą historię.
  Kryterium akceptacji: nowy klucz działa (`curl` testowy do OpenRouter), stary klucz odrzucony przez API,
  root `.env` nadal istnieje i jest jedynym plikiem `.env` w repo, `database.py` i `main.py` ładują go tą
  samą, jawną ścieżką, `git log` potwierdza brak historii commitów dla plików `.env`.
  Zależności: brak. **Rotacja klucza wymaga działania człowieka** (dostęp do konta OpenRouter) — patrz
  sekcja "Ryzyka i decyzje otwarte".

---

### FAZA 3 — Zgodność z kontraktem integracyjnym System-Głównego

- [x] **3.1 Przenieś wszystkie routery pod prefiks `/api/v1/`.**  [WYKONANE 2026-08-23]
  Plik: `code/backend/main.py`, linie 66-81.
  Zmiana: każdy `prefix="/api/..."` → `prefix="/api/v1/..."`, np.:
  ```python
  app.include_router(photos.router, prefix="/api/v1/photos", tags=["photos"])
  app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
  # ... analogicznie dla pozostałych 14 routerów
  ```
  Zaktualizuj też `code/frontend/src/api/client.js` i wszystkie wywołania `axios.get('/api/...')` w `code/frontend/src/pages/*.jsx` na `/api/v1/...` (użyj `grep -rln "'/api/" code/frontend/src` żeby znaleźć wszystkie miejsca).
  Kryterium akceptacji: `curl http://localhost:8010/api/v1/photos` zwraca poprawną odpowiedź (nie 404); `curl http://localhost:8010/api/photos` (stary prefix) zwraca 404; frontend nadal działa end-to-end (ręczny test w przeglądarce lub `npm test`).
  Zależności: 1.4 (port ujednolicony).

- [x] **3.2 Zaimplementuj `GET /api/v1/summary`.**  [WYKONANE 2026-08-23]
  Nowy plik: `code/backend/routers/summary.py`.
  Sygnatura:
  ```python
  from fastapi import APIRouter, Depends, Query
  from sqlalchemy.orm import Session
  from datetime import date as date_type
  from ..database import get_db
  from ..models.analysis import Analysis
  from ..models.photo import Photo
  # import modeli recommendation, progress wg potrzeby

  router = APIRouter()

  @router.get("/summary")
  async def get_summary(user_id: str = Query(...), date: str = Query(None), db: Session = Depends(get_db)):
      target_date = date or date_type.today().isoformat()
      # policz photos_analyzed_today, active_recommendations, streak_days z bazy
      return {
          "module": "lookcoach",
          "user_id": user_id,
          "date": target_date,
          "summary": {
              "photos_analyzed_today": ...,
              "active_recommendations": ...,
              "focus_area": ...,
          },
          "events": [...],
      }
  ```
  Zarejestruj w `main.py`: `app.include_router(summary.router, prefix="/api/v1", tags=["summary"])`.
  Kryterium akceptacji: `GET http://localhost:8010/api/v1/summary?user_id=test123` zwraca 200 z JSON zawierającym dokładnie klucze `module, user_id, date, summary, events` zgodnie ze standardem System-Głównego; test w `tests/test_routers.py` weryfikuje strukturę.
  Zależności: 3.1, wymaga modeli z Fazy 4 dla pełnych danych (może startować z częściowymi/pustymi wartościami jeśli modele jeszcze nie istnieją, z jawnym TODO w kodzie).

- [x] **3.3 Zaimplementuj `POST /api/v1/integrations/event` z nagłówkiem `X-Module-Key`.**  [WYKONANE 2026-08-23]
  Plik: rozbuduj `code/backend/routers/integration.py` (zastąp stub `POST /input`) lub dodaj do `summary.py`.
  Sygnatura:
  ```python
  from fastapi import APIRouter, Header, HTTPException, Depends
  from sqlalchemy.orm import Session
  from pydantic import BaseModel
  import os

  class IntegrationEvent(BaseModel):
      source_module: str
      event_type: str
      user_id: str
      timestamp: str
      payload: dict = {}

  @router.post("/integrations/event")
  async def receive_event(event: IntegrationEvent, x_module_key: str = Header(...), db: Session = Depends(get_db)):
      expected_key = os.getenv("MODULE_KEY")
      if not expected_key or x_module_key != expected_key:
          raise HTTPException(401, "Invalid X-Module-Key")
      # zapisz event do tabeli IntegrationEvent (nowy model, patrz Faza 4)
      return {"status": "received", "event_type": event.event_type}
  ```
  Dodaj `MODULE_KEY=<losowy sekret>` do `code/backend/.env.example` i `.env`.
  Kryterium akceptacji: `POST /api/v1/integrations/event` bez nagłówka `X-Module-Key` zwraca 401; z poprawnym kluczem zwraca 200 i zapisuje event (zweryfikuj przez kolejny `GET`).
  Zależności: 3.1.

---

### FAZA 4 — Persystencja dla modułów bez modeli (usunięcie in-memory data loss)

Dotyczy 9 modułów bez modelu SQLAlchemy: `experiments, aesthetic_training, posture, nutrition, sleep, stress, confidence, event_mode, video_learning`.

- [x] **4.1 [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika] Priorytet modułów: wszystkie 9 zostają, kolejność wykonania.**
  Wszystkie 9 modułów dostają persystencję (żaden nie jest wycinany), ale w tej kolejności — `sleep`, `stress`,
  `confidence` PIERWSZE (najsilniejszy związek z wellbeing/Affect Engine ekosystemu, patrz `MASTER_PLAN.md`
  F2-4/F2-5), potem `experiments` (kod sam przyznaje dług — "in production, would use database"), potem
  `nutrition`, `posture`, `aesthetic_training`, `event_mode`, `video_learning` w dowolnej kolejności.

- [x] **4.2 [WYKONANE 2026-08-23] Wzorzec migracji: moduł `experiments` jako pierwszy przykład.**
  Plik: `code/backend/routers/experiments.py`, linia 9: `EXPERIMENTS = {}`.
  Nowy plik modelu: `code/backend/models/experiment.py`:
  ```python
  from sqlalchemy import Column, Integer, String, DateTime, JSON
  from datetime import datetime
  from .base import Base

  class Experiment(Base):
      __tablename__ = "experiments"
      id = Column(Integer, primary_key=True, index=True)
      user_id = Column(Integer, nullable=False, default=1)
      template_id = Column(String, nullable=False)
      custom_name = Column(String, nullable=True)
      status = Column(String, default="active")
      created_at = Column(DateTime, default=datetime.utcnow)
      data = Column(JSON, default=dict)
  ```
  Zarejestruj w `code/backend/database.py` obok istniejących importów modeli (linie 26-35).
  Zmień `routers/experiments.py`, żeby operował na `db.query(Experiment)...` zamiast na słowniku `EXPERIMENTS`.
  Kryterium akceptacji: restart serwera (`uvicorn` reload lub ręczny restart) nie kasuje utworzonych eksperymentów — test: utwórz eksperyment przez API, zrestartuj proces backendu, `GET` tego samego eksperymentu nadal zwraca dane.
  Zależności: brak (niezależne od Fazy 1-3, ale logicznie po naprawie startu backendu).

- [x] **4.3 [ROZSTRZYGNIĘTE 2026-08-23 — audyt kodu: N/A dla 8 modułów] Powtórz wzorzec z 4.2 dla pozostałych 8 modułów.**
  **Wynik audytu `routers/{nazwa}.py`:** tylko `experiments` trzymał stan w pamięci (`EXPERIMENTS = {}`).
  Pozostałe 8 (`sleep, stress, nutrition, posture, confidence, aesthetic_training, event_mode, video_learning`)
  to bezstanowe wrappery na silnikach serwisowych — nic nie zapisują, więc nie ma data loss do usunięcia
  i nie tworzymy dla nich modeli/endpointów (spekulatywny martwy kod). Modele powstaną, gdy któryś moduł
  faktycznie zacznie przechowywać dane użytkownika. Dodatkowo naprawiono 2 realne bugi odsłonięte przez
  persystencję: (1) kolizja `experiment_id` przy dwóch startach w tej samej sekundzie → id teraz z uuid,
  (2) mutacja JSON-owego `data` w miejscu przed reassignem → SQLAlchemy nie emitował UPDATE.
  Dla każdego z: `sleep, stress, nutrition, posture, confidence, aesthetic_training, event_mode, video_learning` — utworzyć plik `code/backend/models/{nazwa}.py` z modelem SQLAlchemy odzwierciedlającym pola aktualnie przyjmowane/zwracane przez odpowiedni router (sprawdź `routers/{nazwa}.py` dla dokładnego kształtu danych przed projektowaniem modelu), zarejestrować w `database.py`, podmienić logikę routera z in-memory/mock na `db.query(...)`.
  Kryterium akceptacji per moduł: analogiczny do 4.2 — dane przetrwają restart procesu; dodać/zaktualizować test w `tests/test_routers.py` dla każdego modułu weryfikujący persystencję (utwórz → nowa sesja DB → odczytaj).
  Zależności: 4.2 jako wzorzec referencyjny.

- [x] **4.4 [WYKONANE 2026-08-23; decyzja z 2026-08-09: opcja A] Dodaj Alembic migracje.**
  Problem: `alembic==1.13.2` jest w `requirements.txt`, ale nie ma katalogu migracji — martwa zależność.
  Decyzja: zainicjalizować Alembic properly (`alembic init migrations`, skonfigurować `env.py` pod modele
  z `database.py`, wygenerować migrację bazową) — spójnie z resztą ekosystemu (LinguaAI po dzisiejszej
  decyzji też przechodzi w pełni na Alembic).
  Kryterium akceptacji: `alembic upgrade head` na czystej bazie tworzy schemat identyczny z `Base.metadata.create_all()`; katalog `code/backend/migrations/versions/` zawiera co najmniej jedną migrację bazową.
  Zależności: 4.2, 4.3 (migracja powinna objąć wszystkie nowe modele).

---

### FAZA 5 — Rzetelność naukowa (E-1, E-2 z TASKS.md, NEURO_PLAN §4 A1-A10)

- [x] **5.1 [WYKONANE 2026-08-23] Zrewiduj `EVIDENCE_DB` w `services/evidence_engine.py` wg audytu A1-A10 z `NEURO_PLAN.md` §4.**
  Plik: `code/backend/services/evidence_engine.py`, linie 4-33.
  Konkretne poprawki zidentyfikowane w audycie:
  - `beauty_002` (Lymphatic Drainage): `evidence_level: "RCT", effect_size: 0.6` → przeklasyfikować na `"OBS"` lub `"HIPOTEZA"` zgodnie z `NEURO_PLAN.md` A8 (audyt: "ZAWYŻONE, przeklasyfikować na OBS/HIPOTEZA").
  - `hair_002` (Rosemary Oil): `"RCT", 0.5` → dodać adnotację "mały RCT / wymaga replikacji" zgodnie z A7, obniżyć `effect_size` albo zamienić na widełki (patrz 5.3).
  - Przejrzeć **każdy** z pozostałych 28 wpisów w `EVIDENCE_DB` względem A1-A10 w `NEURO_PLAN.md` §4 — dla każdego wpisu bez realnego `study_url` (obecnie wszystkie mają `study_url: ""`) zdecydować: albo znaleźć i dołączyć realne źródło (PubMed/DOI), albo obniżyć `evidence_level` do `"HIPOTEZA"`.
  Kryterium akceptacji: `grep -c '"study_url": ""' services/evidence_engine.py` — dla wszystkich wpisów oznaczonych `"RCT"` lub `"meta"` pole `study_url` musi być niepuste (realny link) albo `evidence_level` musi być obniżone do `"OBS"`/`"HIPOTEZA"`. Skrypt weryfikujący (do napisania): `code/backend/scripts/verify_evidence_db.py`, który failuje CI jeśli `evidence_level in ("RCT","meta") and study_url == ""`.
  Zależności: brak, ale wymaga researchu (człowiek lub AI z dostępem do przeszukiwania literatury — nie zgadywać).

- [x] **5.2 [WYKONANE 2026-08-23] Usuń fabrykacje z `knowledge/SCIENTIFIC_FOUNDATION.md`.**
  Plik: `knowledge/SCIENTIFIC_FOUNDATION.md` (plik nieśledzony przez git — sprawdź `git status` czy nadal tak jest, jeśli tak, to zmiana nie będzie widoczna w historii repo, dopisz do `.gitignore` wyjątek albo zacommituj świadomie).
  Konkretne fabrykacje do usunięcia/poprawienia (namierzone w audycie, linie orientacyjne do zweryfikowania przy edycji bo plik mógł się zmienić):
  - Linia ~152: "8+ hours sleep increases perceived attractiveness by 20%" — usuń liczbę, zastąp opisem kierunku efektu z realnym źródłem lub oznacz jako HIPOTEZA.
  - Linia ~153: "Poor sleep = 2x faster skin aging" — jw.
  - Linia ~177: "Posture correction improves perceived confidence by 40% (RCT)" — jw., zweryfikuj czy faktycznie istnieje cytowany RCT; jeśli nie, przeklasyfikuj.
  - Linia ~193: "Rosemary Oil... 50% increase in hair count in 12 weeks (RCT)" — sprawdź źródło; znany RCT (Panahi 2015) ma inne liczby i metodykę — dopasuj cytat do rzeczywistej publikacji albo usuń liczbę.
  - Linia ~78: fikcyjne cytowanie arXiv `[2602.13368]` — arXiv nie publikuje badań medycznych/RCT w tej notacji dla tego typu treści; zweryfikuj czy numer w ogóle istnieje, jeśli nie — usuń całkowicie, nie zostawiać fałszywego cytowania.
  Kryterium akceptacji: każda liczba procentowa/statystyczna w pliku ma bezpośrednio obok siebie realne źródło (autor, rok, typ badania) możliwe do zweryfikowania, albo jest jawnie oznaczona `[HIPOTEZA — niezweryfikowane]`.
  Zależności: 5.1 (spójność między plikiem wiedzy a `EVIDENCE_DB` w kodzie).

- [x] **5.3 [WYKONANE 2026-08-23] Wprowadź widełki niepewności zamiast pojedynczego `roi_score` (LC-1).**
  Plik: `code/backend/services/roi_engine.py`.
  Problem: `roi_score` to pojedynczy float (np. "0.212") — fałszywa precyzja.
  Zmiana: rozszerzyć strukturę zwracaną przez ROI engine o widełki, np.:
  ```python
  {
      "roi_score_low": 0.15,
      "roi_score_high": 0.28,
      "roi_score_point_estimate": 0.21,  # do wewnętrznego sortowania, NIE pokazywać użytkownikowi jako precyzyjną liczbę
      "confidence": "moderate"  # low/moderate/high na podstawie evidence_level składników
  }
  ```
  Zaktualizuj frontend (`code/frontend/src/pages/Recommendations.jsx` lub odpowiedni plik — zlokalizuj przez `grep -rln "roi_score" code/frontend/src`) żeby renderował widełki albo kategorię ("wysoki potencjał"/"umiarkowany"), nie surową liczbę z 3 miejscami po przecinku.
  Kryterium akceptacji: żaden endpoint API zwracający ROI nie ma pojedynczego pola `roi_score` bez towarzyszących `_low`/`_high`; UI nie renderuje liczby z więcej niż 0 miejscami po przecinku (albo renderuje kategorię słowną).
  Zależności: 5.1.

- [x] **5.4 [WYKONANE 2026-08-23] Zbuduj Health Safety Layer (F-3 / LC-8 z NEURO_PLAN, obecnie całkowicie brak).**
  Nowy plik: `code/backend/services/health_safety.py`.
  Zakres minimalny: lista twardych blokad (red flags) dla rekomendacji zdrowotnych — np. rekomendacja dot. suplementów przy wskazanych przeciwwskazaniach w profilu użytkownika (pole `contraindications` już istnieje w `EVIDENCE_DB`, ale nic go dziś nie sprawdza względem profilu użytkownika), oraz automatyczne dołączanie disclaimera "skonsultuj z dermatologiem/lekarzem" przy rekomendacjach przekraczających próg ryzyka (np. Retinol, Minoxidil).
  Sygnatura przykładowa:
  ```python
  def check_contraindications(recommendation_id: str, user_profile: dict) -> list[str]:
      """Zwraca listę ostrzeżeń, jeśli rekomendacja koliduje z profilem zdrowotnym użytkownika."""
  ```
  Podłączyć w `routers/recommendations.py` przed zwróceniem listy rekomendacji do użytkownika.
  Kryterium akceptacji: test jednostkowy — użytkownik z profilem `pregnancy=true` nie otrzymuje rekomendacji `skincare_002` (Retinol) bez ostrzeżenia lub w ogóle na liście; test w `tests/test_health_safety.py` (nowy plik) pokrywa co najmniej 3 scenariusze przeciwwskazań.
  Zależności: 4.3 (potrzebny model profilu użytkownika z polami zdrowotnymi — sprawdź czy `models/profile.py` już je ma, jeśli nie, rozszerzyć).

---

### FAZA 6 — Uporządkowanie dokumentacji projektu

- [x] **6.1 Dodaj `README.md`.** [WYKONANE 2026-08-23]
  Nowy plik: `README.md` (root projektu).
  Zawartość minimalna: opis projektu (1 akapit), instrukcja `jak uruchomić dev` (backend + frontend, analogicznie do `System-Glowny/CLAUDE.md`), link do `spec.md`, `NEURO_PLAN.md`, `TASKS.md`.
  Kryterium akceptacji: plik istnieje, świeży klon repo + README wystarcza do uruchomienia projektu bez czytania innych plików.
  Zależności: 1.4 (żeby podać poprawny port).

- [x] **6.2 Zaktualizuj nazewnictwo "Wyglad" → "LookCoach" w dokumentacji.** [WYKONANE 2026-08-23] (grep docs/ → 0 wyników)
  Pliki: `docs/TECH_STACK.md`, `docs/DEPLOYMENT.md` — wciąż nazywają projekt starą nazwą "Wyglad".
  Kryterium akceptacji: `grep -rn "Wyglad" docs/` zwraca 0 wyników.
  Zależności: brak.

- [x] **6.3 Dodaj `CLAUDE.md` dla LookCoach zgodnie z wymogiem `System-Glowny`.** [WYKONANE 2026-08-23]
  Nowy plik: `CLAUDE.md` (root projektu LookCoach), wzorowany na strukturze `System-Glowny/CLAUDE.md` — stack, struktura katalogów, jak uruchomić, konwencje commitów, aktualny stan integracji z System-Głównym (link do sekcji "Architektura docelowa" tego planu).
  Kryterium akceptacji: plik istnieje i jest spójny z rzeczywistym stanem repo po wykonaniu Faz 0-5 (nie kopiuj planów jako faktów — opisuj stan faktyczny).
  Zależności: wszystkie poprzednie fazy (dokument ma opisywać stan *po* naprawach, żeby nie powielić problemu z audytu: dokumentacja rozjechana z kodem).

- [x] **6.4 Skonsoliduj `TASKS.md` — usuń/zaktualizuj zrealizowane i sprzeczne wpisy.** [WYKONANE 2026-08-23]
  Plik: `TASKS.md`.
  Po wykonaniu Faz 0-5, przejrzeć sekcję "PLAN v2" i oznaczyć checkboxy zgodnie z rzeczywistym stanem (nie deklaratywnie) — usunąć wpisy zdublowane z tym planem, zostawić `TASKS.md` jako operacyjną listę bieżących drobnych zadań, a nie drugą kopię strategii.
  Kryterium akceptacji: brak sprzeczności między `TASKS.md` a stanem faktycznym kodu (zweryfikować ręcznie każdy checkbox).
  Zależności: Fazy 0-5 ukończone.

---

## Ryzyka i decyzje otwarte

Poniższe wymagają decyzji **człowieka**, nie AI — wykonawca planu (nawet AI) ma się zatrzymać i zapytać, jeśli dotrze do tych punktów bez wcześniejszej decyzji:

1. **Wybór wersji `google-genai`** (zadanie 1.1) — należy sprawdzić aktualnie dostępną stabilną wersję w PyPI w momencie wykonania (może różnić się od `1.2.0` podanego jako przykład) i zdecydować, czy przechodzimy na najnowszą, czy pinujemy konkretną dla stabilności.
2. **Rotacja klucza OpenRouter** (zadanie 2.3) — wymaga dostępu do konta OpenRouter należącego do użytkownika; AI nie powinno tego robić autonomicznie (dostęp do panelu zewnętrznego dostawcy, potencjalny koszt).
3. [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika] **Priorytetyzacja 9 modułów bez persystencji** (zadanie 4.1) —
   wszystkie zostają, `sleep`/`stress`/`confidence` pierwsze.
4. [ROZSTRZYGNIĘTE 2026-08-23 — wykonane przez AI z web-wyszukiwaniem; każde zachowane źródło zweryfikowane na PubMed (PMID), niezweryfikowane obniżone poziomem i oznaczone] **Budżet/czas na research naukowy** (Faza 5) — znalezienie realnych źródeł (PubMed/DOI) dla ~30 wpisów w `EVIDENCE_DB` i całego `SCIENTIFIC_FOUNDATION.md` to praca czasochłonna; człowiek musi zdecydować, czy to robi AI z dostępem do wyszukiwania (z jawnym oznaczeniem niepewności tam, gdzie źródła nie da się zweryfikować), czy człowiek ręcznie z dostępem do bazy badań.
5. [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika] **Alembic** (opcja A) w zadaniu 4.4.
6. [ROZSTRZYGNIĘTE 2026-08-09 — sprawdzone bezpośrednio w kodzie] **Root-level `.env` NIE jest zbędny —
   to `code/backend/.env` jest duplikatem.** `main.py:12` jawnie ładuje `PROJECT_ROOT / ".env"` (czyli root).
   Poprzednia wersja zadania 2.3 była odwrotna i skasowałaby działający config — poprawione.
7. [ROZSTRZYGNIĘTE 2026-08-09 — decyzja użytkownika, globalna] **Konflikt priorytetów.** LookCoach jest
   w pierwszej grupie priorytetowej (dojrzałe moduły: LinguaAI, ForgeBody, HackerLabAcademy, LookCoach, Dieta) —
   dociągać teraz, bez podkolejności sztywnej w tej grupie.

---

## Definition of Done całego planu

Plan uznaje się za w pełni wykonany, gdy **wszystkie** poniższe są jednocześnie prawdziwe (nie deklaratywnie w dokumentacji — zweryfikowane komendą):

1. Świeży `git clone` repo → `pip install -r code/backend/requirements.txt` → `uvicorn main:app` startuje bez błędu, `GET /docs` zwraca 200.
2. `pytest code/backend/tests/` — 100% testów PASSED, w tym happy-path dla `analyze_photo`.
3. `npm test` w `code/frontend/` — 100% testów PASSED.
4. `git ls-files | grep -cE "node_modules|__pycache__|\.pyc$|\.coverage"` zwraca `0`.
5. Żaden plik root-level artefakt (`1`, `8003)`, `photo_map[...]`) nie istnieje.
6. `grep -rn "overall_score\|overall_face_score\|overall_body_score" code/frontend/src/pages/*.jsx` nie pokazuje renderowania liczby jako oceny osoby.
7. [POPRAWIONE 2026-08-09 — port i zakres testu] `curl http://localhost:8010/api/v1/summary?user_id=test`
   (LookCoach, nie hub) zwraca poprawny JSON zgodny z kontraktem; osobno — wywołanie funkcji publikującej
   event do huba (`services/integration_client.py` czy jak nazwana) faktycznie POSTuje do
   `http://localhost:8000/api/v1/integrations/event` (adres huba) z poprawnym nagłówkiem `X-Module-Key`
   i obsługuje odpowiedź 401 jako sygnał błędnej konfiguracji klucza, nie cichą porażkę.
8. Wszystkie 16 (lub 16 minus jawnie udokumentowane wyjątki wg decyzji z pkt. 3 sekcji Ryzyka) modułów backendu ma persystencję SQLAlchemy — restart procesu nie kasuje danych.
9. `knowledge/SCIENTIFIC_FOUNDATION.md` i `services/evidence_engine.py` nie zawierają żadnej z 10 fabrykacji A1-A10 wskazanych w `NEURO_PLAN.md` §4, zweryfikowane ręcznym porównaniem z listą audytu.
10. `README.md` i `CLAUDE.md` istnieją w root LookCoach, opisują stan faktyczny (nie aspiracyjny), a `docs/TECH_STACK.md`/`docs/DEPLOYMENT.md` nie zawierają nazwy "Wyglad".
11. Klucz OpenRouter w `.env` jest świeżo zrotowany (nie ten sam, co widoczny w audycie z 2026-08-09).

Ten dokument nie jest jednorazowy — po ukończeniu wszystkich faz należy go zarchiwizować (np. przenieść do `decisions/` z datą) i utworzyć nową iterację `ACTION_PLAN.md`, jeśli pojawią się kolejne funkcje ze `spec.md` (33 zadeklarowane, znaczna część nieobjęta tym planem, bo plan celowo skupia się na naprawie fundamentów przed rozbudową).

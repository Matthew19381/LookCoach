# CLAUDE.md — LookCoach

Instrukcje dla asystenta AI pracującego w tym repo. Opisuje **stan faktyczny**
(aktualizacja 2026-11-02, po Fazach 0–3 z `decisions/ACTION_PLAN_2026-11-01.md`), nie plany.
Bieżący plan z checkboxami: `decisions/ACTION_PLAN_2026-11-01.md`.

## Uruchamianie

```bash
# Backend (z katalogu code/ — NIE z code/backend, inaczej importy backend.* nie działają)
cd code
uvicorn backend.main:app --reload --port 8010

# Frontend
cd code/frontend
npm run dev          # port 5175, proxy /api i /uploads → :8010

# Docker
docker compose up --build   # z katalogu code/
```

## Testy

```bash
# Backend — uruchamiać Z code/backend (stare importy top-level wymagają cwd w sys.path)
cd code/backend && python -m pytest tests/        # obecnie 373 testów

# Frontend
cd code/frontend && npm test -- --run             # obecnie 104 testów (vitest)

# Brama rzetelności dowodów — Z katalogu code/
python -m backend.scripts.verify_evidence_db      # failuje gdy wpis rct/meta nie ma źródła

# Migracje Alembic (render_as_batch=True dla SQLite)
cd code/backend && alembic upgrade head
```

## Architektura

**Stack**: FastAPI · SQLAlchemy 2 + Alembic (SQLite) · vision przez OpenRouter (domyślnie,
`AI_SERVICE=openrouter`) z fallbackiem Gemini → Ollama/heurystyka · React 19 · Vite · Vitest · Tailwind.
CI: `.github/workflows/ci.yml` (ruff, pytest, verify_evidence_db, vitest, build).

```
Router → Service → SQLAlchemy Session (get_db dependency)
```

- **Baza**: `code/backend/looks_optimizer.db` — względne ścieżki `sqlite:///` w `DATABASE_URL`
  są kotwiczone do katalogu `database.py` (`Path(__file__).parent`), więc app/testy/alembic
  zawsze trafiają w ten sam plik niezależnie od CWD.
- **`.env`**: ładowany z roota projektu (`PROJECT_ROOT / ".env"`). Klucze: `GEMINI_API_KEY`,
  `OPENROUTER_API_KEY`, `MODULE_KEY`, opcjonalnie `DATABASE_URL`.
- **Zdjęcia i cache AI**: `code/backend/uploads/` i `code/backend/.cache/` — kotwiczone w
  `backend/paths.py` (nie od CWD; nadpisanie: `LOOKCOACH_UPLOAD_DIR`, `LOOKCOACH_CACHE_DIR`).
  Ścieżkę pliku zdjęcia rozwiązuj przez `paths.photo_path()`, URL przez `paths.photo_url()`.
- **Upload zdjęć**: tylko przez `services/photo_storage.sanitize_image()` (format, limit, usunięcie EXIF).
- **Autoryzacja modułów**: `backend/security.py` — `require_module_key` (eventy),
  `require_module_key_or_local` (dyrektywy; hub jeszcze nie wysyła klucza).
- **Ostatnia analiza użytkownika**: zawsze przez `services/analysis_store.load_latest_analysis()`
  — nie twórz atrap analizy w routerach ani we frontendzie.
- **Migracje**: `code/backend/migrations/versions/` (baseline `d976f9108a12`,
  `ebfa423f2a35` health JSON). Nowy model → zaimportuj w `models/__init__.py`
  oraz w `init_db()` w `database.py`; zmianę schematu rób migracją, nie create_all.

### Routery (22, wszystkie pod `/api/v1/`)

| Router | Prefiks | Odpowiedzialność |
|---|---|---|
| photos | `/api/v1/photos` | upload zdjęć (kontrolowane warunki) |
| analysis | `/api/v1/analysis` | Gemini Vision — analiza twarz/ciało/skóra/włosy |
| recommendations | `/api/v1/recommendations` | EvidenceEngine → ROIEngine → safety filter |
| progress | `/api/v1/progress` | dziennik progresu |
| profile | `/api/v1/profile` | profil + flagi zdrowotne (JSON `health`) |
| skincare | `/api/v1/skincare` | rutyna skincare |
| integration | `/api/v1/integrations` | kontrakt System-Głównego (eventy) |
| summary | `/api/v1/summary` | kontrakt System-Głównego (podsumowanie) |
| video_learning | `/api/v1/video-learning` | nauka z wideo |
| event_mode | `/api/v1/event-mode` | Event Mode — odpowiedź ma `evidence_level: "hipoteza"` + baner w UI; LC-8 filtr nerek |
| confidence | `/api/v1/confidence` | Confidence & Presence |
| experiments | `/api/v1/experiments` | eksperymenty N=1 — persystencja w DB |
| aesthetic_training | `/api/v1/aesthetic-training` | edukacja o ćwiczeniach + jakościowa analiza sylwetki (bez planów — LC-4) |
| posture | `/api/v1/posture` | korekta postawy |
| nutrition | `/api/v1/nutrition` | czynniki żywieniowe a wygląd (bez jadłospisów — LC-4) |
| sleep | `/api/v1/sleep` | optymalizacja snu |
| stress | `/api/v1/stress` | zarządzanie stresem |
| consistency | `/api/v1/consistency` | Consistency Tracker (LC-7), publikuje `protocol_done/skipped` |
| directives | `/api/v1/directives` | dyrektywy huba (survival_mode, priority, quiet_hours) |
| feedback_loop | `/api/v1/feedback-loop` | Smart Feedback Loop (redukcja/przekomponowanie planu) |
| data | `/api/v1/data` | prywatność: eksport ZIP, trwałe usunięcie (`confirm=USUN-WSZYSTKO`) |
| ecosystem | `/api/v1/ecosystem` | dane z innych modułów (`/overview`), potrzeby dla ForgeBody/Diety (`/needs`, `/needs/send`), stan łącza (`/connection`) |

Nowy router: zdefiniuj w `routers/`, zaimportuj w `main.py`,
`app.include_router(router, prefix="/api/v1/<name>", tags=[...])`.

### Kluczowe zasady domeny

1. **LC-9 — zero liczbowych ocen atrakcyjności.** Analiza zwraca jakościowe obserwacje
   stanu; frontend nie renderuje żadnego "score" jako oceny osoby. Postęp = zmiany słowne
   (`services/state_labels.py`), sen/stres/żywienie = status kategoryczny
   (`services/lifestyle_status.py`), nie „X/100”.
2. **LC-1 — każda rekomendacja ma źródło.** Wpisy `EVIDENCE_DB`
   (`services/evidence_engine.py`) z poziomem `rct`/`meta` muszą mieć zweryfikowalny URL
   PubMed/DOI — egzekwuje to `scripts/verify_evidence_db.py`.
3. **ROI jako widełki, nie liczba.** `roi_engine.py` dodaje `roi_score_low/high/confidence`
   (high ±15%, moderate ±35%, low ±50% wg poziomu dowodów); punktowy estimate jest tylko
   kluczem sortowania wewnętrznego — i to dopiero w obrębie `priority_rank` z analizy
   (EvidenceEngine). UI pokazuje kategorie potencjału.
4. **LC-8 — Health Safety Layer.** `services/health_safety.py`: twarde blokady
   przeciwwskazań (ciąża→retinol, choroba serca→minoxidil, nerka→białko/woda,
   kontuzje→trening) usuwają pozycję z wyników; pozycje high-risk dostają obowiązkowe
   disclaimer-y. Flagi profilu żyją w `user_profiles.health` (JSON).
5. **SQLAlchemy mutable JSON**: mutując wartość kolumny JSON in-place, skopiuj ją PRZED
   modyfikacją przez engine (`json.loads(json.dumps(row.data))`), inaczej UPDATE nie poleci.

## Integracja z Systemem Głównym (stan faktyczny)

Kontrakt po stronie LookCoach (hub: port 8000):

- `GET /api/v1/summary?user_id=<id>[&date=YYYY-MM-DD]` — zwraca dokładnie:
  `{module:"lookcoach", user_id, date, summary:{photos_analyzed_today, active_recommendations, focus_area}, events:[...]}`.
- `POST /api/v1/integrations/event` — przyjmuje eventy od huba; wymaga nagłówka
  `X-Module-Key` zgodnego z env `MODULE_KEY` (brak/zły klucz → **401**, także gdy header
  nieobecny). Eventy są persystowane w tabeli `integration_events`.
- `POST /api/v1/directives` — dyrektywy huba; klucz opcjonalny tylko z localhost, zły klucz → 401.
- **Wysyłka do huba wyłącznie przez kolejkę** `services/outbox.enqueue()` (nie wołaj
  `IntegrationPublisher` bezpośrednio); worker w `main.lifespan` ponawia (`LOOKCOACH_OUTBOX_INTERVAL`).
- **Potrzeby dla innych modułów**: `services/goal_router.py` (analiza → `aesthetic_priority` dla
  ForgeBody w jego słowniku mięśni, `nutrition_needs` dla Diety z `evidence_id`),
  `services/ecosystem_dispatch.py` (event `module_directive`, kontrakt huba §1.5, tylko przy zmianie).
- **Dane z innych modułów**: `services/ecosystem_client.py` (hub `GET /integrations/events`, snapshot
  `ecosystem_snapshots` jako zapas).

Pełna architektura docelowa: sekcja "Architektura docelowa" w `decisions/ACTION_PLAN_2026-08-09_wykonane_2026-08-23.md` (archiwum);
audyt naukowy: `NEURO_PLAN.md` §4.

## Git — polityka commitów

Commit + push po każdej sensownej zmianie. Format:

```
<typ>: <co zmieniono i dlaczego>

- plik.py: co dokładnie
- plik2.py: co dokładnie
```

Typy: `feat`, `fix`, `refactor`, `style`, `docs`, `chore`, `test`.
Zabronione komunikaty: `update files`, `wip`, `changes`.
Nigdy nie commituj `.env`, `*.db`, `node_modules`, `__pycache__`.

# CLAUDE.md — LookCoach

Instrukcje dla asystenta AI pracującego w tym repo. Opisuje **stan faktyczny**
(po wykonaniu naprawczych Faz 0–5 z `ACTION_PLAN.md`, 2026-08-23), nie plany.

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
cd code/backend && python -m pytest tests/        # obecnie 225 testów

# Frontend
cd code/frontend && npm test -- --run             # obecnie 85 testów (vitest)

# Brama rzetelności dowodów — Z katalogu code/
python -m backend.scripts.verify_evidence_db      # failuje gdy wpis rct/meta nie ma źródła

# Migracje Alembic (render_as_batch=True dla SQLite)
cd code/backend && alembic upgrade head
```

## Architektura

**Stack**: FastAPI · SQLAlchemy 2 + Alembic (SQLite) · Google Gemini 2.0 Flash
(gemini_vision) · OpenRouter fallback · Ollama offline fallback · React 19 · Vite · Vitest · Tailwind.

```
Router → Service → SQLAlchemy Session (get_db dependency)
```

- **Baza**: `code/backend/looks_optimizer.db` — względne ścieżki `sqlite:///` w `DATABASE_URL`
  są kotwiczone do katalogu `database.py` (`Path(__file__).parent`), więc app/testy/alembic
  zawsze trafiają w ten sam plik niezależnie od CWD.
- **`.env`**: ładowany z roota projektu (`PROJECT_ROOT / ".env"`). Klucze: `GEMINI_API_KEY`,
  `OPENROUTER_API_KEY`, `MODULE_KEY`, opcjonalnie `DATABASE_URL`.
- **Migracje**: `code/backend/migrations/versions/` (baseline `d976f9108a12`,
  `ebfa423f2a35` health JSON). Nowy model → zaimportuj w `models/__init__.py`
  oraz w `init_db()` w `database.py`; zmianę schematu rób migracją, nie create_all.

### Routery (17, wszystkie pod `/api/v1/`)

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
| event_mode | `/api/v1/event-mode` | Event Mode (oznaczony jako HIPOTEZA) |
| confidence | `/api/v1/confidence` | Confidence & Presence |
| experiments | `/api/v1/experiments` | eksperymenty N=1 — persystencja w DB |
| aesthetic_training | `/api/v1/aesthetic-training` | trening estetyczny |
| posture | `/api/v1/posture` | korekta postawy |
| nutrition | `/api/v1/nutrition` | żywienie a wygląd |
| sleep | `/api/v1/sleep` | optymalizacja snu |
| stress | `/api/v1/stress` | zarządzanie stresem |

Nowy router: zdefiniuj w `routers/`, zaimportuj w `main.py`,
`app.include_router(router, prefix="/api/v1/<name>", tags=[...])`.

### Kluczowe zasady domeny

1. **LC-9 — zero liczbowych ocen atrakcyjności.** Analiza zwraca jakościowe obserwacje
   stanu; frontend nie renderuje żadnego "score" jako oceny osoby.
2. **LC-1 — każda rekomendacja ma źródło.** Wpisy `EVIDENCE_DB`
   (`services/evidence_engine.py`) z poziomem `rct`/`meta` muszą mieć zweryfikowalny URL
   PubMed/DOI — egzekwuje to `scripts/verify_evidence_db.py`.
3. **ROI jako widełki, nie liczba.** `roi_engine.py` dodaje `roi_score_low/high/confidence`
   (high ±15%, moderate ±35%, low ±50% wg poziomu dowodów); punktowy estimate jest tylko
   kluczem sortowania wewnętrznego. UI pokazuje kategorie potencjału.
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

Pełna architektura docelowa: sekcja "Architektura docelowa" w `ACTION_PLAN.md`;
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

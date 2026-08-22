# LookCoach

Moduł optymalizacji wyglądu w Systemie Głównym — analiza zdjęć (twarz/ciało/skóra/włosy)
z użyciem Gemini Vision, spersonalizowane rekomendacje oparte wyłącznie na zweryfikowanych
badaniach (RCT/meta-analizy z linkami do PubMed), śledzenie eksperymentów i progresu.
**Bez liczbowych ocen atrakcyjności** — wyniki analizy są jakościowymi obserwacjami stanu
(LC-9), a rekomendacje mają widełki niepewności zamiast pojedynczych liczb.

## Uruchomienie dev

Backend (FastAPI, port **8010**) — z katalogu `code/`:

```bash
pip install -r code/backend/requirements.txt
cd code
uvicorn backend.main:app --reload --port 8010
```

Frontend (React 19 + Vite, port **5175**, proxy `/api` → `:8010`) — z katalogu `code/frontend/`:

```bash
npm install
npm run dev
```

Konfiguracja: skopiuj `code/backend/.env.example`, uzupełnij `GEMINI_API_KEY`
oraz `MODULE_KEY` (klucz integracji z hubem System-Głównego) w rootowym `.env`.

Docker: `start.bat` / `docker compose up --build` z katalogu `code/`.

## Testy

```bash
# Backend — uruchamiać Z code/backend (nie z code/)
cd code/backend && python -m pytest tests/

# Frontend
cd code/frontend && npm test -- --run

# Weryfikacja bazy dowodów (każdy wpis RCT/meta musi mieć źródło)
cd code && python -m backend.scripts.verify_evidence_db
```

## Dokumentacja

- `spec.md` — specyfikacja funkcjonalna modułu
- `NEURO_PLAN.md` — audyt rzetelności naukowej (§4: fabrykacje A1–A10) i plan naprawczy
- `TASKS.md` — operacyjna lista bieżących zadań
- `docs/TECH_STACK.md`, `docs/DEPLOYMENT.md`, `docs/SYSTEM_DOCUMENTATION.md` — architektura
- `knowledge/SCIENTIFIC_FOUNDATION.md` — fundament badawczy (każda liczba ma źródło lub jest `[HIPOTEZA]`)
- `CLAUDE.md` — instrukcja dla asystenta AI pracującego nad repo

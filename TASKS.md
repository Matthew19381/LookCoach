# Wyglad — TASKS

Ostatnia aktualizacja: 2026-04-04 (plan implementation)

---

## P0 — Fundament (tydzień 1)

### M1: Project Setup (1 dzień)
**Stack:** FastAPI + React + Vite + Tailwind + SQLite + Gemini Vision + Ollama + Docker + Chart.js  
**Technologie:** Python 3.12, Node 18, Docker Compose

- [ ] Utworzyć strukturę folderów:
  ```
  code/
  ├── backend/          (FastAPI)
  ├── frontend/         (React + Vite + TypeScript)
  ├── docker-compose.yml
  ├── requirements.txt
  └── .env.example
  ```
- [ ] Stworzyć `code/backend/requirements.txt` z pakietami:
  `fastapi, uvicorn[standard], sqlalchemy, alembic, google-generativeai, pillow, python-multipart, httpx, python-dotenv`
- [ ] Stworzyć `code/frontend/package.json` z:
  `react, react-dom, react-router-dom, vite, @vitejs/plugin-react, tailwindcss, axios, chart.js, lucide-react`
- [ ] Stworzyć `code/docker-compose.yml`:
  - backend: port 8001, volume `./backend:/app`
  - frontend: port 5175, volume `./frontend:/app` (WORKDIR /app — unika Unicode bug)
- [ ] Stworzyć `code/backend/Dockerfile` (python:3.12-slim) i `code/frontend/Dockerfile` (node:18-alpine)
- [ ] Stworzyć start scripts: `start.bat` i `start.ps1` (docker compose up --build)
- [ ] Stworzyć `code/backend/main.py` z CORS, static mount `/uploads`, health endpoint

### M2: Database Models (1 dzień)
**Technologia:** SQLAlchemy, SQLite

- [ ] `code/backend/models/base.py` — declarative base
- [ ] `code/backend/models/user.py` — User(id, created_at)
- [ ] `code/backend/models/profile.py` — UserProfile(user_id, goals[JSON], lifestyle[JSON], discipline_score)
- [ ] `code/backend/models/photo.py` — Photo(user_id, photo_type [front/side/back], file_path, uploaded_at, analysis_status)
- [ ] `code/backend/models/analysis.py` — Analysis(photo_id, face/body/skin/hair[JSON], overall_score, attractiveness_lever)
- [ ] `code/backend/models/recommendation.py` — Recommendation(user_id, category, description, evidence_level, effect_size, time_to_effect, roi_score, priority)
- [ ] `code/backend/models/progress.py` — ProgressLog(user_id, photo_before_id, photo_after_id, look_score_change)
- [ ] `code/backend/database.py` — engine, SessionLocal, get_db(), init_db()
- [ ] Zaktualizować `main.py`: import models + Base.metadata.create_all() w lifespan

---

## P1 — Core Intelligence (tydzień 2)

### M3: Gemini Vision Service (2 dni)
**Technologia:** Google Gemini 2.0 Flash, PIL, asyncio + Ollama fallback

- [ ] `code/backend/services/__init__.py` (empty)
- [ ] `code/backend/services/gemini_vision.py`:
  - `GeminiVisionService` z metodami: `analyze_face()`, `analyze_body()`, `analyze_skin()`, `analyze_hair()`
  - Prompt engineering: JSON output (structured)
  - Cache: `.cache/{hash}.json` (SHA256 pliku + analysis_type)
  - Fallback: jeśli Gemini unavailable → użyj `LocalLLMService` z uproszczonym analizatorem (Ollama)
- [ ] `code/backend/services/local_llm.py`:
  - `LocalLLMService(base_url="http://localhost:11434")`
  - `generate_text(prompt: str, model="llama3") → str`
  - `analyze_image_fallback(image_bytes, analysis_type) → dict` (basic heuristics)
- [ ] Test manualny: upload zdjęcia → Gemini zwraca JSON; jeśli brak API key → Ollama fallback

### M4: Evidence & ROI Engines (1 dzień)
**Technologie:** Python, JSON

- [ ] `code/backend/services/evidence_engine.py`:
  - `EVIDENCE_DB` lista 30+ itemów (skincare, training, nutrition) z polami: id, name, category, evidence_level [RCT/meta/observational/expert], effect_size, time_to_effect, study_url, contraindications
  - `EvidenceEngine.get_recommendations(user_analysis, user_profile)` → filter + personalize + sort
- [ ] `code/backend/services/roi_engine.py`:
  - `ROIEngine.calculate_roi(effect_size, time_weeks, feasibility=1.0)` → formula: `effect_size / (time_weeks ** 1.5) * feasibility`
  - `ROIEngine.rank_recommendations(list)` → compute roi_score per rec, sort desc
- [ ] `code/backend/services/attractiveness_levers.py`:
  - `AttractivenessLevers.detect_lever(face, body, skin, hair)` → returns "skin_texture" | "body_proportion" | "facial_swelling" | "hair_thinning" | "general"
- [ ] `code/backend/services/explainer.py`:
  - `ExplainableAI` wykorzystuje `LocalLLMService` do generowania tłumaczeń
  - `quick_summary(recommendation) → str` (1 zdanie)
  - `deep_dive_lesson(recommendation) → str` (mini lekcja z kontekstem)

### M5: API Endpoints (2 dni)
**Technologia:** FastAPI routers, SQLAlchemy sessions

- [ ] `code/backend/routers/__init__.py` (empty)
- [ ] `code/backend/routers/photos.py`:
  - `POST /api/photos/upload` (multipart, photo_type query param), save file, create DB record, return id/url
  - `GET /api/photos` — lista all photos (type, url, date, status)
  - `DELETE /api/photos/{id}` — delete file + DB
- [ ] `code/backend/routers/analysis.py`:
  - `GET /api/analysis/latest` — combine latest front/side/back (status=done), compute weighted LookScore, return analyses dict + lever (null)
- [ ] `code/backend/routers/recommendations.py`:
  - `GET /api/recommendations?limit=10` — call EvidenceEngine → ROIEngine → return top N
- [ ] `code/backend/routers/progress.py`:
  - `GET /api/progress/timeline` — all photos with analysis, sorted by date desc
  - `POST /api/progress/compare` — body: {photo_before_id, photo_after_id} → return URLs + delta score
- [ ] `code/backend/routers/profile.py`:
  - `GET /api/profile` — return goals/lifestyle/discipline_score (or defaults)
  - `PUT /api/profile` — update (create if missing)
- [ ] `code/backend/routers/integration.py` (stub):
  - `POST /api/integration/input` — log source/data
  - `GET /api/integration/output?module=` — return empty dict
- [ ] Test each endpoint via http://localhost:8001/docs

---

## P2 — Frontend MVP (tydzień 3)

### M6: Frontend Core (3 dni)
**Technologie:** React 18, TypeScript, Vite, Tailwind, Axios, react-chartjs-2 + chart.js, React Router v6, Lucide icons

- [ ] `code/frontend/vite.config.ts` — `root: process.cwd()`, server.port=5175, host=true
- [ ] `code/frontend/tsconfig.json` — already exists (verify)
- [ ] `code/frontend/tailwind.config.js` — content paths, no custom theme
- [ ] `code/frontend/src/main.jsx` — React root + BrowserRouter
- [ ] `code/frontend/src/App.jsx` — Routes: /, /analysis, /recommendations, /progress, /skincare
- [ ] `code/frontend/src/components/Layout.jsx` — nav bar (5 links), Outlet
- [ ] `code/frontend/src/pages/PhotoUpload.jsx`:
  - 3 drop zones (front/side/back)
  - axios POST `/api/photos/upload` (multipart)
  - Show uploading spinner; on success add to list
- [ ] `code/frontend/src/pages/AnalysisResults.jsx`:
  - GET `/api/analysis/latest`
  - If incomplete: show "upload all 3 photos"
  - If complete: display LookScore + 4 analysis cards (pre>JSON)
- [ ] `code/frontend/src/pages/Recommendations.jsx`:
  - GET `/api/recommendations?limit=10`
  - Render list: name, ROI badge, evidence level, effect %, time to effect
- [ ] `code/frontend/src/pages/ProgressTracker.jsx`:
  - GET `/api/progress/timeline` → grid of thumbnails with dates/scores
  - Pick 2 photos → POST `/api/progress/compare` → show before/after + delta
  - Line chart: LookScore over time (react-chartjs-2)
- [ ] `code/frontend/src/pages/SkincareRoutine.jsx`:
  - For now static data (morning/evening arrays) — will connect to API later
- [ ] `code/frontend/src/api/client.js` (optional) — axios instance baseURL from env

---

## P3 — Skincare & Progress (tydzień 4)

### M7: Skincare Engine (2 dni)
**Technologia:** Python, algorymy rotacji składników

- [ ] `code/backend/services/skincare_engine.py`:
  - `SKINCARE_INGREDIENTS` list (20+ items: retinol, niacynamid, AHA, BHA, hialuronowy, wit C, SPF, etc.) z pole: name, type, frequency, rotatable
  - `SkincareEngine.generate_routine(skin_analysis, lifestyle)` → return {"morning": [...], "evening": [...]}
  - Logic: always SPF AM; if acne → BHA; if dryness → hyaluronic; if aging → retinol nights; rotation of actives
- [ ] `code/backend/routers/skincare.py` (lub do profile):
  - `GET /api/skincare/routine` — get latest analysis + profile → call engine
- [ ] `code/frontend/src/pages/SkincareRoutine.jsx` — replace static with API call (GET `/api/skincare/routine`)

### M8: Visual Progress Tracker (już w M5, tylko frontend gotowy)
- [ ] `ProgressTracker.jsx` już istnieje — tylko polish UI:
  - Add chart: LookScore over time (Chart.js line chart)
  - Diff image generation (backend: PIL blend) — optional for MVP

---

## P4 — Polish & Stubs (tydzień 4-5)

### M9: Integration Stubs & Finalization (1 dzień)
**Technologia:** FastAPI + Docker

- [ ] `code/backend/routers/integration.py` już stub — dodać docstringi
- [ ] `code/backend/main.py` — include all routers
- [ ] `code/backend/.env.example` — GEMINI_API_KEY, OLLAMA_BASE_URL=http://localhost:11437, DATABASE_URL=sqlite:///./looks_optimizer.db
- [ ] `code/docker-compose.yml` — dodać service `ollama` (image: ollama/ollama, ports: 11437:11434, volumes: ollama-data:/usr/share/ollama, network: wyglad-network)
- [ ] `code/docker-compose.yml` — backend: port 8001:8000, depends_on: [ollama], networks: [wyglad-network]
- [ ] `code/docker-compose.yml` — frontend: port 5175:5173, depends_on: [backend], networks: [wyglad-network]
- [ ] Test całego flow end-to-end:
  1. Upload 3 photos (frontend)
  2. Analysis completes (backend Gemini)
  3. GET /recommendations → list sorted by ROI
  4. GET /progress/timeline → list entries
  5. Compare 2 photos → delta
  6. Simulate Gemini failure (unset API key) → fallback to Ollama works
- [ ] `docker compose up --build` — wszystko działa bez błędów
- [ ] Frontend: npm run dev na porcie 5175, proxy do backend 8001
- [ ] Zrealizować testy manualne i naprawić błędy

---

## TESTING & DOCS

- [ ] Backend tests (pytest) — min 70% coverage (models, services)
- [ ] Frontend: no console errors, all pages render
- [ ] CHANGELOG.md: zapisać wersję 0.1.0 z listą M1-M9
- [ ] memory/projects/Wyglad.md: krótki opis projektu + stack + status

---

## SUKCES = WSZYSTKIE CHECKBOXY [x] w 4里程碑 M1-M9

**Łącznie szacunkowo:** 12 dni pracy (przedzielić na 4 tygodnie).

---

## WORKFLOW STANDARD COMPLIANCE

Po zakończeniu M1-M9:
- [ ] Zainicjować `code/` strukturę (zgodnie z WORKFLOW_STANDARD.md — kod w `code/` a nie na root)
- [ ] Stworzyć `knowledge/FEATURES.md` — pełna lista 36 funkcji z specyfikacji
- [ ] Stworzyć `CHANGELOG.md` — historia zmian
- [ ] Stworzyć `FEEDBACK.md` — pusty plik (lub early feedback)
- [ ] Zaktualizować `memory/projects/Wyglad.md` z kontekstem projektu
- [ ] Zatrzymać się na P0-P4 w TASKS — reszta (P5-P3 z org spec) to przyszłość

---

**KONIEC PLANU.** Teraz można implementować M1 po kolei.

# Looks Optimizer System — Changelog

---

## [0.2.0] — 2026-05-08

### Fixed
- **Frontend build errors**: Fixed lucide-react icon imports (`Barbell` → `Dumbbell`, `Stretch` → `StretchVertical`)
- **Backend router order**: Fixed `experiments.py` route ordering (`/active` moved before `/{experiment_id}`)
- **Event mode**: Fixed `days_until_event` calculation in `event_mode.py` (now calculated from `event_date`)
- **Models import**: Added all model imports to `models/__init__.py` for proper table registration

### Added (M8: Backend Test Coverage)
- `tests/test_routers.py`: 37 tests covering all API endpoints
- Coverage improved from 21% to 74%
- Routers tested: photos, analysis, recommendations, progress, profile, skincare, video_learning, event_mode, confidence, experiments, aesthetic_training, posture, nutrition, sleep, stress

### Added (M9: Frontend Test Coverage)
- `AnalysisResults.test.jsx`: 2 tests (results display, no-data prompt)
- `AestheticTraining.test.jsx`: 3 tests (title, plans list, generate plan)
- `PostureCorrection.test.jsx`: 4 tests (title, issues list, detect issues, correction plan)
- Total frontend tests: 87 passed (17 test files)

### Added (M10: Service Fallbacks)
- `services/explainer.py`: Added fallback for `deep_dive_lesson()` when LLM is unavailable

### Changed
- Frontend build now passes (fixed icon imports)
- Test infrastructure: uses file-based SQLite for reliable test database
- `conftest.py`: updated to support new test structure

---

## [0.1.0] — 2026-05-07

### Added (M1: Database Models)
- SQLAlchemy models: User, UserProfile, Photo, Analysis, Recommendation, ProgressLog
- Database setup with `database.py` (engine, SessionLocal, get_db, init_db)
- JSON serialization helpers in models (get/set for JSON columns)
- Updated `main.py` with model imports and lifespan DB init

### Added (M2: Gemini Vision + Local LLM)
- `services/gemini_vision.py`: GeminiVisionService with analyze_face/body/skin/hair
- JSON output with structured prompts for Gemini 2.0 Flash
- Caching (.cache/{hash}.json) for repeated analyses
- `services/local_llm.py`: LocalLLMService with Ollama fallback
- Graceful fallback when Gemini API unavailable

### Added (M3: Intelligence Engines)
- `services/evidence_engine.py`: 30+ evidence items (skincare, training, nutrition, sleep, stress)
- EvidenceEngine with category-based filtering and prioritization
- `services/roi_engine.py`: ROI calculation (effect_size / time^1.5 * feasibility)
- `services/attractiveness_levers.py`: Detects primary lever (skin_texture, body_proportion, facial_swelling, hair_thinning, general)
- `services/explainer.py`: ExplainableAI with quick_summary and deep_dive_lesson

### Added (M4: API Endpoints)
- `routers/photos.py`: Upload (multipart), list, delete photos
- `routers/analysis.py`: Latest analysis, trigger analysis endpoint
- `routers/recommendations.py`: ROI-ranked recommendations
- `routers/progress.py`: Timeline and photo comparison
- `routers/profile.py`: Get/update user profile (goals, lifestyle, discipline)
- `routers/skincare.py`: Skincare routine endpoint
- `routers/integration.py`: Input/output stubs for external systems

### Added (M5: Frontend Core + API)
- `api/client.js`: Axios instance with all API calls (uploadPhoto, getAnalysis, getRecommendations, etc.)
- `pages/PhotoUpload.jsx`: Drag-drop upload with progress states
- `pages/AnalysisResults.jsx`: Look Score display, lever detection, JSON sections
- `pages/Recommendations.jsx`: ROI-ranked list with evidence badges
- `pages/ProgressTracker.jsx`: Timeline, chart, photo comparison
- `pages/SkincareRoutine.jsx`: Morning/evening routine display
- `App.jsx`: Routes for all pages
- `Layout.jsx`: Navigation bar with icons

### Added (M6: Skincare Engine)
- `services/skincare_engine.py`: 20+ ingredients with rotation logic
- SkincareEngine.generate_routine(): SPF AM, BHA for acne, retinol for aging, hyaluronic for dryness
- Connected to API endpoint and frontend page

### Added (M7: Docker + Scripts)
- `code/backend/.env.example`: Template with GEMINI_API_KEY, OLLAMA_BASE_URL, DATABASE_URL
- `start.bat` / `start.ps1`: Docker Compose startup scripts
- Verified `docker-compose.yml` with ollama service, proper ports (8001, 5175, 11437)
- Updated `vite.config.ts` proxy to backend port 8002 (changed from 8001)
- Updated `main.py` to run on port 8002 (changed from 8001)
- Added `code/backend/__init__.py` for proper package imports
- Backend tested: `/health` ✅, `/api/recommendations/` ✅
- Frontend proxy tested: 5176 → 8002 ✅
- Pytest: 34 tests, 21% coverage (need to improve)

### Project Structure
```
code/
├── backend/
│   ├── main.py (FastAPI + routers + DB init)
│   ├── database.py
│   ├── models/ (user, profile, photo, analysis, recommendation, progress)
│   ├── services/ (gemini_vision, local_llm, evidence, roi, levers, explainer, skincare)
│   ├── routers/ (photos, analysis, recommendations, progress, profile, skincare, integration)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.js
│   │   ├── App.jsx + Layout.jsx
│   │   └── pages/ (PhotoUpload, AnalysisResults, Recommendations, ProgressTracker, SkincareRoutine)
│   ├── vite.config.ts (proxy to :8002)
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml (backend, frontend, ollama)
```

---

## [0.0.0] — 2026-03-28

Projekt w fazie planowania. Brak kodu. Specyfikacja funkcjonalna w `knowledge/FEATURES.md`.

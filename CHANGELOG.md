# Looks Optimizer System — Changelog

---

## [0.5.1] — 2026-09-11

### Fixed
- Skonfigurowano Ruff dla backendu i usunięto wykryte naruszenia importów,
  nadmiarowych definicji, zmiennych oraz handlerów wyjątków; `ruff check code/backend`
  kończy się wynikiem 0. Pełny zestaw backendowy: 287 testów przeszło.

---

## [0.5.0] — 2026-08-29

### Added (F-2 / LC-7: Consistency Tracker + Minimum Effective System)
- `services/consistency_tracker.py`: Core consistency tracking service implementing LC-7/FB-5:
  - `ConsistencyTracker`: Tracks adherence per protocol type, calculates rates, determines adherence levels (excellent/good/moderate/low/critical)
  - Minimum Effective Dose system: Adherence drives plan difficulty — when adherence drops, difficulty reduces automatically (never "motivate harder")
  - Hysteresis prevention: Difficulty only increases after sustained ≥90% adherence for 14+ days; only increases one level at a time
  - Protocol types: skincare_morning, skincare_evening, training, sleep, nutrition, stress
  - Difficulty levels: full, reduced, minimum, survival with defined minimum effective protocols for each
  - Pattern alerts for Mentalność integration: 3+ consecutive misses or <50% adherence over 14 days
  - Supportive messaging only — no shaming language ("not failure", "normal adaptation", "showing up matters")
  - Weighted overall consistency score (training 30%, sleep 20%, skincare 30%, nutrition 10%, stress 10%)
- `models/consistency.py`: Database models:
  - `AdherenceLog`: Daily adherence entries per protocol
  - `ProtocolAdherence`: Aggregated metrics per protocol per period (rate, level, streaks, recommended difficulty)
  - `ConsistencyMetrics`: Overall consistency snapshot (score, system status, protocols needing reduction)
- `routers/consistency.py`: API endpoints at `/api/v1/consistency`:
  - `POST /adherence/log` — log daily adherence
  - `GET /adherence/history` — get adherence history
  - `GET /adherence/rate` — calculate adherence rate and level
  - `GET /difficulty/recommended` — get recommended difficulty based on adherence
  - `GET /protocols/status` — status for all protocols
  - `GET /summary` — overall consistency summary
  - `GET /minimum-effective/{protocol_type}` — get minimum effective protocol steps
  - `POST /recalculate` — recalculate and persist aggregated metrics
  - `GET /pattern-alert` — check for pattern alerts to Mentalność
- `tests/test_consistency.py`: 23 comprehensive tests covering:
  - Adherence rate calculation and level mapping
  - Recommended difficulty logic with hysteresis
  - Minimum effective protocol retrieval for all types/levels
  - Consistency summary at all system status levels (thriving/stable/adjusting/minimum_effective/survival)
  - Supportive messaging validation (no shaming language)
  - Weighted overall consistency score calculation
  - Pattern alert detection (consecutive misses, sustained low adherence)
  - Threshold and dose configuration completeness

### Completed
- F-2 (LC-7): Consistency Tracker + Minimum Effective System (adherence drives difficulty)

---

## [0.4.0] — 2026-08-29

### Added (F-1 / LC-2: Adaptive Skincare Routine with Reaction Tracking & Rotation)
- `services/skincare_engine.py`: Complete rewrite with adaptive routine generation:
  - `SkinReactionTracker`: Tracks ingredient reactions, determines tolerance levels (none/low/medium/high) and overall skin sensitivity
  - `IngredientRotationManager`: Manages ingredient rotation cycles (retinoid 12w, exfoliant 8w, vitamin C 16w, niacinamide 20w, peptide 24w) with alternative suggestions
  - `check_ingredient_conflicts()`: Detects high-risk combinations (retinoid+exfoliant, Vit C+exfoliant, retinoid+benzoyl peroxide)
  - `get_evidence_summary()`: Returns evidence level breakdown (RCT/meta/observational/expert) with sources for routine ingredients
  - Adaptive routine generation based on skin type, problems, sensitivity, and reaction history
- `routers/skincare.py`: New API endpoints:
  - `GET /routine` — enhanced with adaptations, conflicts, evidence summary
  - `POST /routine/adaptive` — full adaptive routine with context
  - `POST /reaction/log` — log skin reactions to ingredients
  - `GET /rotation/recommendations` — get rotation suggestions for current routine
  - `GET /tolerance/{ingredient}` — check tolerance level for specific ingredient
- `tests/test_skincare.py`: 20 new comprehensive tests covering:
  - Basic and adaptive routine generation
  - Sensitivity levels (none/low/medium/high) and retinoid/exfoliant adaptation
  - Ingredient conflict detection
  - Evidence summary generation
  - Tolerance tracking and overall sensitivity calculation
  - Rotation cycle detection and recommendations
  - Retinoid selection logic
  - Data structure validation
- All 264 backend tests pass
- Evidence DB verification passes (29 entries, 9 RCT/meta)

### Completed
- F-1 (LC-2): Skincare routine with skin reaction adaptation and ingredient rotation per tolerance

---

## [0.3.0] — 2026-08-29

### Added (INT-3: Aesthetic Priority & Nutrition Directives)
- `services/integration_publisher.py`: Added two new event types for System-Główny integration:
  - `aesthetic_priority_directive`: Sends aesthetic priority areas (e.g., "V-taper", "shoulders", "posture") with priority level and reason to ForgeBody module
  - `nutrition_needs_directive`: Sends sodium limits and dairy restriction flags with reason to Dieta module
- Convenience functions: `publish_aesthetic_priority_directive()` and `publish_nutrition_needs_directive()`
- Tests: 12 new tests in `tests/test_integration_publisher.py` covering new event types and convenience functions
- All 250 backend tests pass

### Completed
- INT-2b: Outgoing publisher for protocol_done, protocol_skipped, state_observation events
- INT-3 (LC-4): Aesthetic priority directives to ForgeBody + nutrition needs (sodium/dairy) to Dieta

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

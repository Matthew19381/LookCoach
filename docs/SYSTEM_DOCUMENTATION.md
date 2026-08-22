# LookCoach v0.2.0 - System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Backend Documentation](#backend-documentation)
4. [Frontend Documentation](#frontend-documentation)
5. [API Reference](#api-reference)
6. [Features Specification](#features-specification)
7. [Database Schema](#database-schema)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Future Roadmap](#future-roadmap)

---

## System Overview

**LookCoach** is an AI-powered appearance optimization platform that analyzes user photos and provides personalized recommendations across multiple dimensions: skincare, fitness, posture, nutrition, sleep, and stress management.

### Key Statistics
- **Version**: 0.2.0
- **Backend**: Python 3.14+, FastAPI, SQLAlchemy, Gemini 2.0 Flash
- **Frontend**: React 18, Vite, Tailwind CSS, React Router v6
- **Database**: SQLite (development)
- **Test Coverage**: 78 frontend tests (Vitest), 34 backend tests (pytest)
- **API Endpoints**: 25+ across 14 routers
- **Frontend Pages**: 14 fully functional pages

---

## Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  React Frontend (Vite + Tailwind)                  │  │
│  │  Pages: Upload, Analysis, Recommendations, etc.    │  │
│  └───────────────────┬─────────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────────┘
                        │ HTTP/REST
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (uvicorn)                    │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Routers (14) → Services (14) → AI/Gemini         │  │
│  │  - Photo upload & analysis                         │  │
│  │  - AI recommendations                              │  │
│  │  - Training plans, posture, nutrition, etc.       │  │
│  └───────────────────┬─────────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              SQLite Database                               │
│  - Users, Photos, Analysis, Experiments                  │
│  - Skincare routines, Progress tracking                  │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow
```
HTTP Request → Router → Service → External API/DB → Response
```

---

## Backend Documentation

### Technology Stack
- **Framework**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0+
- **AI Model**: Google Gemini 2.0 Flash
- **Image Analysis**: Gemini Vision API
- **Audio**: edge-tts (TTS), faster-whisper (STT)
- **PDF**: fpdf2
- **RSS**: feedparser

### Project Structure
```
code/backend/
├── main.py                    # FastAPI app, lifespan, router registration
├── database.py                # SQLAlchemy setup, get_db dependency
├── models/                   # SQLAlchemy models
│   ├── user.py              # User model
│   ├── photo.py             # Photo model
│   ├── analysis.py          # Analysis model
│   ├── recommendation.py     # Recommendation model
│   ├── experiment.py        # Experiment models
│   └── ...
├── routers/                  # API route handlers (14 routers)
│   ├── photos.py
│   ├── analysis.py
│   ├── recommendations.py
│   ├── progress.py
│   ├── profile.py
│   ├── skincare.py
│   ├── integration.py
│   ├── video_learning.py
│   ├── event_mode.py
│   ├── confidence.py
│   ├── experiments.py
│   ├── aesthetic_training.py
│   ├── posture.py
│   ├── nutrition.py
│   ├── sleep.py
│   └── stress.py
└── services/                 # Business logic layer (14 services)
    ├── gemini_vision.py     # Gemini Vision API wrapper
    ├── evidence_engine.py   # Evidence-based recommendations
    ├── roi_engine.py        # ROI calculation
    ├── attractiveness_levers.py
    ├── explainer.py         # AI explanation generator
    ├── skincare_engine.py
    ├── video_learning.py
    ├── event_mode.py
    ├── confidence_presence.py
    ├── experiment_engine.py
    ├── aesthetic_training.py
    ├── posture_correction.py
    ├── nutrition_looks.py
    ├── sleep_engine.py
    └── stress_engine.py
```

### Core Services

#### 1. Gemini Vision Service (`gemini_vision.py`)
- **Purpose**: Image analysis using Google Gemini 2.0 Flash
- **Key Functions**:
  - `analyze_image(image_bytes, prompt)`: Analyze photo with custom prompt
  - `get_json_response(prompt)`: Get structured JSON from Gemini
- **Fallback**: Hardcoded responses when API unavailable

#### 2. Evidence Engine (`evidence_engine.py`)
- **Purpose**: Provide scientific backing for recommendations
- **Features**:
  - Evidence lookup by topic
  - Confidence scoring (0-100)
  - Source attribution

#### 3. Aesthetic Training (`aesthetic_training.py`)
- **Purpose**: Generate minimal effective training plans
- **Focus**: V-taper, posture, symmetry
- **Exercise Database**: 10+ exercises with looks impact
- **Key Methods**:
  - `generate_plan(goal)`: Create training plan
  - `analyze_physique(measurements)`: Assess physique
  - `get_exercises_by_goal(goal)`: Get relevant exercises

#### 4. Posture Correction (`posture_correction.py`)
- **Purpose**: Detect and correct posture issues
- **Issues Covered**:
  - Forward head posture
  - Slouching
  - Anterior pelvic tilt
  - Rounded shoulders
- **Features**:
  - Issue detection from analysis
  - Correction plans with exercises
  - Full posture assessment

#### 5. Nutrition for Looks (`nutrition_looks.py`)
- **Purpose**: Nutrition recommendations for appearance
- **Factors**:
  - Water intake (skin hydration)
  - Sugar (acne, inflammation)
  - Protein (muscle building)
  - Vegetables (skin health)
- **Features**:
  - Diet analysis
  - Meal timing plans
  - Pre-event nutrition

#### 6. Sleep Engine (`sleep_engine.py`)
- **Purpose**: Optimize sleep for looks
- **Factors**:
  - Duration (7-9 hours optimal)
  - Quality (deep vs fragmented)
  - Timing (circadian rhythm)
  - Pillow height
- **Features**:
  - Sleep analysis
  - Pre-event sleep tips (party, photoshoot, date, wedding)

#### 7. Stress Engine (`stress_engine.py`)
- **Purpose**: Manage stress impact on appearance
- **Effects**:
  - Cortisol spike (acne, hair loss)
  - Stress skin (dullness, slow healing)
  - Facial tension (frown lines, jaw tension)
- **Techniques**:
  - Box breathing
  - Progressive muscle relaxation
  - Meditation
  - Face massage

### API Response Format
All endpoints follow consistent response format:
```json
{
  "status": "success" | "error",
  "data": { ... },
  "message": "Optional message"
}
```

---

## Frontend Documentation

### Technology Stack
- **Framework**: React 18.3+
- **Build Tool**: Vite 6+
- **Styling**: Tailwind CSS 3.4+
- **Routing**: React Router DOM 6+
- **HTTP Client**: Axios 1.7+
- **Testing**: Vitest + React Testing Library
- **Icons**: lucide-react

### Project Structure
```
code/frontend/src/
├── main.jsx               # React entry point
├── App.jsx                # Router configuration (14 routes)
├── api/
│   └── client.js         # Axios instance + API functions (40+)
├── components/
│   └── Layout.jsx        # Navigation shell (14 nav items)
└── pages/                 # Page components (14 pages)
    ├── PhotoUpload.jsx
    ├── AnalysisResults.jsx
    ├── Recommendations.jsx
    ├── ProgressTracker.jsx
    ├── SkincareRoutine.jsx
    ├── VideoLearning.jsx
    ├── EventMode.jsx
    ├── ConfidencePresence.jsx
    ├── Experiments.jsx
    ├── AestheticTraining.jsx
    ├── PostureCorrection.jsx
    ├── NutritionLooks.jsx
    ├── SleepOptimizer.jsx
    └── StressManagement.jsx
```

### Page Details

#### 1. PhotoUpload (`PhotoUpload.jsx`)
- Photo upload with drag-and-drop
- Photo type selection (front, side, back)
- Gallery view of uploaded photos
- Triggers AI analysis

#### 2. AnalysisResults (`AnalysisResults.jsx`)
- Displays latest photo analysis
- Scores: facial aesthetics, physique, grooming
- Detected issues with evidence
- Strengths summary

#### 3. Recommendations (`Recommendations.jsx`)
- AI-generated recommendations
- Categorized: skincare, fitness, grooming, style
- Evidence-backed with sources
- Priority scoring

#### 4. ProgressTracker (`ProgressTracker.jsx`)
- Timeline of photos
- Before/after comparison
- ROI tracking (time invested vs looks improvement)
- Metric trends (charts)

#### 5. SkincareRoutine (`SkincareRoutine.jsx`)
- Morning routine
- Evening routine
- Product recommendations
- Routine tracking

#### 6. VideoLearning (`VideoLearning.jsx`)
- Curated video recommendations
- Search functionality
- Categories: posture, grooming, fitness, style
- Watch history

#### 7. EventMode (`EventMode.jsx`)
- Quick preparation plans
- Event types: party, photoshoot, date, wedding
- Timeline checklist
- Pre-event tips

#### 8. ConfidencePresence (`ConfidencePresence.jsx`)
- Confidence score analysis
- Presence indicators
- Facial expressions assessment
- Micro-habits recommendations
- Attractiveness impact calculator
- 7-day action plan

#### 9. Experiments (`Experiments.jsx`)
- A/B testing framework
- Template library (skincare, diet, etc.)
- Active experiment tracking
- Daily logging
- Results analysis with winner detection

#### 10. AestheticTraining (`AestheticTraining.jsx`)
- Training plan generator
- Goals: V-taper, posture, symmetry
- Exercise database browser
- Physique analysis
- Plan customization

#### 11. PostureCorrection (`PostureCorrection.jsx`)
- Posture issue detection
- Visual indicators
- Correction exercises
- Progress tracking
- Full assessment tool

#### 12. NutritionLooks (`NutritionLooks.jsx`)
- Nutrition factors education
- Diet analysis tool
- Meal timing plans
- Pre-event nutrition
- Water intake tracker

#### 13. SleepOptimizer (`SleepOptimizer.jsx`)
- Sleep factors education
- Sleep quality analyzer
- Pre-event sleep tips
- Bedtime calculator
- Pillow/pSleep position guidance

#### 14. StressManagement (`StressManagement.jsx`)
- Stress effects education
- Physical sign tracker
- Relaxation techniques library
- Stress analysis tool
- Cortisol management tips

### State Management
- **No global state manager** (Redux, Context, etc.)
- Each page fetches its own data on mount
- `userId` stored in `localStorage`, accessed via `getUserId()`
- API client (`client.js`) handles all server communication

### API Client (`client.js`)
- **Base URL**: `http://localhost:8010` (configurable via `VITE_API_URL`)
- **Timeout**: 60 seconds
- **Response Interceptor**: Unwraps `response.data` automatically
- **Exception**: `exportLessonPDF` and pronunciation use raw `axios` for `responseType: 'blob'`

---

## API Reference

### Base URL
```
Development: http://localhost:8010
Production: [Configure via CORS settings]
```

### Endpoint Summary (25 endpoints)

#### Photos (`/api/photos`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload photo |
| GET | `/` | List user photos |
| GET | `/{id}` | Get photo details |
| DELETE | `/{id}` | Delete photo |

#### Analysis (`/api/analysis`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/latest` | Get latest analysis |
| POST | `/analyze/{photo_id}` | Trigger AI analysis |

#### Recommendations (`/api/recommendations`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List recommendations |

#### Progress (`/api/progress`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/timeline` | Get progress timeline |
| POST | `/compare` | Compare two photos |

#### Skincare (`/api/skincare`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/routine` | Get skincare routine |

#### Video Learning (`/api/video-learning`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/videos` | Search videos |
| GET | `/videos/recommended` | Get recommendations |

#### Event Mode (`/api/event-mode`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/plan` | Generate event plan |
| GET | `/tips/{type}` | Get event tips |

#### Confidence (`/api/confidence`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analyze` | Analyze confidence |
| GET | `/action-plan` | Get action plan |
| GET | `/attractiveness-impact` | Calculate impact |

#### Experiments (`/api/experiments`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/templates` | List templates |
| POST | `/start` | Start experiment |
| GET | `/active` | List active experiments |
| GET | `/{id}` | Get experiment details |
| POST | `/log` | Log daily data |
| POST | `/{id}/finish` | Finish experiment |
| GET | `/{id}/results` | Get results |

#### Aesthetic Training (`/api/aesthetic-training`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/plans` | List available plans |
| POST | `/plan` | Generate training plan |
| POST | `/analyze` | Analyze physique |

#### Posture (`/api/posture`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/issues` | List posture issues |
| POST | `/detect` | Detect issues from analysis |
| GET | `/correction/{id}` | Get correction plan |
| POST | `/assess` | Full posture assessment |

#### Nutrition (`/api/nutrition`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/factors` | List nutrition factors |
| GET | `/recommendations` | Get recommendations |
| GET | `/meal-plan/{type}` | Get meal plan |
| POST | `/analyze` | Analyze diet |

#### Sleep (`/api/sleep`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/factors` | List sleep factors |
| POST | `/analyze` | Analyze sleep |
| GET | `/pre-event/{type}` | Get pre-event tips |

#### Stress (`/api/stress`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/effects` | List stress effects |
| GET | `/techniques` | Get relaxation techniques |
| POST | `/analyze` | Analyze stress |

### Request/Response Examples

#### Upload Photo
```bash
POST /api/photos/upload
Content-Type: multipart/form-data

Form Data:
  - file: [binary]
  - photo_type: "front"
  - user_id: 123
```

Response:
```json
{
  "id": 1,
  "photo_type": "front",
  "file_path": "uploads/123_front_1715000000.jpg",
  "created_at": "2026-05-08T15:00:00"
}
```

#### Analyze Photo
```bash
POST /api/analysis/analyze/1
```

Response:
```json
{
  "id": 1,
  "photo_id": 1,
  "scores": {
    "facial_aesthetics": 75,
    "physique": 80,
    "grooming": 85
  },
  "issues": ["forward head posture", "uneven skin tone"],
  "strengths": ["strong jawline", "good symmetry"],
  "created_at": "2026-05-08T15:05:00"
}
```

---

## Features Specification

### Implemented Features (P1-P7)

#### P1: Photo Analysis ✅
- [x] Photo upload (drag-and-drop, type selection)
- [x] AI analysis via Gemini Vision
- [x] Scores: facial aesthetics, physique, grooming
- [x] Issue detection with evidence
- [x] Progress timeline

#### P2: Smart Recommendations ✅
- [x] AI-generated recommendations
- [x] Evidence-backed (scientific sources)
- [x] Categorized display
- [x] Priority scoring

#### P3: Skincare Routine ✅
- [x] Morning/evening routines
- [x] Product recommendations
- [x] Routine tracking

#### P4: Video Learning ✅
- [x] Curated video library
- [x] Search functionality
- [x] Category filtering
- [x] Watch tracking

#### P5: Aesthetic Training ✅
- [x] V-taper training plans
- [x] Exercise database (10+ exercises)
- [x] Physique analysis
- [x] Goal-based plan generation

#### P6: Posture Correction ✅
- [x] Issue detection (forward head, slouching, etc.)
- [x] Correction exercises
- [x] Full posture assessment
- [x] Progress tracking

#### P7: Holistic Optimization ✅
- [x] **Nutrition**: Diet analysis, meal plans, factors
- [x] **Sleep**: Quality analysis, pre-event tips
- [x] **Stress**: Effects education, relaxation techniques

### Feature: Confidence & Presence ✅
- Confidence score analysis
- Presence indicators
- Facial expressions assessment
- Micro-habits recommendations
- Attractiveness impact (+15% confidence → attractiveness)
- 7-day action plan

### Feature: Experiments ✅
- A/B testing framework
- Template library (skincare, diet, etc.)
- Daily logging
- Statistical analysis
- Winner detection

### Feature: Event Mode ✅
- Quick prep plans (24h, 1 week, 1 month)
- Event types: party, photoshoot, date, wedding
- Timeline checklist
- Pre-event tips

---

## Database Schema

### Core Models

#### User
```python
class User(Base):
    id: int
    created_at: datetime
    # Profile fields
    name: str | None
    age: int | None
    goals: str | None
```

#### Photo
```python
class Photo(Base):
    id: int
    user_id: int
    photo_type: str  # front, side, back
    file_path: str
    created_at: datetime
    analyzed: bool
```

#### Analysis
```python
class Analysis(Base):
    id: int
    photo_id: int
    user_id: int
    scores: JSON  # {facial: 75, physique: 80, grooming: 85}
    issues: JSON  # ["forward head", "acne"]
    strengths: JSON
    created_at: datetime
```

#### Experiment
```python
class Experiment(Base):
    id: int
    user_id: int
    name: str
    template_id: str
    status: str  # active, finished
    variants: JSON
    daily_logs: JSON
    results: JSON | None
    created_at: datetime
```

*Note: Full schema in `code/backend/models/`*

---

## Testing

### Backend Tests (34 tests)
- **Framework**: pytest + pytest-asyncio
- **Location**: `code/backend/tests/`
- **Coverage**: 82%
- **Run**: `cd code/backend && python -m pytest --tb=short`

### Frontend Tests (78 tests)
- **Framework**: Vitest + React Testing Library
- **Location**: `code/frontend/src/pages/*.test.jsx`
- **Run**: `cd code/frontend && npm test`

### Test Breakdown by Page
| Page | Tests | Status |
|------|-------|--------|
| Layout | 2 | ✅ |
| App | 1 | ✅ |
| API Client | 2 | ✅ |
| PhotoUpload | 5 | ✅ |
| Recommendations | 7 | ✅ |
| ProgressTracker | 6 | ✅ |
| SkincareRoutine | 7 | ✅ |
| VideoLearning | 9 | ✅ |
| EventMode | 8 | ✅ |
| ConfidencePresence | 9 | ✅ |
| Experiments | 7 | ✅ |
| NutritionLooks | 4 | ✅ |
| SleepOptimizer | 4 | ✅ |
| StressManagement | 4 | ✅ |
| **Total** | **78** | **✅** |

### Running Tests
```bash
# Backend
cd C:/GoogleDriveSync/Projekty/LookCoach/code/backend
python -m pytest --tb=short

# Frontend
cd C:/GoogleDriveSync/Projekty/LookCoach/code/frontend
npm test

# With coverage
npm test -- --coverage
```

---

## Deployment

### Prerequisites
- Python 3.14+
- Node.js 20+
- Git
- Google Gemini API key

### Backend Deployment

#### 1. Environment Setup
```bash
cd C:/GoogleDriveSync/Projekty/LookCoach/code/backend
cp .env.example .env
# Edit .env:
# GEMINI_API_KEY=your_key_here
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
# Or manually:
pip install fastapi uvicorn sqlalchemy python-dotenv google-generativeai
```

#### 3. Run Backend
```bash
# Development (with reload)
uvicorn backend.main:app --reload --port 8010

# Production
uvicorn backend.main:app --host 0.0.0.0 --port 8010
```

#### 4. Verify
```bash
curl http://localhost:8010/health
# {"status": "healthy", "service": "LookCoach"}
```

### Frontend Deployment

#### 1. Install Dependencies
```bash
cd C:/GoogleDriveSync/Projekty/LookCoach/code/frontend
npm install
```

#### 2. Configure Environment
```bash
# Create .env
echo "VITE_API_URL=http://localhost:8010" > .env
```

#### 3. Run Development Server
```bash
npm run dev
# Opens at http://localhost:5173
```

#### 4. Build for Production
```bash
npm run build
# Output: dist/
```

#### 5. Preview Production Build
```bash
npm run preview
```

### Docker Deployment (Optional)
```dockerfile
# Dockerfile example
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]
```

---

## Future Roadmap

### Version 0.3.0 (Planned)
- [ ] User authentication (JWT)
- [ ] Social features (share progress)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration with wearables (Apple Watch, Fitbit)

### Version 1.0.0 (Target)
- [ ] Multi-language support
- [ ] AI voice coach
- [ ] AR posture correction overlay
- [ ] Marketplace (products, services)
- [ ] Subscription tiers (Free, Pro, Elite)

### Known Limitations
1. SQLite not suitable for production (use PostgreSQL)
2. No authentication (anyone can access any user's data)
3. File uploads not validated for malicious content
4. No rate limiting on API endpoints
5. Gemini API key exposed in backend (use secret management)

---

## Appendix

### Environment Variables
```bash
# Backend (.env)
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./lingua_ai.db  # Optional, default is SQLite

# Frontend (.env)
VITE_API_URL=http://localhost:8010
```

### Useful Commands
```bash
# View API docs
open http://localhost:8010/docs

# Check backend logs
tail -f logs/backend.log

# Reset database
rm code/backend/lingua_ai.db

# Update dependencies
cd code/backend && pip install -U -r requirements.txt
cd code/frontend && npm update
```

### Troubleshooting

**Backend won't start:**
- Check Python version (3.12 required, per ecosystem standard)
- Verify .env file exists with GEMINI_API_KEY
- Ensure port 8010 is not in use

**Frontend can't connect to backend:**
- Verify backend is running on port 8010
- Check CORS settings in main.py
- Ensure VITE_API_URL is correct

**Tests failing:**
- Run `npm install` to update dependencies
- Clear vitest cache: `npx vitest --clearCache`
- Check for port conflicts

---

**Documentation Version**: 1.0
**Last Updated**: 2026-05-08
**Maintainers**: Matthew19381
**Repository**: https://github.com/Matthew19381/LookCoach

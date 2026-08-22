# LookCoach — Task Roadmap

**Status:** v0.2.0 - Backend foundation complete, needs functional enhancements

---

## 🔗 PLAN v2 — AUDYT DOWODÓW + INTEGRACJA Z SYSTEMEM GŁÓWNYM (2026-07-19)

_Kontekst: `NEURO_PLAN.md` (zawiera pełny audyt SCIENTIFIC_FOUNDATION.md — sekcja 4)
+ `System-Glowny/MASTER_PLAN.md`._

⚠️ **UWAGA: sekcja "SCIENTIFIC RESEARCH FOUNDATION" poniżej oraz plik
`knowledge/SCIENTIFIC_FOUNDATION.md` zawierają twierdzenia bez pokrycia
w literaturze** (m.in. "+15-20% atrakcyjności za symetrię", "+20% za sen",
tabele przyrostów per ćwiczenie, cytowanie [2602.13368]). Pełna lista:
`NEURO_PLAN.md` §4. Do czasu rewizji NIE przenosić tych liczb do kodu/UI.

### E — Rzetelność dowodów (NEURO_PLAN faza 1)
- [ ] E-1: **LC-1** Evidence/ROI Engine v2: każda interwencja = {źródło, poziom
      dowodów, widełki efektu, czas}; ROI z niepewnością; wpisy przez Evidence
      Registry Systemu Głównego
- [ ] E-2: Rewizja SCIENTIFIC_FOUNDATION.md wg audytu (A1-A10 w NEURO_PLAN §4):
      usunięcie fabrykacji, przeklasyfikowanie gua sha/rozmarynu/sodu, dopisanie
      realnych źródeł (Hughes 2013, Axelsson 2010, Rhodes 2006...)
- [ ] E-3: **LC-9** Wyniki analizy twarzy jako obserwacje stanu — usunięcie
      liczbowych ocen atrakcyjności z UI (ryzyko dysmorficzne); detektor
      kompulsywnego skanowania → sygnał do Mentalności

### F — Funkcje (NEURO_PLAN fazy 2-3)
- [ ] F-1: **LC-2** Rutyna skincare (SPF/retinoid/niacynamid) z adaptacją do reakcji
- [ ] F-2: **LC-7** Consistency Tracker + Minimum Effective System (adherencja
      steruje trudnością)
- [ ] F-3: **LC-8** Health Safety Layer (twarde blokady + odsyłanie do dermatologa)
- [ ] F-4: **LC-6** Visual Progress: zdjęcia w kontrolowanych warunkach
- [ ] F-5: **LC-5** Event Mode oznaczony jako protokół HIPOTEZA z ostrzeżeniami

### INT — Integracja z Systemem Głównym
- [ ] INT-1: `GET /api/v1/summary` (adherencja protokołów, aktywne protokoły,
      obserwacje stanu, `wellbeing_contribution`)
- [ ] INT-2: Publisher eventów (`protocol_done`, `protocol_skipped`, `state_observation`)
      → `:8000` z `X-Module-Key`
- [ ] INT-3: **LC-4** Priorytet estetyczny jako dyrektywa do ForgeBody (dobór
      akcesoriów), potrzeby żywieniowe (sód/nabiał) do Diety — LookCoach nie
      generuje własnych planów treningowych/diet
- [ ] INT-4: Subskrypcja Affect Engine (sen/stres) — Sleep Engine bez własnego trackera
- [ ] INT-5: Poranna rutyna skincare jako pozycja planu dnia (planner)

---

## 📊 CURRENT STATE ANALYSIS

### Projekt: LookCoach (Looks Optimizer AI)
- **Stack:** FastAPI + React + Vite + Tailwind + SQLite + Gemini Vision + Ollama fallback
- **Backend:** 14 routers, 14 services, SQLAlchemy, 37 tests (74% coverage)
- **Frontend:** 14 pages, 87 tests, Axios API client
- **AI Services:** Gemini 2.0 Flash (primary), OpenRouter (fallback), Ollama (offline fallback)

---

## 🔬 SCIENTIFIC RESEARCH FOUNDATION

### Top Evidence-Based Interventions (według istniejących badań)

#### Najwyższy ROI (Effect/Time):
| Interwencja | Kategoria | Effect Size | Czas | ROI Score | Badania |
|-------------|-----------|-------------|------|-----------|---------|
| SPF 30+ Daily | skincare | 0.90 | 1 tydzień | 0.90 | RCT - najsilniejsza ochrona przeciwsłoneczna |
| 8h Sleep | sleep | 0.80 | 1 tydzień | 0.80 | RCT - sen wpływa na naprawę skóry |
| Hyaluronic Acid | skincare | 0.60 | 2 tygodnie | 0.212 | RCT - nawilżenie skóry |
| Low Sodium | nutrition | 0.60 | 2 tygodnie | 0.212 | RCT - redukcja obrzęków twarzy |
| Lymphatic Drainage | beauty | 0.60 | 2 tygodnie | 0.212 | RCT - redukcja obrzęków |
| Water 3L/day | nutrition | 0.50 | 3 tygodnie | 0.096 | RCT - hidratacja skóry |

#### Kluczowe Badania do Rozważenia:

**1. Body Proportions:**
- V-taper (shoulder/waist ratio) - badania wskazują na ratio ~1.5-1.6 jako optymalne dla mężczyzn
- W-H ratio (0.7) - uniwersalny wskaźnik atrakcyjności dla kobiet
- Symetria twarzy - kluczowy czynnik poprawiający perceived attractiveness o 15-20%

**2. Facial Features:**
- Width ratio (interocular/facial width) wpływa na perceived beauty
- Symmetry scoring - ocena symetrii proporcji twarzy
- Skin quality score - bezpośrednio koreluje z perceived age

**3. Training:**
- Pull-ups/Deadlifts - najskuteczniejsze na V-taper w 8-12 tygodni
- Face pulls - poprawa postawy 6-8 tygodni
- Chin tucks - redukcja forward head posture w 6 tygodni

---

## 🎯 PROPOSED SYSTEM ENHANCEMENTS

### Core Missing Functions (HIGH IMPACT)

#### F1. Smart Recommendation Engine
- [ ] `recommendations.py` → użyj prawdziwych danych z analizy
- [ ] Personalized priority scoring based on analysis gaps
- [ ] Adaptive recommendations (change as user progresses)
- [ ] Integration z profile preferences (goals/lifestyle)

#### F2. Progress Correlation Engine
- [ ] Correlation: sleep_hours ↔ skin_score
- [ ] Correlation: sodium_intake ↔ facial_puffiness
- [ ] Correlation: workout_frequency ↔ v_taper_score
- [ ] Correlation: stress_level ↔ muscle_tension
- [ ] Visual correlation charts w ProgressTracker

#### F3. Habit Tracker System
- [ ] `habits.py` router - codzienne nawyki (water, skincare, sleep, posture)
- [ ] Streak counter - ile dni z rzędu trzymasz nawyk
- [ ] Habit completion → przyrost LookScore
- [ ] Integration z experiments dla A/B testów nawyków

#### F4. Before/After Analysis
- [ ] Pixel diff analysis - highlight zmiany
- [ ] Side-by-side comparison z overlay toggle
- [ ] AI-generated progress notes
- [ ] Auto-detection improvement areas

---

## 🚀 ADVANCED FEATURES PROPOSAL

### A1. Weekly Insights Engine
- [ ] `insights.py` service - analiza tygodniowa
- [ ] Trend detection: "Twoja skóra się poprawiła, ale sen się pogorszył"
- [ ] Pattern recognition: "Po treningu V-taper rośnie szybciej"
- [ ] Automated email/SMS z insights

### A2. Dynamic Goal Adjustment
- [ ] Auto-adjust goals based on progress rate
- [ ] "Skin improving fast - add maintenance routine"
- [ ] "Body plateau - increase training intensity"
- [ ] Goal difficulty scaling

### A3. Social Features
- [ ] Progress sharing (anonimowe statystyki)
- [ ] Community challenges (30-day skincare, etc.)
- [ ] Leaderboard - "Top LookScore improvement"
- [ ] Mentor matching algorithm

### A4. AI Photo Coach
- [ ] Real-time feedback podczas uploadu
- [ ] Photo quality scoring (proper lighting, angle)
- [ ] Suggestion: "Take photo in better lighting for accurate analysis"
- [ ] Comparison z idealnym profile

### A5. Routine Scheduler
- [ ] Calendar integration
- [ ] Reminders dla skincare, supplement, workout
- [ ] Adaptive timing (based on user's schedule)
- [ ] Habit stacking suggestions

---

## 📱 NEW MODULES TO ADD

### N1. Supplement Tracker
- [ ] Database: popular supplements dla looks (biotin, zinc, vitamin D, omega-3)
- [ ] Dosage recommendations
- [ ] Interaction warnings (retinol + vitamin A)
- [ ] Progress tracking

### N2. Fashion Advisor
- [ ] Silhouette analysis (co maskuje, co podkreśla)
- [ ] Color matching based on skin tone
- [ ] Outfit suggestions dla events
- [ ] Wardrobe minimalization guide

### N3. Voice Coach
- [ ] Audio feedback dla ćwiczeń
- [ ] Voice-guided skincare routine
- [ ] Meditation scripts dla stres management
- [ ] Progress updates w formie podcastu

### N4. Barcode Scanner
- [ ] Skanowanie produktów kosmetycznych
- [ ] Ingredient analysis (aktywa, kontraindikacje)
- [ ] Safety check (pregnancy, allergies)
- [ ] Alternative suggestions

### N5. Weather Optimization
- [ ] Humidity impact na skórę
- [ ] UV index + sunscreen recommendations
- [ ] Temperature → workout timing
- [ ] Seasonal routine adjustments

---

## 🔬 SCIENTIFIC ENHANCEMENTS

### S1. Enhanced Evidence Engine
- [ ] Meta-analysis aggregation
- [ ] Confidence intervals dla effect sizes
- [ ] Contradiction detection (conflicting studies)
- [ ] Personal contraindication checker

### S2. Genetic Insights (Future)
- [ ] Skin type predisposition
- [ ] Muscle building potential
- [ ] Metabolism speed
- [ ] Personalized timelines

### S3. Lab Integration
- [ ] Blood test analysis (vitamin D, B12, iron, cortisol)
- [ ] Hormone impact on looks
- [ ] Deficiency recommendations
- [ ] Supplement prioritization

---

## 💰 MONETIZATION FEATURES

### M1. Premium Insights
- [ ] Advanced analytics (correlations, trends)
- [ ] Priority AI processing
- [ ] Custom routine generator
- [ ] Video call consultation

### M2. Product Integration
- [ ] Affiliate links do rekomendowanych produktów
- [ ] Price tracking (kiedy taniej kupić)
- [ ] Bundle deals dla routines
- [ ] Subscription management

---

## 🛠 TECHNICAL BACKLOG (existing)

### T1. Repository Cleanup
- [ ] Usuń garbage files: `1`, `8003)` w root
- [ ] Wyczyń `__pycache__/` katalogi
- [ ] Usuń `.coverage` z repo

### T2. Code Quality
- [ ] Stwórz `CLAUDE.md`
- [ ] Stwórz `pyproject.toml`
- [ ] Uzupełnij type hints (29% → 90%)
- [ ] Dodaj `.pre-commit-config.yaml`

### T3. Frontend Integration
- [ ] PhotoUpload → auto-analyze po uploadzie
- [ ] AnalysisResults → prawdziwe dane z API
- [ ] Recommendations → personalizacja po analizie
- [ ] SkincareRoutine → użyj danych skóry z analizy
- [ ] ProgressTracker → prawdziwe porównania

### T4. Bug Fixes
- [ ] `analysis.py:94` - brak importu `Path`
- [ ] Gemini Vision - brak eleganckiego handlingu braku API key
- [ ] Docker ports mismatch (8003 vs 8000)

---

## 📈 ROADMAP TIMELINE

### Month 1: Foundation
- Cleanup + bug fixes
- Frontend real data integration
- Habit tracker MVP

### Month 2: Intelligence
- Correlation engine
- Weekly insights
- Before/after analysis

### Month 3: Engagement
- Social features (anonimowe)
- Voice coach
- Weather optimization

### Month 4: Premium
- Supplement tracker
- Fashion advisor
- Barcode scanner
- Monetization prep

---

*Ostatnia aktualizacja: 2026-07-10*
# Projekt: LookCoach (Wygląd)

## Kontekst
AI-powered Looks Optimizer — system do optymalizacji wyglądu (twarz, ciało, skóra, włosy).

## Stack technologiczny
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy + SQLite
- **Frontend**: React 18 + Vite + TypeScript + Tailwind CSS + React Router v6
- **AI**: Google Gemini 2.0 Flash (cloud) + Ollama Llama3 (local fallback)
- **Containers**: Docker + Docker Compose
- **Charts**: Chart.js (react-chartjs-2)

## Struktura katalogów
```
LookCoach/
├── code/
│   ├── backend/ (FastAPI + routers + services + models)
│   └── frontend/ (React + Vite + TS)
├── docs/ (TECH_STACK.md, DEPLOYMENT.md)
├── knowledge/ (FEATURES.md)
├── decisions/ (puste)
├── logs/ (puste)
├── 03_Projects/LookCoach/ (duplikat struktury)
└── memory/projects/ (ten plik)
```

## Status (2026-05-07)
- **Wersja**: 0.1.0 (MVP)
- **Milestones**: M1-M7 ukończone
- **Backend**: modele, serwisy, 7 routerów API
- **Frontend**: 5 stron, API client, nawigacja
- **Docker**: compose z backend, frontend, ollama

## Do zrobienia (P5+)
- Moduły z spec.md: Video Learning, Event Mode, Confidence & Presence, Personal Experiment Engine
- Testy (pytest, jest)
- Autoryzacja użytkowników (JWT)
- Pełna integracja z YouTube API (video learning)

## Uwagi
- Kod w `code/` (zgodnie z WORKFLOW_STANDARD)
- Importy w backendzie: względne (`.models`, `.services`)
- CORS: porty 5173, 5175
- Fallback: Gemini → Ollama → heuristics

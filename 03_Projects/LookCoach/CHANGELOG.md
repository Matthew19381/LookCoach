# Changelog

All notable changes to LookCoach will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- M1: Project Setup – complete folder structure, Docker config, FastAPI scaffold, React+Vite+Tailwind frontend
- Stack: FastAPI, React 18, Vite, Tailwind, SQLite, Gemini Vision, Ollama LLM, Docker Compose, Chart.js
- Port assignment: API 8001, FE 5175, Ollama 11437, isolated network `lookcoach-network`
- Backend main.py with CORS, static uploads, health endpoint
- Frontend scaffold: Layout, navigation (5 pages), PhotoUpload stub, placeholder pages
- Documentation: docs/TECH_STACK.md, docs/DEPLOYMENT.md
- knowledge/FEATURES.md – full feature inventory (33 modules)

### Changed
- Project renamed from "Wyglad" to "LookCoach"

### Fixed
- N/A

## [0.1.0] – 2026-04-07

### Added
- Initial project structure (`code/` folder per WORKFLOW_STANDARD)
- Backend requirements.txt with FastAPI, SQLAlchemy, Gemini, Pillow, etc.
- Docker Compose configuration with backend, frontend, ollama services
- Frontend package.json with React, React Router, Chart.js, Lucide icons
- Vite config with proxy to backend (port 8001)
- Tailwind CSS setup
- Basic React routing and layout with navigation

### Changed
- N/A

### Fixed
- N/A

---

**Next milestones:** M2 (Database Models), M3 (Gemini Vision + Local LLM), M4 (Evidence & ROI Engines), M5 (API Endpoints), M6 (Frontend Core), M7 (Skincare Engine), M8 (Progress Tracker), M9 (Finalization)

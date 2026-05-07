# Tech Stack — Looks Optimizer

## Architektura

| Warstwa | Technologia | Cel |
|---------|-------------|-----|
| **Backend** | Python 3.12 + FastAPI | REST API, automatyzacja, AI integracja |
| **Frontend** | React 18 + Vite + React Router v6 | SPA, responsywny UI |
| **Baza danych** | SQLite (SQLAlchemy + Alembic) | Przechowywanie danych treningowych |
| **Konteneryzacja** | Docker + Docker Compose | Izolacja, łatwe deployment |
| **LLM lokalny** | Ollama (Llama) | Adaptacja planów, generowanie treści |
| **AI chmurowe** | Google Gemini Flash/Pro | Analiza sylwetki, quizy, ocena zdjęć |
| **Frontend UI** | Tailwind CSS | Styling |
| **Charts** | Chart.js (react-chartjs-2) | Wykresy progresu |

## Uzasadnienie wyboru technologii

### Backend: FastAPI
- Wysoka wydajność (async/await)
- Automatic OpenAPI docs
- Type hints → mniej błędów
- Idealny do AI/ML workloads

### Frontend: React 18 + Vite
- Szybki dev server (HMR)
- TypeScript-first
- Duży ecosystem
- React Router v6 — industry standard

### Database: SQLite + SQLAlchemy
- Zero-config, file-based
- Wystarczający na MVP
- Alembic — migrations out-of-box
- Możliwość migracji do PostgreSQL później

### Docker Compose
- Izolacja środowisk
- Łatwe `docker compose up`
- Dev + prod z tymi samymi imagami

### LLM: Ollama (Llama)
- **Lokalnie** — privacy, offline, 0 cost
- Adaptacja planów bez rate limits
- Fallback jeśli Gemini unavailable

### AI Cloud: Gemini Flash/Pro
- State-of-the-art vision models
- Analiza zdjęć (face/body/skin/hair)
- JSON output → structured data
- Flash = cheap, Pro = high accuracy

### UI: Tailwind CSS
- Utility-first → szybki prototyping
- Responsive out-of-box
- Custom design system możliwy

### Charts: Chart.js
- Lekka biblioteka
- Dobra TypeScript support
- Wystarczająca dla LookScore timeline

## Environment Variables

```bash
# .env
GEMINI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=sqlite:///./looks_optimizer.db
```

## Porty (izolacja per projekt)

- Backend: `http://localhost:8001`  (ForgeBody: 8000, LinguaAI: 8000)
- Frontend: `http://localhost:5175` (ForgeBody: 5174, LinguaAI: 5173)
- Ollama: `http://localhost:11437` (ForgeBody: 11435, LinguaAI: 11436)
- Gemini: API (cloud)

## Development Workflow

1. `docker compose up -d ollama` (pull llama2 / llama3)
2. `uvicorn main:app --reload --port 8001` (backend)
3. `npm run dev` (frontend, vite port 5175)
4. Open `http://localhost:5175`

---

**Stack approval:** ✓ Konfigurowalny (zmiana modelu, bazy, portów bez refactoru)

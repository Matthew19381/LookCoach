# LookCoach — Usprawnienia

> Ostatnia aktualizacja: 2026-06-07

## ✅ Zrobione

- [x] **.gitignore** — reguły VCS istnieją
- [x] **requirements.txt** — zależności zdefiniowane
- [x] **Testy** — 14 plików testowych w `code/backend/tests/`

## 📋 Do zrobienia

### Wysoki priorytet
- [ ] **Wyczyść śmieci z repo** — garbage files w root: `1`, `8003)` (puste/uszkodzone pliki)
- [ ] **Wyczyść __pycache__** — wiele katalogów `.pyc` w `code/backend/models/`, `routers/`, `services/`
- [ ] **Zaktualizuj .gitignore** — dodaj: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.coverage`, `htmlcov/`
- [ ] **Dodaj CLAUDE.md** — brak dokumentacji projektu dla modelu
- [ ] **Dodaj pyproject.toml** — brak metadanych pakietu

### Średni priorytet
- [ ] **Dodaj .pre-commit-config.yaml** — ruff lint+format, trailing whitespace
- [ ] **Uzupełnij type hints** — tylko 29% plików ma typy (18/62). Priorytet:
  - `code/backend/services/analysis.py`
  - `code/backend/routers/`
- [ ] **Przenieś testy** — `code/backend/tests/` → `tests/` (konwencja Python)

### Niski priorytet
- [ ] **Dodaj README.md** — opis projektu, stack, quick start

---

## 📁 Struktura

```
LookCoach/
├── code/backend/         # FastAPI backend
│   ├── routers/          # API endpoints
│   ├── services/         # Logika biznesowa (gemini_vision, analysis)
│   ├── models/           # SQLAlchemy models
│   ├── tests/            # 14 plików testowych (przenieść do root/tests/)
│   └── requirements.txt  # Zależności
├── frontend/             # Node.js frontend
├── decisions/            # ADR docs
└── .gitignore            # ✅ Wymaga aktualizacji
```

## 🔗 Linki

- [CHANGELOG](CHANGELOG.md)

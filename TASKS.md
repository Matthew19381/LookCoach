# LookCoach — Task Roadmap

**Status:** v0.3.0 — fundamenty naprawione (ACTION_PLAN Fazy 0–6, 2026-08-23).
Ten plik to **operacyjna lista bieżących zadań**, nie druga kopia strategii.
Strategia i architektura docelowa: `decisions/ACTION_PLAN_2026-08-09_wykonane_2026-08-23.md` + `NEURO_PLAN.md`.

---

## ✅ Zrealizowane (Fazy 0–5 — szczegóły w `decisions/ACTION_PLAN_2026-08-09_wykonane_2026-08-23.md`)

- [x] E-1 (**LC-1**) Evidence/ROI v2: widełki niepewności wg poziomu dowodów,
      `verify_evidence_db.py` jako brama rzetelności. *(pozostaje: podpięcie pod
      Evidence Registry Systemu Głównego)*
- [x] E-2: Rewizja `knowledge/SCIENTIFIC_FOUNDATION.md` wg audytu A1–A10
      (fabrykacje usunięte, każda liczba ma PMID lub jest `[HIPOTEZA]`).
- [x] E-3 (**LC-9**): analiza 100% jakościowa, zero liczbowych ocen atrakcyjności
      w UI/backendzie. *(pozostaje: detektor kompulsywnego skanowania → Mentalność)*
- [x] F-3 (**LC-8**): Health Safety Layer — twarde blokady przeciwwskazań +
      obowiązkowe disclaimer-y high-risk (12 testów).
- [x] INT-1: `GET /api/v1/summary` zgodny z kontraktem huba
      *(celowo bez `wellbeing_contribution` — do decyzji po stronie System-Głównego)*.
- [x] INT-2 (część): endpoint odbiorczy `POST /api/v1/integrations/event`
      z weryfikacją `X-Module-Key`, persystencja eventów.
- [x] Persystencja eksperymentów N=1 + Alembic (baseline + migracja health JSON).
- [x] Port 8010, wszystkie API pod `/api/v1/`, README.md + CLAUDE.md.

## 🔧 Bieżące zadania

### Integracja z Systemem Głównym
- [x] INT-2b: Publisher wychodzący (`protocol_done`, `protocol_skipped`,
      `state_observation`) → hub `:8000/api/v1/integrations/event`
      z `X-Module-Key`; obsługa 401 jako błąd konfiguracji, nie cicha porażka.
- [x] INT-3 (**LC-4**): priorytet estetyczny jako dyrektywa do ForgeBody,
      potrzeby żywieniowe (sód/nabiał) do Diety — LookCoach nie generuje
      własnych planów treningowych/diet.
- [ ] INT-4: Subskrypcja Affect Engine (sen/stres) — Sleep Engine bez własnego trackera.
- [ ] INT-5: Poranna rutyna skincare jako pozycja planu dnia (planner).

### Funkcje (NEURO_PLAN fazy 2–3)
- [ ] F-1 (**LC-2**): rutyna skincare istnieje, ale wymaga adaptacji do reakcji skóry.
- [ ] F-2 (**LC-7**): Consistency Tracker + Minimum Effective System
      (adherencja steruje trudnością).
- [ ] F-4 (**LC-6**): Visual Progress — zdjęcia w kontrolowanych warunkach.
- [ ] F-5 (**LC-5**): Event Mode oznaczony jako protokół HIPOTEZA z ostrzeżeniami.

### Drobne techniczne
- [ ] Rotacja klucza OpenRouter w `.env` (czynność człowieka — dostęp do panelu).
- [ ] Type hints w backendzie (obecnie częściowe).
- [ ] `.pre-commit-config.yaml` + `pyproject.toml`.

## 💡 Backlog (pomysły, brak priorytetu)

- Correlation Engine (sen ↔ skóra, sód ↔ obrzęki itd.) — wyłącznie jakościowo (LC-9).
- Before/After porównania zdjęć side-by-side (bez scoringu).
- Photo quality check przed analizą (oświetlenie/kąt).
- Barcode scanner kosmetyków + safety check (pregnancy/allergies).

*Ostatnia aktualizacja: 2026-08-23*

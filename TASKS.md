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
- [x] INT-3b (2026-09-27): odbiór dyrektyw huba `POST /api/v1/directives` (survival_mode → poziom SURVIVAL w Consistency Trackerze).
- [ ] INT-4: Subskrypcja Affect Engine (sen/stres) — Sleep Engine bez własnego trackera.
- [ ] INT-5: Poranna rutyna skincare jako pozycja planu dnia (planner).

### Funkcje (NEURO_PLAN fazy 2–3)
- [x] F-1 (**LC-2**): rutyna skincare z adaptacją do reakcji skóry i rotacją składników wg tolerancji — zaimplementowano `SkinReactionTracker`, `IngredientRotationManager`, `check_ingredient_conflicts`, `get_evidence_summary`, nowe endpointy API (`/routine/adaptive`, `/reaction/log`, `/rotation/recommendations`, `/tolerance/{ingredient}`), 20 nowych testów.
- [x] F-2 (**LC-7**): Consistency Tracker + Minimum Effective System (adherencja steruje trudnością). Zaimplementowano `ConsistencyTracker` z `AdherenceLog`, `ProtocolAdherence`, `ConsistencyMetrics` modelami, router `/api/v1/consistency` z endpointami do logowania adherencji, obliczania rate, rekomendowanego trudności, minimum effective protocol, summary, pattern alerts. 23 testy w `test_consistency.py`.
- [ ] F-4 (**LC-6**): Visual Progress — zdjęcia w kontrolowanych warunkach.
- [ ] F-5 (**LC-5**): Event Mode oznaczony jako protokół HIPOTEZA z ostrzeżeniami.

### Drobne techniczne
- [x] Rotacja składników (F-1): historia z „Użyłem dziś” (produkty użytkownika), skan zdjęcia składu (2026-09-27).
- [ ] Rotacja klucza OpenRouter w `.env` (czynność człowieka — dostęp do panelu).
- [ ] Type hints w backendzie (obecnie częściowe).
- [ ] `.pre-commit-config.yaml` + `pyproject.toml`.
- [x] Backend Ruff: konfiguracja w `pyproject.toml`, czysty wynik `ruff check code/backend`
      oraz pełny zestaw 287 testów backendowych.

## 💡 Backlog (pomysły, brak priorytetu)

- Correlation Engine (sen ↔ skóra, sód ↔ obrzęki itd.) — wyłącznie jakościowo (LC-9).
- Before/After porównania zdjęć side-by-side (bez scoringu).
- Photo quality check przed analizą (oświetlenie/kąt).
- Barcode scanner kosmetyków + safety check (pregnancy/allergies).

*Ostatnia aktualizacja: 2026-08-23*

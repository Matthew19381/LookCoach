# LookCoach

Wygląd: analiza zdjęć, rekomendacje z poziomem dowodu, rutyny. Moduł ekosystemu System-Główny.

## Najpierw mapa, nie dokumenty
- Porty, uruchamianie, API, zależności: `C:\Projects\KB\mapa\INDEX.md` (w chmurze: repo `Matthew19381/KB`, katalog `mapa/`);
  ten moduł: `mapa/moduly/LookCoach.md`. Czytaj tylko potrzebną sekcję.
- Bieżący plan: `decisions/ACTION_PLAN_2026-11-01.md`. Audyt naukowy: `NEURO_PLAN.md` §4.
- Pełna dawna wersja tego pliku (tabela 26 routerów, kontrakt huba): `docs/archiwum/CLAUDE-do-2026-11-06.md`.

## Zasady (Mateusz)
- Usługi uruchamiaj tylko przez `Start-ScheduledTask -TaskName Ekosystem-Start`.
- Push i scalanie tylko po zgodzie Mateusza. Repo jest **publiczne**: przed push skan sekretów. Nie zmieniaj plików `.env`.

## Zasady domeny (twarde)
1. LC-9: zero liczbowych ocen atrakcyjności; postęp słowami (`services/state_labels.py`), styl życia kategoriami (`services/lifestyle_status.py`).
2. LC-1: każdy wpis `EVIDENCE_DB` (`services/evidence_engine.py`) z poziomem rct/meta ma URL PubMed/DOI; pilnuje `python -m backend.scripts.verify_evidence_db` (z `code/`).
3. ROI jako widełki (`roi_engine.py`), UI pokazuje kategorie potencjału, nie liczbę.
4. LC-8: `services/health_safety.py` usuwa przeciwwskazane pozycje; flagi w `user_profiles.health` (JSON).

## Pułapki
- Backend uruchamiaj z `code/` (`backend.main:app`), testy z `code/backend` (`python -m pytest tests/`); frontend `cd code/frontend && npm test -- --run`.
- Migracje: `code/backend/migrations/versions/`; zmiana schematu = nowa migracja (`cd code/backend && alembic revision --autogenerate`), nie `create_all`. Nowy model: import w `models/__init__.py`.
- Względne `sqlite:///` kotwiczone do katalogu `database.py`; zdjęcia i cache w `backend/paths.py` (`photo_path()`, `photo_url()`).
- Upload tylko przez `services/photo_storage.sanitize_image()` (usuwa EXIF). Ostatnia analiza tylko przez `services/analysis_store.load_latest_analysis()`.
- Do huba wyłącznie przez kolejkę `services/outbox.enqueue()`, nie przez `IntegrationPublisher` bezpośrednio.
- Mutując kolumnę JSON, najpierw ją skopiuj (`json.loads(json.dumps(...))`), inaczej UPDATE nie poleci.
- Nowe modele w stylu `Mapped[...]` (mypy).

## Konwencje
Commity `<typ>: co i dlaczego` z listą plików (feat, fix, refactor, style, docs, chore, test). Nigdy `.env`, `*.db`, `node_modules`.

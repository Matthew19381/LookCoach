# Deployment & Isolation — LookCoach

## 🔥 Rozwiązania konfliktów multi-project

### 1. Porty hosta — rejestr: `System-Glowny/CLAUDE.md` (jedyne źródło prawdy)

| Moduł | API | Frontend (dev) |
|---|---|---|
| System-Główny (hub) | 8000 | 5173 |
| ForgeBody | 8002 | 5182 |
| Dieta | 8009 | 5189 |
| **LookCoach** | **8010** | **5175** (Ollama w Dockerze: 11437) |

### 1a. Dostęp sieciowy (2026-11-02, plan 2.2)

Zdjęcia ciała to dane wrażliwe, a API nie ma logowania (system jednoosobowy, decyzja D2):

- **Backend słucha tylko na `127.0.0.1`**: `uvicorn` domyślnie (nie dodawaj `--host 0.0.0.0`
  poza kontenerem), w Dockerze port publikowany jako `127.0.0.1:8010:8010`. Hub działa na tym
  samym komputerze, więc łączy się bez zmian.
- **Telefon w LAN** łączy się z frontendem (Vite `host: true`, port 5175), który proxuje `/api`
  i `/uploads` do backendu. To świadomy wyjątek: każdy w Twojej sieci domowej, kto zna adres,
  zobaczy aplikację. Nie wystawiaj portu 5175 do internetu (bez przekierowań na routerze).
- Upload przyjmuje tylko JPEG/PNG/WEBP do 15 MB; plik jest przekodowywany, co usuwa EXIF
  (w tym lokalizację GPS) — `services/photo_storage.py`.

### 2. Wolumeny Docker — izolacja per Docker Compose project

Każdy `docker-compose.yml` definiuje własne wolumeny:

```yaml
volumes:
  lookcoach-ollama-data:  # tylko dla tego projektu
  lookcoach-db-data:      # jeśli db w kontenerze
```

Docker Compose traktuje każdy folder jako oddzielny **project** → wolumeny nie kolidują.

### 3. Sieci Docker — każdy projekt ma własną bridge network

```yaml
networks:
  lookcoach-network:
    driver: bridge
```

Kontenery w `lookcoach-network` nie widzą kontenerów z innych projektów (chyba że celowo podpięte).

### 4. Pliki bazy danych

- Każdy projekt ma swój `*.db` we własnym folderze
- Brak współdzielenia zasobów

## 📊 Struktura dysku

```
03_Projects/
├── ForgeBody/
│   └── code/
│       ├── docker-compose.yml  ← własne wolumeny/network/porty
│       ├── backend/
│       └── frontend/
├── LinguaAI/
│   ├── docker-compose.yml
│   ├── backend/
│   └── frontend/
└── LookCoach/
    ├── docker-compose.yml      ← izolowane
    ├── code/
    │   ├── backend/
    │   └── frontend/
    └── data/                   # bazy, cache (opcjonalnie)
```

Wszystkie projekty współistnieją w `03_Projects/` bez konfliktów dzięki:
- Różnym portom hosta
- Izolacji wolumenów
- Wydzielonym sieciom Docker
- Lokalnym plikom DB

---

**Key takeaway:** Każdy projekt to samodzielny Docker Compose ecosystem. Nie ma globalnych zasobów dzielonych między projektami.

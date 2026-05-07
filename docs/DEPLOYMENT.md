# Deployment & Isolation — Looks Optimizer

## 🔥 Rozwiązania konfliktów multi-project

### 1. Porty hosta — każdy projekt ma własne zestawienie

| Projekt | API port | Frontend port | Ollama port |
|---------|----------|---------------|-------------|
| ForgeBody | 8000 | 5174 | 11435 |
| LinguaAI | 8000 | 5173 | 11436 |
| **Wyglad** | **8001** | **5175** | **11437** |

**Uwaga:** Porty API (8000) można dzielić tylko jeśli nie uruchamia się równolegle. Dla pełnej izolacji każdy projekt ma unikalny port API.

### 2. Wolumeny Docker — izolacja per Docker Compose project

Każdy `docker-compose.yml` definiuje własne wolumeny:

```yaml
volumes:
  wyglad-ollama-data:  # tylko dla tego projektu
  wyglad-db-data:      # jeśli db w kontenerze
```

Docker Compose traktuje każdy folder jako oddzielny **project** → wolumeny nie kolidują.

### 3. Sieci Docker — każdy projekt ma własną bridge network

```yaml
networks:
  wyglad-network:
    driver: bridge
```

Kontenery w `wyglad-network` nie widzą kontenerów z innych projektów (chyba że celowo podpięte).

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
└── Wyglad/
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

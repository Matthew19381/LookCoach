# LookCoach – Feature Inventory

**Total Modules:** 33 (from spec.md)
**Implementation Status:** M1 completed, M2-M9 pending

---

## Core Intelligence (5)

1. **Dynamiczny profil użytkownika** – cele, styl życia, discipline model, historia progresu
2. **Evidence Engine** – poziom dowodów (RCT/meta), siła efektu, czas do efektu, filtrowanie pseudonauki
3. **Explainable AI** – tryb szybki (1 zdanie) + deep dive (mini lekcja) + tłumaczenie "dlaczego" i konsekwencje
4. **Looks ROI Engine** – ranking działań (efekt vs czas vs trudność), dynamiczne priorytety
5. **Attractiveness Levers System** – wykrywa główne ograniczenia wyglądu, skupia się na największym ROI

---

## Analiza wyglądu (AI) (5)

6. **Face Analyzer PRO** – proporcje twarzy, opuchlizna/retention wody, napięcie mięśni twarzy, analiza skóry
7. **Face State Detection** – wykrywa: zmęczenie, odwodnienie, "puffy face", generuje szybkie działania
8. **Body Analyzer** – proporcje sylwetki (V-taper), asymetrie, brakujące partie mięśni
9. **Skin Diagnostic AI** – typ skóry, problemy dermatologiczne, tracking zmian
10. **Hair Analyzer** – gęstość, linia włosów, rekomendacje stylu i pielęgnacji

---

## Skincare + Techniki (3)

11. **Skincare Engine** – rutyna (rano/wieczór), rotacja składników aktywnych, adaptacja do reakcji skóry
12. **Beauty Techniques Module** – gua sha, masaż limfatyczny, zimna woda/cold exposure, napięcie mięśni twarzy, poprawa wyglądu włosów
13. **Video Learning Engine** – materiały instruktażowe z YouTube (tylko wysokiej jakości) powiązane z technikami

---

## Sylwetka (2)

14. **Aesthetic Training Engine** – minimalny efektywny plan, priorytet estetyczny (V-taper), eliminacja zbędnych ćwiczeń
15. **Posture Correction System** – wykrywanie: garbienia, forward head posture; plan korekcji

---

## Dieta (2)

16. **Nutrition for Looks Engine** – dieta pod skórę, hormony, retencję wody; dynamiczna adaptacja
17. **Event Mode** – przygotowanie na konkretny dzień; optymalizacja twarzy/skóry; manipulacja: wodą, snem, dietą

---

## Regeneracja (2)

18. **Sleep Engine** – optymalizacja jakości snu, wpływ na wygląd
19. **Stress Engine** – wpływ kortyzolu, szybkie interwencje

---

## Tracking (3)

20. **Visual Progress Tracker** – porównanie zdjęć, wykrywanie zmian
21. **Look Score System** – twarz, skóra, sylwetka, globalny indeks
22. **Consistency Tracker** – mierzy trzymanie planu, dostosowuje trudność

---

## Adaptacja (3)

23. **Smart Feedback Loop** – brak efektów → zmiana planu; przeciążenie → redukcja
24. **Minimum Effective System** – dopasowanie do realnej konsekwencji; eliminacja "idealnych, ale niewykonalnych" planów
25. **Fast Fix Protocols** – szybkie poprawki: twarz (10–30 min), skóra (1–3 dni)

---

## Edukacja (1)

26. **Micro-Learning System** – krótkie lekcje, poziomy trudności

---

## Automatyzacja (1)

27. **AI Look Coach** – codzienne wskazówki, alerty (pogorszenie skóry, brak progresu)

---

## Eksperymenty (1)

28. **Personal Experiment Engine** – testowanie: dieta, skincare, techniki; wybór najlepszego wariantu

---

## Integracje (2)

29. **API Input** – przyjmuje dane: zmęczenie, stres, sen
30. **API Output** – zwraca: rekomendacje, zmiany planu dla głównego systemu

---

## Tryby (1)

31. **Tryby działania** – maintenance, improvement, event

---

## Bezpieczeństwo (1)

32. **Health Safety Layer** – blokada ekstremalnych zaleceń, ostrzeżenia

---

## Confidence Layer (1)

33. **Confidence & Presence System** – analiza: postawy ciała, ekspresji twarzy; rekomendacje: poprawa mowy ciała, mikro nawyki; wpływ na percepcję atrakcyjności

---

## Milestone Mapping

| Milestone | Features Implemented |
|-----------|---------------------|
| M1 | Project Setup (0 features, infrastructure only) |
| M2 | Database Models (0 features, persistence layer) |
| M3 | Gemini Vision Service + Local LLM (6,7,8,9,10 – analysis core) |
| M4 | Evidence & ROI Engines (1,2,3,4,5 – recommendation core) |
| M5 | API Endpoints (wire up all features) |
| M6 | Frontend Core (UI for all features) |
| M7 | Skincare Engine (11 + 12 partial) |
| M8 | Visual Progress Tracker (20,21,22) |
| M9 | Integration Stubs + Finalization (29,30) |

**Remaining features (after M9):** 13,14,15,16,17,18,19,23,24,25,26,27,28,31,32,33 → future sprints

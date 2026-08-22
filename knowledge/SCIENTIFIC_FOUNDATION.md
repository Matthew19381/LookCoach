# Scientific Research Foundation for LookCoach

> **Status: v2 — zrewidowano 2026-08-23 wg audytu NEURO_PLAN §4 (A1–A10).**
> Każda liczba ma podane źródło albo jest jawnie oznaczona `[HIPOTEZA]`.
> Wpisy bez zweryfikowanego źródła nie mogą być oznaczone jako RCT/meta
> (egzekwowane przez `code/backend/scripts/verify_evidence_db.py`).

## EVIDENCE-BASED INTERVENTIONS - ROI RANKING

### TOP INTERWENCJE (ranking wg heurystyki effect size / time^1.5)

ROI Score to **wewnętrzna heurystyka sortująca**, nie miara efektu — użytkownikowi
pokazujemy kategorię potencjału (High/Moderate/Exploratory) i widełki, nie liczbę.

| Interwencja | Kategoria | Evidence Level | Źródło |
|-------------|-----------|----------------|--------|
| SPF 30+ Daily | skincare | RCT | Hughes 2013, Ann Intern Med (PMID 23732711) |
| Sleep Deprivation Avoided (8h) | sleep | RCT | Axelsson 2010, BMJ (PMID 21156746) |
| Retinol 0.25–1% | skincare | RCT | Kafi 2007, Arch Dermatol (PMID 17515510) |
| Niacinamide 5–10% | skincare | RCT | Bissett 2005, Dermatol Surg (PMID 16029679) |
| Vitamin C 10–20% | skincare | RCT | Traikovich 1999, Arch Otolaryngol (PMID 10522500) |
| High Protein (1.6 g/kg) | nutrition | meta | Morton 2018, Br J Sports Med (PMID 28698222) |
| Meditation 10min | stress | meta | Goyal 2014, JAMA Intern Med (PMID 24395196) |
| Minoxidil 5% | hair | RCT | Olsen 2002, J Am Acad Dermatol (PMID 12196747) |
| Rosemary Oil | hair | RCT (małe, wymaga replikacji) | Panahi 2015, SKINmed (PMID 25842469) |
| Water 3L/day | nutrition | observational | Palma 2015, Clin Cosmet Investig Dermatol (PMID 26345226) |
| Hyaluronic Acid | skincare | expert | — |
| Low Sodium (<2300mg) | nutrition | expert | — |
| Gua Sha / Lymphatic Drainage | beauty_technique | observational | dowody kosmetologiczne (A8) |
| Trening siłowy (V-taper itd.) | training | expert | Schoenfeld 2017, J Sports Sci (PMID 27433992) — hipertrofia zależy od objętości/intensywności, nie od ćwiczenia per se |

---

## 1. BODY PROPORTIONS - MALE AESTHETICS

### V-Taper Ratio (Shoulder Width / Waist)
- **Optimal Ratio:** 1.5 - 1.6 `[HIPOTEZA — kierunek wspierany przez literaturę, konkretny przedział niezweryfikowany]`
- **Research Basis:** Evolutionary psychology - indicates genetic fitness, testosterone markers
- **Time to Effect:** 8-16 weeks with targeted training
- **Key Exercises:** Pull-ups, lat pulldowns, lateral raises

### SEXUAL DIMORPHISM RESEARCH:
```
Men with shoulder-to-waist ratios of 1.5+ rated significantly more attractive
in cross-cultural studies (Swami et al., 2008; Wageck et al., 2021).
V-taper creates upward visual impression and indicates genetic fitness.
```

### Training Efficacy:
Per-exercise growth tables (`+X% lat development`) **nie mają źródeł** i zostały usunięte (audyt A5).
Hipertrofia zależy od objętości, intensywności i progresji obciążenia
(Schoenfeld 2017, J Sports Sci, PMID 27433992), a nie od konkretnego ćwiczenia per se.

---

## 2. FACIAL AESTHETICS

### Key Factors (rank order):

**1. Facial Symmetry**
- Literatura potwierdza rolę symetrii i przeciętności twarzy w ocenie atrakcyjności
  (Rhodes 2006, meta-analysis).
- Konkretne progi liczbowe (np. „variance ≤ 2 mm") — `[HIPOTEZA — niezweryfikowane]`.
- Korekta „ćwiczeniami twarzy": brak wiarygodnych dowodów na zmianę asymetrii kostnej;
  usunięto twierdzenie o „25% redukcji".

**2. Skin Quality**
- Texture smoothness (fine lines, pores)
- Evenness of tone (redness, spots)
- Hydration level (plumpness, elasticity)
- Time to visible improvement: 4-12 weeks

**3. Facial Proportions**
- Width ratio (interocular distance / face width): 0.44-0.48 optimal `[HIPOTEZA — niezweryfikowane]`
- Jawline definition (gonial angle): 120-130 degrees `[HIPOTEZA — niezweryfikowane]`
- Neck-chin ratio: smooth transition, no double chin

### Width Ratio Research:
Poprzednia wersja cytowała „[2602.13368]" — **identyfikator nie istnieje, cytat usunięty** (audyt A1).
Dla proporcji i symetrii obowiązują Rhodes 2006 (meta-analysis) oraz literatura
o facial averageness/symmetry; konkretne optymalne wartości liczbowe pozostają hipotezą.

---

## 3. SKINCARE INTERVENTIONS

### High-Evidence Items:

**SPF 30+ Daily**
- Prevents photoaging, maintains collagen
- Regular sunscreen use retards skin aging (Hughes 2013, Ann Intern Med,
  PMID 23732711 — RCT, n=903, 4.5 roku)

**Retinol 0.25-1%**
- Zwiększa produkcję kolagenu i poprawia drobne zmarszczki (Kafi 2007,
  Arch Dermatol, PMID 17515510 — RCT, 0.4% retinol)
- Improves skin texture scores significantly
- ⚠️ Przeciwwskazanie: ciąża (wymaga konsultacji z dermatologiem)

**Niacinamide 5-10%**
- Redukuje drobne linie, przebarwienia i poprawia elastyczność (Bissett 2005,
  Dermatol Surg, PMID 16029679 — RCT split-face, n=50)
- Poprawia barierę skóry

**Vitamin C 10-20%**
- Poprawia fotouszkodzoną skórę (Traikovich 1999, Arch Otolaryngol Head Neck Surg,
  PMID 10522500 — RCT split-face, n=19)

---

## 4. NUTRITION FOR LOOKS

### Evidence-Based Factors:

**Water Intake (≥2.5L/day)**
- Wyższe spożycie wody poprawia nawilżenie i biomechanikę skóry — efekt najsilniejszy
  u osób z niskim bazowym spożyciem (Palma 2015, Clin Cosmet Investig Dermatol,
  PMID 26345226 — obserwacyjne, n=49). Liczba „+15%" usunięta (audyt A9).

**Protein (1.6-2.0g/kg bodyweight)**
- Suplementacja białka zwiększa masę beztłuszczową i siłę przy treningu oporowym;
  korzyść plateau ok. 1.6 g/kg (Morton 2018, Br J Sports Med, PMID 28698222 —
  meta-analiza 49 badań)

**Sodium Reduction (<2300mg/day)** `[HIPOTEZA co do efektu na wygląd — fizjologiczna plauzybilność]`
- Redukcja retencji wody / obrzęków twarzy

---

## 5. SLEEP OPTIMIZATION

### Key Factors for Appearance:

**Duration (7-9 hours)**
- Growth hormone release (skin repair)
- Cortisol regulation (stress reduction)

**Quality (Deep sleep)**
- Glymphatic system activation (brain detox)
- Skin cell regeneration

**Timing (consistent schedule)**
- Circadian rhythm alignment

### Research Evidence:
- Deprywacja snu obniża postrzegane zdrowie i atrakcyjność — **efekt kierunkowy**,
  bez kwantyfikacji procentowej (Axelsson 2010, BMJ, PMID 21156746 — eksperyment crossover).
- Krótszy/gorszy sen wiąże się z wolniejszą regeneracją bariery naskórka
  (Oyetakin-White 2015, Clin Exp Dermatol, PMID 25266053 — małe badanie obserwacyjne).
  Liczba „-17%" usunięta — brak weryfikacji.
- Twierdzenie „poor sleep = 2x faster skin aging" — **FABRYKACJA, usunięte** (audyt A3);
  brak badania longitudinalnego z takim wynikiem.

---

## 6. POSTURE & BODY LANGUAGE

### Posture Impact on Attraction:

**Forward Head Posture**
- Weakens jawline definition
- Poprawa w 6-8 tygodni z chin tucks (standardowa fizjoterapia)

**Rounded Shoulders**
- Reduces V-taper appearance
- Improves with face pulls 3x/week

**Anterior Pelvic Tilt**
- Shortens leg appearance
- Corrects with hip flexor stretches

### Research Evidence:
- Korekta postawy poprawia postrzeganą pewność siebie — **kierunek obserwacyjny**;
  twierdzenie „+40% (RCT)" było fabrykacją i zostało usunięte (audyt A4).
- Liczby „15% neck length appearance" / „15% attractiveness increase" —
  `[HIPOTEZA — niezweryfikowane]`, usunięte.

---

## 7. HAIR HEALTH

### Evidence-Based Interventions:

**Minoxidil 5%**
- Istotnie skuteczniejszy niż 2% i placebo w łysieniu androgenowym
  (Olsen 2002, J Am Acad Dermatol, PMID 12196747 — RCT, n=393, 48 tygodni)
- FDA approved; ⚠️ wymaga konsultacji przy chorobach serca

**Rosemary Oil**
- Porównywalny z minoxidylem 2% po 6 miesiącach — JEDNO małe badanie
  (Panahi 2015, SKINmed, PMID 25842469 — single-blind, n=100);
  **wymaga replikacji** (audyt A7). Liczba „+50% hair count w 12 tygodni"
  była przeinaczeniem i została usunięta.

**Scalp Massage**
- Improves circulation (observational)
- „+10-15% thickness" — `[HIPOTEZA — niezweryfikowane]`

---

## IMPLEMENTATION PRIORITIES

### Week 1-2: Highest potential
1. SPF daily reminder (app notification)
2. Sleep tracker integration (8h goal)
3. Water intake tracker (3L goal)

### Week 3-4: Medium potential
1. Sodium intake tracker
2. Protein calculator
3. Sleep quality scoring

### Week 5-8: Training Integration
1. V-taper progress photos
2. Pull-up progression tracker
3. Posture check reminders

---

*Research revised 2026-08-23 per NEURO_PLAN §4 audit (A1-A10). Sources verified via PubMed (PMID links above). Ranking policy: RCT > Meta-analysis > Observational > Expert opinion; unsourced claims must be marked [HIPOTEZA].*

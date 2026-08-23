# NEURO_PLAN — LookCoach (v1.0)

> Część ekosystemu: `System-Glowny/MASTER_PLAN.md` (standard naukowy: sekcja 0).
> Zawiera AUDYT `knowledge/SCIENTIFIC_FOUNDATION.md` (sekcja 4) — zgodnie
> z decyzją o pełnym rygorze.

## 1. Rola w ekosystemie
Optymalizacja wyglądu wg uczciwego ROI: silnik Evidence/ROI zostaje (dobra
architektura), ale liczby wymagają ponownego ugruntowania. Zasada: rekomendacja
bez wiarygodnego źródła spada do poziomu HIPOTEZA i nie może być prezentowana
z liczbowym "effect size".

## 2. Fundament naukowy (twierdzenia, które BRONIĄ się w literaturze)
| Obszar | Co pokazują badania | Źródło | Poziom |
|---|---|---|---|
| Fotoprotekcja (SPF) | codzienny SPF spowalnia fotostarzenie — twardy RCT | Hughes et al. 2013 (Ann Intern Med, 4.5 roku) | RCT |
| Retinoidy | poprawa zmarszczek/tekstury — najlepiej przebadany składnik | liczne RCT (tretinoina: Weiss 1988; retinol: Kafi 2007) | RCT/META |
| Niacynamid | bariera, przebarwienia, łojotok — umiarkowane RCT | np. Hakozaki 2002; Draelos 2006 | RCT |
| Witamina C | antyoksydacja/fotoprotekcja wspomagająca, rozjaśnianie | RCT małe; przeglądy dermatologiczne | RCT (małe) |
| Sen a atrakcyjność postrzegana | niewyspani oceniani jako mniej atrakcyjni/zdrowi | Axelsson et al. 2010 (BMJ); Sundelin 2017 | RCT-lab |
| Minoxidil 5% | wzrost gęstości włosów — FDA, wiele RCT | Olsen et al. 2002 i in. | META |
| Proporcje sylwetki (V-taper) | preferencje dla wyższego stosunku barki/talia u mężczyzn — replikowane w badaniach preferencji | np. Dixson et al. 2003; Swami & Tovée | OBS |
| Postawa | wpływ postawy na percepcję pewności/atrakcyjności — kierunkowo tak, liczby niepewne | badania percepcji sylwetki | OBS |
| Sód a retencja wody | manipulacja sodem zmienia retencję — mechanizm solidny; "efekt na twarz w 48h" = ekstrapolacja | fizjologia nerkowa; brak RCT "twarzowych" | OBS/HIPOTEZA |

## 3. Funkcje
| ID | Funkcja | Podstawa | Poziom |
|---|---|---|---|
| LC-1 | **Evidence/ROI Engine v2**: każda interwencja = {źródło, poziom, szacunek efektu z widełkami, czas do efektu}; ROI liczone na widełkach, ranking z niepewnością (nie fałszywa precyzja "0.212") | standard ekosystemu | — |
| LC-2 | Rutyna skincare (SPF/retinoid/niacynamid) z adaptacją do reakcji skóry; rotacja składników wg tolerancji | Hughes 2013; RCT retinoidów | RCT |
| LC-3 | Sleep Engine = konsument Affect Engine (nie własny tracker); komunikat oparty o Axelsson 2010, bez wymyślonych procentów | Axelsson 2010 | RCT-lab |
| LC-4 | Trening estetyczny: delegacja do ForgeBody (priorytet V-taper jako dyrektywa), nie własny generator planów | integracja; Dixson 2003 (cel) | OBS |
| LC-5 | Event Mode (przygotowanie na dzień X): manipulacja sodem/snem/nawodnieniem jako protokół oznaczony OBS/HIPOTEZA, z ostrzeżeniami zdrowotnymi | mechanizmy fizjologiczne | HIPOTEZA |
| LC-6 | Visual Progress Tracker: zdjęcia w kontrolowanych warunkach (światło/pora/pozycja) — bez tego porównania mierzą oświetlenie, nie postęp | metodologia pomiaru | — |
| LC-7 | Consistency Tracker + Minimum Effective System (już w FEATURES — dobre): adherencja steruje trudnością planu | Lally 2010; jak FB-5 | OBS |
| LC-8 | Health Safety Layer: twarde blokady (min. kalorie, zakaz łączenia agresywnych aktywów, odsyłanie do dermatologa przy zmianach skórnych) | bezpieczeństwo | — |
| LC-9 | Analiza twarzy AI: wyniki jako obserwacje ("retencja wody wyżej niż zwykle"), NIE oceny liczbowe atrakcyjności — patrz audyt A6 i sekcja anty-wzorce | — | — |

## 4. AUDYT SCIENTIFIC_FOUNDATION.md (twierdzenia do poprawy/oznaczenia)
| # | Twierdzenie w dokumencie | Werdykt | Uzasadnienie |
|---|---|---|---|
| A1 | Cytowanie "[2602.13368] Width Ratios..." | **NIEZWERYFIKOWANE — usunąć lub podać realne źródło** | wygląda na identyfikator arXiv, nie znajduję takiej pracy; proporcje twarzy mają literaturę (facial averageness/symmetry: Rhodes 2006, META) — użyć jej |
| A2 | "8+ hours sleep increases perceived attractiveness by 20%" | **FABRYKACJA LICZBY** | Axelsson 2010 pokazuje efekt kierunkowy w ocenach, nie "+20%" |
| A3 | "Poor sleep = 2x faster skin aging" | **FABRYKACJA** | brak badania longitudinalnego z takim wynikiem; jest OBS o gorszej barierze skóry przy złym śnie (Oyetakin-White 2015, małe) |
| A4 | "Posture correction improves perceived confidence by 40% (RCT)" | **FABRYKACJA** | nie znajduję takiego RCT; kierunek OBS |
| A5 | "Pull-ups +12-15% lat development in 8 weeks" itd. | **FABRYKACJA precyzji** | tabele przyrostów per ćwiczenie nie mają źródeł; hipertrofia zależy od objętości/intensywności (Schoenfeld 2017), nie od ćwiczenia per se |
| A6 | "Facial symmetry ≤2mm variance optimal", "width ratio 0.44-0.48", "gonial angle 120-130°" | **HIPOTEZA** | literatura potwierdza rolę symetrii/przeciętności (Rhodes 2006, META), ale nie te progi liczbowe |
| A7 | Rosemary oil "50% increase in hair count (RCT)" | **PRZEINACZENIE** | Panahi 2015: rozmaryn ≈ minoxidil 2% po 6 mies. w JEDNYM małym RCT; bez "+50%"; oznaczyć RCT-małe/replikacja potrzebna |
| A8 | Gua sha / lymphatic drainage "RCT, effect 0.6" | **ZAWYŻONE** | dowody głównie kosmetologiczne/obserwacyjne; przeklasyfikować na OBS/HIPOTEZA |
| A9 | "Skin hydration +15% in 2 weeks (water 3L)" | **WĄTPLIWE** | badania nawodnienia skóry pokazują efekty u osób z niskim spożyciem (Palma 2015, OBS); liczba do usunięcia |
| A10 | SPF/retinol/niacynamid/minoxidil/protein/sleep duration | **OK co do kierunku** | zostają; dopisać źródła (sekcja 2) i zamienić punktowe "effect" na widełki |

Działanie: SCIENTIFIC_FOUNDATION.md dostaje status "v1 — do rewizji wg NEURO_PLAN
sekcja 4"; nowe wpisy wyłącznie przez Evidence Registry.

## 5. Anty-wzorce
- Zakaz liczbowych "scoringów atrakcyjności" twarzy użytkownika (ryzyko dysmorficzne;
  brak walidowanej skali) — tylko obserwacje stanu (LC-9) i trend zadbania.
- Zakaz obiecywania efektów liczbowych bez źródła (patrz audyt).
- Przy sygnałach dysmorfofobii (kompulsywne skanowanie, pogarszający się afekt
  przy użyciu modułu) → sygnał do Mentalności, sugestia konsultacji.

## 6. Integracje
- Publikuje: adherencja protokołów, obserwacje stanu (skóra/retencja), cele
  estetyczne → ForgeBody/Dieta.
- Subskrybuje: sen/stres (Affect), trening (ForgeBody), dieta (sód/białko).

## 7. Fazy
1. Sekcja 4 (audyt) + LC-1 (Evidence v2) — fundament uczciwości.
2. LC-2, LC-3, LC-7, LC-8.
3. LC-4, LC-5, LC-6, LC-9.

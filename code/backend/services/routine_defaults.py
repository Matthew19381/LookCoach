"""Default skincare routine offered until the user builds their own
(owner request 2026-10-15). Kept small on purpose: only steps with the best
evidence available are active; the rest are optional, switched off, with the
limits of their study stated. Sources checked 2026-10-15/17."""

EVIDENCE = {
    "spf": {
        "level": "RCT",
        "ref": "Hughes 2013, Ann Intern Med: n=903 dorosłych <55 lat, 4,5 roku; codzienny krem z filtrem "
               "szerokiego spektrum vs używanie według uznania: o 24% mniej oznak fotostarzenia "
               "(względna szansa 0,76; 95% CI 0,59–0,98).",
        "url": "https://pubmed.ncbi.nlm.nih.gov/23732711/",
    },
    "cleansing": {
        "level": "expert",
        "ref": "Opinia ekspertów (dermatologia), bez badania z randomizacją.",
        "url": "",
    },
    "moisturizer": {
        "level": "RCT (mała próba)",
        "ref": "Buraczewska i in. 2008, Arch Dermatol Res: n=20 zdrowych osób, 7 tygodni, podwójnie ślepa "
               "próba. Krem z 20% lipidów i 5% mocznika wzmocnił barierę skóry, a krem węglowodorowy "
               "(40% lipidów) ją osłabił. Efekt zależy od składu kremu.",
        "url": "https://doi.org/10.1007/s00403-008-0906-6",
    },
    "retinol": {
        "level": "RCT (mała próba)",
        "ref": "Kafi 2007, Arch Dermatol: 0,4% retinol do 3 razy w tygodniu przez 24 tygodnie na ramieniu "
               "osób w wieku średnio 87 lat (36 osób, 23 ukończyły); mniej drobnych zmarszczek. "
               "Nie badano twarzy młodych osób. Nie w ciąży.",
        "url": "https://pubmed.ncbi.nlm.nih.gov/17515510/",
    },
    "niacinamide": {
        "level": "RCT (mała próba)",
        "ref": "Bissett 2005, Dermatol Surg: 5% niacynamid 2 razy dziennie przez 12 tygodni, połowa twarzy "
               "vs podłoże, 50 kobiet w wieku 40–60 lat; poprawa przebarwień, drobnych zmarszczek "
               "i zażółcenia. Nie badano mężczyzn ani młodszych osób.",
        "url": "https://pubmed.ncbi.nlm.nih.gov/16029679/",
    },
}

EVERY_DAY = "0123456"

# In order of use within each slot.
# slot, name, evidence key, essential (kept in survival mode), active, weekdays, note
DEFAULT_STEPS = [
    ("morning", "Umyj twarz", "cleansing", False, True, EVERY_DAY, "Letnia woda albo łagodny żel, bez szorowania."),
    ("morning", "Serum z niacynamidem 5%", "niacinamide", False, False, EVERY_DAY,
     "Opcjonalne. Dowody tylko u kobiet 40–60 lat."),
    ("morning", "Krem z filtrem SPF 30+", "spf", True, True, EVERY_DAY,
     "Szerokie spektrum (UVA i UVB). Na twarz i szyję, także w pochmurne dni."),
    ("evening", "Umyj twarz łagodnym żelem", "cleansing", True, True, EVERY_DAY, "Letnia woda, bez szorowania."),
    ("evening", "Krem nawilżający", "moisturizer", False, True, EVERY_DAY,
     "Gdy skóra jest sucha lub ściągnięta. W badaniu krem z 5% mocznikiem wzmocnił barierę skóry, a krem na bazie węglowodorów (parafiny) ją osłabił."),
    ("evening", "Retinol 0,25–0,5%", "retinol", False, False, "024",
     "Opcjonalne. Ustawione na pn, śr, pt (w badaniu do 3 razy w tygodniu); może podrażniać."),
]

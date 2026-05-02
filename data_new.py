import random

# ═══════════════════════════════════════════════════════════════════════════════
# MEZŐNYJÁTÉKOSOK TULAJDONSÁGAI (36 db)
# ═══════════════════════════════════════════════════════════════════════════════

OUTFIELD_SKILLS = [
    # TECHNICAL (14 db)
    "szogletek", "beadas", "cselez", "befejezes", "elso_erintest",
    "szabadrugas", "fejes", "tavoli_loves", "tavoldobas", "emberfogast",
    "passz", "buntetoezes", "szereles", "technika",
    
    # MENTAL (14 db)
    "agresszio", "antipacio", "batorsag", "hidegver", "koncentracio",
    "donteshozatal", "elszantsag", "lelekmenyesseg", "vezetoi", "labda_nelkul",
    "pozicionalas", "csapatjatek", "latas", "munkabirasag",
    
    # PHYSICAL (8 db)
    "gyorsulas", "mozgekonyság", "egyensuly", "fejesero",
    "termeszetes_allapot", "gyorsasag", "allokepeség", "ero"
]

OUTFIELD_LABELS = {
    # TECHNICAL
    "szogletek": "Szögletek",
    "beadas": "Beadás",
    "cselez": "Cselezés",
    "befejezes": "Befejezés",
    "elso_erintest": "Első érintés",
    "szabadrugas": "Szabadrúgás",
    "fejes": "Fejes",
    "tavoli_loves": "Távoli lövés",
    "tavoldobas": "Távoldobás",
    "emberfogast": "Emberfogás",
    "passz": "Passz",
    "buntetoezes": "Büntető",
    "szereles": "Szerelés",
    "technika": "Technika",
    
    # MENTAL
    "agresszio": "Agresszió",
    "antipacio": "Helyzetfelismerés",
    "batorsag": "Bátorság",
    "hidegver": "Hidegvér",
    "koncentracio": "Koncentráció",
    "donteshozatal": "Döntéshozatal",
    "elszantsag": "Elszántság",
    "lelekmenyesseg": "Leleményesség",
    "vezetoi": "Vezetői képesség",
    "labda_nelkul": "Labda nélkül",
    "pozicionalas": "Pozícionálás",
    "csapatjatek": "Csapatjáték",
    "latas": "Látás",
    "munkabirasag": "Munkabírás",
    
    # PHYSICAL
    "gyorsulas": "Gyorsulás",
    "mozgekonyság": "Mozgékonyság",
    "egyensuly": "Egyensúly",
    "fejesero": "Ugrásmagasság",
    "termeszetes_allapot": "Természetes erő",
    "gyorsasag": "Gyorsaság",
    "allokepeség": "Állóképesség",
    "ero": "Erő"
}

OUTFIELD_SHORT = {
    # TECHNICAL
    "szogletek": "Szögl.",
    "beadas": "Beadás",
    "cselez": "Cselez",
    "befejezes": "Befejez",
    "elso_erintest": "1.érint",
    "szabadrugas": "Szabadr",
    "fejes": "Fejes",
    "tavoli_loves": "Távlöv",
    "tavoldobas": "Távdob",
    "emberfogast": "Emberfog",
    "passz": "Passz",
    "buntetoezes": "Büntet",
    "szereles": "Szerel",
    "technika": "Technik",
    
    # MENTAL
    "agresszio": "Agressz",
    "antipacio": "Antip.",
    "batorsag": "Bátor",
    "hidegver": "Hidegv",
    "koncentracio": "Koncen",
    "donteshozatal": "Döntés",
    "elszantsag": "Elszánt",
    "lelekmenyesseg": "Lelém.",
    "vezetoi": "Vezet",
    "labda_nelkul": "Lbd.nélk",
    "pozicionalas": "Pozíc.",
    "csapatjatek": "Csapat",
    "latas": "Látás",
    "munkabirasag": "Munkab",
    
    # PHYSICAL
    "gyorsulas": "Gyors.",
    "mozgekonyság": "Mozg.",
    "egyensuly": "Egyen.",
    "fejesero": "Fejese",
    "termeszetes_allapot": "Term.áll",
    "gyorsasag": "Gyorsas",
    "allokepeség": "Állók.",
    "ero": "Erő"
}

# ═══════════════════════════════════════════════════════════════════════════════
# KAPUSOK TULAJDONSÁGAI (36 db)
# ═══════════════════════════════════════════════════════════════════════════════

GK_SKILLS = [
    # GOALKEEPING (13 db)
    "magassag_eres", "terulet_uralma", "kommunikacio", "furcsasag",
    "gk_elso_erintest", "kezes", "rugas", "egy_az_egy_ellen",
    "gk_passz", "oklozes", "reflexek", "kirohanasok", "dobes",
    
    # MENTAL (14 db) - ugyanaz, mint mezőnyjátékosoknál
    "agresszio", "antipacio", "batorsag", "hidegver", "koncentracio",
    "donteshozatal", "elszantsag", "lelekmenyesseg", "vezetoi", "labda_nelkul",
    "pozicionalas", "csapatjatek", "latas", "munkabirasag",
    
    # PHYSICAL (8 db) - ugyanaz, mint mezőnyjátékosoknál
    "gyorsulas", "mozgekonyság", "egyensuly", "fejesero",
    "termeszetes_allapot", "gyorsasag", "allokepeség", "ero",
    
    # TECHNICAL (3 db)
    "gk_szabadrugas", "gk_buntetoezes", "gk_technika"
]

GK_LABELS = {
    # GOALKEEPING
    "magassag_eres": "Vetődés",
    "terulet_uralma": "Terület uralma",
    "kommunikacio": "Kommunikáció",
    "furcsasag": "Kiszámíthatatlanság",
    "gk_elso_erintest": "Első érintés",
    "kezes": "Labdafogás",
    "rugas": "Kirúgás",
    "egy_az_egy_ellen": "Egy az egy ellen",
    "gk_passz": "Passz",
    "oklozes": "Öklözés",
    "reflexek": "Reflexek",
    "kirohanasok": "Kirohanások",
    "dobes": "Dobás",
    
    # MENTAL (azonos a mezőnyjátékosokkal)
    "agresszio": "Agresszió",
    "antipacio": "Helyzetfelismerés",
    "batorsag": "Bátorság",
    "hidegver": "Hidegvér",
    "koncentracio": "Koncentráció",
    "donteshozatal": "Döntéshozatal",
    "elszantsag": "Elszántság",
    "lelekmenyesseg": "Leleményesség",
    "vezetoi": "Vezetői képesség",
    "labda_nelkul": "Labda nélkül",
    "pozicionalas": "Pozícionálás",
    "csapatjatek": "Csapatjáték",
    "latas": "Látás",
    "munkabirasag": "Munkabírás",
    
    # PHYSICAL (azonos a mezőnyjátékosokkal)
    "gyorsulas": "Gyorsulás",
    "mozgekonyság": "Mozgékonyság",
    "egyensuly": "Egyensúly",
    "fejesero": "Ugrásmagasság",
    "termeszetes_allapot": "Természetes erő",
    "gyorsasag": "Gyorsaság",
    "allokepeség": "Állóképesség",
    "ero": "Erő",
    
    # TECHNICAL
    "gk_szabadrugas": "Szabadrúgás",
    "gk_buntetoezes": "Büntetőezés",
    "gk_technika": "Technika"
}

GK_SHORT = {
    # GOALKEEPING
    "magassag_eres": "Mag.ér",
    "terulet_uralma": "Ter.ur",
    "kommunikacio": "Komm.",
    "furcsasag": "Furcs.",
    "gk_elso_erintest": "1.érint",
    "kezes": "Kezezés",
    "rugas": "Rúgás",
    "egy_az_egy_ellen": "1v1",
    "gk_passz": "Passz",
    "oklozes": "Öklöz",
    "reflexek": "Reflex",
    "kirohanasok": "Kirohan",
    "dobes": "Dobás",
    
    # MENTAL
    "agresszio": "Agressz",
    "antipacio": "Antip.",
    "batorsag": "Bátor",
    "hidegver": "Hidegv",
    "koncentracio": "Koncen",
    "donteshozatal": "Döntés",
    "elszantsag": "Elszánt",
    "lelekmenyesseg": "Lelém.",
    "vezetoi": "Vezet",
    "labda_nelkul": "Lbd.nélk",
    "pozicionalas": "Pozíc.",
    "csapatjatek": "Csapat",
    "latas": "Látás",
    "munkabirasag": "Munkab",
    
    # PHYSICAL
    "gyorsulas": "Gyors.",
    "mozgekonyság": "Mozg.",
    "egyensuly": "Egyen.",
    "fejesero": "Fejese",
    "termeszetes_allapot": "Term.áll",
    "gyorsasag": "Gyorsas",
    "allokepeség": "Állók.",
    "ero": "Erő",
    
    # TECHNICAL
    "gk_szabadrugas": "Szabadr",
    "gk_buntetoezes": "Büntet",
    "gk_technika": "Technik"
}

# ═══════════════════════════════════════════════════════════════════════════════
# POZÍCIÓK ÉS CSOPORTOK
# ═══════════════════════════════════════════════════════════════════════════════

POSITIONS = [
    "Kapus",
    "Szélső védő",
    "Középső védő",
    "Védekező középpályás",
    "Szélső középpályás",
    "Középső középpályás",
    "Támadó középpályás",
    "Csatár"
]

# Pozíciók főcsoportok szerint
POSITION_GROUPS = {
    "Kapusok": ["Kapus"],
    "Védők": ["Szélső védő", "Középső védő"],
    "Védekező középpályások": ["Védekező középpályás"],
    "Középpályások": ["Szélső középpályás", "Középső középpályás"],
    "Támadó középpályások": ["Támadó középpályás"],
    "Csatárok": ["Csatár"]
}

# TODO: Ez később kerül megadásra a felhasználó által
# Egyelőre placeholder értékek
POSITION_SKILLS = {
    "Kapus": {
        "primary": [
            "magassag_eres","kommunikacio","gk_elso_erintest","kezes",
            "egy_az_egy_ellen","reflexek","kirohanasok",
            "antipacio","hidegver","koncentracio","pozicionalas","latas",
            "gyorsasag","mozgekonyság"
        ],
        "secondary": [
            "terulet_uralma","rugas","gk_passz","dobes",
            "donteshozatal",
            "fejesero",
            "gk_szabadrugas","gk_buntetoezes"
        ]
    },
    "Szélső védő": {
        "primary": [
            "elso_erintest","fejes","emberfogast","szereles",
            "agresszio","antipacio","hidegver","donteshozatal","labda_nelkul","pozicionalas","munkabirasag",
            "gyorsulas","fejesero","gyorsasag","allokepeség"
        ],
        "secondary": [
            "beadas","cselez","tavoldobas","technika","passz",
            "koncentracio","elszantsag","lelekmenyesseg","csapatjatek"
        ]
    },
    "Középső védő": {
        "primary": [
            "elso_erintest","fejes","emberfogast","szereles",
            "agresszio","antipacio","hidegver","donteshozatal","labda_nelkul","pozicionalas","munkabirasag",
            "gyorsulas","fejesero","gyorsasag","allokepeség"
        ],
        "secondary": [
            "technika","passz",
            "koncentracio","elszantsag","lelekmenyesseg","csapatjatek"
        ]
    },
    "Védekező középpályás": {
        "primary": [
            "elso_erintest","passz","emberfogast","szereles",
            "antipacio","hidegver","donteshozatal","labda_nelkul","pozicionalas","munkabirasag","csapatjatek",
            "gyorsulas","gyorsasag","allokepeség"
        ],
        "secondary": [
            "technika",
            "termeszetes_allapot","ero",
            "agresszio","koncentracio","elszantsag","lelekmenyesseg"
        ]
    },
    "Szélső középpályás": {
        "primary": [
            "szogletek","beadas","cselez","passz","technika",
            "antipacio","batorsag","donteshozatal","labda_nelkul","pozicionalas","latas",
            "gyorsulas","gyorsasag","mozgekonyság","allokepeség"
        ],
        "secondary": [
            "befejezes","elso_erintest","szabadrugas","tavoli_loves","tavoldobas",
            "hidegver","koncentracio","elszantsag","lelekmenyesseg","csapatjatek","munkabirasag",
            "termeszetes_allapot","ero"
        ]
    },
    "Középső középpályás": {
        "primary": [
            "cselez","elso_erintest","tavoli_loves","passz","technika",
            "antipacio","koncentracio","donteshozatal","elszantsag","lelekmenyesseg","csapatjatek","munkabirasag",
            "gyorsulas","gyorsasag","allokepeség"
        ],
        "secondary": [
            "emberfogast","szabadrugas","szereles",
            "batorsag","hidegver","vezetoi","labda_nelkul","pozicionalas",
            "mozgekonyság","fejesero","termeszetes_allapot","ero"
        ]
    },
    "Támadó középpályás": {
        "primary": [
            "elso_erintest","passz","technika","tavoli_loves",
            "antipacio","batorsag","donteshozatal","lelekmenyesseg","pozicionalas","munkabirasag",
            "gyorsulas","gyorsasag","allokepeség"
        ],
        "secondary": [
            "cselez","szabadrugas","fejes","befejezes","buntetoezes",
            "hidegver","koncentracio","elszantsag","vezetoi","labda_nelkul","csapatjatek",
            "termeszetes_allapot","ero"
        ]
    },
    "Csatár": {
        "primary": [
            "cselez","befejezes","elso_erintest","fejes","buntetoezes","technika",
            "antipacio","batorsag","lelekmenyesseg","labda_nelkul","pozicionalas",
            "gyorsulas","gyorsasag","allokepeség","termeszetes_allapot","ero"
        ],
        "secondary": [
            "szabadrugas","passz",
            "hidegver","koncentracio","donteshozatal","elszantsag","munkabirasag",
            "mozgekonyság","egyensuly","fejesero"
        ]
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# FORMÁCIÓK (változatlan)
# ═══════════════════════════════════════════════════════════════════════════════

FORMATIONS = [
    "3-4-3","3-5-2","3-4-1-2","3-1-4-2","3-5-1-1",
    "4-4-2","4-3-3","4-3-3(sz.)","4-5-1","4-1-4-1","4-4-1-1",
    "4-3-1-2","4-1-3-2","4-1-3-1-1",
    "5-3-2","5-2-3","5-4-1",
]

FORMATION_GROUPS = {
    "3 védővel": ["3-4-3","3-5-2","3-4-1-2","3-1-4-2","3-5-1-1"],
    "4 védővel": ["4-4-2","4-3-3","4-3-3(sz.)","4-5-1","4-1-4-1","4-4-1-1","4-3-1-2","4-1-3-2","4-1-3-1-1"],
    "5 védővel": ["5-3-2","5-2-3","5-4-1"],
}

FORMATION_ROWS = {
    "3-4-3":      [("DEF",3,"def"),("MID",4,"mid"),("ATT",3,"att")],
    "3-5-2":      [("DEF",3,"def"),("MID",5,"mid"),("ATT",2,"att")],
    "3-5-1-1":    [("DEF",3,"def"),("MID",5,"mid"),("AM",1,"am"),("ATT",1,"att")],
    "4-4-2":      [("DEF",4,"def"),("MID",4,"mid"),("ATT",2,"att")],
    "4-3-3":      [("DEF",4,"def"),("MID",3,"mid"),("ATT",3,"att")],
    "4-3-3(sz.)": [("DEF",4,"def"),("MID",3,"mid"),("ATT",3,"att")],
    "4-5-1":      [("DEF",4,"def"),("MID",5,"mid"),("ATT",1,"att")],
    "5-3-2":      [("DEF",5,"def"),("MID",3,"mid"),("ATT",2,"att")],
    "5-2-3":      [("DEF",5,"def"),("MID",2,"mid"),("ATT",3,"att")],
    "5-4-1":      [("DEF",5,"def"),("MID",4,"mid"),("ATT",1,"att")],
    "3-1-4-2":    [("DEF",3,"def"),("DM",1,"dm"),("MID",4,"mid"),("ATT",2,"att")],
    "3-4-1-2":    [("DEF",3,"def"),("MID",4,"mid"),("AM",1,"am"),("ATT",2,"att")],
    "4-1-4-1":    [("DEF",4,"def"),("DM",1,"dm"),("MID",4,"mid"),("ATT",1,"att")],
    "4-4-1-1":    [("DEF",4,"def"),("MID",4,"mid"),("AM",1,"am"),("ATT",1,"att")],
    "4-3-1-2":    [("DEF",4,"def"),("MID",3,"mid"),("AM",1,"am"),("ATT",2,"att")],
    "4-1-3-2":    [("DEF",4,"def"),("DM",1,"dm"),("MID",3,"mid"),("ATT",2,"att")],
    "4-1-3-1-1":  [("DEF",4,"def"),("DM",1,"dm"),("MID",3,"mid"),("AM",1,"am"),("ATT",1,"att")],
}

ROW_POSITIONS = {
    "def": ["Középső védő","Szélső védő"],
    "dm":  ["Védekező középpályás"],
    "mid": ["Középső középpályás","Szélső középpályás"],
    "am":  ["Támadó középpályás"],
    "att": ["Csatár"],
}

AI_FORMATIONS = [
    "4-4-2","4-3-3","3-5-2","4-5-1","5-3-2","3-4-3","4-1-4-1","3-1-4-2","4-4-1-1"
]

# ═══════════════════════════════════════════════════════════════════════════════
# JÁTÉKOS NEVEK (változatlan)
# ═══════════════════════════════════════════════════════════════════════════════

MAGYAR_VEZETEK = [
    "Nagy","Kovács","Tóth","Szabó","Horváth","Varga","Kiss","Molnár","Németh","Farkas",
    "Balogh","Papp","Takács","Juhász","Lukács","Fekete","Fehér","Simon","Rácz","Szőke",
    "Bogdán","Orbán","Magyar","Gál","Mészáros","Pintér","Győri","Halász","Soós","Hegyi",
    "Bíró","Oláh","Kocsis","Balázs","Fodor","Fülöp","Szilárd","Berki","Bartók","Gönczi",
    "Huszár","Illés","Kardos","Máté","Nemes","Orsós","Pataki","Radics","Sárközi","Tamás",
    "Virág","Vásárhelyi","Antal","Ács","Barta","Csizmadia","Dózsa","Erdős","Faragó","Gerencsér"
]

MAGYAR_KERESZT = [
    "Ádám","Péter","Zoltán","Gábor","László","Dávid","Márton","Bence","Attila","Balázs",
    "Csaba","Dénes","Endre","Ferenc","György","Henrik","Imre","János","Kálmán","Levente",
    "Máté","Norbert","Olivér","Patrik","Richárd","Sándor","Tamás","Tibor","Viktor","Zsolt",
    "Áron","Benedek","Dominik","Ervin","Félix","Gergő","Hunor","István","Jakab","Kristóf",
    "Lóránt","Milán","Nándor","Oszkár","Pál","Roland","Szabolcs","Titusz","Vencel","Zalán"
]

CSAPAT_NEVEK = [
    "Ajka FC","Debrecen FC","Eger FC","Fehérvár FC","Győr Athletic FC",
    "Hajdúböszörmény FC","Jászberény FC","Kaposvár FC","Komárom Athletic FC",
    "Miskolc FC","Nagykanizsa FC","Nyíregyháza FC","Pécs FC","Szolnok FC",
    "Tatabánya FC","Veszprém FC","Zalaegerszeg FC","Székesfehérvár FC",
    "Pápa Athletic FC","Salgótarján FC","Szombathely FC","Dunaújváros FC",
    "Kecskemét FC","Gyöngyös Athletic FC"
]

_used_names = set()

def gen_name():
    for _ in range(300):
        n = f"{random.choice(MAGYAR_VEZETEK)} {random.choice(MAGYAR_KERESZT)}"
        if n not in _used_names:
            _used_names.add(n)
            return n
    return f"Játékos{random.randint(10000,99999)}"

# ═══════════════════════════════════════════════════════════════════════════════
# SKILL BUDGET RENDSZER
# ═══════════════════════════════════════════════════════════════════════════════

def gen_skills_for_budget(position, budget):
    """
    Skillpontok elosztása a pozíció szerint:
    - Min 3 minden skillnél
    - Max 20, max 2 db 20-as
    - Primary > secondary > tertiary átlagos értékek
    """
    is_gk = (position == "Kapus")
    skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
    n = len(skill_list)

    pos_data = POSITION_SKILLS.get(position, {})
    primary_set   = set(pos_data.get("primary", []))
    secondary_set = set(pos_data.get("secondary", []))

    # Minimum érték: budget arányában (legalább 3, de legfeljebb 6)
    min_val = max(3, min(6, budget // (n * 3)))
    skills = {s: min_val for s in skill_list}
    used = min_val * n
    remaining = max(0, budget - used)

    # Súlyok: primary=3.5, secondary=2.0, tertiary=0.8
    weights = {}
    for s in skill_list:
        if s in primary_set:      weights[s] = 3.5
        elif s in secondary_set:  weights[s] = 2.0
        else:                     weights[s] = 0.8

    total_w = sum(weights.values())
    # Elosztás zajjal
    raw = {}
    for s in skill_list:
        share = (weights[s] / total_w) * remaining
        noise = random.uniform(-share * 0.3, share * 0.3)
        raw[s] = max(0.0, share + noise)

    # Normalizálás
    raw_sum = sum(raw.values())
    if raw_sum > 0:
        scale = remaining / raw_sum
        for s in skill_list:
            raw[s] = raw[s] * scale

    # Hozzáadás, cap 19 (20-at külön kezeljük)
    for s in skill_list:
        add = int(raw[s])
        skills[s] = min(19, skills[s] + add)

    # Max 2 primary skill mehet 20-ra, valószínűsége budget-arányos
    peak_prob = min(0.95, max(0.0, (budget - 150) / 500.0))
    peak_candidates = sorted(primary_set & set(skill_list), key=lambda s: -weights[s])
    peak_count = 0
    for s in peak_candidates:
        if peak_count >= 2:
            break
        if random.random() < peak_prob:
            skills[s] = 20
            peak_count += 1

    # Biztosítás: minden 3-19 között (kivéve 20-asok)
    for s in skill_list:
        if skills[s] != 20:
            skills[s] = max(3, min(19, skills[s]))

    return skills


def gen_player(position=None, team_id=None, age=None):
    """Játékos generálása tehetség rendszerrel."""
    if position is None:
        position = random.choice(POSITIONS)
    if age is None:
        age = random.randint(15, 35)
    age = max(15, min(35, age))

    is_gk = (position == "Kapus")
    skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS

    # Tehetség: start és peak total meghatározása
    start_total = random.randint(150, 180)
    peak_total  = random.randint(600, 650)

    # Jelenlegi budget a korhoz arányosan
    if age <= 28:
        progress = (age - 15) / 13.0
        current_budget = int(start_total + (peak_total - start_total) * progress)
    else:
        # 28 után hanyatlás: 1/3 ütemmel az edzési tempónak
        from training import compute_pts_per_day, TRAINING_DAYS_PER_SEASON
        ppd = compute_pts_per_day(start_total, peak_total)
        decline_per_season = ppd * TRAINING_DAYS_PER_SEASON / 3.0
        years_past_peak = age - 28
        current_budget = max(start_total, int(peak_total - decline_per_season * years_past_peak))

    current_budget = max(start_total, current_budget)
    skills = gen_skills_for_budget(position, current_budget)

    # Tehetség értéke
    from training import compute_pts_per_day, get_talent_label
    ppd = compute_pts_per_day(start_total, peak_total)
    talent = get_talent_label(ppd)

    personal = random.choice(skill_list)

    return {
        "name": gen_name(),
        "position": position,
        "age": age,
        "is_gk": is_gk,
        "skills": skills,
        "skill_gains":  {s: 0 for s in skill_list},
        "skill_losses": {s: 0 for s in skill_list},
        "training_points": {s: 0.0 for s in skill_list},
        "personal_training": personal,
        "start_total": start_total,
        "peak_total": peak_total,
        "pts_per_day": ppd,
        "talent": talent,
    }


def score_player_for_slot(player, row_type):
    """Pontozza, mennyire illik a játékos egy formációs pozícióba (0-100)."""
    preferred_pos = ROW_POSITIONS.get(row_type, [])
    pos_match = 1.5 if player["position"] in preferred_pos else 1.0
    
    is_gk = player.get("is_gk", False)
    
    # Kulcs skilleket pozíciónként
    if is_gk or row_type == "gk":
        key_skills = ["reflexek", "kezes", "egy_az_egy_ellen"]
    else:
        key_skills_map = {
            "def": ["szereles", "allokepeség", "pozicionalas"],
            "dm":  ["szereles", "passz", "pozicionalas"],
            "mid": ["passz", "latas", "pozicionalas"],
            "am":  ["passz", "cselez", "befejezes"],
            "att": ["befejezes", "pozicionalas", "labda_nelkul"],
        }
        key_skills = key_skills_map.get(row_type, ["passz"])
    
    skill_val = sum(player["skills"].get(s, 0) for s in key_skills) / len(key_skills)
    return skill_val * pos_match

def auto_lineup(team):
    """Automatikus felállítás a legjobb játékosokkal."""
    form = team.get("formation", "4-4-2")
    rows = FORMATION_ROWS.get(form, FORMATION_ROWS["4-4-2"])
    players = [p for p in team["players"] if not p.get("retired", False)]
    
    slots = [("GK", "gk")]
    for (row_lbl, count, rtype) in rows:
        for i in range(count):
            slots.append((f"{row_lbl}{i+1}", rtype))
    
    used = set()
    lineup = {}
    
    # Kapus először
    gk_cands = sorted([p for p in players if p["position"] == "Kapus"],
                      key=lambda p: -p["skills"].get("reflexek", 0))
    if gk_cands:
        lineup["GK"] = gk_cands[0]["name"]
        used.add(gk_cands[0]["name"])
    elif players:
        lineup["GK"] = players[0]["name"]
        used.add(players[0]["name"])
    
    # Többi pozíció
    for slot_lbl, rtype in slots[1:]:
        avail = [p for p in players if p["name"] not in used]
        if not avail:
            break
        best = max(avail, key=lambda p: score_player_for_slot(p, rtype))
        lineup[slot_lbl] = best["name"]
        used.add(best["name"])
    
    return lineup

# ═══════════════════════════════════════════════════════════════════════════════
# CSAPAT SZÍNEK (változatlan)
# ═══════════════════════════════════════════════════════════════════════════════

AI_TEAM_COLORS = [
    ((220,30,30),(255,255,255),(255,180,0)),
    ((30,80,200),(200,200,200),(0,180,100)),
    ((180,30,180),(255,255,0),(80,200,80)),
    ((20,120,20),(255,100,0),(200,200,255)),
    ((0,180,180),(0,0,80),(255,120,120)),
    ((255,140,0),(80,0,80),(200,255,200)),
    ((100,0,0),(255,230,200),(0,120,200)),
    ((0,60,140),(255,220,0),(200,0,0)),
    ((40,40,40),(255,255,0),(0,200,220)),
    ((180,160,0),(0,40,120),(255,100,100)),
    ((200,80,0),(0,120,60),(220,220,255)),
    ((80,0,120),(255,200,80),(0,160,160)),
    ((0,100,80),(255,255,180),(180,0,60)),
    ((140,0,60),(220,220,220),(0,80,180)),
    ((60,60,180),(255,180,60),(60,160,60)),
    ((200,200,0),(60,0,60),(100,200,255)),
    ((0,140,200),(255,80,80),(200,255,100)),
    ((160,80,0),(200,240,255),(80,0,80)),
    ((0,80,0),(255,150,200),(200,160,0)),
    ((120,120,0),(0,80,160),(240,120,80)),
    ((200,0,100),(200,255,200),(60,60,120)),
    ((0,160,80),(255,60,60),(220,180,0)),
]

def colors_conflict(c1, c2, threshold=80):
    """Ellenőrzi, hogy két szín túl hasonló-e."""
    return sum(abs(a-b) for a, b in zip(c1, c2)) < threshold

def pick_away_color(home_c, away_home_c, away_away_c, away_third_c):
    """Kiválasztja azt a vendégmezét, ami nem ütközik a hazai csapat mezével."""
    for c in [away_away_c, away_third_c, away_home_c]:
        if not colors_conflict(home_c, c):
            return c
    return away_away_c

# 25 játékos fix összetétel: 2K+2VK+2TK+3SzV+3KV+3Sz+3KK+3Cs = 21 + 4 random
SQUAD_TEMPLATE = [
    ("Kapus", 2),
    ("Szélső védő", 3),
    ("Középső védő", 3),
    ("Védekező középpályás", 2),
    ("Szélső középpályás", 3),
    ("Középső középpályás", 3),
    ("Támadó középpályás", 2),
    ("Csatár", 3),
    # 4 random
]
SQUAD_TOTAL = 25
SQUAD_FIXED = sum(c for _, c in SQUAD_TEMPLATE)  # 21
SQUAD_RANDOM = SQUAD_TOTAL - SQUAD_FIXED  # 4

def gen_team(name, team_id, player_formation=None, kit_colors=None):
    formation = player_formation or random.choice(AI_FORMATIONS)
    if kit_colors is None:
        idx = team_id % len(AI_TEAM_COLORS)
        kit_colors = AI_TEAM_COLORS[idx]

    players = []
    # Fix összetétel - random korok 15-35 között
    for pos, count in SQUAD_TEMPLATE:
        for _ in range(count):
            age = random.randint(15, 35)
            players.append(gen_player(pos, team_id, age=age))
    # 4 random poszt
    for _ in range(SQUAD_RANDOM):
        pos = random.choice(POSITIONS)
        age = random.randint(15, 35)
        players.append(gen_player(pos, team_id, age=age))

    from training import DAYS
    return {
        "id": team_id,
        "name": name,
        "players": players,
        "formation": formation,
        "lineup": {},
        "set_piece_takers": {"corner":"","freekick":"","throwin":"","penalty":""},
        "wins": 0, "draws": 0, "losses": 0,
        "goals_for": 0, "goals_against": 0, "points": 0,
        "kit_home": list(kit_colors[0]),
        "kit_away": list(kit_colors[1]),
        "kit_third": list(kit_colors[2]),
    }


def generate_league(player_team_name, player_kit=None):
    _used_names.clear()
    random.shuffle(CSAPAT_NEVEK)
    names = CSAPAT_NEVEK[:19]
    teams = []
    for i, name in enumerate(names):
        teams.append(gen_team(name, i, kit_colors=AI_TEAM_COLORS[i % len(AI_TEAM_COLORS)]))
    
    player_colors = None
    if player_kit and len(player_kit) >= 3:
        player_colors = (tuple(player_kit[0]), tuple(player_kit[1]), tuple(player_kit[2]))
    elif player_kit and len(player_kit) == 1:
        player_colors = (tuple(player_kit[0]), (255, 255, 255), (255, 180, 0))
    
    player_team = gen_team(player_team_name, 19, "4-4-2", kit_colors=player_colors)
    player_team["formation"] = "4-4-2"
    teams.append(player_team)
    
    for t in teams:
        t["lineup"] = auto_lineup(t)
    
    return teams

def generate_schedule(teams):
    ids = [t["id"] for t in teams]
    n = len(ids)
    schedule = []
    all_rounds = []
    
    for round_num in range(2):
        tl = ids[:]
        if n % 2:
            tl.append(None)
        m = len(tl)
        for _ in range(m - 1):
            week = []
            for i in range(m // 2):
                h, a = tl[i], tl[m - 1 - i]
                if h is not None and a is not None:
                    week.append((h, a) if round_num == 0 else (a, h))
            all_rounds.append(week)
            tl = [tl[0]] + [tl[-1]] + tl[1:-1]
    
    random.shuffle(all_rounds)
    return all_rounds

def replace_retired_player(team, player_idx):
    """Nyugdíjas játékos cseréje új 15 éves játékossal."""
    old_p = team["players"][player_idx]
    new_p = gen_player(old_p.get("position", random.choice(POSITIONS)), team["id"], age=15)
    team["players"][player_idx] = new_p
    return new_p

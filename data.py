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
    "buntetoezes": "Büntetőezés",
    "szereles": "Szerelés",
    "technika": "Technika",
    
    # MENTAL
    "agresszio": "Agresszió",
    "antipacio": "Anticipáció",
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
    "fejesero": "Fejesero",
    "termeszetes_allapot": "Természetes állapot",
    "gyorsasag": "Gyorsaság",
    "allokepeség": "Állóképesség",
    "ero": "Ero"
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
    "ero": "Ero"
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
    "magassag_eres": "Magasság érés",
    "terulet_uralma": "Terület uralma",
    "kommunikacio": "Kommunikáció",
    "furcsasag": "Furcsaság",
    "gk_elso_erintest": "Első érintés",
    "kezes": "Kezezés",
    "rugas": "Rúgás",
    "egy_az_egy_ellen": "Egy az egy ellen",
    "gk_passz": "Passz",
    "oklozes": "Öklözés",
    "reflexek": "Reflexek",
    "kirohanasok": "Kirohanások",
    "dobes": "Dobás",
    
    # MENTAL (azonos a mezőnyjátékosokkal)
    "agresszio": "Agresszió",
    "antipacio": "Anticipáció",
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
    "fejesero": "Fejesero",
    "termeszetes_allapot": "Természetes állapot",
    "gyorsasag": "Gyorsaság",
    "allokepeség": "Állóképesség",
    "ero": "Ero",
    
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
    "ero": "Ero",
    
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
        "primary": ["reflexek", "kezes", "egy_az_egy_ellen"],
        "secondary": ["rugas", "terulet_uralma", "pozicionalas"],
        "tertiary": ["kommunikacio", "hidegver"]
    },
    "Szélső védő": {
        "primary": ["szereles", "pozicionalas", "beadas"],
        "secondary": ["gyorsasag", "allokepeség", "passz"],
        "tertiary": ["emberfogast", "antipacio"]
    },
    "Középső védő": {
        "primary": ["szereles", "fejes", "pozicionalas"],
        "secondary": ["ero", "antipacio", "koncentracio"],
        "tertiary": ["passz", "batorsag"]
    },
    "Védekező középpályás": {
        "primary": ["szereles", "passz", "pozicionalas"],
        "secondary": ["allokepeség", "donteshozatal", "csapatjatek"],
        "tertiary": ["emberfogast", "munkabirasag"]
    },
    "Szélső középpályás": {
        "primary": ["beadas", "gyorsasag", "cselez"],
        "secondary": ["passz", "allokepeség", "technika"],
        "tertiary": ["tavoli_loves", "antipacio"]
    },
    "Középső középpályás": {
        "primary": ["passz", "latas", "pozicionalas"],
        "secondary": ["donteshozatal", "csapatjatek", "technika"],
        "tertiary": ["allokepeség", "hidegver"]
    },
    "Támadó középpályás": {
        "primary": ["passz", "cselez", "befejezes"],
        "secondary": ["latas", "donteshozatal", "technika"],
        "tertiary": ["tavoli_loves", "lelekmenyesseg"]
    },
    "Csatár": {
        "primary": ["befejezes", "pozicionalas", "labda_nelkul"],
        "secondary": ["fejes", "ero", "elso_erintest"],
        "tertiary": ["tavoli_loves", "technika"]
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

def skill_budget_for_age(age, is_gk=False):
    """
    Mezőnyjátékosok: 15 éves -> 150-180 pont, 28 éves -> 600-700 pont
    Kapusok: 15 éves -> 140-170 pont, 28 éves -> 580-680 pont
    """
    age = max(15, min(35, age))
    
    if is_gk:
        min_start, max_start = 140, 170
        min_peak, max_peak = 580, 680
    else:
        min_start, max_start = 150, 180
        min_peak, max_peak = 600, 700
    
    # Véletlenszerű célérték választása a tartományból
    start_budget = random.randint(min_start, max_start)
    peak_budget = random.randint(min_peak, max_peak)
    
    if age <= 28:
        # Lineáris növekedés 15-től 28-ig
        progress = (age - 15) / 13.0
        return int(start_budget + (peak_budget - start_budget) * progress)
    else:
        # Hanyatlás 28 után: 30%-ot veszít 35 éves koráig
        decline = int(peak_budget * 0.30 * (age - 28) / 7)
        return max(100, peak_budget - decline)

def gen_skills_for_pos_budget(position, budget):
    """Elosztja a skillpontokat a pozíció szerint."""
    is_gk = (position == "Kapus")
    skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
    skills = {s: 0 for s in skill_list}
    
    pos_data = POSITION_SKILLS.get(position)
    if pos_data is None:
        # Véletlenszerű elosztás
        remaining = budget
        sks = list(skill_list)
        random.shuffle(sks)
        for s in sks:
            if remaining <= 0:
                break
            add = random.randint(0, min(4, remaining))
            skills[s] = min(20, add)
            remaining -= add
        return skills
    
    primary = pos_data["primary"]
    secondary = pos_data["secondary"]
    tertiary = pos_data["tertiary"]
    remaining = budget
    
    # Elosztás: primary 50%, secondary 35%, tertiary 15%
    pri_budget = int(remaining * 0.50)
    sec_budget = int(remaining * 0.35)
    ter_budget = remaining - pri_budget - sec_budget
    
    def distribute(skill_list_subset, b):
        nonlocal remaining
        if not skill_list_subset or b <= 0:
            return
        per = b // len(skill_list_subset)
        extra = b - per * len(skill_list_subset)
        for i, s in enumerate(skill_list_subset):
            pts = per + (1 if i < extra else 0) + random.randint(-1, 1)
            pts = max(0, min(20, pts, remaining))
            skills[s] = min(20, skills[s] + pts)
            remaining -= pts
    
    distribute(primary, pri_budget)
    distribute(secondary, sec_budget)
    if tertiary:
        distribute(tertiary, ter_budget)
    
    # Maradék elosztása
    if remaining > 0:
        sks = list(skill_list)
        random.shuffle(sks)
        for s in sks:
            if remaining <= 0:
                break
            add = random.randint(0, min(2, remaining))
            skills[s] = min(20, skills[s] + add)
            remaining -= add
    
    return skills

def gen_player(position=None, team_id=None, age=None):
    if position is None:
        position = random.choice(POSITIONS)
    if age is None:
        age = random.randint(15, 35)
    
    is_gk = (position == "Kapus")
    budget = skill_budget_for_age(age, is_gk)
    skills = gen_skills_for_pos_budget(position, budget)
    
    skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
    personal = random.choice(skill_list)
    
    return {
        "name": gen_name(),
        "position": position,
        "age": age,
        "skills": skills,
        "skill_gains": {s: 0 for s in skill_list},
        "training_points": {s: 0.0 for s in skill_list},
        "personal_training": personal,
        "team_id": team_id,
        "retired": False,
        "is_gk": is_gk
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

def gen_team(name, team_id, player_formation=None, kit_colors=None):
    formation = player_formation or random.choice(AI_FORMATIONS)
    if kit_colors is None:
        idx = team_id % len(AI_TEAM_COLORS)
        kit_colors = AI_TEAM_COLORS[idx]
    
    players = []
    lineup_spec = [
        ("Kapus", 2),
        ("Szélső védő", 3),
        ("Középső védő", 3),
        ("Védekező középpályás", 1),
        ("Szélső középpályás", 3),
        ("Középső középpályás", 3),
        ("Támadó középpályás", 1),
        ("Csatár", 3)
    ]
    
    for pos, count in lineup_spec:
        for _ in range(count):
            players.append(gen_player(pos, team_id))
    players.append(gen_player(None, team_id))  # 1 random
    
    from training import DAYS
    ai_schedule = {}
    skill_list = OUTFIELD_SKILLS  # AI csapatok többsége mezőnyjátékos
    for day in DAYS:
        if day == "Szombat":
            ai_schedule[day] = None
        else:
            ai_schedule[day] = random.choice(skill_list)
    
    return {
        "id": team_id,
        "name": name,
        "players": players,
        "formation": formation,
        "lineup": {},
        "set_piece_takers": {"corner": "", "freekick": "", "throwin": "", "penalty": ""},
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "points": 0,
        "ai_schedule": ai_schedule,
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
    old = team["players"][player_idx]
    new_p = gen_player(old["position"], team["id"], age=15)
    team["players"][player_idx] = new_p
    return new_p

from data_new import OUTFIELD_SKILLS, OUTFIELD_LABELS, GK_SKILLS, GK_LABELS

DAYS = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]

# Edzésre kiválasztható skilleket a játékos típusa szerint határozzuk meg
def get_trainable_skills(is_gk):
    """Visszaadja az edzésre kiválasztható skilleket a játékos típusa szerint."""
    return GK_SKILLS if is_gk else OUTFIELD_SKILLS

def get_trainable_labels(is_gk):
    """Visszaadja az edzésre kiválasztható skillek címkéit a játékos típusa szerint."""
    return GK_LABELS if is_gk else OUTFIELD_LABELS

# ═══════════════════════════════════════════════════════════════════════════════
# EDZÉS MATEMATIKA
# ═══════════════════════════════════════════════════════════════════════════════

# Mezőnyjátékosok: 15 éves -> 150-180 pont, 28 éves -> 600-700 pont
# Átlagosan: 165 pont -> 650 pont = 485 pont növekedés
# 13 szezon (15->28) × 38 hét × 6 edzésnap = 2964 edzésnap
# Napi 1 edzés = 485 / 2964 ≈ 0.1636 pont/edzés

# Kapusok: 15 éves -> 140-170 pont, 28 éves -> 580-680 pont
# Átlagosan: 155 pont -> 630 pont = 475 pont növekedés
# 475 / 2964 ≈ 0.1603 pont/edzés

BASE_PTS_PER_SESSION_OUTFIELD = 485.0 / 2964.0  # ≈ 0.1636
BASE_PTS_PER_SESSION_GK = 475.0 / 2964.0        # ≈ 0.1603

def get_training_multiplier(age):
    """Növekedési szorzó. Csúcs 28 évesen, utána csökken. 20 alatt gyorsabb tanulás."""
    if age <= 20:
        return 1.2
    if age <= 28:
        return 1.0
    if age <= 32:
        return 0.5  # Még tud fejlődni, de lassabban
    return 0.2

def default_week_schedule(is_gk=False):
    """Alapértelmezett heti edzésterv."""
    sched = {}
    default_skill = "reflexek" if is_gk else "passz"
    for day in DAYS:
        sched[day] = None if day == "Szombat" else default_skill
    return sched

def apply_training_day(players, day_index):
    """Egy edzésnap alkalmazása. Minden játékos a saját személyes edzését csinálja."""
    day_name = DAYS[day_index % 7]
    if day_name == "Szombat":
        return
    
    for p in players:
        age = p.get("age", 17)
        is_gk = p.get("is_gk", False)
        mult = get_training_multiplier(age)
        
        personal_sk = p.get("personal_training", "passz")
        skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
        
        if personal_sk not in skill_list:
            personal_sk = "reflexek" if is_gk else "passz"
        
        # Alappontok per edzés
        base_pts = BASE_PTS_PER_SESSION_GK if is_gk else BASE_PTS_PER_SESSION_OUTFIELD
        per_session = base_pts * mult
        
        p["training_points"][personal_sk] = p["training_points"].get(personal_sk, 0) + per_session
        
        # Szintlépés ellenőrzése
        _check_level_ups(p, is_gk)

def _check_level_ups(p, is_gk):
    """Ellenőrzi, hogy valamelyik skill elérte-e a szintlépéshez szükséges pontot."""
    skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
    
    for sk in skill_list:
        pts = p["training_points"].get(sk, 0)
        while pts >= 1.0:
            cur = p["skills"].get(sk, 0)
            if cur < 20:
                p["skills"][sk] = cur + 1
                p["skill_gains"][sk] = p["skill_gains"].get(sk, 0) + 1
            pts -= 1.0
        p["training_points"][sk] = max(0.0, pts)

def age_up_season(teams, player_team_id):
    """Szezon végén: minden játékos öregszik, hanyatlás/nyugdíjazás kezelése."""
    from data_new import replace_retired_player, OUTFIELD_SKILLS, GK_SKILLS
    
    for team in teams:
        for i, p in enumerate(team["players"]):
            p["age"] = p.get("age", 17) + 1
            is_gk = p.get("is_gk", False)
            skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
            p["skill_gains"] = {s: 0 for s in skill_list}
            
            age = p["age"]
            # Hanyatlás 28 után
            if age > 28:
                # 30%-ot veszít 7 év alatt = ~4.3% évente
                for sk in skill_list:
                    cur = p["skills"].get(sk, 0)
                    if cur > 0:
                        lose = max(0, round(cur * (0.30 / 7), 2))
                        p["skills"][sk] = max(0, cur - int(lose + 0.5))
            
            # Nyugdíjazás 35 évesen
            if age >= 35:
                p["retired"] = True
                new_p = replace_retired_player(team, i)
                team["players"][i] = new_p
        
        # Újra automatikus felállítás
        from data_new import auto_lineup
        team["lineup"] = auto_lineup(team)

def apply_ai_training(teams, day_index, player_team_id):
    """AI csapatok edzése a megadott napon."""
    day_name = DAYS[day_index % 7]
    if day_name == "Szombat":
        return
    
    for team in teams:
        if team["id"] == player_team_id:
            continue
        apply_training_day(team["players"], day_index)

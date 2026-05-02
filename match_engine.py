"""
match_engine.py – Valódi fizikai meccsmotor
"""
import random, math

PITCH_W = 90.0
PITCH_H = 45.0
GOAL_WIDTH = 7.32
GOAL_Y_MIN = (PITCH_H - GOAL_WIDTH) / 2
GOAL_Y_MAX = (PITCH_H + GOAL_WIDTH) / 2
BOX_DEPTH = 16.5
BOX_Y_MIN = (PITCH_H - 40.32) / 2
BOX_Y_MAX = (PITCH_H + 40.32) / 2
HALFTIME = 45 * 60
FULLTIME  = 90 * 60

def sk(player, key, default=10):
    return player.get("skills", {}).get(key, default)

def physical_state(player, elapsed_sec):
    """
    Fizikai állapot 0..300 valós másodperc alapján.
    Meccs elején 1.0, meccs végén min_state.
    """
    MATCH_SECS = 300.0
    is_gk = player.get("position", "") == "Kapus"
    allokep = sk(player, "allokepeség", 10)
    if is_gk:
        min_state = 0.80 + (allokep / 20.0) * 0.15
    else:
        min_state = 0.55 + (allokep / 20.0) * 0.30
    sub_entry = player.get("sub_entry_sec", 0)
    if sub_entry > 0:
        t = min(1.0, (elapsed_sec - sub_entry) / max(1, MATCH_SECS - sub_entry))
    else:
        t = min(1.0, elapsed_sec / MATCH_SECS)
    return max(min_state, 1.0 - (1.0 - min_state) * t)

def effective_speed(player, elapsed_sec):
    base = sk(player, "gyorsasag", 10) / 20.0 * 10.0 + 3.0
    return base * physical_state(player, elapsed_sec)

def shot_power(player):
    bef = sk(player, "befejezes", 10)
    tav = sk(player, "tavoli_loves", 10)
    ero = sk(player, "ero", 10)
    speed = 10.0 + (bef - 10) * 0.5 + (tav - 10) * 0.3 + (ero - 10) * 0.2
    return max(0.0, min(20.0, speed))

def pass_range(player):
    passz = sk(player, "passz", 10)
    ero   = sk(player, "ero", 10)
    return 5.0 + passz / 20.0 * 30.0 + ero / 20.0 * 5.0

def cross_range(player):
    bead = sk(player, "beadas", 10)
    ero  = sk(player, "ero", 10)
    return 5.0 + bead / 20.0 * 45.0 + ero / 20.0 * 5.0

def direction_accuracy(player):
    tech = sk(player, "technika", 10)
    if tech >= 13:
        return random.uniform(0.95, 1.00)
    elif tech >= 6:
        return random.uniform(0.75, 0.95)
    else:
        return random.uniform(0.50, 0.74)

def apply_inaccuracy(tx, ty, px, py, accuracy):
    angle = math.atan2(ty - py, tx - px)
    max_dev = (1.0 - accuracy) * math.pi / 4
    dev = random.uniform(-max_dev, max_dev)
    dist = math.sqrt((tx - px)**2 + (ty - py)**2)
    new_angle = angle + dev
    return px + dist * math.cos(new_angle), py + dist * math.sin(new_angle)

def keeper_saves(keeper, power):
    kezes = sk(keeper, "kezes", 10)
    reflexek = sk(keeper, "reflexek", 10)
    # Alap mentési arány: ~80% (csak 1/5 lövés gól)
    # Cél: on-target lövések ~60-70%-át menti a kapus
    # Gól/lövés összesített: ~10-12% (on-target ~40%, mentés ~70%)
    # Cél: ~2-3 gól/meccs 15-20 lövés mellett → ~12-15% gól/lövés
    # on_target ~30%, mentési arány ~55% → gól/on_target ~45%
    save_prob = 0.44 + (kezes + reflexek) / 40.0 * 0.20  # 0.44-0.64
    save_prob -= power / 20.0 * 0.28
    save_prob = max(0.30, min(0.85, save_prob))
    import random as _r
    return _r.random() < save_prob

def first_touch_success(player):
    elso = sk(player, "elso_erintest", 10)
    return random.random() < (0.40 + elso / 20.0 * 0.60)

def tackle_probability(attacker, defender, elapsed_sec):
    att_avg = (sk(attacker, "gyorsasag") + sk(attacker, "mozgekonyság") + sk(attacker, "cselez")) / 3.0
    def_avg = (sk(defender, "gyorsasag") + sk(defender, "mozgekonyság") + sk(defender, "szereles")) / 3.0
    att_avg *= physical_state(attacker, elapsed_sec)
    def_avg *= physical_state(defender, elapsed_sec)
    diff = def_avg - att_avg
    if abs(diff) <= 2.0: prob = 0.50
    elif diff > 2.0: prob = 0.90
    else: prob = 0.10
    return random.random() < prob

def is_foul(): return random.random() < 0.10
def is_yellow(): return random.random() < 0.09
def is_red(): return random.random() < 0.05

def is_offside(att_x, ball_x, def_xs, attacking_right):
    if attacking_right:
        if att_x <= PITCH_W / 2 or att_x <= ball_x: return False
        srt = sorted(def_xs, reverse=True)
        return len(srt) >= 2 and att_x > srt[1]
    else:
        if att_x >= PITCH_W / 2 or att_x >= ball_x: return False
        srt = sorted(def_xs)
        return len(srt) >= 2 and att_x < srt[1]

def simulate_match(home_team, away_team):
    """Ligaeredmény-szimulálás (nem animált)."""
    def team_strength(team):
        players = team.get("players", [])[:11]
        if not players: return 10.0
        total = sum(sum(p.get("skills", {}).values()) / max(1, len(p.get("skills", {}))) for p in players)
        return total / len(players)
    hs = team_strength(home_team)
    as_ = team_strength(away_team)
    h_prob = (hs * 1.1) / max(1, hs * 1.1 + as_)
    avg_goals = 2.6
    hg = ag = 0
    for _ in range(8):
        if random.random() < avg_goals / 8:
            if random.random() < h_prob: hg += 1
            else: ag += 1
    events = []
    used = set()
    h_squad = home_team.get("players", [{"name": "?"}])[:11]
    a_squad = away_team.get("players", [{"name": "?"}])[:11]
    for _ in range(hg):
        m = random.randint(5, 89)
        while m in used: m = random.randint(5, 89)
        used.add(m)
        sc = random.choice(h_squad)
        events.append({"minute": m, "type": "goal", "team": "home", "player": sc.get("name", "?")})
    for _ in range(ag):
        m = random.randint(5, 89)
        while m in used: m = random.randint(5, 89)
        used.add(m)
        sc = random.choice(a_squad)
        events.append({"minute": m, "type": "goal", "team": "away", "player": sc.get("name", "?")})
    events.sort(key=lambda e: e["minute"])
    return hg, ag, events

def simulate_all_matches(teams, schedule, matchday):
    if matchday >= len(schedule): return []
    results = []
    team_map = {t["id"]: t for t in teams}
    for home_id, away_id in schedule[matchday]:
        home = team_map[home_id]
        away = team_map[away_id]
        hg, ag, evts = simulate_match(home, away)
        home["goals_for"] += hg; home["goals_against"] += ag
        away["goals_for"] += ag; away["goals_against"] += hg
        if hg > ag: home["wins"] += 1; home["points"] += 3; away["losses"] += 1
        elif hg < ag: away["wins"] += 1; away["points"] += 3; home["losses"] += 1
        else: home["draws"] += 1; away["draws"] += 1; home["points"] += 1; away["points"] += 1
        results.append({"home": home["name"], "away": away["name"],
                        "home_id": home_id, "away_id": away_id,
                        "home_goals": hg, "away_goals": ag, "events": evts})
    return results

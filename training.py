import random
from data_new import OUTFIELD_SKILLS, OUTFIELD_LABELS, GK_SKILLS, GK_LABELS

DAYS = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]

def get_trainable_skills(is_gk):
    return GK_SKILLS if is_gk else OUTFIELD_SKILLS

def get_trainable_labels(is_gk):
    return GK_LABELS if is_gk else OUTFIELD_LABELS

TRAINING_DAYS_PER_SEASON = 6 * 38
SEASONS_TO_PEAK = 13  # 15-tol 28-ig

TALENT_THRESHOLDS = [
    (0.149, "Tehetségtelen"),
    (0.154, "Kissé tehetségtelen"),
    (0.159, "Átlagos"),
    (0.165, "Tehetséges"),
    (999.0, "Szupertehetség"),
]

def get_talent_label(pts_per_day):
    for threshold, label in TALENT_THRESHOLDS:
        if pts_per_day < threshold:
            return label
    return "Szupertehetség"

def compute_pts_per_day(start_total, peak_total):
    total_days = TRAINING_DAYS_PER_SEASON * SEASONS_TO_PEAK
    return (peak_total - start_total) / total_days

def default_week_schedule(is_gk=False):
    sched = {}
    d = "reflexek" if is_gk else "passz"
    for day in DAYS:
        sched[day] = None if day == "Szombat" else d
    return sched

def _count_maxed(p):
    return sum(1 for v in p["skills"].values() if v >= 20)

def _check_level_ups(p, is_gk):
    skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
    for sk in skill_list:
        pts = p["training_points"].get(sk, 0)
        while pts >= 1.0:
            cur = p["skills"].get(sk, 0)
            if cur < 20:
                if cur == 19 and _count_maxed(p) >= 2:
                    pts -= 1.0
                    continue
                p["skills"][sk] = cur + 1
                p["skill_gains"][sk] = p["skill_gains"].get(sk, 0) + 1
            pts -= 1.0
        p["training_points"][sk] = max(0.0, pts)

def apply_training_day(players, day_index):
    day_name = DAYS[day_index % 7]
    if day_name == "Szombat":
        return
    for p in players:
        age = p.get("age", 17)
        if age >= 28:
            continue
        is_gk = p.get("is_gk", False)
        skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
        personal_sk = p.get("personal_training", "reflexek" if is_gk else "passz")
        if personal_sk not in skill_list:
            personal_sk = "reflexek" if is_gk else "passz"
        pts_per_day = p.get("pts_per_day", 0.13)
        p["training_points"][personal_sk] = p["training_points"].get(personal_sk, 0) + pts_per_day
        _check_level_ups(p, is_gk)

def apply_decline_day(players, day_index):
    day_name = DAYS[day_index % 7]
    if day_name == "Szombat":
        return
    for p in players:
        age = p.get("age", 17)
        if age < 28:
            continue
        is_gk = p.get("is_gk", False)
        skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
        pts_per_day = p.get("pts_per_day", 0.13)
        decline = pts_per_day / 3.0
        sk = random.choice(skill_list)
        p["training_points"][sk] = p["training_points"].get(sk, 0) - decline
        while p["training_points"].get(sk, 0) <= -1.0:
            cur = p["skills"].get(sk, 0)
            if cur > 3:
                p["skills"][sk] = cur - 1
                p.setdefault("skill_losses", {})[sk] = p.get("skill_losses", {}).get(sk, 0) + 1
            p["training_points"][sk] = p["training_points"].get(sk, 0) + 1.0

def age_up_season(teams, player_team_id):
    from data_new import replace_retired_player, OUTFIELD_SKILLS, GK_SKILLS, auto_lineup
    for team in teams:
        for i, p in enumerate(team["players"]):
            p["age"] = p.get("age", 17) + 1
            is_gk = p.get("is_gk", False)
            sl = GK_SKILLS if is_gk else OUTFIELD_SKILLS
            p["skill_gains"] = {s: 0 for s in sl}
            p["skill_losses"] = {s: 0 for s in sl}
            if p["age"] >= 36:
                p["retired"] = True
                team["players"][i] = replace_retired_player(team, i)
        team["lineup"] = auto_lineup(team)

def apply_ai_training(teams, day_index, player_team_id):
    day_name = DAYS[day_index % 7]
    if day_name == "Szombat":
        return
    from data_new import POSITION_SKILLS
    for team in teams:
        if team["id"] == player_team_id:
            continue
        for p in team["players"]:
            is_gk = p.get("is_gk", False)
            sl = GK_SKILLS if is_gk else OUTFIELD_SKILLS
            pos_data = POSITION_SKILLS.get(p.get("position", ""), {})
            primary = pos_data.get("primary", sl[:3])
            best = next((s for s in primary if s in sl), sl[0])
            p["personal_training"] = best
        apply_training_day(team["players"], day_index)
        apply_decline_day(team["players"], day_index)

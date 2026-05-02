import json, os, random
from data_new import generate_league, generate_schedule, OUTFIELD_SKILLS, GK_SKILLS, auto_lineup
from training import apply_training_day, apply_decline_day, apply_ai_training, age_up_season, DAYS
from match_engine import simulate_all_matches

class GameState:
    def __init__(self):
        self.mode = None
        self.player_team_name = ""
        self.teams = []
        self.schedule = []
        self.current_day = 0
        self.matchday = 0
        self.season = 1
        self.match_results = []
        self.last_match_events = None
        self.last_round_results = []
        self.match_stats_history = []  # list of {matchday, home, away, sh, sa, events, stats, subs}
        self.team_schedule = {}
        self.news = []
        self.player_team_id = 19

    def start_team_mode(self, team_name, kit_colors=None):
        self.mode = "team"
        self.player_team_name = team_name
        self.teams = generate_league(team_name, player_kit=kit_colors)
        self.schedule = generate_schedule(self.teams)
        for t in self.teams:
            if t["name"] == team_name:
                self.player_team_id = t["id"]; break
        self.add_news(f"Üdvözlünk a {team_name} menedzserjeként!")
        self.add_news("A bajnokság rajtol! Sok sikert!")

    def get_player_team(self):
        for t in self.teams:
            if t["id"] == self.player_team_id: return t
        return self.teams[-1]

    def add_news(self, msg):
        self.news.insert(0, msg)
        if len(self.news) > 30: self.news.pop()

    def get_day_name(self):
        return DAYS[self.current_day % 7]

    def is_matchday(self):
        return self.get_day_name() == "Szombat"

    def next_day(self):
        day_name = self.get_day_name()
        pt = self.get_player_team()
        day_idx = self.current_day % 7

        if day_name != "Szombat":
            # Player team: fejlődés (28 alatt) vagy hanyatlás (28 felett)
            apply_training_day(pt["players"], day_idx)
            apply_decline_day(pt["players"], day_idx)
            # AI teams
            apply_ai_training(self.teams, day_idx, self.player_team_id)
            self.add_news(f"{day_name}: Edzés befejezve.")
        else:
            # Match day
            results = simulate_all_matches(self.teams, self.schedule, self.matchday)
            self.match_results.extend(results)
            self.last_round_results = results
            for r in results:
                if r["home_id"]==self.player_team_id or r["away_id"]==self.player_team_id:
                    self.last_match_events = r
                    hg,ag = r["home_goals"],r["away_goals"]
                    if r["home_id"]==self.player_team_id:
                        rs = f"{pt['name']} {hg}:{ag} {r['away']}"
                    else:
                        rs = f"{r['home']} {hg}:{ag} {pt['name']}"
                    self.add_news(f"Meccseredmény: {rs}")
                    break
            self.matchday += 1

            if self.matchday >= len(self.schedule):
                # Season end
                age_up_season(self.teams, self.player_team_id)
                # Re-auto-lineup AI teams
                for t in self.teams:
                    if t["id"] != self.player_team_id:
                        t["lineup"] = auto_lineup(t)
                self.season += 1
                self.matchday = 0
                for t in self.teams:
                    t["wins"]=t["draws"]=t["losses"]=0
                    t["goals_for"]=t["goals_against"]=t["points"]=0
                self.schedule = generate_schedule(self.teams)
                self.add_news(f"Szezon vége! {self.season}. szezon kezdődik.")

        self.current_day += 1

    def get_standings(self):
        return sorted(self.teams,
                      key=lambda t: (-t["points"],-(t["goals_for"]-t["goals_against"]),-t["goals_for"]))

    def save_match_stats(self, match_anim):
        """Save stats for Meccsek tab."""
        if not match_anim: return
        self.match_stats_history.append({
            'matchday': self.matchday-1,  # already incremented
            'home': match_anim.hn, 'away': match_anim.an,
            'home_id': self.last_match_events.get('home_id',-1) if self.last_match_events else -1,
            'away_id': self.last_match_events.get('away_id',-1) if self.last_match_events else -1,
            'sh': match_anim.sh, 'sa': match_anim.sa,
            'goal_log': list(match_anim._goal_log),
            'cards': list(match_anim.cards),
            'stats': {k:{kk:vv for kk,vv in v.items()} for k,v in match_anim._stats.items()},
            'sub_log': list(match_anim._sub_log),
        })

    def apply_match_result(self, home_goals, away_goals):
        """Override the simulated result with the 2D match result."""
        if self.last_match_events is None: return
        r = self.last_match_events
        old_hg = r["home_goals"]; old_ag = r["away_goals"]
        pid = self.player_team_id
        home_team = next((t for t in self.teams if t["id"]==r["home_id"]), None)
        away_team = next((t for t in self.teams if t["id"]==r["away_id"]), None)
        if not home_team or not away_team: return
        def undo(team, gf, ga):
            team["goals_for"]=max(0,team["goals_for"]-gf)
            team["goals_against"]=max(0,team["goals_against"]-ga)
            if gf>ga:    team["wins"]=max(0,team["wins"]-1);   team["points"]=max(0,team["points"]-3)
            elif gf==ga: team["draws"]=max(0,team["draws"]-1); team["points"]=max(0,team["points"]-1)
            else:        team["losses"]=max(0,team["losses"]-1)
        def apply(team, gf, ga):
            team["goals_for"]+=gf; team["goals_against"]+=ga
            if gf>ga:    team["wins"]+=1;   team["points"]+=3
            elif gf==ga: team["draws"]+=1;  team["points"]+=1
            else:        team["losses"]+=1
        undo(home_team, old_hg, old_ag); undo(away_team, old_ag, old_hg)
        apply(home_team, home_goals, away_goals); apply(away_team, away_goals, home_goals)
        r["home_goals"]=home_goals; r["away_goals"]=away_goals
        for res in self.last_round_results:
            if res.get("home_id")==r["home_id"] and res.get("away_id")==r["away_id"]:
                res["home_goals"]=home_goals; res["away_goals"]=away_goals; break
        pt=self.get_player_team()
        if r["home_id"]==pid: self.news[0]=f"Meccseredmény: {pt['name']} {home_goals}:{away_goals} {r['away']}"
        else:                 self.news[0]=f"Meccseredmény: {r['home']} {home_goals}:{away_goals} {pt['name']}"

    def set_personal_training(self, player, skill):
        player["personal_training"] = skill

    def set_team_training(self, day, idx, skill):
        if day in self.team_schedule and self.team_schedule[day] is not None:
            self.team_schedule[day][idx] = skill

    def save(self, path):
        # Formation és set_piece_takers már a teams dict-ben van tárolva
        data = {
            "mode":self.mode,"player_team_name":self.player_team_name,
            "player_team_id":self.player_team_id,"teams":self.teams,
            "schedule":self.schedule,"current_day":self.current_day,
            "matchday":self.matchday,"season":self.season,
            "team_schedule":self.team_schedule,"news":self.news,
        }
        with open(path,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)

    def _migrate_player(self, p):
        """Betöltéskor frissíti a játékost az új rendszerre (talent, pts_per_day stb.)."""
        from data_new import OUTFIELD_SKILLS, GK_SKILLS, gen_skills_for_budget
        from training import compute_pts_per_day, get_talent_label, TRAINING_DAYS_PER_SEASON
        is_gk = p.get("is_gk", False)
        skill_list = GK_SKILLS if is_gk else OUTFIELD_SKILLS
        age = p.get("age", 22)

        # Ha nincs tehetség adat vagy a skillek rosszak: teljes regenerálás
        vals = list(p.get("skills", {}).values())
        cnt_20 = sum(1 for v in vals if v >= 20)
        cnt_low = sum(1 for v in vals if v < 3)
        needs_regen = (cnt_20 > 2 or cnt_low > 0 or not p.get("pts_per_day"))

        if needs_regen:
            # Tehetség értékek
            start_total = p.get("start_total", random.randint(150, 180))
            peak_total  = p.get("peak_total",  random.randint(600, 650))
            ppd = compute_pts_per_day(start_total, peak_total)
            # Budget korhoz arányosan
            if age <= 28:
                progress = (age - 15) / 13.0
                budget = int(start_total + (peak_total - start_total) * progress)
            else:
                decline_per_season = ppd * TRAINING_DAYS_PER_SEASON / 3.0
                budget = max(start_total, int(peak_total - decline_per_season * (age - 28)))
            p["skills"] = gen_skills_for_budget(p.get("position", ""), budget)
            p["start_total"] = start_total
            p["peak_total"] = peak_total
            p["pts_per_day"] = ppd
            p["talent"] = get_talent_label(ppd)
            p["training_points"] = {s: 0.0 for s in skill_list}
            p["skill_gains"] = {s: 0 for s in skill_list}
        else:
            # Csak a hiányzó mezőket töltjük fel
            if not p.get("pts_per_day"):
                st = p.get("start_total", 160)
                pt = p.get("peak_total", 625)
                ppd = compute_pts_per_day(st, pt)
                p["pts_per_day"] = ppd
                p["talent"] = get_talent_label(ppd)
            for s in skill_list:
                p["training_points"].setdefault(s, 0.0)
                p["skill_gains"].setdefault(s, 0)

    def load(self, path):
        with open(path,"r",encoding="utf-8") as f:
            data = json.load(f)
        self.mode=data["mode"]; self.player_team_name=data["player_team_name"]
        self.player_team_id=data["player_team_id"]; self.teams=data["teams"]
        self.schedule=data["schedule"]; self.current_day=data["current_day"]
        self.matchday=data["matchday"]; self.season=data["season"]
        self.team_schedule=data["team_schedule"]; self.news=data["news"]
        # Régi mentések migrálása
        for team in self.teams:
            for p in team.get("players", []):
                self._migrate_player(p)

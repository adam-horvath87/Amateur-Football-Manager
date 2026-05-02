"""
match_anim.py – 2D meccsmotor, valós idejű (B-verzió)
1 meccs = 300 mp valós idő, FPS=60
"""
import pygame, math, random
from match_engine import (
    sk, physical_state, effective_speed, shot_power, pass_range, cross_range,
    direction_accuracy, apply_inaccuracy, keeper_saves, first_touch_success,
    tackle_probability, is_foul, is_yellow, is_red, is_offside,
    PITCH_W, PITCH_H, GOAL_WIDTH, GOAL_Y_MIN, GOAL_Y_MAX,
    BOX_DEPTH, BOX_Y_MIN, BOX_Y_MAX, HALFTIME, FULLTIME
)
from data_new import FORMATION_ROWS

GAME_W, GAME_H = 1024, 768
FPS = 60
MATCH_SECS = 300   # 1 meccs = 300 valós másodperc

PITCH = pygame.Rect(12, 52, 1000, 592)  # teljes szélességű pálya

MX = PITCH.width  / PITCH_W
MY = PITCH.height / PITCH_H

def m2px(mx, my):
    return PITCH.x + mx * MX, PITCH.y + my * MY

def clamp(v, lo, hi): return max(lo, min(hi, v))
def dst(ax, ay, bx, by): return math.sqrt((ax-bx)**2 + (ay-by)**2)

# ── Színek ────────────────────────────────────────────────────────────────────
C_BG    = (10,14,22);   C_PANEL  = (18,24,38);  C_PANEL2 = (24,32,52)
C_TEXT  = (220,230,245);C_SUBTXT = (130,150,180);C_BORDER = (40,55,80)
C_ACCENT= (0,200,120);  C_ACC2   = (255,180,0);  C_RED    = (220,60,60)
C_NAVY  = (15,22,50);   C_WHITE  = (255,255,255);C_YELLOW = (255,220,0)
C_GREEN_BAR = (40,180,60); C_ORANGE_BAR = (220,140,20); C_RED_BAR = (200,40,40)
HOME_KIT=(45,110,225); HOME_GLW=(120,180,255)
AWAY_KIT=(215,45,45);  AWAY_GLW=(255,130,130)

_FC = {}
def fnt(sz, bold=False):
    k = (sz, bold)
    if k not in _FC:
        for n in ["DejaVuSans","FreeSans","Ubuntu","Arial"]:
            try: _FC[k] = pygame.font.SysFont(n, sz, bold=bold); break
            except: pass
        if k not in _FC: _FC[k] = pygame.font.SysFont(None, sz, bold=bold)
    return _FC[k]

def dtc(s, t, sz, c, cx, cy, bold=False):
    r = fnt(sz, bold).render(str(t), True, c)
    s.blit(r, (cx - r.get_width()//2, cy - r.get_height()//2))

def dt(s, t, sz, c, x, y, bold=False):
    r = fnt(sz, bold).render(str(t), True, c); s.blit(r, (x, y)); return r.get_width()

# ── Pálya rajz ────────────────────────────────────────────────────────────────
def draw_pitch(surf):
    r = PITCH; rw, rh = r.width, r.height; cx, cy = r.centerx, r.centery
    sw = rw // 14
    for i in range(14):
        col = (38,110,38) if i%2==0 else (34,100,34)
        pygame.draw.rect(surf, col, (r.x+i*sw, r.y, sw+1, rh))
    pygame.draw.rect(surf, C_WHITE, r, 2)
    pygame.draw.line(surf, C_WHITE, (cx, r.y), (cx, r.bottom), 1)
    cr = int(min(rw,rh)*0.120)
    pygame.draw.circle(surf, C_WHITE, (cx,cy), cr, 1)
    pygame.draw.circle(surf, C_WHITE, (cx,cy), 3)
    # Tizenhatosok
    pw = int(rw*0.183); ph = int(rh*0.530)
    pygame.draw.rect(surf, C_WHITE, (r.x, cy-ph//2, pw, ph), 1)
    pygame.draw.rect(surf, C_WHITE, (r.right-pw, cy-ph//2, pw, ph), 1)
    # Kis kaputerületek
    gw = int(rw*0.068); gh = int(rh*0.265)
    pygame.draw.rect(surf, C_WHITE, (r.x, cy-gh//2, gw, gh), 1)
    pygame.draw.rect(surf, C_WHITE, (r.right-gw, cy-gh//2, gw, gh), 1)
    # Kapuk (hálóval)
    gnw = 18; gnh = int(GOAL_WIDTH * MY)
    for net_x, flip in [(r.x - gnw, False), (r.right, True)]:
        net = pygame.Rect(net_x, cy - gnh//2, gnw, gnh)
        pygame.draw.rect(surf, (200,200,200), net, 1)
        for ny in range(net.y, net.bottom, 7):
            pygame.draw.line(surf, (130,130,130), (net.x, ny), (net.right, ny), 1)
        for nx in range(net.x, net.right, 7):
            pygame.draw.line(surf, (130,130,130), (nx, net.y), (nx, net.bottom), 1)
    # 11-esek
    pygame.draw.circle(surf, C_WHITE, (r.x+int(rw*0.127), cy), 3)
    pygame.draw.circle(surf, C_WHITE, (r.right-int(rw*0.127), cy), 3)

# ── Formáció pozíció builder ──────────────────────────────────────────────────

# Pozíció rövidítések
POS_ABBREV = {
    "Kapus":"GK","Szélső védő":"WB","Középső védő":"CB","Védekező középpályás":"DM",
    "Középpályás":"MF","Szélső középpályás":"WM","Támadó középpályás":"AM",
    "Szélső":"W","Csatár":"ST","Csatárjelölt":"SS",
    "Szélső védő bal":"LB","Szélső védő jobb":"RB",
}
def pos_short(pdata):
    pos = pdata.get("position","")
    return POS_ABBREV.get(pos, pos[:3] if pos else "?")

# Alap formáció: kicsit visszafogottabb, a csapatnyomás tolja előre
# Home: bal saját kaputól indul (0.04), csatárok kb. a félpályáig (0.48)
# A _apply_team_pressure és a _do_carry viszi őket előre
ROLE_X_FRAC = {"gk":0.04,"def":0.20,"dm":0.32,"mid":0.42,"am":0.60,"att":0.75}

def build_formation_positions(formation, side):
    rows = FORMATION_ROWS.get(formation, FORMATION_ROWS["4-4-2"])
    attacks_right = (side == "home")
    positions = []
    gk_xf = 0.05 if attacks_right else 0.95
    positions.append(("gk", 0.5, gk_xf))
    seen_xf = {gk_xf}
    for rl, cnt, rt in rows:
        xf = ROLE_X_FRAC.get(rt, 0.50)
        while xf in seen_xf: xf += 0.08
        seen_xf.add(xf)
        actual_xf = xf if attacks_right else (1.0 - xf)
        for i in range(cnt):
            yf = (i+1) / (cnt+1)
            positions.append((rt, yf, actual_xf))
    return positions

# ── SimPlayer ─────────────────────────────────────────────────────────────────
class SimPlayer:
    def __init__(self, pdata, role, hx_m, hy_m, kit, glow, side, number):
        self.data   = pdata
        self.role   = role
        self.side   = side
        self.number = number
        self.name   = pdata.get("name","?").split()[-1]
        self.kit    = kit
        self.glow   = glow
        self.is_gk  = (role == "gk")
        self.attacks_right = (side == "home")
        # Formáció-alapú "otthon" pozíció
        self.hx = float(hx_m)
        self.hy = float(hy_m)
        # Aktuális pozíció
        self.x  = float(hx_m)
        self.y  = float(hy_m)
        self.vx = 0.0
        self.vy = 0.0
        # Célpont
        self.tx = self.x
        self.ty = self.y
        self.has_ball  = False
        self.subbed_off= False
        self._move_t   = random.randint(0, 90)
        self._speed_mode = 0.5   # séta/közepes/sprint mód (0.25/0.55/1.0)
        self._carry_spd  = 1.0   # labdavezetési sebesség szorzó
        self._spd_var  = random.uniform(0.92, 1.08)
        self.stats = {"shots":0,"goals":0,"passes":0,"tackles":0,
                      "fouls":0,"yellow":0,"red":0,"assists":0}
        self.sub_entry_sec = 0

    # ── Zóna ─────────────────────────────────────────────────────────────────
    def home_zone(self):
        """Formáció-alapú mozgási zóna."""
        atk = self.attacks_right
        base_x = self.hx
        base_y = self.hy
        # GK: kaputerületen belül
        if self.is_gk:
            # Kapus CSAK a kapu előtt mozoghat (szűk zóna)
            if atk:
                return (0.5, 4.0, GOAL_Y_MIN-0.5, GOAL_Y_MAX+0.5)
            else:
                return (PITCH_W-4.0, PITCH_W-0.5, GOAL_Y_MIN-0.5, GOAL_Y_MAX+0.5)
        # Más pozíciók: szerepfüggő zóna
        role_margins = {
            "def": (PITCH_W*0.08, PITCH_W*0.22),  # szűkebb, csak hátul
            "dm":  (PITCH_W*0.10, PITCH_W*0.28),
            "mid": (PITCH_W*0.14, PITCH_W*0.30),
            "am":  (PITCH_W*0.10, PITCH_W*0.60),
            "att": (PITCH_W*0.08, PITCH_W*0.70),  # csatárok elérhetik a 16-ost
        }
        mx_back, mx_fwd = role_margins.get(self.role, (PITCH_W*0.12, PITCH_W*0.28))
        margin_y = PITCH_H * 0.22
        if atk:
            x0 = max(0.5, base_x - mx_back)
            x1 = min(PITCH_W-0.5, base_x + mx_fwd)
        else:
            x0 = max(0.5, base_x - mx_fwd)
            x1 = min(PITCH_W-0.5, base_x + mx_back)
        y0 = max(0.5, base_y - margin_y)
        y1 = min(PITCH_H-0.5, base_y + margin_y)
        return (x0, x1, y0, y1)

    def in_box_attack(self):
        px, py = self.x, self.y
        if self.attacks_right:
            return px >= PITCH_W - BOX_DEPTH and BOX_Y_MIN <= py <= BOX_Y_MAX
        return px <= BOX_DEPTH and BOX_Y_MIN <= py <= BOX_Y_MAX

    # ── Mozgás ───────────────────────────────────────────────────────────────
    def _is_wide_back(self):
        """Szélső hátvéd-e? (nem szélső középpályás)"""
        pos=self.data.get("position","")
        return "Szélső védő" in pos or "szélső védő" in pos.lower()

    def _is_wide_mid(self):
        """Szélső középpályás-e?"""
        pos=self.data.get("position","")
        return ("Szélső középp" in pos or "szélső középp" in pos.lower()
                or (self.role=="mid" and (self.hy<PITCH_H*0.28 or self.hy>PITCH_H*0.72)))

    def update_movement(self, ball_x, ball_y, elapsed_sec):
        if self.subbed_off: return

        max_spd = self._spd_mps(elapsed_sec) / FPS   # m/frame
        accel   = self._accel_factor()                # lerp per frame

        # ── KAPUS: pontosan a kapuközéppontba áll, labdával arányban ─────────
        if self.is_gk:
            # Kapus a saját kapuját védi (ami mögötte van = ellentétes a támadás irányával)
            goal_line_x = 1.0 if self.attacks_right else PITCH_W - 1.0
            goal_cy     = PITCH_H / 2
            dx_gl = ball_x - goal_line_x
            dy_gl = ball_y - goal_cy
            dist_gl = math.sqrt(dx_gl*dx_gl + dy_gl*dy_gl) or 1
            # Kapus 1.5-3m-re áll a kapuvonaltól a labda irányában
            reach = clamp(1.5 + dist_gl * 0.04, 1.0, 4.0)
            opt_x = goal_line_x + (dx_gl/dist_gl) * reach
            opt_y = goal_cy     + (dy_gl/dist_gl) * reach
            # Kapus MÖGÖTTE lévő kapunál marad (nem előtte!)
            if self.attacks_right:
                # Home 1.félid: kapu x=0 oldalon → kapus ott marad
                opt_x = clamp(opt_x, 0.3, BOX_DEPTH*0.42)
            else:
                # Home 2.félid / Away 1.félid: kapu x=PITCH_W oldalon
                opt_x = clamp(opt_x, PITCH_W-BOX_DEPTH*0.42, PITCH_W-0.3)
            opt_y = clamp(opt_y, GOAL_Y_MIN-0.5, GOAL_Y_MAX+0.5)
            self.tx = opt_x; self.ty = opt_y; self._move_t = 1
            # Kapus gyors, sima mozgás
            dx = opt_x - self.x; dy = opt_y - self.y
            d  = math.sqrt(dx*dx+dy*dy)
            if d > 0.1:
                step = min(max_spd * 1.2, d)
                self.x += dx/d * step
                self.y += dy/d * step
            self.x = clamp(self.x, 0.5, PITCH_W-0.5)
            self.y = clamp(self.y, 0.5, PITCH_H-0.5)
            return

        # ── LABDABIRTOKOS: sebesség az előtte lévő ellenfél távolságától függ ──
        if self.has_ball:
            # Legközelebbi ellenfél
            from_side = "home" if self.side=="home" else "away"
            opp_side  = "away" if self.side=="home" else "home"
            # Nem férünk hozzá a csapathoz itt, de az _spd_var tartalmazza a saját véletlent
            # A sebességmód: sprint ha szabad (~sprint), lassul ha közel az ellenfél
            # (A tényleges ellenfél-ellenőrzés a _tick-ben van, itt csak a sebességet kezeljük)
            carry_spd = max_spd * getattr(self, '_carry_spd', 1.0)
            gx = PITCH_W * 0.88 if self.attacks_right else PITCH_W * 0.12
            dx = gx - self.x
            dy = (PITCH_H/2 - self.y) * 0.25
            d  = math.sqrt(dx*dx + dy*dy)
            if d > 1.0:
                want_vx = (dx/d) * carry_spd
                want_vy = (dy/d) * carry_spd
                self.vx += (want_vx - self.vx) * accel
                self.vy += (want_vy - self.vy) * accel
                self.x  += self.vx
                self.y  += self.vy
            self.x = clamp(self.x, 0.5, PITCH_W-0.5)
            self.y = clamp(self.y, 0.5, PITCH_H-0.5)
            return

        # ── LABDA NÉLKÜLI JÁTÉKOS: pozíciótartás változó sebességgel ───────
        # Sebesség mód: séta / közepes / sprint (véletlenszerűen váltakozik)
        self._move_t -= 1
        if self._move_t <= 0:
            self._move_t = random.randint(150, 300)
            # Sebesség mód: 30% séta, 45% közepes, 25% sprint
            r_spd = random.random()
            if r_spd < 0.30:
                self._speed_mode = 0.28
            elif r_spd < 0.75:
                self._speed_mode = 0.58
            else:
                self._speed_mode = 1.0
            x0, x1, y0, y1 = self.home_zone()
            r = random.random()
            # Csatárok: mindig az ellenfél 16-osán belül/közelében
            if self.role == "att":
                gx_goal = PITCH_W*0.92 if self.attacks_right else PITCH_W*0.08
                self.tx = clamp(gx_goal + random.uniform(-5, 2), x0, x1)
                self.ty = clamp(PITCH_H/2 + random.uniform(-7, 7), y0, y1)
                self._speed_mode = max(self._speed_mode, 0.75)  # gyorsabb
            elif self.role == "am" and r < 0.75:
                gx_goal = PITCH_W*0.82 if self.attacks_right else PITCH_W*0.18
                self.tx = clamp(gx_goal + random.uniform(-6, 4), x0, x1)
                self.ty = clamp(PITCH_H/2 + random.uniform(-9, 9), y0, y1)
                self._speed_mode = max(self._speed_mode, 0.65)
            elif self.role in ("am","mid") and r < 0.75:
                # Labda közelébe húzódik
                self.tx = clamp(ball_x + random.uniform(-8, 8), x0, x1)
                self.ty = clamp(ball_y + random.uniform(-6, 6), y0, y1)
            elif r < 0.88:
                # Alappozícióhoz tér vissza
                self.tx = clamp(self.hx + random.uniform(-4, 4), x0, x1)
                self.ty = clamp(self.hy + random.uniform(-4, 4), y0, y1)
            else:
                self.tx = random.uniform(x0, x1)
                self.ty = random.uniform(y0, y1)

        eff_spd = max_spd * getattr(self, '_speed_mode', 0.5)
        dx = self.tx - self.x
        dy = self.ty - self.y
        d  = math.sqrt(dx*dx + dy*dy)
        if d > 0.3:
            want_vx = (dx/d) * eff_spd
            want_vy = (dy/d) * eff_spd
            self.vx += (want_vx - self.vx) * accel
            self.vy += (want_vy - self.vy) * accel
            self.x  += self.vx
            self.y  += self.vy
        else:
            self.vx *= 0.5; self.vy *= 0.5

        self.x = clamp(self.x, 0.5, PITCH_W-0.5)
        self.y = clamp(self.y, 0.5, PITCH_H-0.5)

    def _spd_mps(self, elapsed_sec):
        """
        Max sebesség: gyorsasag=10 → 4.0 m/s (alap)
                      gyorsasag=20 → 8.0 m/s (kétszeres)
                      gyorsasag=1  → 0.8 m/s
        Lineáris: spd = gyorsasag * 0.4 m/s
        """
        gyors = sk(self.data, "gyorsasag", 10)
        base  = gyors * 0.45          # 0.45–9.0 m/s (gyorsasag 1–20)
        return base * physical_state(self.data, elapsed_sec)

    def _accel_factor(self):
        """
        Gyorsulási tényező: mennyire gyorsan közelíti meg a kívánt sebességet.
        gyorsulas=20 → 3mp alatt éri el max sebességét → fast lerp ~0.22/frame
        gyorsulas=10 → 6mp alatt → lerp ~0.11/frame
        gyorsulas=1  → 12mp alatt → lerp ~0.055/frame
        Képlet: accel = gyorsulas / 20 * 0.20 + 0.02
        """
        gyorsulas = sk(self.data, "gyorsulas", 10)
        return gyorsulas / 20.0 * 0.20 + 0.02  # 0.03–0.22

    def run_toward(self, tx, ty, elapsed_sec):
        """Célpont felé fut max sebességgel (labda megszerzéséhez)."""
        spd   = self._spd_mps(elapsed_sec) / FPS
        accel = self._accel_factor()
        dx = tx - self.x; dy = ty - self.y
        d  = math.sqrt(dx*dx+dy*dy)
        if d < 0.5: return True
        want_vx = dx/d * spd; want_vy = dy/d * spd
        self.vx += (want_vx-self.vx)*accel
        self.vy += (want_vy-self.vy)*accel
        self.x  += self.vx; self.y += self.vy
        return False

    def phys_pct(self, elapsed_sec):
        return int(physical_state(self.data, elapsed_sec) * 100)

    # ── Rajz ─────────────────────────────────────────────────────────────────
    def draw(self, surf, elapsed_sec=0):
        if self.subbed_off: return
        px, py = m2px(self.x, self.y)
        ix, iy = int(px), int(py)
        r = 11
        if self.has_ball:
            pygame.draw.circle(surf, self.glow, (ix,iy), r+5, 2)
        pygame.draw.circle(surf, self.kit, (ix,iy), r)
        pygame.draw.circle(surf, C_WHITE, (ix,iy), r, 2)
        bright = self.kit[0]*0.299 + self.kit[1]*0.587 + self.kit[2]*0.114
        num_col = (15,15,15) if bright > 150 else C_WHITE
        ns = fnt(9, True).render(str(self.number), True, num_col)
        surf.blit(ns, (ix - ns.get_width()//2, iy - ns.get_height()//2))
        if self.has_ball:
            ts = fnt(11).render(self.name, True, C_WHITE)
            bw = ts.get_width()+8; bh = ts.get_height()+3
            bg = pygame.Surface((bw,bh), pygame.SRCALPHA)
            bg.fill((0,0,0,180))
            surf.blit(bg, (ix-bw//2, iy-r-bh-2))
            surf.blit(ts, (ix-ts.get_width()//2, iy-r-bh))

# ── SimBall – ívelt repülés ───────────────────────────────────────────────────
class SimBall:
    def __init__(self):
        self.x = PITCH_W/2; self.y = PITCH_H/2
        self.vx = 0.0;      self.vy = 0.0
        self.carrier = None
        self.trail   = []
        # Ív animáció
        self.arc_t     = 0.0   # 0..1 haladás az ívben
        self.arc_total = 0     # teljes ívhossz frame-ben
        self.arc_sx    = 0.0; self.arc_sy = 0.0   # start
        self.arc_ex    = 0.0; self.arc_ey = 0.0   # end
        self.arc_h     = 0.0   # maximális magasság pixel-ben
        self.arc_active= False
        self.arc_on_target = False  # gól felé repül-e
        self.arc_callback  = None  # lambda, amikor megérkezik
        self._out_side = None   # "top"/"bottom" ha kiment
        self._out_x    = 0.0   # x pozíció ahol kiment
        self._out_base = None  # "left"/"right" alapvonal
        self._out_y    = 0.0   # y ahol kiment az alapvonalon

    def attach(self, p):
        self.arc_active = False
        self.carrier = p
        self.vx = 0.0; self.vy = 0.0
        p.has_ball = True

    def release_arc(self, tx, ty, height, frames, on_target=False, callback=None):
        """Ívelt passz/lövés indítása."""
        if self.carrier:
            self.carrier.has_ball = False
            self.carrier = None
        self.arc_sx = self.x; self.arc_sy = self.y
        self.arc_ex = tx;     self.arc_ey = ty
        self.arc_h  = height  # pixel magasság (0 = talajszint)
        self.arc_total = max(1, frames)
        self.arc_t = 0.0
        self.arc_active = True
        self.arc_on_target = on_target
        self.arc_callback  = callback

    def snap(self, x, y):
        self.arc_active = False
        self.x = float(x); self.y = float(y)
        self.vx = 0.0; self.vy = 0.0
        if self.carrier:
            self.carrier.has_ball = False
            self.carrier = None

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12: self.trail.pop(0)

        if self.arc_active:
            self.arc_t += 1.0 / self.arc_total
            t = min(1.0, self.arc_t)
            self.x = self.arc_sx + (self.arc_ex - self.arc_sx) * t
            self.y = self.arc_sy + (self.arc_ey - self.arc_sy) * t
            # Befejezés
            if self.arc_t >= 1.0:
                self.arc_active = False
                self.x = self.arc_ex; self.y = self.arc_ey
                if self.arc_callback:
                    self.arc_callback()
            return

        if self.carrier:
            self.x = self.carrier.x
            self.y = self.carrier.y
            return

        # Szabadon guruló labda (nem ívelt) – súrlódás
        self.vx *= 0.88; self.vy *= 0.88
        self.x  += self.vx; self.y += self.vy
        if self.x < 0.5:
            self.x = 0.5; self.vx *= -0.4
            self._out_base = "left"; self._out_y = self.y
        if self.x > PITCH_W-0.5:
            self.x = PITCH_W-0.5; self.vx *= -0.4
            self._out_base = "right"; self._out_y = self.y
        if self.y < 0.5:
            self.y = 0.5; self.vy *= -0.4
            self._out_side = "top"; self._out_x = self.x
        if self.y > PITCH_H-0.5:
            self.y = PITCH_H-0.5; self.vy *= -0.4
            self._out_side = "bottom"; self._out_x = self.x

    def speed(self):
        if self.arc_active: return 1.0
        return math.sqrt(self.vx**2+self.vy**2)

    def draw(self, surf):
        # Trail
        n = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            px, py = m2px(tx, ty)
            a = int(15 + 55 * (i+1)/max(1,n))
            ts = pygame.Surface((8,8), pygame.SRCALPHA)
            pygame.draw.circle(ts, (255,255,255,a), (4,4), 2)
            surf.blit(ts, (int(px)-4, int(py)-4))

        px, py = m2px(self.x, self.y)
        ix, iy = int(px), int(py)

        # Ív: a magasságot pixel-eltolásként jelenítjük meg (felfelé)
        arc_offset_y = 0
        if self.arc_active:
            t = self.arc_t
            arc_offset_y = int(-self.arc_h * 4 * t * (1-t))  # parabola csúcs közepén

        draw_y = iy + arc_offset_y
        # Árnyék a talajon
        if arc_offset_y < -4:
            shadow_r = max(3, 7 - abs(arc_offset_y)//8)
            sha = pygame.Surface((shadow_r*2+2, shadow_r+2), pygame.SRCALPHA)
            pygame.draw.ellipse(sha, (0,0,0,60), (0,0,shadow_r*2,shadow_r))
            surf.blit(sha, (ix-shadow_r, iy-shadow_r//2))

        r_ball = 7 + (abs(arc_offset_y)//15)  # levegőben kicsit nagyobb
        pygame.draw.circle(surf, (240,240,240), (ix, draw_y), r_ball)
        pygame.draw.circle(surf, (40,40,40),    (ix, draw_y), r_ball, 1)
        # Futball-minta
        for ang in [0, 120, 240]:
            a = math.radians(ang)
            pygame.draw.arc(surf, (60,60,60),
                (ix-4, draw_y-4, 8, 8), a, a+math.radians(60), 2)

# ── Bíró ─────────────────────────────────────────────────────────────────────
class Referee:
    def __init__(self, home_kit, away_kit):
        self.x = float(PITCH.centerx); self.y = float(PITCH.centery)
        self.tx = self.x; self.ty = self.y; self._t = 0
        def lum(c): return c[0]*0.299+c[1]*0.587+c[2]*0.114
        if lum(home_kit) < 80 or lum(away_kit) < 80:
            self.col = (255,220,0); self.tcol = (0,0,0)
        else:
            self.col = (30,30,30);  self.tcol = (255,220,0)

    def update(self, bx, by):
        px, py = m2px(bx, by)
        self._t -= 1
        if self._t <= 0:
            self._t = random.randint(80,180)
            tx = PITCH.centerx+(px-PITCH.centerx)*0.45+random.uniform(-60,60)
            ty = PITCH.centery+(py-PITCH.centery)*0.35+random.uniform(-45,45)
            self.tx = clamp(tx, PITCH.x+20, PITCH.right-20)
            self.ty = clamp(ty, PITCH.y+20, PITCH.bottom-20)
        self.x += (self.tx-self.x)*0.010
        self.y += (self.ty-self.y)*0.010

    def draw(self, surf):
        ix,iy = int(self.x),int(self.y)
        pygame.draw.circle(surf,self.col,(ix,iy),10)
        pygame.draw.circle(surf,(160,160,160),(ix,iy),10,2)
        ns = fnt(8,True).render("B",True,self.tcol)
        surf.blit(ns,(ix-ns.get_width()//2,iy-ns.get_height()//2))

# ── Csere panel (fizikai állapottal + visszavonás) ───────────────────────────
class SubPanel:
    """
    Csere panel: bal = pályán lévők, jobb = kispad.
    Kétlépéses kiválasztás: (1) kattints a kintire (pirossal jelöli),
    (2) kattints a + gombra a bejövőnél → pending párba kerül.
    Végén OK vagy Visszavonás.
    """
    PW = 700; PH = 640
    def __init__(self, gs, match_anim):
        self.gs  = gs; self.ma = match_anim
        self.open = False
        self.pending = []      # [(out_SimPlayer, in_pdata|None), ...]
        self._sel_out = None   # ideiglenesen kijelölt kinti játékos

    def toggle(self): self.open = not self.open
    def close(self):  self.open = False; self._sel_out = None

    def _elapsed(self): return self.ma.elapsed_sec
    def _panel_r(self):
        return pygame.Rect(GAME_W//2-self.PW//2, 50, self.PW, self.PH)

    def _field(self):
        side = self.ma._player_side
        return self.ma.hp if side=="home" else self.ma.ap
    def _bench(self):
        side = self.ma._player_side
        return self.ma.bench_h if side=="home" else self.ma.bench_a
    def _used(self):
        side = self.ma._player_side
        return self.ma.subs_h if side=="home" else self.ma.subs_a

    def _col_x(self):
        r = self._panel_r()
        col_w = (self.PW-18)//2
        return r.x+6, r.x+6+col_w+6, col_w   # lx, rx, col_w

    def draw(self, surf):
        if not self.open: return
        pr = self._panel_r()
        pygame.draw.rect(surf, C_PANEL, pr, border_radius=8)
        pygame.draw.rect(surf, C_BORDER, pr, 1, border_radius=8)

        used = self._used()
        dt(surf,"CSERÉK",13,C_ACCENT,pr.x+10,pr.y+7)
        dt(surf,f"Felhasznált: {used}/5",11,C_SUBTXT,pr.x+150,pr.y+8)

        lx, rx, col_w = self._col_x()
        y0 = pr.y+28
        pygame.draw.line(surf,C_BORDER,(lx+col_w,y0),(lx+col_w,pr.bottom-54),1)
        dt(surf,"Pályán:",11,C_SUBTXT,lx,y0)
        dt(surf,"Kispadon:",11,C_SUBTXT,rx,y0)

        # ── Bal: pályán lévők ─────────────────────────────────────────────
        bar_w = 52; yl = y0+18
        for p in self._field():
            if p.subbed_off: continue
            pct   = p.phys_pct(self._elapsed())
            is_out_pending = any(op is p for op,_ in self.pending)
            is_sel = (self._sel_out is p)
            bg = (65,20,20) if (is_out_pending or is_sel) else C_PANEL2
            rr = pygame.Rect(lx, yl, col_w-4, 23)
            pygame.draw.rect(surf, bg, rr, border_radius=4)
            if is_out_pending: pygame.draw.rect(surf,C_RED,rr,1,border_radius=4)
            elif is_sel:       pygame.draw.rect(surf,C_ACC2,rr,1,border_radius=4)
            # Pozíció rövidítés + szám + név
            abbr = pos_short(p.data)
            dt(surf,f"#{p.number} {p.name}",11,C_TEXT,rr.x+5,yl+4)
            dt(surf,abbr,9,C_SUBTXT,rr.right-bar_w-38,yl+6)
            bar_col = C_GREEN_BAR if pct>65 else (C_ORANGE_BAR if pct>35 else C_RED_BAR)
            bx2 = rr.right-bar_w-4
            pygame.draw.rect(surf,(25,25,25),(bx2,yl+7,bar_w,9),border_radius=3)
            pygame.draw.rect(surf,bar_col,(bx2,yl+7,int(bar_w*pct/100),9),border_radius=3)
            yl+=26

        # ── Jobb: kispadon lévők ──────────────────────────────────────────
        yr = y0+18
        for pdata in self._bench():
            if pdata.get("_on_field"): continue
            is_in = any(ip is pdata for _,ip in self.pending)
            bg = (20,55,25) if is_in else C_PANEL2
            rr = pygame.Rect(rx, yr, col_w-4, 23)
            pygame.draw.rect(surf, bg, rr, border_radius=4)
            if is_in: pygame.draw.rect(surf,C_ACCENT,rr,1,border_radius=4)
            abbr = pos_short(pdata)
            name = pdata.get("name","?").split()[-1]
            dt(surf,f"{name} ({abbr})",11,C_TEXT,rr.x+5,yr+4)
            # + gomb csak ha van kijelölt kinti ÉS ez még nincs párban
            if self._sel_out and not is_in:
                btn = pygame.Rect(rr.right-22,yr+3,18,17)
                pygame.draw.rect(surf,C_ACCENT,btn,border_radius=3)
                dtc(surf,"+",12,C_WHITE,btn.centerx,btn.centery)
            yr+=26

        # ── Függőben lévő cserék ──────────────────────────────────────────
        pend_y = pr.bottom-105
        if self.pending:
            pygame.draw.line(surf,C_BORDER,(pr.x+6,pend_y),(pr.right-6,pend_y),1)
            pend_y+=4
            dt(surf,"Függőben:",11,C_ACC2,pr.x+10,pend_y); pend_y+=18
            for i,(op,ip) in enumerate(self.pending):
                rr = pygame.Rect(pr.x+6,pend_y,self.PW-52,20)
                pygame.draw.rect(surf,(28,48,28),rr,border_radius=3)
                in_name = ip.get("name","?").split()[-1] if ip else "(válassz kispadost)"
                dt(surf,f"#{op.number} {op.name}  →  {in_name}",10,C_TEXT,rr.x+6,pend_y+3)
                xb = pygame.Rect(pr.right-44,pend_y+2,18,16)
                pygame.draw.rect(surf,C_RED,xb,border_radius=3)
                dtc(surf,"✕",10,C_WHITE,xb.centerx,xb.centery)
                pend_y+=23

        # ── OK / Visszavonás ──────────────────────────────────────────────
        if self.pending:
            btn_y = pr.bottom-44
            ok_r = pygame.Rect(pr.x+8,    btn_y, (self.PW-24)//2, 36)
            no_r = pygame.Rect(pr.x+8+(self.PW-24)//2+8, btn_y, (self.PW-24)//2, 36)
            pygame.draw.rect(surf,C_ACCENT,ok_r,border_radius=6)
            pygame.draw.rect(surf,C_RED,   no_r,border_radius=6)
            dtc(surf,"✓ Csere végrehajtása",12,C_WHITE,ok_r.centerx,ok_r.centery)
            dtc(surf,"✕ Visszavonás",12,C_WHITE,no_r.centerx,no_r.centery)

    def handle_click(self, mx, my):
        if not self.open: return
        pr = self._panel_r()
        if not pr.collidepoint(mx,my): self.close(); return

        used  = self._used()
        lx, rx, col_w = self._col_x()
        y0    = pr.y+28

        # ── OK / Visszavonás gombok ───────────────────────────────────────
        if self.pending:
            btn_y = pr.bottom-44
            ok_r = pygame.Rect(pr.x+8, btn_y, (self.PW-24)//2, 36)
            no_r = pygame.Rect(pr.x+8+(self.PW-24)//2+8, btn_y, (self.PW-24)//2, 36)
            if ok_r.collidepoint(mx,my):
                side = self.ma._player_side
                for op,ip in self.pending:
                    if ip is not None and used < 5:
                        self.ma._do_substitution(op,ip,side); used+=1
                self.pending.clear(); self._sel_out=None; return
            if no_r.collidepoint(mx,my):
                self.pending.clear(); self._sel_out=None; return

        # ── Függőben X gombok ─────────────────────────────────────────────
        pend_y = pr.bottom-105+4+18
        for i,(op,ip) in enumerate(self.pending):
            xb = pygame.Rect(pr.right-44,pend_y+2,18,16)
            if xb.collidepoint(mx,my):
                # Ha ez volt a sel_out, töröljük azt is
                if self._sel_out is op: self._sel_out=None
                self.pending.pop(i); return
            pend_y+=23

        # ── Bal oszlop: pályán lévő kijelölése (out) ─────────────────────
        yl = y0+18
        for p in self._field():
            if p.subbed_off: continue
            rr = pygame.Rect(lx, yl, col_w-4, 23)
            if rr.collidepoint(mx,my):
                already_pending = any(op is p for op,_ in self.pending)
                if already_pending: yl+=26; continue
                # Kijelöljük vagy visszavonjuk
                if self._sel_out is p:
                    self._sel_out = None
                else:
                    self._sel_out = p
                return
            yl+=26

        # ── Jobb oszlop: kispadon lévő + gombja ──────────────────────────
        yr = y0+18
        for pdata in self._bench():
            if pdata.get("_on_field"): yr+=26; continue
            is_in = any(ip is pdata for _,ip in self.pending)
            if not is_in and self._sel_out:
                btn = pygame.Rect(rx+col_w-26, yr+3, 18, 17)
                if btn.collidepoint(mx,my):
                    # Párba rakjuk a kijelölt outtal
                    self.pending.append((self._sel_out, pdata))
                    self._sel_out = None
                    return
            yr+=26

# ── Fő MatchAnim osztály ──────────────────────────────────────────────────────
class MatchAnim:
    def __init__(self, match_data, gs=None, lineup_h=None, lineup_a=None,
                 round_results=None, set_piece_takers=None):
        self.md  = match_data
        self.gs  = gs
        self.hn  = match_data.get("home","Hazai")
        self.an  = match_data.get("away","Vendég")
        self.sh  = 0; self.sa = 0
        self.frame= 0; self.elapsed_sec= 0.0
        self.done = False; self.paused = False
        self.speed_multiplier = 1
        self._halftime_flag  = False
        self._halftime_pause = 0   # visszaszámlálás
        self._goal_flash = 0; self._goal_team = None
        self._stats = {s:{"shots":0,"on_target":0,"corners":0,"fouls":0,
                          "possession":0,"passes":0,"offsides":0} for s in ("home","away")}
        self._goal_log = []; self._sub_log = []; self.cards = []; self.log = []
        self._round_results = round_results or []
        self._action_cd = 0
        self._carrier   = None
        self._poss      = "home"
        self._set_piece = None; self._set_piece_t = 0
        self._pass_recipient = None
        self._kickoff_phase = True   # amíg igaz: mindenki a saját térfele
        self._kickoff_done  = False  # elvégezték-e már a kezdőrúgást

        # Kit
        self.home_kit  = HOME_KIT; self.away_kit  = AWAY_KIT
        self.home_glow = HOME_GLW; self.away_glow = AWAY_GLW
        pid = getattr(gs,"player_team_id",19) if gs else 19
        if gs:
            from data_new import pick_away_color
            for t in gs.teams:
                if t["id"]==match_data.get("home_id",-1):
                    self.home_kit  = tuple(t.get("kit_home",HOME_KIT))
                    self.home_glow = tuple(min(255,v+80) for v in self.home_kit)
                if t["id"]==match_data.get("away_id",-1):
                    self.away_kit  = pick_away_color(self.home_kit,
                        tuple(t.get("kit_home",AWAY_KIT)),
                        tuple(t.get("kit_away",(215,45,45))),
                        tuple(t.get("kit_third",(255,180,0))))
                    self.away_glow = tuple(min(255,v+80) for v in self.away_kit)
        gk_h = tuple(max(0,v-60) for v in self.home_kit)
        gk_a = tuple(max(0,v-60) for v in self.away_kit)
        self._player_side = "home" if match_data.get("home_id")==pid else "away"

        h_sq=[]; a_sq=[]; h_form="4-4-2"; a_form="4-4-2"
        if gs:
            tm={t["id"]:t for t in gs.teams}
            ht=tm.get(match_data.get("home_id",-1),{})
            at=tm.get(match_data.get("away_id",-1),{})
            h_form=ht.get("formation","4-4-2"); a_form=at.get("formation","4-4-2")
            h_sq=ht.get("players",[]); a_sq=at.get("players",[])

        # lineup_h/lineup_a: a taktika képernyőn beállított kezdőcsapat
        # Ezek {slot_id: player_dict} formátumúak
        # A sorrendet a formáció pozíciói alapján állítjuk fel
        # lineup_h/a: {slot_id: player_dict} VAGY {slot_id: name_string}
        # Normalizálás: stringből dict-re
        def normalize_lineup(lineup, squad):
            if not lineup: return None
            name_map = {p["name"]:p for p in squad}
            result={}
            for slot,val in lineup.items():
                if isinstance(val,str):
                    if val in name_map: result[slot]=name_map[val]
                elif isinstance(val,dict):
                    result[slot]=val
            return result if result else None
        lineup_h_n = normalize_lineup(lineup_h, h_sq)
        lineup_a_n = normalize_lineup(lineup_a, a_sq)
        # AI csapatok: auto_lineup alapján
        if not lineup_h_n and gs:
            from data_new import auto_lineup
            ai_lineup_h = gs.teams[next((i for i,t in enumerate(gs.teams) if t["id"]==match_data.get("home_id",-1)),0)].get("lineup",{})
            lineup_h_n = normalize_lineup(ai_lineup_h, h_sq)
        if not lineup_a_n and gs:
            ai_lineup_a = gs.teams[next((i for i,t in enumerate(gs.teams) if t["id"]==match_data.get("away_id",-1)),0)].get("lineup",{})
            lineup_a_n = normalize_lineup(ai_lineup_a, a_sq)
        h_ordered = self._order_squad_from_lineup(lineup_h_n, h_sq, h_form, "home") if lineup_h_n else h_sq
        a_ordered = self._order_squad_from_lineup(lineup_a_n, a_sq, a_form, "away") if lineup_a_n else a_sq

        self.hp, self.bench_h = self._build_squad("home",h_form,h_ordered,self.home_kit,self.home_glow,gk_h)
        self.ap, self.bench_a = self._build_squad("away",a_form,a_ordered,self.away_kit,self.away_glow,gk_a)
        self.ball = SimBall()
        self.ball.snap(PITCH_W/2, PITCH_H/2)
        self.ref  = Referee(self.home_kit,self.away_kit)
        self.subs_h=0; self.subs_a=0
        self._sub_panel = SubPanel(gs, self)
        # Mindenki a saját térfelén (home bal, away jobb)
        for p in self.hp:
            p.hx = clamp(p.hx, 0.5, PITCH_W/2 - 0.5)
            p.x  = p.hx; p.y = p.hy; p.tx = p.hx; p.ty = p.hy
        for p in self.ap:
            p.hx = clamp(p.hx, PITCH_W/2 + 0.5, PITCH_W - 0.5)
            p.x  = p.hx; p.y = p.hy; p.tx = p.hx; p.ty = p.hy
        kicker = next((p for p in self.hp if p.role in ("att","am","mid")), self.hp[1])
        kicker.x = PITCH_W/2 - 0.5; kicker.y = PITCH_H/2
        kicker.tx = kicker.x; kicker.ty = kicker.y
        self._give_ball(kicker)
        self._kickoff_phase = True; self._kickoff_done = False

        # Kontroll gombok
        self._pause_r= pygame.Rect(GAME_W//2-162,GAME_H-46,96,38)
        self._speed_r= pygame.Rect(GAME_W//2-60, GAME_H-46,96,38)
        self._subs_r = pygame.Rect(GAME_W//2+42, GAME_H-46,96,38)
        # Post-match stats
        self._stats_tab    = "match"
        self._stats_scroll = 0
        # Set piece takers (main.py-ból átadott)
        self._sp_takers = set_piece_takers or {}

    # ── Squad builder ─────────────────────────────────────────────────────────
    def _order_squad_from_lineup(self, lineup, full_squad, formation, side):
        """
        lineup: {slot_id: player_dict} (taktika képernyőről, pl {"GK": p, "DL": p2, ...})
        full_squad: az összes játékos
        Visszaad: 11 fős listát + kispad.
        """
        if not lineup:
            return full_squad
        # A lineup dict értékei a starters (GK + pozíciók)
        starters = []
        used_names = set()
        # GK első
        gk = lineup.get("GK")
        if gk and gk.get("name") not in used_names:
            starters.append(gk); used_names.add(gk["name"])
        # Többi slot sorrendben (DEF → DM → MID → AM → ATT)
        slot_priority = ["DL","DCL","DC","DCR","DR",
                         "DM","DM1","DM2",
                         "ML","MCL","MC","MCR","MR",
                         "MC1","MC2","MC3","MC4","MC5",
                         "AM","AM1","AM2",
                         "FL","FR","ST1","ST2","ST3","ATT"]
        for slot_id in slot_priority:
            p = lineup.get(slot_id)
            if p and p.get("name") not in used_names:
                starters.append(p); used_names.add(p["name"])
        # Ha valami kimaradt a lineup-ból (más slot névvel)
        for slot_id, p in lineup.items():
            if p and p.get("name") not in used_names:
                starters.append(p); used_names.add(p["name"])
            if len(starters) >= 11: break
        # Egészítsük ki 11-re full_squad-ból
        for p in full_squad:
            if len(starters) >= 11: break
            if p.get("name") not in used_names:
                starters.append(p); used_names.add(p["name"])
        # Kispad
        bench = [p for p in full_squad if p.get("name") not in used_names]
        return starters[:11] + bench

    def _build_squad(self, side, formation, squad_raw, kit, glow, gk_kit):
        positions = build_formation_positions(formation, side)
        players=[]; bench=[]
        sq = squad_raw[:]
        for i,(role,yf,xf) in enumerate(positions[:11]):
            mx_m=xf*PITCH_W; my_m=yf*PITCH_H
            # Kapus pontosan a kapuvonal mögé kerül
            if role=="gk":
                mx_m = 1.0 if side=="home" else PITCH_W-1.0
                my_m = PITCH_H/2
            k = gk_kit if role=="gk" else kit
            pdata = sq[i] if i<len(sq) else {"name":f"{'H' if side=='home' else 'A'}{i+1}","skills":{},"position":"Középpályás"}
            p = SimPlayer(pdata,role,mx_m,my_m,k,glow,side,i+1)
            players.append(p)
        for pdata in sq[11:]:
            bench.append(pdata)
        return players, bench

    # ── Labda + birtok ────────────────────────────────────────────────────────
    def _give_ball(self, p):
        if self._carrier: self._carrier.has_ball=False
        self._carrier=p; self.ball.attach(p)
        self._poss = "home" if p in self.hp else "away"

    def _lose_ball(self):
        if self._carrier: self._carrier.has_ball=False
        self._carrier=None; self.ball.carrier=None

    def _tp(self,side): return self.hp if side=="home" else self.ap
    def _op(self,side): return "away" if side=="home" else "home"
    def _pick(self,side,roles=None,exclude=None):
        pool=[p for p in self._tp(side) if not p.subbed_off]
        if roles: pool=[p for p in pool if p.role in roles]
        if exclude: pool=[p for p in pool if p is not exclude]
        return random.choice(pool) if pool else None
    def _keeper(self,side):
        pool=[p for p in self._tp(side) if p.role=="gk" and not p.subbed_off]
        return pool[0] if pool else None
    def _pick_nearest(self,side,tx,ty,exclude=None):
        pool=[p for p in self._tp(side) if not p.subbed_off]
        if exclude: pool=[p for p in pool if p is not exclude]
        return min(pool,key=lambda p:dst(p.x,p.y,tx,ty)) if pool else None
    def _pick_fwd(self,side):
        pool=[p for p in self._tp(side) if not p.subbed_off and p.role!="gk"]
        if not pool: return None
        return max(pool,key=lambda p:p.x) if side=="home" else min(pool,key=lambda p:p.x)

    # ── Döntési logika ────────────────────────────────────────────────────────
    def _dist_to_goal(self,player):
        gx = PITCH_W if player.attacks_right else 0.0
        return dst(player.x,player.y,gx,PITCH_H/2)

    def _in_shoot_range(self,player):
        # Max lőtávolság: 22m (realisztikus)
        return self._dist_to_goal(player) <= 22.0

    def _should_shoot(self,player):
        if player.is_gk: return False
        if not self._in_shoot_range(player): return False
        dist=self._dist_to_goal(player)
        opp=self._op(self._poss)
        # Ha csak a kapus van közte és a kapu között: MINDIG lő
        defenders=[p for p in self._tp(opp) if not p.subbed_off and not p.is_gk]
        gx=PITCH_W if player.attacks_right else 0.0
        blocking=[d for d in defenders
                  if self._point_to_line_dist(d.x,d.y,player.x,player.y,gx,PITCH_H/2)<4
                  and dst(d.x,d.y,gx,PITCH_H/2)<dist]
        if not blocking and dist<22: return True
        if player.in_box_attack():
            bef=sk(player.data,"befejezes",10)
            return random.random()<(0.70+(bef-10)/20*0.20)  # magasabb esély
        tav=sk(player.data,"tavoli_loves",10)
        prob=0.18+(tav-10)/20*0.16+(0.10 if dist<22 else 0)
        return random.random()<prob

    def _should_cross(self,player):
        if player.is_gk: return False
        is_wide=player.y<PITCH_H*0.25 or player.y>PITCH_H*0.75
        if not is_wide: return False
        if player.attacks_right and player.x<PITCH_W*0.60: return False
        if not player.attacks_right and player.x>PITCH_W*0.40: return False
        bead=sk(player.data,"beadas",10)
        return random.random()<(0.20+(bead-10)/20*0.20)

    def _pass_frames(self, px, py, tx, ty):
        """Passz animáció hossza frame-ben: 0.4-1.2 mp."""
        d=dst(px,py,tx,ty)
        return int(clamp(d/PITCH_W*300, 45, 120))  # lassabb labda

    def _do_shoot(self,player,elapsed_sec):
        power=shot_power(player.data)
        tech =sk(player.data,"technika",10)
        bef  =sk(player.data,"befejezes",10)
        gx   =PITCH_W if player.attacks_right else 0.0
        dist =dst(player.x,player.y,gx,PITCH_H/2)
        side =self._poss; opp=self._op(side)
        player.stats["shots"]+=1; self._stats[side]["shots"]+=1
        on_target_base=0.32+(tech+bef)/40*0.16-dist/45*0.16
        on_target=random.random()<clamp(on_target_base,0.12,0.52)
        tgy=random.uniform(GOAL_Y_MIN+0.3,GOAL_Y_MAX-0.3) if on_target \
            else random.uniform(GOAL_Y_MIN-4,GOAL_Y_MAX+4)
        # Ívelt lövés animáció
        arc_h  = 20 + dist * 0.8   # magasabb ívű távolról
        frames = int(clamp(dist/PITCH_W*140, 18, 55))
        keeper = self._keeper(opp)
        def on_arrive():
            if not on_target:
                # Attacker lövése mellé: KIRÚGÁS (a védekező csapatnak)
                # (ha a védő üti ki: szöglet – de alapból a lövés mellé megy)
                self._set_piece_t = 60
                self._set_piece = f"goalkick_{'h' if opp=='home' else 'a'}"
                self._add_log("⬛ Kapu mellé. → Kirúgás")
                if keeper:
                    keeper.tx = (0.5 if keeper.attacks_right else PITCH_W-0.5)
                    keeper.ty = PITCH_H/2; keeper._move_t=1
                return
            self._stats[side]["on_target"]+=1
            if keeper and keeper_saves(keeper.data,power):
                # Kapus ütötte ki? → szöglet lehetséges
                if random.random()<0.30:
                    self._set_piece=f"corner_{'h' if side=='home' else 'a'}"
                    self._set_piece_t=60
                    self._stats[side]["corners"]+=1
                    self._add_log(f"🧤 {keeper.name} kimenti! → Szöglet")
                    self._lose_ball()
                else:
                    self._give_ball(keeper); self._add_log(f"🧤 {keeper.name} kivédi!")
                return
            self._score_goal(player,side,elapsed_sec)
        self._lose_ball()
        self.ball.release_arc(gx,tgy,arc_h,frames,on_target=on_target,callback=on_arrive)

    def _do_pass(self,player,elapsed_sec):
        if not self._kickoff_done:
            self._kickoff_done = True
            # Csatárok előreindulnak az ellenfél hátvédsorára
            for p in self._tp(self._poss):
                if p.role in ("att","am") and not p.has_ball and not p.subbed_off:
                    opp_defs=[d for d in self._tp(self._op(self._poss))
                              if d.role in ("def","dm") and not d.subbed_off]
                    if opp_defs:
                        target_def=random.choice(opp_defs)
                        p.tx=clamp(target_def.x+random.uniform(-5,5),0.5,PITCH_W-0.5)
                        p.ty=clamp(target_def.y+random.uniform(-4,4),0.5,PITCH_H-0.5)
                        p._move_t=1; p._speed_mode=1.0
        side=self._poss
        fwd_pool=[p for p in self._tp(side)
                  if p is not player and not p.subbed_off
                  and ((player.attacks_right and p.x>player.x-5)
                       or (not player.attacks_right and p.x<player.x+5))]
        if not fwd_pool: fwd_pool=[p for p in self._tp(side) if p is not player and not p.subbed_off]
        if not fwd_pool: return
        target=random.choice(fwd_pool)
        dist=dst(player.x,player.y,target.x,target.y)
        max_r=pass_range(player.data)
        if dist>max_r:
            target=min(fwd_pool,key=lambda p:dst(player.x,player.y,p.x,p.y))
        acc=direction_accuracy(player.data)
        tx,ty=apply_inaccuracy(target.x,target.y,player.x,player.y,acc)
        frames=self._pass_frames(player.x,player.y,tx,ty)
        arc_h = 4 + random.uniform(0,8)   # alacsony ív passzhoz
        player.stats["passes"]+=1; self._stats[side]["passes"]+=1
        # Elvágás ellenőrzés
        opp=self._op(side)
        intercepted=False
        for d in [p for p in self._tp(opp) if not p.subbed_off]:
            dtp=self._point_to_line_dist(d.x,d.y,player.x,player.y,target.x,target.y)
            if dtp<3.5:
                szereles=sk(d.data,"szereles",10); passz=sk(player.data,"passz",10)
                prob=0.08+(szereles-passz)/20*0.25
                if random.random()<prob:
                    def on_intercept(d=d):
                        self._give_ball(d); self._add_log(f"✂️ {d.name} elvágja!")
                    self._lose_ball()
                    self.ball.release_arc(d.x,d.y,arc_h//2,frames,callback=on_intercept)
                    intercepted=True; break
        if not intercepted:
            def on_arrive(t=target):
                if first_touch_success(t.data):
                    self._give_ball(t)
                else:
                    self._lose_ball()
                    self.ball.snap(clamp(t.x+random.uniform(-2,2),1,PITCH_W-1),
                                   clamp(t.y+random.uniform(-2,2),1,PITCH_H-1))
            self._lose_ball()
            self.ball.release_arc(tx,ty,arc_h,frames,callback=on_arrive)

    def _do_cross(self,player,elapsed_sec):
        side=self._poss; opp=self._op(side)
        gx=PITCH_W if player.attacks_right else 0.0
        tx=gx-(5 if player.attacks_right else -5)
        ty=random.uniform(PITCH_H*0.30,PITCH_H*0.70)
        arc_h=30+random.uniform(0,15)
        frames=self._pass_frames(player.x,player.y,tx,ty)+10
        att_pool=[p for p in self._tp(side) if p.role in("att","am") and not p.subbed_off]
        keeper=self._keeper(opp)
        def on_arrive():
            if keeper and sk(keeper.data,"terulet_uralma",10)>=14 and random.random()<0.3:
                self._give_ball(keeper); self._add_log(f"🧤 {keeper.name} kijön!"); return
            if att_pool:
                hp=random.choice(att_pool)
                fejes=sk(hp.data,"fejes",10)
                if random.random()<(0.30+(fejes-10)/20*0.35):
                    self._do_header(hp,side,elapsed_sec); return
            if keeper: self._give_ball(keeper)
        self._lose_ball()
        self.ball.release_arc(tx,ty,arc_h,frames,callback=on_arrive)
        self._add_log(f"⚡ {player.name} beadás!")

    def _do_header(self,player,side,elapsed_sec):
        opp=self._op(side)
        gx=PITCH_W if player.attacks_right else 0.0
        power=sk(player.data,"fejes",10)/20*18
        fejes=sk(player.data,"fejes",10)
        in_goal=random.random()<(0.38+(fejes-10)/20*0.28)
        player.stats["shots"]+=1; self._stats[side]["shots"]+=1
        tgy=random.uniform(GOAL_Y_MIN+0.3,GOAL_Y_MAX-0.3)
        if in_goal:
            self._stats[side]["on_target"]+=1
            keeper=self._keeper(opp)
            if keeper and keeper_saves(keeper.data,power):
                self._give_ball(keeper); self._add_log(f"🧤 {keeper.name} fejest véd!"); return
            self._score_goal(player,side,elapsed_sec)
        else:
            keeper=self._keeper(opp)
            if keeper: self._give_ball(keeper)

    def _do_dribble(self,player,elapsed_sec):
        side=self._poss; opp=self._op(side)
        defenders=[p for p in self._tp(opp) if not p.subbed_off and not p.is_gk]
        near=[d for d in defenders if dst(d.x,d.y,player.x,player.y)<6]
        if near:
            defender=min(near,key=lambda d:dst(d.x,d.y,player.x,player.y))
            if tackle_probability(player.data,defender.data,elapsed_sec):
                self._give_ball(defender); defender.stats["tackles"]+=1
                self._add_log(f"⚡ {defender.name} szerel!")
                if is_foul():
                    self._stats[opp]["fouls"]+=1
                    if is_red():
                        defender.stats["red"]+=1; defender.subbed_off=True
                        self.cards.append((int(elapsed_sec/300*90),defender.name,defender.side,"piros"))
                        self._add_log(f"🔴 Piros lap! {defender.name}")
                        self._give_ball(player)
                        self._set_piece=f"freekick_{'h' if side=='home' else 'a'}"
                    elif is_yellow():
                        defender.stats["yellow"]+=1
                        self.cards.append((int(elapsed_sec/300*90),defender.name,defender.side,"sárga"))
                        self._add_log(f"🟡 Sárgalap: {defender.name}")
                return
        gx=PITCH_W if player.attacks_right else 0.0
        dx=gx-player.x; dy=(PITCH_H/2-player.y)*0.3
        d=math.sqrt(dx*dx+dy*dy) or 1
        player.tx=clamp(player.x+dx/d*3,1,PITCH_W-1)
        player.ty=clamp(player.y+dy/d*2,1,PITCH_H-1)

    def _do_substitution(self,out_player,in_pdata,side):
        in_pdata["_on_field"]=True
        in_pdata["sub_entry_sec"]=self.elapsed_sec
        kit=self.home_kit if side=="home" else self.away_kit
        glow=self.home_glow if side=="home" else self.away_glow
        if side=="home": self.subs_h+=1
        else: self.subs_a+=1
        new_p=SimPlayer(in_pdata,out_player.role,out_player.hx,out_player.hy,kit,glow,side,out_player.number)
        new_p.x=out_player.x; new_p.y=out_player.y
        if out_player.has_ball:
            out_player.has_ball=False
            self._carrier=new_p; self.ball.attach(new_p)
        out_player.subbed_off=True
        lst=self.hp if side=="home" else self.ap
        idx=lst.index(out_player); lst[idx]=new_p
        minute=int(self.elapsed_sec/300*90)
        self._sub_log.append((minute,out_player.name,in_pdata.get("name","?"),side))
        self._add_log(f"🔄 {minute}' {out_player.name} → {in_pdata.get('name','?').split()[-1]}")

    def _score_goal(self,player,side,elapsed_sec):
        minute=int(elapsed_sec/300*90)
        if side=="home": self.sh+=1
        else: self.sa+=1
        player.stats["goals"]+=1
        self._goal_log.append((minute,player.name,side))
        self._add_log(f"⚽ {minute}' {player.name} – GÓL! [{self.sh}:{self.sa}]")
        self._goal_flash=120; self._goal_team=side
        # Replay: az elmúlt 5mp frame-jeit tároljuk
        if hasattr(self,"_frame_buffer") and len(self._frame_buffer)>0:
            self._replay_frames=list(self._frame_buffer)
            self._replay_idx=0; self._in_replay=True
        # Mindenki visszatér az alappozíciójához
        for p in self.hp+self.ap:
            p.tx=p.hx; p.ty=p.hy; p._move_t=1; p.vx=0; p.vy=0
        # Labda a középre, majd a kapott gól csapata kezd
        self.ball.snap(PITCH_W/2, PITCH_H/2)
        opp=self._op(side)
        # Gól utáni visszaállás: MINDENKI a saját térfelére, formáció pozícióba teleportál
        for p in self.hp + self.ap:
            if p.subbed_off: continue
            # Teleport az alappozícióba (saját térfélen)
            p.x = p.hx; p.y = p.hy
            # Ha valahogy a másik oldalra esett az hx, korrigáljuk
            if p.attacks_right:
                p.x = clamp(p.hx, 0.5, PITCH_W/2 - 0.5)
            else:
                p.x = clamp(p.hx, PITCH_W/2 + 0.5, PITCH_W - 0.5)
            p.y = clamp(p.hy, 0.5, PITCH_H-0.5)
            p.tx = p.x; p.ty = p.y
            p.vx = 0.0; p.vy = 0.0; p._move_t = random.randint(30,80)
        kicker=self._pick(opp,roles=["att","am","mid"])
        if not kicker: kicker=self._pick(opp)
        if kicker:
            kicker.x=PITCH_W/2 + (1.5 if kicker.attacks_right else -1.5)
            kicker.y=PITCH_H/2
            kicker.tx=kicker.x; kicker.ty=kicker.y
            self._give_ball(kicker)
        self._kickoff_phase=True; self._kickoff_done=False
        self._action_cd=180  # 3mp kickoff szünet

    def _handle_set_piece(self,elapsed_sec):
        if not self._set_piece: return
        self._set_piece_t-=1
        if self._set_piece_t>0: return
        sp=self._set_piece; self._set_piece=None
        side="home" if sp.endswith("_h") else "away"
        kind=sp[:-2]  # "corner","freekick","goalkick","throwin","penalty"
        if kind=="corner":      self._do_corner(side,elapsed_sec)
        elif kind=="corner_run":
            if hasattr(self,"_corner_run_data") and self._corner_run_data:
                taker,tx,ty,arc_h,cb,cside = self._corner_run_data
                self._corner_run_data=None
                # Taker pontosan a labdánál (szögletponton)
                taker.x = self.ball.x; taker.y = self.ball.y
                frames=self._pass_frames(taker.x,taker.y,tx,ty)+18
                self._lose_ball()
                self.ball.release_arc(tx,ty,arc_h,frames,callback=cb)
                self._add_log(f"⚡ Szöglet beadás!")
        elif kind=="freekick":   self._do_freekick(side,elapsed_sec)
        elif kind=="goalkick":   self._do_goalkick(side,elapsed_sec)
        elif kind=="goalkick_run":
            # Nekifutás lejárt → kapus kirúg
            if hasattr(self, "_goalkick_data") and self._goalkick_data:
                keeper, tx, ty, arc_h, frames, cb = self._goalkick_data
                self._goalkick_data = None
                self._lose_ball()
                self.ball.release_arc(tx, ty, arc_h, frames, callback=cb)
                self._add_log(f"🦶 Kirúgás!")
        elif kind=="throwin":    self._do_throwin(side,elapsed_sec)
        elif kind=="penalty":    self._do_penalty(side,elapsed_sec)

    def _do_corner(self,side,elapsed_sec):
        """Szöglet: MINDEN játékos a 16-osba, majd beadás."""
        opp = self._op(side)
        # A szögletpont PONTOS X koordinátája: ahol a labda kiment
        # Ha kiment a bal alapvonalon (x≈0): szöglet az x=0 sarokban
        # Ha kiment a jobb alapvonalon (x≈PITCH_W): szöglet az x=PITCH_W sarokban
        # A taker és a beadás iránya ebből következik
        if self.ball.x < PITCH_W/2:
            gx = 0.0   # bal sarok
            goal_x_atk = 0.0   # a bal kapunál szöglet → az a kapu előtt lesz a jatékos tömeg
        else:
            gx = PITCH_W   # jobb sarok
            goal_x_atk = PITCH_W
        sy = 0.5 if self.ball.y < PITCH_H/2 else PITCH_H-0.5
        # Szögletet végző: taker a szögletponthoz
        taker = self._pick(side, roles=["am","mid","def"])
        if not taker: taker = self._pick(side)
        if not taker: return
        taker.x = gx; taker.y = sy
        self._give_ball(taker)
        self._add_log(f"🚩 Szöglet – {taker.name}!")
        # Beadás iránya: a kapu ELÉ, ahol a szöglet elvégzésre kerül
        # box_near_x: a 16-os vonal X koordinátája az adott kapunál
        box_near_x = (goal_x_atk + BOX_DEPTH) if goal_x_atk < PITCH_W/2 else (goal_x_atk - BOX_DEPTH)
        sign = 1 if goal_x_atk > PITCH_W/2 else -1   # +1=jobb kapu, -1=bal kapu
        for p in self._tp(side):
            if p is taker or p.is_gk or p.subbed_off: continue
            if p.role in ("def","dm"):
                p.x = clamp(box_near_x - sign*2, 0.5, PITCH_W-0.5)
                p.y = PITCH_H/2 + random.uniform(-8,8)
            else:
                p.x = clamp(goal_x_atk - sign*(6+random.uniform(0,8)), 0.5, PITCH_W-0.5)
                p.y = clamp(PITCH_H/2 + random.uniform(-GOAL_WIDTH*1.5, GOAL_WIDTH*1.5),
                            BOX_Y_MIN+1, BOX_Y_MAX-1)
            p.vx=0; p.vy=0; p.tx=p.x; p.ty=p.y
        for p in self._tp(opp):
            if p.is_gk or p.subbed_off: continue
            if p.role in ("att","am"):
                p.x = clamp(box_near_x + sign*3, 0.5, PITCH_W-0.5)
                p.y = PITCH_H/2 + random.uniform(-10,10)
            else:
                p.x = clamp(goal_x_atk - sign*(3+random.uniform(0,10)), 0.5, PITCH_W-0.5)
                p.y = clamp(PITCH_H/2 + random.uniform(-GOAL_WIDTH*2, GOAL_WIDTH*2),
                            BOX_Y_MIN, BOX_Y_MAX)
            p.vx=0; p.vy=0; p.tx=p.x; p.ty=p.y
        tx = clamp(goal_x_atk - sign*(5+random.uniform(0,6)), 1, PITCH_W-1)
        ty = PITCH_H/2 + random.uniform(-GOAL_WIDTH, GOAL_WIDTH)
        # Szöglet: nekifutás szimulálása (set_piece_t = nekifutás idő)
        keeper=self._keeper(opp)
        att_pool=[p for p in self._tp(side) if not p.is_gk and not p.subbed_off and p is not taker]
        # Szöglet közben a játékosok MARADNAK a 16-oson belül (tx ne változzon)
        for p2 in self._tp(side)+self._tp(opp):
            if not p2.is_gk and not p2.subbed_off and p2 is not taker:
                p2._move_t = 9999  # ne változzon a célpont amíg a labda repül
        def on_corner_arrive():
            # Visszaengedjük a mozgást
            for p2 in self._tp(side)+self._tp(opp):
                p2._move_t = 0
            if keeper and sk(keeper.data,"terulet_uralma",10)>=13 and random.random()<0.30:
                self._give_ball(keeper); self._add_log(f"🧤 {keeper.name} kijön!"); return
            if att_pool:
                hp=random.choice(att_pool)
                fejes=sk(hp.data,"fejes",10)
                if random.random()<(0.30+(fejes-10)/20*0.28):
                    self._do_header(hp,side,elapsed_sec); return
            if keeper: self._give_ball(keeper)
        # Nekifutás (1.5mp), majd beadás
        self._corner_run_data=(taker, tx, ty, 42, on_corner_arrive, side)
        self._set_piece="corner_run"; self._set_piece_t=90

    def _do_throwin(self,side,elapsed_sec):
        """Bedobás: a Távoldobás képesség alapján, kézből passzol."""
        takers_name = self._sp_takers.get("throwin","")
        taker = None
        if takers_name:
            taker = next((p for p in self._tp(side) if not p.subbed_off and p.name in takers_name), None)
        if not taker: taker = self._pick(side, roles=["def","dm","mid"])
        if not taker: return
        # Odamegy a dobás helyére (labda aktuális pozíciója az oldalvonalon)
        throw_x = clamp(self.ball.x, 1.0, PITCH_W-1.0)
        throw_y = 0.5 if self.ball.y < PITCH_H/2 else PITCH_H-0.5
        taker.x=throw_x; taker.y=throw_y
        self._give_ball(taker)
        self._add_log(f"🤾 Bedobás – {taker.name}")
        # Célpont: csapattárs a bedobás helyéhez közel
        target=self._pick(side, exclude=taker)
        if not target: return
        tavdob=sk(taker.data,"tavoldobas",10)
        max_dist=10+tavdob/20*25   # 10-35m
        d_to_t=dst(taker.x,taker.y,target.x,target.y)
        if d_to_t>max_dist:
            target=min([p for p in self._tp(side) if p is not taker and not p.subbed_off],
                       key=lambda p:dst(taker.x,taker.y,p.x,p.y))
        arc_h=8; frames=self._pass_frames(taker.x,taker.y,target.x,target.y)
        def on_arrive(t=target):
            if first_touch_success(t.data): self._give_ball(t)
            else: self._lose_ball()
        self._lose_ball()
        self.ball.release_arc(target.x,target.y,arc_h,frames,callback=on_arrive)

    def _do_goalkick(self,side,elapsed_sec):
        """
        Kirúgás animáció:
        1. Kapus odamegy a labdához (kaputól 5m, labda y közelébe)
        2. Leállítja a labdát (~1mp várakozás)
        3. Nekifut és kirúgja (ívelt animáció)
        """
        keeper=self._keeper(side)
        if not keeper:
            taker=self._pick(side)
            if taker: self._give_ball(taker); self._do_freekick(side,elapsed_sec)
            return
        # Kirúgás pozíciója: a labda által elhagyott kapu Y koordinátájához közel
        # Kapu vonal x: kapus attacks_right → kapu x=0, else x=PITCH_W
        goal_x = 0.0 if keeper.attacks_right else PITCH_W
        kick_y = clamp(self.ball.y, GOAL_Y_MIN - 3.0, GOAL_Y_MAX + 3.0)
        kick_x = (goal_x + 5.0) if keeper.attacks_right else (goal_x - 5.0)
        kick_x = clamp(kick_x, 1.0, PITCH_W-1.0)
        # Kapus teleportál a kirúgás helyére (látható pozíció)
        keeper.x = kick_x; keeper.y = kick_y
        self.ball.snap(kick_x, kick_y)
        self._give_ball(keeper)
        self._add_log(f"🦶 {keeper.name} kirúgást végez...")
        # Rugas skill: max távolság
        rugas_skill = sk(keeper.data, "rugas", 10)
        max_dist = 10.0 + rugas_skill / 20.0 * 65.0
        # Technika: pontosság
        tech = sk(keeper.data, "technika", 10)
        acc  = 0.5 + tech / 20.0 * 0.40
        # Célpont
        fwd = self._pick_fwd(side)
        if not fwd:
            fwd = self._pick(side, roles=["mid","am"])
        if fwd:
            d_fwd = dst(kick_x, kick_y, fwd.x, fwd.y)
            if d_fwd > max_dist:
                dx = fwd.x-kick_x; dy = fwd.y-kick_y
                nm = math.sqrt(dx*dx+dy*dy) or 1
                tx = kick_x + dx/nm * max_dist
                ty = kick_y + dy/nm * max_dist
            else:
                tx, ty = fwd.x, fwd.y
            tx, ty = apply_inaccuracy(tx, ty, kick_x, kick_y, acc)
            tx = clamp(tx, 1.0, PITCH_W-1.0)
            ty = clamp(ty, 1.0, PITCH_H-1.0)
            arc_h  = 30 + max_dist * 0.35
            # Hosszú, lassú animáció → látható nekifutás érzete
            frames = int(clamp(dst(kick_x,kick_y,tx,ty)/PITCH_W*420, 70, 180))
            def on_arrive(t=fwd, rx=tx, ry=ty):
                if dst(t.x,t.y,rx,ry) < 6 and first_touch_success(t.data):
                    self._give_ball(t)
                else:
                    self._lose_ball(); self.ball.snap(rx, ry)
            # Várakozás (nekifutás szimulálása): set_piece_t-vel
            self._goalkick_data = (keeper, tx, ty, arc_h, frames, on_arrive)
            self._set_piece = "goalkick_run"
            self._set_piece_t = 45   # ~0.75mp nekifutás
        else:
            self._do_pass(keeper, elapsed_sec)

    def _do_freekick(self,side,elapsed_sec):
        # A rögzített helyzetek menüben megadott szabadrúgás lövő
        sp_name=self._sp_takers.get("freekick","")
        taker=None
        if sp_name:
            taker=next((p for p in self._tp(side) if not p.subbed_off
                        and p.name in sp_name), None)
        if not taker: taker=self._pick(side,roles=["am","mid"])
        if not taker: taker=self._pick(side)
        if not taker: return
        self._give_ball(taker)
        dist=self._dist_to_goal(taker)
        if 16 <= dist <= 35:
            # Sorfal: 3-5 ellenfél 5m-re a labdától a kapu irányában
            opp=self._op(side)
            wall_players=[p for p in self._tp(opp)
                          if not p.subbed_off and not p.is_gk][:random.randint(3,5)]
            gx=PITCH_W if taker.attacks_right else 0.0
            dx=gx-taker.x; dy=PITCH_H/2-taker.y
            d=math.sqrt(dx*dx+dy*dy) or 1
            for i,wp in enumerate(wall_players):
                wp.x=clamp(taker.x+dx/d*5+(i-2)*1.5, 1, PITCH_W-1)
                wp.y=clamp(taker.y+dy/d*5, 1, PITCH_H-1)
                wp.tx=wp.x; wp.ty=wp.y; wp.vx=0; wp.vy=0
            self._add_log(f"🎯 Szabadrúgás ({dist:.0f}m) – {taker.name}")
            self._do_shoot(taker,elapsed_sec)
        elif dist > 35:
            # Beadás a kapu elé
            self._add_log(f"🎯 Szabadrúgás beadás ({dist:.0f}m)")
            self._do_cross(taker,elapsed_sec)
        else:
            self._do_shoot(taker,elapsed_sec)

    def _do_penalty(self,side,elapsed_sec):
        taker=self._pick(side,roles=["att","am","mid"])
        if not taker: return
        self._give_ball(taker)
        opp=self._op(side); keeper=self._keeper(opp)
        bunt=sk(taker.data,"befejezes",10)
        prob=0.70+(bunt-10)/20*0.20
        if keeper: prob-=sk(keeper.data,"reflexek",10)/20*0.10
        if random.random()<prob: self._score_goal(taker,side,elapsed_sec)
        else:
            if keeper: self._give_ball(keeper)
            self._add_log("🧤 Büntető kivédve!")

    def _point_to_line_dist(self,px,py,ax,ay,bx,by):
        dx=bx-ax; dy=by-ay; d=math.sqrt(dx*dx+dy*dy)
        if d<0.01: return dst(px,py,ax,ay)
        return abs(dx*(ay-py)-(ax-px)*dy)/d

    def _tackle_attempt(self,attacker,elapsed_sec):
        opp=self._op(self._poss)
        defenders=[p for p in self._tp(opp) if not p.subbed_off and not p.is_gk]
        near=[d for d in defenders if dst(d.x,d.y,attacker.x,attacker.y)<1.5]
        if not near: return
        defender=min(near,key=lambda d:dst(d.x,d.y,attacker.x,attacker.y))
        success=tackle_probability(attacker.data,defender.data,elapsed_sec)
        if success:
            # 12% eséllyel szabálytalanság
            foul_chance=0.12
            if random.random()<foul_chance:
                self._stats[opp]["fouls"]+=1
                self._add_log(f"🟡 Szabálytalanság – {defender.name}!")
                if is_yellow():
                    defender.stats["yellow"]+=1
                    self.cards.append((int(elapsed_sec/MATCH_SECS*90),defender.name,defender.side,"sárga"))
                    self._add_log(f"🟡 Sárgalap: {defender.name}")
                # Szabadrúgás a sértett csapatnak
                fk_side=self._poss
                self.ball.snap(clamp(attacker.x,1,PITCH_W-1),clamp(attacker.y,1,PITCH_H-1))
                self._lose_ball()
                self._set_piece=f"freekick_{'h' if fk_side=='home' else 'a'}"
                self._set_piece_t=60
                return
            self._give_ball(defender); defender.stats["tackles"]+=1
            self._add_log(f"⚡ {defender.name} szerel!")

    def _decide(self,player,elapsed_sec):
        if player.is_gk: self._gk_decide(player,elapsed_sec); return
        if self._should_shoot(player): self._do_shoot(player,elapsed_sec); return
        # SZÉLSŐ: oldalon fut és beadást kísért meg
        if self._should_wide_run(player):  self._do_wide_run(player,elapsed_sec); return
        if self._should_cross(player):     self._do_cross(player,elapsed_sec); return
        # LABDAVEZETÉS ha szabad az út
        if self._is_open_space(player):    self._do_carry(player,elapsed_sec); return
        cselez=sk(player.data,"cselez",10)
        if random.random()<(0.15+(cselez-10)/20*0.15): self._do_dribble(player,elapsed_sec)
        else: self._do_pass(player,elapsed_sec)

    def _should_wide_run(self,player):
        """Szélső futás: szélső középpályások és szélső csatárok oldalvonal mentén."""
        if player.is_gk: return False
        if player.role not in ("att","am","mid"): return False
        is_wide = player.y < PITCH_H*0.32 or player.y > PITCH_H*0.68
        if not is_wide: return False
        if player.attacks_right:
            in_good_pos = PITCH_W*0.38 < player.x < PITCH_W*0.80
        else:
            in_good_pos = PITCH_W*0.20 < player.x < PITCH_W*0.62
        if not in_good_pos: return False
        bead=sk(player.data,"beadas",10); gyors=sk(player.data,"gyorsasag",10)
        return random.random()<(0.28+(bead+gyors-20)/40*0.22)

    def _do_wide_run(self,player,elapsed_sec):
        """Szélső: oldalvonal MENTÉN az alapvonalhoz, majd beadás a 16-osba."""
        side=self._poss
        # Cél: alapvonal közelében, de az oldalvonal mentén (y marad)
        gx = PITCH_W*0.944 if player.attacks_right else PITCH_W*0.056  # ~5m az alapvonaltól
        gy = clamp(player.y, 1.0, PITCH_H-1.0)  # Y nem változik (oldalvonal mentén)
        player.tx=gx; player.ty=gy; player._move_t=1
        player._speed_mode=1.0   # sprint
        pass  # szélen fut - nincs log
        # Ha már az alapvonal közelében van: azonnal beadás
        dist_to_base = abs(player.x - gx)
        if dist_to_base < 8:
            self._do_cross(player, elapsed_sec)
            return
        # Különben várunk amíg odaér
        self._action_cd = FPS*2

    def _is_open_space(self,player):
        """Van-e szabad terület előtte (senki nincs 8m-en belül előtte)?"""
        if player.is_gk: return False
        opp=self._op(self._poss)
        defenders=[p for p in self._tp(opp) if not p.subbed_off]
        gx=PITCH_W if player.attacks_right else 0.0
        # Megnézzük az előre vezető pályaszakaszt
        for d in defenders:
            ahead = (d.x>player.x-3) if player.attacks_right else (d.x<player.x+3)
            if ahead and dst(d.x,d.y,player.x,player.y)<6: return False
        # Csak ha nem vagyunk túl messze a kaputól
        dist=dst(player.x,player.y,gx,PITCH_H/2)
        return dist>15

    def _do_carry(self,player,elapsed_sec):
        """Labdavezetés: fut a labdával előre."""
        side=self._poss
        gx=PITCH_W*0.85 if player.attacks_right else PITCH_W*0.15
        dx=gx-player.x; dy=(PITCH_H/2-player.y)*0.15
        d=math.sqrt(dx*dx+dy*dy) or 1
        dist=7+random.uniform(0,6)
        player.tx=clamp(player.x+dx/d*dist,1,PITCH_W-1)
        player.ty=clamp(player.y+dy/d*dist,1,PITCH_H-1)
        player._move_t=1
        self._action_cd=random.randint(30,55)
        pass  # labdavezetés - nincs log

    def _gk_decide(self,keeper,elapsed_sec):
        # Kapus vár 2-3 mp-et mielőtt dönt
        if not hasattr(keeper,"_gk_hold_t"):
            keeper._gk_hold_t=random.randint(5,8)
        keeper._gk_hold_t-=1
        if keeper._gk_hold_t>0:
            return  # még vár
        keeper._gk_hold_t=random.randint(5,8)  # reset
        r=random.random()
        if r<0.35: self._do_pass(keeper,elapsed_sec)
        elif r<0.75:
            fwd=self._pick_fwd(self._poss)
            if fwd:
                arc_h=38; frames=self._pass_frames(keeper.x,keeper.y,fwd.x,fwd.y)+5
                def on_arrive(t=fwd):
                    if first_touch_success(t.data): self._give_ball(t)
                    else: self._lose_ball()
                self._lose_ball()
                self.ball.release_arc(fwd.x,fwd.y,arc_h,frames,callback=on_arrive)
                self._add_log(f"🦶 {keeper.name} kirúg.")
        else: self._do_pass(keeper,elapsed_sec)

    def _apply_team_pressure(self):
        """
        Csapatnyomás: a labda pozíciója alapján az egész csapat tolódik.
        Minden frame-ben finoman befolyásolja a célpontot (tx/ty).
        """
        bx = self.ball.x
        atk_side = self._poss
        def_side = self._op(atk_side)
        if atk_side=="home":
            pressure = bx / PITCH_W
        else:
            pressure = 1.0 - bx / PITCH_W
        pressure = clamp(pressure, 0.05, 0.95)
        shift = (pressure - 0.5) * 55.0  # ±27.5m max

        for p in self._tp(atk_side):
            if p.subbed_off or p.is_gk or p.has_ball: continue
            # Célpont: alappozíció + shift (előre tolva)
            target_x = clamp(p.hx + (shift if atk_side=="home" else -shift), 0.5, PITCH_W-0.5)
            # Csatárok aktívan a kapu elé futnak
            if p.role in ("att","am") and pressure > 0.45:
                if atk_side=="home":
                    target_x = clamp(PITCH_W - BOX_DEPTH*0.8, 0.5, PITCH_W-0.5)
                else:
                    target_x = clamp(BOX_DEPTH*0.8, 0.5, PITCH_W-0.5)
            # Csak ha a célpont változott sokat: frissítjük
            if abs(target_x - p.tx) > 3:
                p.tx = target_x; p._move_t = min(p._move_t, 60)

        for p in self._tp(def_side):
            if p.subbed_off or p.is_gk: continue
            target_x = clamp(p.hx - (shift if def_side=="home" else -shift)*0.65, 0.5, PITCH_W-0.5)
            # Védők: ne húzódjanak a 16-oson belülre
            if p.role == "def":
                if def_side=="home": target_x = max(target_x, PITCH_W*0.183)
                else: target_x = min(target_x, PITCH_W*(1-0.183))
            if abs(target_x - p.tx) > 3:
                p.tx = target_x; p._move_t = min(p._move_t, 60)
            # Szélső hátvéd: ha be van szorítva (pressure>0.60) → középre húzódik
            if p.role == "def" and pressure > 0.60:
                is_wide = p.hy < PITCH_H*0.30 or p.hy > PITCH_H*0.70
                if is_wide:
                    # Y irányban a kapu közepe felé húzódik
                    center_pull = 0.35 + (pressure-0.60)*0.8   # 0.35–0.60
                    target_y = PITCH_H/2 + (p.hy-PITCH_H/2)*(1.0-center_pull)
                    if abs(target_y - p.ty) > 2:
                        p.ty = clamp(target_y, 2, PITCH_H-2)
                        p._move_t = min(p._move_t, 50)

    def _check_offside_positions(self):
        """Csatárok ne legyenek lesben: ne legyenek közelebb az ellenfél kapujához
        mint az utolsó előtti védő."""
        for atk_side in ("home","away"):
            def_side = self._op(atk_side)
            attackers = [p for p in self._tp(atk_side)
                         if not p.subbed_off and p.role in ("att","am") and not p.has_ball]
            defenders = [p for p in self._tp(def_side) if not p.subbed_off]
            if not defenders or not attackers: continue
            # Utolsó előtti védő pozíciója
            if atk_side == "home":  # home jobbra támad (1.félidő)
                # Legmesszebb jobb oldali védő (kisebb x = kevésbé jobbra)
                def_xs = sorted([p.x for p in defenders])
                if len(def_xs) < 2: continue
                offside_line = def_xs[-2]  # utolsó előtti = 2. jobbra legtávolabbi
                for att in attackers:
                    if att.x > offside_line:
                        att.tx = max(att.tx, offside_line - 1.0)
                        att._move_t = min(att._move_t, 30)
            else:  # away balra támad
                def_xs = sorted([p.x for p in defenders], reverse=True)
                if len(def_xs) < 2: continue
                offside_line = def_xs[-2]
                for att in attackers:
                    if att.x < offside_line:
                        att.tx = min(att.tx, offside_line + 1.0)
                        att._move_t = min(att._move_t, 30)

    def _ai_substitutions(self):
        """AI csapat automatikusan cserél fáradt játékosokat."""
        for side in ("home","away"):
            if side == self._player_side: continue  # emberi csapat nem itt cserél
            used = self.subs_h if side=="home" else self.subs_a
            if used >= 5: continue
            bench = self.bench_h if side=="home" else self.bench_a
            available = [p for p in bench if not p.get("_on_field")]
            if not available: continue
            field = self.hp if side=="home" else self.ap
            # Legfáradtabb nem-kapus játékos keresése
            tired = [p for p in field if not p.subbed_off and not p.is_gk]
            if not tired: continue
            most_tired = min(tired, key=lambda p: p.phys_pct(self.elapsed_sec))
            if most_tired.phys_pct(self.elapsed_sec) < 65:
                # Cserél be egy kispadost
                in_p = random.choice(available)
                self._do_substitution(most_tired, in_p, side)

    def _add_log(self,msg):
        self.log.insert(0,msg)
        if len(self.log)>8: self.log.pop()

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self):
        if self.paused or self.done: return
        # Replay mód: lassított visszajátszás
        if getattr(self,"_in_replay",False):
            self._do_replay_step()
            return
        for _ in range(self.speed_multiplier):
            if self.done: break
            self._tick()

    def _do_replay_step(self):
        """Lassított visszajátszás: ténylegesen visszaállítja a pozíciókat."""
        if not self._replay_frames or self._replay_idx>=len(self._replay_frames):
            self._in_replay=False; return
        snap=self._replay_frames[self._replay_idx]
        # Visszaállítás
        self.ball.x=snap["bx"]; self.ball.y=snap["by"]
        self.ball.arc_active=False; self.ball.carrier=None
        for i,p in enumerate(self.hp):
            if i<len(snap["hp"]): p.x,p.y,p.has_ball=snap["hp"][i]
        for i,p in enumerate(self.ap):
            if i<len(snap["ap"]): p.x,p.y,p.has_ball=snap["ap"][i]
        # 0.5x sebesség: minden 2. valós frame-nél lép 1-et
        if self.frame % 2 == 0:
            self._replay_idx+=1
        self.frame+=1
        if self._replay_idx>=len(self._replay_frames):
            self._in_replay=False

    def _tick(self):
        self.frame+=1
        self.elapsed_sec=self.frame/FPS
        # Frame buffer: labda + játékos pozíciók tárolása replay-hez (5mp = 300 frame)
        if not hasattr(self,"_frame_buffer"):
            from collections import deque
            self._frame_buffer=deque(maxlen=300)
            self._in_replay=False; self._replay_frames=[]; self._replay_idx=0
        # Snapshot mentése
        snap={"bx":self.ball.x,"by":self.ball.y,
              "hp":[(p.x,p.y,p.has_ball) for p in self.hp],
              "ap":[(p.x,p.y,p.has_ball) for p in self.ap]}
        self._frame_buffer.append(snap)

        # nincs félidei szünet

        # KICKOFF: mindenki a saját térfelén amíg el nem indul a labda
        if self._kickoff_phase and not self._kickoff_done:
            for p in self.hp + self.ap:
                if p.has_ball or p.subbed_off: continue
                # attacks_right=True → saját kapu bal oldal → saját félpálya x < PITCH_W/2
                # attacks_right=False → saját kapu jobb oldal → saját félpálya x > PITCH_W/2
                if p.attacks_right:
                    safe_x = clamp(p.hx, 0.5, PITCH_W/2 - 1.5)
                else:
                    safe_x = clamp(p.hx, PITCH_W/2 + 1.5, PITCH_W - 0.5)
                if abs(safe_x - p.x) > 0.5:
                    p.tx = safe_x; p.ty = clamp(p.hy, 0.5, PITCH_H-0.5)
                    p._move_t = 1

        if self.elapsed_sec>=150 and not self._halftime_flag:
            self._halftime_flag=True
            self._halftime_pause=FPS*3
            self._add_log(f"⏱ Félidő! [{self.sh}:{self.sa}]")
            # Térfélcsere: tükrözzük a formáció-pozíciókat ÉS azonnal oda teleportáljuk a játékosokat
            # Félidő: home csapat eddig jobbra támadott → mostantól balra
            # away csapat eddig balra támadott → mostantól jobbra
            for p in self.hp:
                p.attacks_right = False   # 2. félidőben home balra támad
                p.hx = PITCH_W - p.hx    # tükrözött alappozíció
                p.x  = p.hx; p.y = p.hy
                p.tx = p.hx; p.ty = p.hy
                p.vx = 0.0; p.vy = 0.0
                p._move_t = random.randint(60,120)
            for p in self.ap:
                p.attacks_right = True    # 2. félidőben away jobbra támad
                p.hx = PITCH_W - p.hx
                p.x  = p.hx; p.y = p.hy
                p.tx = p.hx; p.ty = p.hy
                p.vx = 0.0; p.vy = 0.0
                p._move_t = random.randint(60,120)
            self.ball.snap(PITCH_W/2, PITCH_H/2)
            self._lose_ball()
            # 2. félidő: away kezd, mindenki saját térfelén
            for p in self.hp:
                p.tx = clamp(p.hx, PITCH_W/2+0.5, PITCH_W-0.5)  # 2.félidőben home jobbra
                p.ty = p.hy; p._move_t = 1
            for p in self.ap:
                p.tx = clamp(p.hx, 0.5, PITCH_W/2-0.5)  # away balra
                p.ty = p.hy; p._move_t = 1
            kicker = self._pick("away", roles=["att","am","mid"])
            if not kicker: kicker = self._pick("away")
            if kicker:
                kicker.x = PITCH_W/2 + (1.5 if kicker.attacks_right else -1.5)
                kicker.y = PITCH_H/2
                kicker.tx = kicker.x; kicker.ty = kicker.y
                self._give_ball(kicker)
            self._kickoff_phase=True; self._kickoff_done=False

        if self.elapsed_sec>=MATCH_SECS:
            self.done=True; self._lose_ball()
            self._add_log(f"⏱ Meccs vége! [{self.sh}:{self.sa}]"); return

        if self._goal_flash>0: self._goal_flash-=1

        self.ball.update()

        # Alapvonal kilépés: szöglet vagy kirúgás
        if self.ball._out_base and not self.ball.arc_active and not self._carrier:
            out_side = self.ball._out_base   # "left" vagy "right"
            out_y    = self.ball._out_y
            self.ball._out_base = None
            # Melyik csapat kapusa védi azt az oldalt?
            # left (x=0): home kapusa ha home attacks_right=True (1.félidő)
            #                          VAGY away kapusa ha away attacks_right=False
            # Egyszerűsítve: megnézzük melyik kapusnak van az adott oldalon a kapu
            home_gk = self._keeper("home")
            away_gk = self._keeper("away")
            # Home kapuja: attacks_right=True → x=0 bal oldal, False → x=PITCH_W jobb oldal
            home_defends_left  = (home_gk and home_gk.attacks_right)   # 1.félidő home
            home_defends_right = (home_gk and not home_gk.attacks_right) # 2.félidő home
            if out_side == "left":
                # Left alapvonal = x≈0 oldal
                if home_defends_left:
                    # Home kapuja → ha home csapata rúgta → kirúgás, ha away → szöglet
                    if self._poss == "home":
                        self._set_piece = "goalkick_h"
                        self._add_log("🦶 Kirúgás (hazai)")
                    else:
                        self._set_piece = "corner_a"
                        self._stats["away"]["corners"]+=1
                        self._add_log("🚩 Szöglet (vendég)!")
                else:
                    # Away kapuja a bal oldalon (2.félidő)
                    if self._poss == "away":
                        self._set_piece = "goalkick_a"
                        self._add_log("🦶 Kirúgás (vendég)")
                    else:
                        self._set_piece = "corner_h"
                        self._stats["home"]["corners"]+=1
                        self._add_log("🚩 Szöglet (hazai)!")
            else:  # right = x≈PITCH_W oldal
                if home_defends_right:
                    # Home kapuja a jobb oldalon (2.félidő)
                    if self._poss == "home":
                        self._set_piece = "goalkick_h"
                        self._add_log("🦶 Kirúgás (hazai)")
                    else:
                        self._set_piece = "corner_a"
                        self._stats["away"]["corners"]+=1
                        self._add_log("🚩 Szöglet (vendég)!")
                else:
                    # Away kapuja a jobb oldalon (1.félidő)
                    if self._poss == "away":
                        self._set_piece = "goalkick_a"
                        self._add_log("🦶 Kirúgás (vendég)")
                    else:
                        self._set_piece = "corner_h"
                        self._stats["home"]["corners"]+=1
                        self._add_log("🚩 Szöglet (hazai)!")
            self._set_piece_t = 70
            self._lose_ball()
            self.ball.snap(clamp(self.ball.x,1,PITCH_W-1), clamp(out_y,1,PITCH_H-1))

        # Bedobás: labda elhagyta az oldalvonalat
        if self.ball._out_side and not self.ball.arc_active and not self._carrier:
            out_x = self.ball._out_x
            self.ball._out_side = None
            # Melyik csapaté volt utoljára? → ellenfele dobja be
            opp = self._op(self._poss)
            self._lose_ball()
            self.ball.snap(clamp(out_x,1,PITCH_W-1),
                          0.5 if self.ball.y<PITCH_H/2 else PITCH_H-0.5)
            self._set_piece = f"throwin_{'h' if opp=='home' else 'a'}"
            self._set_piece_t = 45
            self._add_log("🤾 Bedobás!")

        # Labda nélküli állapot: legközelebbi fut érte
        if not self._carrier and not self.ball.arc_active and self.ball.speed()<0.15:
            nh=self._pick_nearest("home",self.ball.x,self.ball.y)
            na=self._pick_nearest("away",self.ball.x,self.ball.y)
            if nh and na:
                dh=dst(nh.x,nh.y,self.ball.x,self.ball.y)
                da=dst(na.x,na.y,self.ball.x,self.ball.y)
                winner=nh if dh<da else na
                mn=dh if dh<da else da
                if mn<3.5: self._give_ball(winner)
                else:
                    for runner in [nh,na]:
                        if runner: runner.tx=self.ball.x; runner.ty=self.ball.y; runner._move_t=1

        # Csapatnyomás: labdabirtokos csapat előre tolódik, védekezők visszahúzódnak
        self._apply_team_pressure()
        for p in self.hp+self.ap:
            p.update_movement(self.ball.x,self.ball.y,self.elapsed_sec)
        self.ref.update(self.ball.x,self.ball.y)

        if self._set_piece: self._handle_set_piece(self.elapsed_sec); return

        self._action_cd-=1
        if self._action_cd<=0 and self._carrier and not self.ball.arc_active:
            self._action_cd=random.randint(15,35)
            self._decide(self._carrier,self.elapsed_sec)

        # Ha nincs presser, a carrier teljes sebességgel fut
        if self._carrier and not self.ball.arc_active:
            self._carrier._carry_spd = getattr(self._carrier, '_carry_spd', 1.0)

        # Minden frame-ben: legközelebbi ellenfél (10m-en belül) nyomja a labdabirtokost
        if self._carrier and not self.ball.arc_active:
            opp = self._op(self._poss)
            defenders = [p for p in self._tp(opp) if not p.subbed_off and not p.is_gk]
            near = [d for d in defenders if dst(d.x,d.y,self._carrier.x,self._carrier.y)<12.0]
            if near:
                presser = min(near, key=lambda d: dst(d.x,d.y,self._carrier.x,self._carrier.y))
                presser.tx = self._carrier.x; presser.ty = self._carrier.y; presser._move_t=1
                presser._speed_mode = 1.0   # sprint a labdabirtokos felé
                d_press = dst(presser.x,presser.y,self._carrier.x,self._carrier.y)
                if d_press < 3.0:
                    self._carrier._carry_spd = max(0.2, d_press/3.0)
                else:
                    self._carrier._carry_spd = 1.0
                if d_press < 1.5:
                    if random.random()<0.08:   # ~4.8/mp esély
                        self._tackle_attempt(self._carrier,self.elapsed_sec)

        # Védők AKTÍVAN fogják a csatárokat (labdabirtokostól függetlenül)
        if not self.ball.arc_active:
            for side in ("home","away"):
                opp = self._op(side)
                defenders = [p for p in self._tp(side)
                             if not p.subbed_off and p.role in ("def","dm") and not p.is_gk]
                attackers = [p for p in self._tp(opp)
                             if not p.subbed_off and p.role in ("att","am")]
                for att in attackers:
                    close_defs=[d for d in defenders if dst(d.x,d.y,att.x,att.y)<14.0]
                    if close_defs:
                        marker=min(close_defs,key=lambda d:dst(d.x,d.y,att.x,att.y))
                        d_to_att=dst(marker.x,marker.y,att.x,att.y)
                        if d_to_att<10.0:
                            # Közvetlenül a csatár felé megy, nem mellé
                            marker.tx=att.x; marker.ty=att.y
                            marker._move_t=1; marker._speed_mode=1.0

        if self._carrier:
            self._stats[self._poss]["possession"]+=1

        # LES ELLENŐRZÉS: csatárok ne legyenek mögötte az utolsó védőnek
        if not self._kickoff_phase:
            self._check_offside_positions()

        # AI cserék: ha a meccs 2/3-ánál járunk, az AI is cserélhet
        if self.frame % (FPS*60) == 0 and self.elapsed_sec > MATCH_SECS*0.50:
            self._ai_substitutions()

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self,surf):
        surf.fill(C_BG)
        draw_pitch(surf)
        if self._goal_flash>0:
            col=self.home_kit if self._goal_team=="home" else self.away_kit
            fls=pygame.Surface((GAME_W,GAME_H),pygame.SRCALPHA)
            fls.fill((*col,min(30,self._goal_flash*2)))
            surf.blit(fls,(0,0))
        for p in self.ap+self.hp: p.draw(surf,self.elapsed_sec)
        self.ref.draw(surf)
        self.ball.draw(surf)
        # nincs félidő overlay
        if self.done:
            bg=pygame.Surface((280,56),pygame.SRCALPHA); bg.fill((0,0,0,210))
            surf.blit(bg,(GAME_W//2-140,PITCH.centery-28))
            dtc(surf,"MECCS VÉGE",28,C_ACCENT,GAME_W//2,PITCH.centery,bold=True)
        # REPLAY overlay
        if getattr(self,"_in_replay",False):
            bg=pygame.Surface((220,40),pygame.SRCALPHA); bg.fill((180,0,0,200))
            surf.blit(bg,(GAME_W//2-110,PITCH.y+8))
            dtc(surf,"● VISSZAJÁTSZÁS",14,C_WHITE,GAME_W//2,PITCH.y+28,bold=True)
        # KICKOFF overlay
        if getattr(self,"_kickoff_phase",False) and not getattr(self,"_kickoff_done",True):
            bg=pygame.Surface((200,36),pygame.SRCALPHA); bg.fill((0,0,0,160))
            surf.blit(bg,(GAME_W//2-100,PITCH.y+8))
            dtc(surf,"KÖZÉPKEZDÉS",13,C_ACC2,GAME_W//2,PITCH.y+26,bold=True)
        self._draw_hud(surf)
        self._draw_controls(surf)
        self._sub_panel.draw(surf)

    def _draw_hud(self,surf):
        sw=420; sh_h=50
        pygame.draw.rect(surf,C_NAVY,(GAME_W//2-sw//2,0,sw,sh_h))
        hn_s=fnt(14).render(self.hn[:16],True,self.home_kit)
        surf.blit(hn_s,(GAME_W//2-sw//2+10,8))
        an_s=fnt(14).render(self.an[:16],True,self.away_kit)
        surf.blit(an_s,(GAME_W//2+sw//2-an_s.get_width()-10,8))
        dtc(surf,f"{self.sh}  –  {self.sa}",28,C_WHITE,GAME_W//2,34,bold=True)
        minute=int(self.elapsed_sec/MATCH_SECS*90)
        pygame.draw.rect(surf,C_NAVY,(0,0,80,36))
        dtc(surf,f"{minute}'",18,C_ACC2,40,18,bold=True)
        total_p=self._stats["home"]["possession"]+self._stats["away"]["possession"]
        if total_p>0:
            h_pct=int(self._stats["home"]["possession"]/total_p*100)
            dtc(surf,f"{h_pct}% – {100-h_pct}%",11,C_SUBTXT,GAME_W//2,46)
        log_y=PITCH.bottom
        pygame.draw.rect(surf,(10,18,45),(0,log_y,GAME_W,74))
        pygame.draw.line(surf,(40,55,80),(0,log_y),(GAME_W,log_y),1)
        for i,evt in enumerate(self.log[:4]):
            col=C_ACC2 if "GÓL" in evt else C_SUBTXT
            if i==0 and "GÓL" in evt: dtc(surf,evt,15,C_ACC2,GAME_W//2,log_y+16,bold=True)
            else: dt(surf,evt,12,col,10,log_y+5+i*17)

    def _draw_controls(self,surf):
        ctrl_y=GAME_H-46
        pygame.draw.rect(surf,C_NAVY,(0,ctrl_y-2,GAME_W,50))
        pygame.draw.line(surf,(40,55,80),(0,ctrl_y-2),(GAME_W,ctrl_y-2),1)
        pb=self._pause_r
        pygame.draw.rect(surf,C_ACC2 if self.paused else C_PANEL2,pb,border_radius=6)
        dtc(surf,"▶ Folytat" if self.paused else "⏸ Szünet",12,(0,0,0) if self.paused else C_WHITE,pb.centerx,pb.centery)
        sp=self._speed_r
        sp_c={1:(50,70,50),2:(70,100,35),4:(110,130,15)}
        pygame.draw.rect(surf,sp_c.get(self.speed_multiplier,(50,70,50)),sp,border_radius=6)
        dtc(surf,{1:"▶▶ 1x",2:"▶▶ 2x",4:"▶▶ 4x"}.get(self.speed_multiplier,"▶▶ 1x"),12,C_WHITE,sp.centerx,sp.centery)
        sb=self._subs_r
        side=self._player_side
        used=self.subs_h if side=="home" else self.subs_a
        pygame.draw.rect(surf,C_RED if used>=5 else C_PANEL2,sb,border_radius=6)
        dtc(surf,f"🔄 Cserék ({used}/5)",12,C_WHITE,sb.centerx,sb.centery)

    def handle_event(self,ev,gmx,gmy):
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            if self._pause_r.collidepoint(gmx,gmy): self.paused=not self.paused; return
            if self._speed_r.collidepoint(gmx,gmy):
                self.speed_multiplier={1:2,2:4,4:1}.get(self.speed_multiplier,1); return
            if self._subs_r.collidepoint(gmx,gmy): self._sub_panel.toggle(); return
            self._sub_panel.handle_click(gmx,gmy)
        if ev.type==pygame.KEYDOWN and ev.key==pygame.K_SPACE:
            self.paused=not self.paused

    # ── Post-match ────────────────────────────────────────────────────────────
    def _draw_match_report(self,surf):
        y=98
        def sec(title,h,fn):
            nonlocal y
            pygame.draw.rect(surf,C_PANEL2,(10,y,GAME_W-20,h),border_radius=7)
            dt(surf,title,13,C_ACCENT,20,y+6); y+=24; fn(); y+=8
        def draw_goals():
            nonlocal y
            hg=[(m,n) for m,n,s in self._goal_log if s=="home"]
            ag=[(m,n) for m,n,s in self._goal_log if s=="away"]
            y0=y;y1=y
            for m,n in hg: dt(surf,f"⚽ {n} ({m}')",13,C_TEXT,20,y0); y0+=18
            for m,n in ag: dt(surf,f"⚽ {n} ({m}')",13,C_TEXT,GAME_W//2+10,y1); y1+=18
            y=max(y0,y1,y+18)
        sec("GÓLSZERZŐK",12+max(1,len(self._goal_log))*18+8,draw_goals)
        def draw_stats():
            nonlocal y
            hn_s=fnt(12).render(self.hn[:18],True,self.home_kit); surf.blit(hn_s,(20,y))
            an_s=fnt(12).render(self.an[:18],True,self.away_kit); surf.blit(an_s,(GAME_W-20-an_s.get_width(),y)); y+=18
            total_p=self._stats["home"]["possession"]+self._stats["away"]["possession"]
            h_pct=int(self._stats["home"]["possession"]/max(1,total_p)*100)
            rows=[("Lövések",self._stats["home"]["shots"],self._stats["away"]["shots"]),
                  ("Kapura",self._stats["home"]["on_target"],self._stats["away"]["on_target"]),
                  ("Szögletek",self._stats["home"]["corners"],self._stats["away"]["corners"]),
                  ("Labdabirtoklás",f"{h_pct}%",f"{100-h_pct}%"),
                  ("Passzok",self._stats["home"]["passes"],self._stats["away"]["passes"])]
            for lbl,hv,av in rows:
                dt(surf,str(hv),13,C_WHITE,20,y); dtc(surf,lbl,12,C_SUBTXT,GAME_W//2,y+2); dt(surf,str(av),13,C_WHITE,GAME_W-50,y); y+=22
        sec("STATISZTIKA",12+18+5*22+8,draw_stats)
        def draw_cards():
            nonlocal y
            if not self.cards: dt(surf,"Nincs lap.",12,C_SUBTXT,20,y); y+=18; return
            for minute,name,side,kind in self.cards:
                dt(surf,f"{'🟡' if kind=='sárga' else '🔴'} {minute}' {name}",12,C_YELLOW if kind=='sárga' else C_RED,20,y); y+=18
        sec("LAPOK",12+max(1,len(self.cards))*18+8,draw_cards)

    def _draw_other_results(self,surf):
        y=98-getattr(self,"_stats_scroll",0)
        pid=getattr(self.gs,"player_team_id",99) if self.gs else 99
        shown=0
        for res in self._round_results:
            if res.get("home_id")==pid or res.get("away_id")==pid: continue
            hg=res.get("home_goals",0); ag=res.get("away_goals",0)
            row_h=42
            if 98<=y+row_h<=GAME_H-60:
                pygame.draw.rect(surf,C_PANEL2,(10,y,GAME_W-20,row_h-3),border_radius=6)
                dtc(surf,f"{res.get('home','?')[:18]}  {hg} : {ag}  {res.get('away','?')[:18]}",14,C_TEXT,GAME_W//2,y+18)
            y+=row_h; shown+=1
        if shown==0: dtc(surf,"Nincs más meccs.",15,C_SUBTXT,GAME_W//2,GAME_H//2)

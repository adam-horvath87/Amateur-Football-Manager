import pygame, sys, os, math, random
from game_state import GameState
from data_new import (OUTFIELD_SKILLS, OUTFIELD_LABELS, OUTFIELD_SHORT,
                      GK_SKILLS, GK_LABELS, GK_SHORT,
                      FORMATIONS, FORMATION_ROWS, FORMATION_GROUPS, auto_lineup)
from training import DAYS, get_trainable_skills, get_trainable_labels

# Edzésre kiválasztható skillek és címkéik (mezőnyjátékosok)
TRAINABLE = get_trainable_skills(False)
TRAINABLE_LABELS = get_trainable_labels(False)
from match_anim import MatchAnim, draw_pitch as _dp_unused, GAME_W, GAME_H, dst

pygame.init()
GAME_SURF = pygame.Surface((GAME_W, GAME_H))
screen = None; FPS = 60

def scale_and_blit():
    ww,wh=screen.get_size(); screen.fill((8,10,18))
    scale=min(ww/GAME_W,wh/GAME_H)
    sw=int(GAME_W*scale); sh=int(GAME_H*scale)
    if sw>0 and sh>0:
        scaled=pygame.transform.scale(GAME_SURF,(sw,sh))
        screen.blit(scaled,((ww-sw)//2,(wh-sh)//2))

def game_mouse():
    mx,my=pygame.mouse.get_pos(); ww,wh=screen.get_size()
    scale=min(ww/GAME_W,wh/GAME_H)
    sw=int(GAME_W*scale); sh=int(GAME_H*scale)
    ox=(ww-sw)//2; oy=(wh-sh)//2
    return int((mx-ox)/max(0.001,scale)), int((my-oy)/max(0.001,scale))

C_BG=(10,14,22);C_PANEL=(18,24,38);C_PANEL2=(24,32,52)
C_ACCENT=(0,200,120);C_ACC2=(255,180,0);C_RED=(220,60,60)
C_TEXT=(220,230,245);C_SUBTXT=(130,150,180);C_BORDER=(40,55,80)
C_HILITE=(30,45,70);C_NAVY=(20,30,60);C_WHITE=(255,255,255);C_GOLD=(255,200,0)
SKILL_SHORT={"stamina":"Áll.","goalkeeping":"Védés","playmaking":"Játéksz.",
             "passing":"Passz","wing":"Szélső","defending":"Védekezés",
             "scoring":"Lövés","set_pieces":"Szabadr."}
SAVE_PATH=os.path.join(os.path.dirname(__file__),"savegame.json")

def _lf(sz,bold=False):
    for n in ["DejaVuSans","FreeSans","Ubuntu","Arial"]:
        try: return pygame.font.SysFont(n,sz,bold=bold)
        except: pass
    return pygame.font.SysFont(None,sz,bold=bold)
F_TITLE=_lf(44,True);F_HEAD=_lf(24,True);F_BIG=_lf(30,True)
F_MED=_lf(18);F_BODY=_lf(16);F_SMALL=_lf(14);F_TINY=_lf(12);F_NUM=_lf(10,True)

def dtc(s,t,f,c,cx,cy):
    r=f.render(str(t),True,c); s.blit(r,(cx-r.get_width()//2,cy-r.get_height()//2))
def dt(s,t,f,c,x,y):
    r=f.render(str(t),True,c); s.blit(r,(x,y)); return r.get_width()
def sc(v):
    if v>=16: return (0,220,120)
    if v>=11: return (140,210,0)
    if v>=6:  return (255,180,0)
    return (210,70,70)

SQ=5; SQ_G=1  # 5px squares, 1px gap

def draw_skill_sq(surf,x,y,sk,val,show_lbl=True,w_lbl=54):
    if show_lbl: dt(surf,SKILL_SHORT.get(sk,sk),F_TINY,C_SUBTXT,x,y+1)
    sx0=x+(w_lbl if show_lbl else 0)
    for i in range(20):
        pygame.draw.rect(surf,sc(val) if i<val else (28,36,56),(sx0+i*(SQ+SQ_G),y,SQ,SQ),border_radius=1)
    dt(surf,str(val),F_TINY,sc(val),sx0+20*(SQ+SQ_G)+3,y+1)

def draw_mini_bar(surf,x,y,sk,val,w=70):
    dt(surf,SKILL_SHORT.get(sk,sk)[:4],F_TINY,C_SUBTXT,x,y)
    bx=x+32; pygame.draw.rect(surf,(28,36,56),(bx,y+1,w,7),border_radius=2)
    if val>0: pygame.draw.rect(surf,sc(val),(bx,y+1,int(w*val/20),7),border_radius=2)
    dt(surf,str(val),F_TINY,sc(val),bx+w+3,y)

class Btn:
    def __init__(self,x,y,w,h,text,col=None,tc=None,font=None,r=7):
        self.rect=pygame.Rect(x,y,w,h); self.text=text
        self.col=col or C_ACCENT; self.tc=tc or C_BG
        self.font=font or F_BODY; self.r=r; self.hov=False
    def draw(self,surf):
        c=tuple(min(255,v+25) for v in self.col) if self.hov else self.col
        pygame.draw.rect(surf,c,self.rect,border_radius=self.r)
        pygame.draw.rect(surf,tuple(min(255,v+55) for v in self.col),self.rect,1,border_radius=self.r)
        dtc(surf,self.text,self.font,self.tc,self.rect.centerx,self.rect.centery)
    def upd(self,gx,gy): self.hov=self.rect.collidepoint(gx,gy)
    def hit(self,ev,gx,gy): return ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and self.rect.collidepoint(gx,gy)

class TxtIn:
    def __init__(self,x,y,w,h,ph=""):
        self.rect=pygame.Rect(x,y,w,h); self.text=""; self.ph=ph; self.active=False; self.ct=0
    def handle(self,ev,gx,gy):
        if ev.type==pygame.MOUSEBUTTONDOWN: self.active=self.rect.collidepoint(gx,gy)
        if self.active and ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_BACKSPACE: self.text=self.text[:-1]
            elif ev.key in(pygame.K_RETURN,pygame.K_KP_ENTER): return True
            elif len(self.text)<30: self.text+=ev.unicode
        return False
    def draw(self,surf):
        pygame.draw.rect(surf,C_PANEL2,self.rect,border_radius=7)
        pygame.draw.rect(surf,C_ACCENT if self.active else C_BORDER,self.rect,2,border_radius=7)
        txt=self.text or self.ph; col=C_TEXT if self.text else C_SUBTXT
        s=F_BODY.render(txt,True,col); surf.blit(s,(self.rect.x+10,self.rect.centery-s.get_height()//2))
        if self.active:
            self.ct+=1
            if(self.ct//30)%2==0:
                cx=self.rect.x+10+F_BODY.size(self.text)[0]
                pygame.draw.line(surf,C_ACCENT,(cx,self.rect.y+6),(cx,self.rect.bottom-6),2)

class DD:
    """Dropdown – görgethető, max 10 elem látható egyszerre."""
    MAX_VISIBLE = 10
    def __init__(self,x,y,w,h,opts,sel=0,font=None):
        self.rect=pygame.Rect(x,y,w,h); self.opts=opts; self.sel=sel
        self.font=font or F_SMALL; self.open=False; self.ih=h
        self.scroll_off=0  # első látható elem indexe
    def _ensure_sel_visible(self):
        if self.sel < self.scroll_off:
            self.scroll_off = self.sel
        elif self.sel >= self.scroll_off + self.MAX_VISIBLE:
            self.scroll_off = self.sel - self.MAX_VISIBLE + 1
    def draw_closed(self,surf):
        pygame.draw.rect(surf,C_PANEL2,self.rect,border_radius=5)
        pygame.draw.rect(surf,C_ACCENT if self.open else C_BORDER,self.rect,1,border_radius=5)
        dtc(surf,self.opts[self.sel],self.font,C_TEXT,self.rect.centerx,self.rect.centery)
        ax,ay=self.rect.right-12,self.rect.centery
        pygame.draw.polygon(surf,C_SUBTXT,[(ax-4,ay-3),(ax+4,ay-3),(ax,ay+4)])
    def draw_open(self,surf):
        if not self.open: return
        self._ensure_sel_visible()
        visible = self.opts[self.scroll_off:self.scroll_off+self.MAX_VISIBLE]
        ph = len(visible)*self.ih
        # Clip to screen bottom
        max_y = surf.get_height()-4
        list_y = min(self.rect.bottom, max_y-ph)
        pygame.draw.rect(surf,C_PANEL,(self.rect.x,list_y,self.rect.w,ph))
        pygame.draw.rect(surf,C_BORDER,(self.rect.x,list_y,self.rect.w,ph),1)
        for j,opt in enumerate(visible):
            i = j + self.scroll_off
            ry=list_y+j*self.ih; r=pygame.Rect(self.rect.x,ry,self.rect.w,self.ih)
            if i==self.sel: pygame.draw.rect(surf,C_HILITE,r)
            dtc(surf,opt,self.font,C_ACCENT if i==self.sel else C_TEXT,r.centerx,r.centery)
            pygame.draw.line(surf,C_BORDER,(r.x,r.bottom),(r.right,r.bottom),1)
        # Görgető jelzők
        if self.scroll_off > 0:
            ax=self.rect.x+self.rect.w//2
            pygame.draw.polygon(surf,C_SUBTXT,[(ax-5,list_y+3),(ax+5,list_y+3),(ax,list_y-3)])
        if self.scroll_off+self.MAX_VISIBLE < len(self.opts):
            ax=self.rect.x+self.rect.w//2; by=list_y+ph
            pygame.draw.polygon(surf,C_SUBTXT,[(ax-5,by-3),(ax+5,by-3),(ax,by+3)])
    def draw(self,surf):
        self.draw_closed(surf); self.draw_open(surf)
    def handle(self,ev,gx,gy):
        if ev.type==pygame.MOUSEBUTTONDOWN:
            if ev.button==1:
                if self.rect.collidepoint(gx,gy): self.open=not self.open; return None
                if self.open:
                    visible = self.opts[self.scroll_off:self.scroll_off+self.MAX_VISIBLE]
                    ph=len(visible)*self.ih
                    max_y=800; list_y=min(self.rect.bottom,max_y-ph)
                    for j in range(len(visible)):
                        i=j+self.scroll_off
                        ry=list_y+j*self.ih
                        if pygame.Rect(self.rect.x,ry,self.rect.w,self.ih).collidepoint(gx,gy):
                            self.sel=i; self.open=False; return i
                    self.open=False
            # Egérgörgő: button 4=fel, 5=le
            if self.open:
                if ev.button==4:
                    self.scroll_off=max(0,self.scroll_off-1)
                elif ev.button==5:
                    self.scroll_off=max(0,min(max(0,len(self.opts)-self.MAX_VISIBLE),self.scroll_off+1))
        if ev.type==pygame.MOUSEWHEEL and self.open:
            self.scroll_off=max(0,min(max(0,len(self.opts)-self.MAX_VISIBLE),self.scroll_off-ev.y))
        return None

class GearMenu:
    IW=150; IH=36
    def __init__(self):
        self.btn=Btn(GAME_W-248,7,44,44,"⚙",C_PANEL2,C_TEXT,F_MED)
        self.open=False; self.items=[("💾  Mentés","save"),("🎮  Új játék","newgame"),("✕  Kilépés","quit")]
    def draw(self,surf):
        self.btn.draw(surf)
        if self.open:
            bx=self.btn.rect.x; by=self.btn.rect.bottom
            pygame.draw.rect(surf,C_PANEL,(bx,by,self.IW,len(self.items)*self.IH))
            pygame.draw.rect(surf,C_BORDER,(bx,by,self.IW,len(self.items)*self.IH),1)
            gx2,gy2=game_mouse()
            for i,(lbl,_) in enumerate(self.items):
                r=pygame.Rect(bx,by+i*self.IH,self.IW,self.IH)
                pygame.draw.rect(surf,C_HILITE if r.collidepoint(gx2,gy2) else C_PANEL2,r)
                pygame.draw.line(surf,C_BORDER,(r.x,r.bottom),(r.right,r.bottom),1)
                dt(surf,lbl,F_SMALL,C_TEXT,r.x+8,r.y+9)
    def handle(self,ev,gx,gy):
        if self.btn.hit(ev,gx,gy): self.open=not self.open; return None
        if self.open and ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            bx=self.btn.rect.x; by=self.btn.rect.bottom
            for i,(_,key) in enumerate(self.items):
                if pygame.Rect(bx,by+i*self.IH,self.IW,self.IH).collidepoint(gx,gy):
                    self.open=False; return key
            self.open=False
        return None
    def upd(self,gx,gy): self.btn.upd(gx,gy)

def draw_tactic_pitch(surf,rect):
    rx,ry,rw,rh=rect.x,rect.y,rect.width,rect.height; cx,cy=rect.centerx,rect.centery
    for i in range(10):
        pygame.draw.rect(surf,(38,110,38) if i%2==0 else (34,100,34),(rx+i*(rw//10),ry,rw//10,rh))
    pygame.draw.rect(surf,C_WHITE,rect,2)
    pygame.draw.line(surf,C_WHITE,(cx,ry),(cx,ry+rh),1)
    r=int(min(rw,rh)*0.10); pygame.draw.circle(surf,C_WHITE,(cx,cy),r,1)
    pw=int(rw*0.16); ph=int(rh*0.52)
    pygame.draw.rect(surf,C_WHITE,(rx,cy-ph//2,pw,ph),1)
    pygame.draw.rect(surf,C_WHITE,(rx+rw-pw,cy-ph//2,pw,ph),1)
    gnh=int(rh*0.16); gnw=10
    pygame.draw.rect(surf,(180,180,180),(rx-gnw,cy-gnh//2,gnw,gnh),2)
    pygame.draw.rect(surf,(180,180,180),(rx+rw,cy-gnh//2,gnw,gnh),2)

def tactic_slots(rect,formation):
    rows=FORMATION_ROWS.get(formation,FORMATION_ROWS["4-4-2"])
    rx,ry,rw,rh=rect.x,rect.y,rect.width,rect.height; cy=rect.centery
    rxf={'gk':0.04,'def':0.20,'dm':0.33,'mid':0.50,'am':0.65,'att':0.78}
    res=[(rx+int(rw*0.04),cy,"GK")]; seen={}
    def make_labels(rl,cnt):
        # Unique labels for each position slot
        if rl=='DEF':
            if cnt==1: return ['DC']
            if cnt==2: return ['DL','DR']
            if cnt==3: return ['DCL','DCR','DC'] if False else ['DCL','DC','DCR']
            if cnt==4: return ['DL','DCL','DCR','DR']
            if cnt==5: return ['DL','DCL','DC','DCR','DR']
            return ['DL']+[f'DC{i}' for i in range(1,cnt-1)]+['DR']
        if rl=='MID':
            if cnt==1: return ['MC']
            if cnt==2: return ['ML','MR']
            if cnt==3: return ['MCL','MC','MCR']
            if cnt==4: return ['ML','MCL','MCR','MR']
            if cnt==5: return ['ML','MCL','MC','MCR','MR']
            return ['ML']+[f'MC{i}' for i in range(1,cnt-1)]+['MR']
        if rl=='ATT': return [f'ST{i+1}' for i in range(cnt)]
        if rl=='DM':  return [f'DM{i+1}' if cnt>1 else 'DM' for i in range(cnt)]
        if rl=='AM':  return [f'AM{i+1}' if cnt>1 else 'AM' for i in range(cnt)]
        return [f'{rl}{i+1}' for i in range(cnt)]
    for rl,cnt,rt in rows:
        xf=rxf.get(rt,0.50)
        while xf in seen.values(): xf+=0.08
        seen[rl]=xf
        labels=make_labels(rl,cnt)
        for i in range(cnt):
            res.append((rx+int(rw*xf),ry+int(rh*(i+1)/(cnt+1)),labels[i]))
    return res

BTN_H=44; INFO_Y=52; INFO_H=22; TB=74; NEWS_H=28

# ── Játékos profil (újratervezett layout) ─────────────────────────────────────
def draw_profile(surf,p,x,y,w,h):
    pygame.draw.rect(surf,C_PANEL2,(x,y,w,h),border_radius=9)
    pygame.draw.rect(surf,C_BORDER,(x,y,w,h),2,border_radius=9)
    is_gk=p.get("is_gk",False)
    tr_labels=get_trainable_labels(is_gk)
    personal=p.get("personal_training","passz")

    # ── Fejléc ─────────────────────────────────────────────────────────
    hdr_y=y+8
    dt(surf,p["name"],F_HEAD,C_TEXT,x+12,hdr_y)
    dt(surf,p["position"],F_SMALL,C_ACCENT,x+12,hdr_y+26)
    dt(surf,f"Kor: {p['age']} év",F_TINY,C_SUBTXT,x+200,hdr_y+26)
    talent=p.get("talent","")
    ppd=p.get("pts_per_day",0)
    TCOLS={"Szupertehetség":(255,215,0),"Tehetséges":(0,200,120),
           "Átlagos":(180,180,180),"Kissé tehetségtelen":(180,120,60),"Tehetségtelen":(180,60,60)}
    if talent:
        dt(surf,f"{talent}  ({ppd:.3f} pt/nap)",F_TINY,TCOLS.get(talent,C_SUBTXT),x+12,hdr_y+44)
    dt(surf,"Személyi edzés: ",F_TINY,C_SUBTXT,x+12,hdr_y+58)
    dt(surf,tr_labels.get(personal,personal),F_TINY,C_ACC2,x+118,hdr_y+58)
    pygame.draw.line(surf,C_BORDER,(x+8,hdr_y+74),(x+w-8,hdr_y+74),1)

    # ── Skillek – FM-stílusú 3 oszlop ──────────────────────────────────
    if is_gk:
        # Kapus: Kapus-skillels / Mentális / Fizikai+Technikai
        from data_new import GK_LABELS as LBL_MAP
        gk_skills  = ["magassag_eres","terulet_uralma","kommunikacio","furcsasag",
                       "gk_elso_erintest","kezes","rugas","egy_az_egy_ellen",
                       "gk_passz","oklozes","reflexek","kirohanasok","dobes"]
        ment_skills= ["agresszio","antipacio","batorsag","hidegver","koncentracio",
                       "donteshozatal","elszantsag","lelekmenyesseg","vezetoi",
                       "labda_nelkul","pozicionalas","csapatjatek","latas","munkabirasag"]
        fiz_skills = ["gyorsulas","mozgekonyság","egyensuly","fejesero",
                       "termeszetes_allapot","gyorsasag","allokepeség","ero"]
        tech_extra = ["gk_szabadrugas","gk_buntetoezes","gk_technika"]
        groups=[("KAPUS",gk_skills),("MENTÁLIS",ment_skills),("FIZIKAI",fiz_skills+tech_extra)]
    else:
        from data_new import OUTFIELD_LABELS as LBL_MAP
        tech_skills= ["szogletek","beadas","cselez","befejezes","elso_erintest",
                       "szabadrugas","fejes","tavoli_loves","tavoldobas",
                       "emberfogast","passz","buntetoezes","szereles","technika"]
        ment_skills= ["agresszio","antipacio","batorsag","hidegver","koncentracio",
                       "donteshozatal","elszantsag","lelekmenyesseg","vezetoi",
                       "labda_nelkul","pozicionalas","csapatjatek","latas","munkabirasag"]
        fiz_skills = ["gyorsulas","mozgekonyság","egyensuly","fejesero",
                       "termeszetes_allapot","gyorsasag","allokepeség","ero"]
        groups=[("TECHNIKAI",tech_skills),("MENTÁLIS",ment_skills),("FIZIKAI",fiz_skills)]

    sk_y0=y+88; col_w=(w-20)//3
    row_h=18
    # Kocka-megjelenítés: 10 kocka = 20 pontnyi skála (minden kocka 2 pontot fed)
    SQ=5; SQ_G=1; SQ_CNT=10  # 10 kocka, mindegyik 2pt-ot jelent
    lbl_w=130  # pixel a névnek

    for ci,(grp_lbl,sks) in enumerate(groups):
        cx=x+6+ci*col_w
        dt(surf,grp_lbl,F_SMALL,C_ACCENT,cx,sk_y0)
        for ri,sk in enumerate(sks):
            val=p["skills"].get(sk,0)
            sy=sk_y0+18+ri*row_h
            full_name=LBL_MAP.get(sk,sk)
            # Név - kiemelés ha primary skill
            lbl_col=C_TEXT if val>=12 else C_SUBTXT
            dt(surf,full_name,F_TINY,lbl_col,cx,sy)
            # Kockák (10 db, minden kocka 2pt)
            bx=cx+lbl_w
            for j in range(SQ_CNT):
                threshold=(j+1)*2  # 2,4,6,...,20
                filled=val>=threshold
                col=sc(val) if filled else (28,36,56)
                pygame.draw.rect(surf,col,(bx+j*(SQ+SQ_G),sy+2,SQ,SQ+3),border_radius=1)
            # Szám
            num_w=dt(surf,str(val),F_TINY,sc(val),bx+SQ_CNT*(SQ+SQ_G)+4,sy)
            # Fejlődés/hanyatlás jelzők
            tx=bx+SQ_CNT*(SQ+SQ_G)+22
            gain=p.get("skill_gains",{}).get(sk,0)
            loss=p.get("skill_losses",{}).get(sk,0)
            if gain>0:
                pygame.draw.polygon(surf,(0,220,100),[(tx,sy+9),(tx+6,sy+9),(tx+3,sy+3)])
                dt(surf,str(gain),F_TINY,(0,220,100),tx+8,sy+2)
            elif loss>0:
                pygame.draw.polygon(surf,(220,60,60),[(tx,sy+3),(tx+6,sy+3),(tx+3,sy+9)])
                dt(surf,str(loss),F_TINY,(220,60,60),tx+8,sy+2)

# ══════════════════════════════════════════════════════════════════════════════
class MenuScreen:
    def __init__(self):
        cx=GAME_W//2
        self.btn_new=Btn(cx-130,310,260,56,"ÚJ JÁTÉK",C_ACCENT,C_BG,F_HEAD)
        self.btn_load=Btn(cx-130,384,260,56,"FOLYTATÁS",C_PANEL2,C_TEXT,F_HEAD)
        self.btn_quit=Btn(cx-130,454,260,48,"KILÉPÉS ✕",C_RED,C_WHITE,F_MED)
        self.has_save=os.path.exists(SAVE_PATH)
        self.stars=[(random.randint(0,GAME_W),random.randint(0,GAME_H),random.random()) for _ in range(120)]
        self.t=0
    def draw(self,surf):
        surf.fill(C_BG); self.t+=1
        for sx,sy,b in self.stars:
            c=int(b*150+20*math.sin(self.t*0.02+b*10)); c=max(0,min(255,c))
            pygame.draw.circle(surf,(c,c,c+40),(sx,sy),1)
        # Title: no emoji rectangle, just text
        dtc(surf,"AMATŐR FOCI MANAGER",F_TITLE,C_ACCENT,GAME_W//2,190)
        self.btn_new.draw(surf)
        if self.has_save: self.btn_load.draw(surf)
        else:
            pygame.draw.rect(surf,(18,18,28),self.btn_load.rect,border_radius=7)
            dtc(surf,"FOLYTATÁS (nincs mentés)",F_SMALL,C_SUBTXT,self.btn_load.rect.centerx,self.btn_load.rect.centery)
        self.btn_quit.draw(surf)
    def upd(self,gx,gy): self.btn_new.upd(gx,gy); self.btn_load.upd(gx,gy); self.btn_quit.upd(gx,gy)
    def handle(self,ev,gx,gy):
        if self.btn_new.hit(ev,gx,gy): return "new"
        if self.btn_quit.hit(ev,gx,gy): return "quit"
        if self.has_save and self.btn_load.hit(ev,gx,gy): return "load"
        return None

class NameScreen:
    PRESET_COLORS=[
        (220,30,30),(30,80,200),(20,120,20),(180,30,180),(255,140,0),
        (0,180,180),(100,0,0),(40,40,40),(180,160,0),(0,100,80),
        (200,80,0),(60,60,180),(200,200,0),(0,140,200),(160,80,0),
        (0,80,0),(120,120,0),(200,0,100),(0,160,80),(140,0,60),
        (255,255,255),(200,200,200),
    ]
    def __init__(self):
        cx=GAME_W//2
        self.inp=TxtIn(cx-190,220,380,44,"pl. Sopron FC")
        self.btn=Btn(cx-95,GAME_H-90,190,48,"KEZDÉS  ▶",C_ACCENT,C_BG,F_HEAD)
        self.phase=0  # 0=name, 1=colors
        self.sel_idx=[0,1,4]  # home, away, third color indices
        self.sel_which=0  # which slot being picked
    def draw(self,surf):
        surf.fill(C_BG)
        if self.phase==0:
            dtc(surf,"AMATŐR FOCI MANAGER",F_TITLE,C_ACCENT,GAME_W//2,100)
            dtc(surf,"ÚJ JÁTÉK",F_HEAD,C_TEXT,GAME_W//2,165)
            dtc(surf,"Add meg a csapatod nevét:",F_BODY,C_SUBTXT,GAME_W//2,195)
            self.inp.draw(surf); self.btn.draw(surf)
        else:
            dtc(surf,"Válaszd ki csapatod színeit:",F_HEAD,C_TEXT,GAME_W//2,160)
            lbls=["Hazai","Idegen","Tartalék"]
            for i,(lbl,idx) in enumerate(zip(lbls,self.sel_idx)):
                cx2=GAME_W//2-200+i*200; cy2=220
                pygame.draw.circle(surf,self.PRESET_COLORS[idx],(cx2,cy2),30)
                if self.sel_which==i:
                    pygame.draw.circle(surf,C_WHITE,(cx2,cy2),33,3)
                dt(surf,lbl,F_SMALL,C_TEXT,cx2-20,cy2+38)
            dt(surf,"Kattints egy körre, majd válassz egy színt:",F_TINY,C_SUBTXT,GAME_W//2-200,280)
            # Color palette
            cols_per_row=11; sw=40; sy0=305
            for i,col in enumerate(self.PRESET_COLORS):
                rx=(GAME_W//2-cols_per_row*sw//2)+(i%cols_per_row)*sw
                ry=sy0+(i//cols_per_row)*sw
                pygame.draw.rect(surf,col,(rx+2,ry+2,sw-4,sw-4),border_radius=5)
                if self.sel_idx[self.sel_which]==i:
                    pygame.draw.rect(surf,C_WHITE,(rx,ry,sw,sw),2,border_radius=5)
            self.btn.draw(surf)
    def upd(self,gx,gy): self.btn.upd(gx,gy)
    def handle(self,ev,gx,gy):
        if self.phase==0:
            e=self.inp.handle(ev,gx,gy)
            if (self.btn.hit(ev,gx,gy) or e) and self.inp.text.strip():
                self.phase=1; return None
            return None
        else:
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                # Click on kit circle
                lbls=[0,1,2]
                for i in lbls:
                    cx2=GAME_W//2-200+i*200; cy2=220
                    if dst(gx,gy,cx2,cy2)<35: self.sel_which=i; return None
                # Click on palette
                cols_per_row=11; sw=40; sy0=305
                for i,col in enumerate(self.PRESET_COLORS):
                    rx=(GAME_W//2-cols_per_row*sw//2)+(i%cols_per_row)*sw
                    ry=sy0+(i//cols_per_row)*sw
                    if pygame.Rect(rx,ry,sw,sw).collidepoint(gx,gy):
                        self.sel_idx[self.sel_which]=i; return None
            if self.btn.hit(ev,gx,gy):
                kits=[self.PRESET_COLORS[self.sel_idx[i]] for i in range(3)]
                return (self.inp.text.strip(), kits)
            return None
    def get_kit(self):
        return [self.PRESET_COLORS[self.sel_idx[i]] for i in range(3)]

class MainScreen:
    def __init__(self,gs):
        self.gs=gs; self.tab="csapat"; self._build()

    def _build(self):
        tw=96; gap=4
        tabs=[("Csapat","csapat"),("Edzés","edzés"),("Taktika","taktika"),("Tabella","tabella"),("Meccsek","meccsek")]
        self.tab_btns=[(Btn(10+i*(tw+gap),6,tw,BTN_H,l,C_PANEL2,C_TEXT,F_MED),k) for i,(l,k) in enumerate(tabs)]
        self.meccs_scroll=0; self.meccs_sel=None
        self.gear=GearMenu()
        self.btn_next=Btn(GAME_W-198,6,190,BTN_H,"Következő nap  ▶",C_ACCENT,C_BG,F_SMALL)
        self.save_flash=0
        self.sel_p=None; self.pscroll=0
        self.train_day="Hétfő"
        self.day_btns=[Btn(10+i*76,TB+8,72,30,d,C_PANEL2,C_TEXT,F_TINY) for i,d in enumerate(DAYS)]
        self.pscroll2=0
        self.formation=self.gs.get_player_team().get("formation","4-4-2")
        self.tact_tab="felallas"
        self._training_dds={}  # Edzés dropdownok
        self.field_p={}; self.drag_p=None; self.tscroll=0
        # Nested formation dropdown: first level = group, second = formation
        self._fg_names=list(FORMATION_GROUPS.keys())
        cur_group=next((g for g,fs in FORMATION_GROUPS.items() if self.formation in fs),self._fg_names[0])
        self.form_group_dd=DD(10,TB+8,120,30,self._fg_names,
                              self._fg_names.index(cur_group),F_TINY)
        self._cur_group=cur_group
        group_forms=FORMATION_GROUPS[cur_group]
        fi=group_forms.index(self.formation) if self.formation in group_forms else 0
        self.form_dd=DD(136,TB+8,120,30,group_forms,fi,F_TINY)
        self._sp_dds={}; self._open_dd:DD|None=None
        self.drag_slot=None
        self.tactic_positions=self._generate_442_positions()
        self.sel_tid=None; self.team_sub="jatekosok"; self.show_td=False; self.td_scroll=0; self.td_sel_p=None
        self.show_match=False; self.match_anim=None
        self.show_post_stats=False   # post-match stats overlay
        self.back_btn=Btn(GAME_W-166,GAME_H-50,158,42,"◀  Vissza",C_RED,C_WHITE,F_SMALL)
        self.tovabb_btn=Btn(GAME_W//2-110,GAME_H-60,220,46,"Tovább  ▶",C_ACCENT,C_BG,F_HEAD)

    def _generate_442_positions(self):
        """Generálja az alapértelmezett 4-4-2 pozíciókat MINDEN slot-tal (5-5-5-5-5)."""
        positions = []
        
        # KAPUS (1 db) - bal szélen
        positions.append({"id":"GK","row":"gk","x":0.05,"y":0.5,"occupied":True})
        
        # VÉDŐK (5 slot) - bal oldal
        def_y = [0.1, 0.3, 0.5, 0.7, 0.9]
        for i in range(5):
            occupied = i < 4  # Első 4 elfoglalt (4-4-2)
            positions.append({"id":f"DEF{i+1}","row":"def","x":0.18,"y":def_y[i],"occupied":occupied})
        
        # DM (5 slot)
        dm_y = [0.1, 0.3, 0.5, 0.7, 0.9]
        for i in range(5):
            occupied = False  # 4-4-2-ben nincs DM
            positions.append({"id":f"DM{i+1}","row":"dm","x":0.35,"y":dm_y[i],"occupied":occupied})
        
        # KÖZÉPPÁLYÁSOK (5 slot)
        mid_y = [0.1, 0.3, 0.5, 0.7, 0.9]
        for i in range(5):
            occupied = i < 4  # Első 4 elfoglalt (4-4-2)
            positions.append({"id":f"MID{i+1}","row":"mid","x":0.52,"y":mid_y[i],"occupied":occupied})
        
        # AM (5 slot)
        am_y = [0.1, 0.3, 0.5, 0.7, 0.9]
        for i in range(5):
            occupied = False  # 4-4-2-ben nincs AM
            positions.append({"id":f"AM{i+1}","row":"am","x":0.69,"y":am_y[i],"occupied":occupied})
        
        # CSATÁROK (5 slot)
        att_y = [0.1, 0.3, 0.5, 0.7, 0.9]
        for i in range(5):
            occupied = i < 2  # Első 2 elfoglalt (4-4-2)
            positions.append({"id":f"ATT{i+1}","row":"att","x":0.86,"y":att_y[i],"occupied":occupied})
        
        return positions
    
    def _get_formation_string(self):
        """Visszaadja a jelenlegi formációt string-ként (pl. "4-4-2")."""
        rows = {"def":0,"dm":0,"mid":0,"am":0,"att":0}
        for pos in self.tactic_positions:
            if pos["row"] == "gk":  # Kapust nem számoljuk
                continue
            if pos["occupied"]:
                rows[pos["row"]] += 1
        parts = []
        if rows["def"]>0: parts.append(str(rows["def"]))
        if rows["dm"]>0: parts.append(str(rows["dm"]))
        if rows["mid"]>0: parts.append(str(rows["mid"]))
        if rows["am"]>0: parts.append(str(rows["am"]))
        if rows["att"]>0: parts.append(str(rows["att"]))
        return "-".join(parts) if parts else "0-0-0"
    
    def _draw_csapat(self,surf):
        lw=222; rh=48; gap=2
        clip_h=GAME_H-TB-NEWS_H
        pygame.draw.rect(surf,C_PANEL,(0,TB,lw,clip_h))
        pygame.draw.line(surf,C_BORDER,(lw,TB),(lw,GAME_H-NEWS_H),1)
        dt(surf,"KERET",F_TINY,C_ACCENT,8,TB+6)
        pt=self.gs.get_player_team()
        list_y0=TB+26
        # Clipping a listára
        surf.set_clip(pygame.Rect(0,list_y0,lw,clip_h-26))
        TCOLS={"Szupertehetség":(255,215,0),"Tehetséges":(0,200,120),
               "Átlagos":(180,180,180),"Kissé tehetségtelen":(180,120,60),"Tehetségtelen":(180,60,60)}
        y=list_y0-self.pscroll
        for p in pt["players"]:
            if y+rh>list_y0 and y<GAME_H-NEWS_H:
                r=pygame.Rect(4,y,lw-8,rh)
                act=self.sel_p and self.sel_p["name"]==p["name"]
                pygame.draw.rect(surf,C_HILITE if act else C_PANEL2,r,border_radius=5)
                if act: pygame.draw.rect(surf,C_ACCENT,r,1,border_radius=5)
                dt(surf,p["name"],F_SMALL,C_TEXT,8,y+4)
                dt(surf,p["position"][:16],F_TINY,C_SUBTXT,8,y+22)
                dt(surf,f"{p['age']}",F_TINY,C_SUBTXT,lw-38,y+4)
                # tehetség csak a profilnál jelenik meg, itt nem
            y+=rh+gap
        surf.set_clip(None)
        # Scrollbar
        total_h=len(pt["players"])*(rh+gap)
        vis_h=clip_h-26
        if total_h>vis_h:
            ratio=vis_h/total_h; bar_h=max(20,int(vis_h*ratio))
            bar_y=list_y0+int((self.pscroll/max(1,total_h-vis_h))*(vis_h-bar_h))
            pygame.draw.rect(surf,C_SUBTXT,(lw-5,bar_y,4,bar_h),border_radius=2)
        if self.sel_p:
            draw_profile(surf,self.sel_p,lw+6,TB+4,GAME_W-lw-12,GAME_H-TB-NEWS_H-8)

    def _draw_edzes(self,surf):
        for i,db in enumerate(self.day_btns):
            dn=DAYS[i]; db.col=C_ACCENT if dn==self.train_day else (C_RED if dn=="Szombat" else C_PANEL2)
            db.tc=C_BG if dn==self.train_day else C_TEXT; db.draw(surf)
        day=self.train_day
        if day=="Szombat":
            dtc(surf,"⚽  MECCSNAP",F_BIG,C_ACCENT,GAME_W//2,GAME_H//2-16)
            dtc(surf,"Edzés nem tartható.",F_BODY,C_SUBTXT,GAME_W//2,GAME_H//2+20); return
        title_y=TB+46
        dt(surf,"SZEMÉLYI EDZÉSEK",F_MED,C_ACCENT,12,title_y)
        dt(surf,"(kattints a változtatáshoz)",F_TINY,C_SUBTXT,230,title_y+4)
        dt(surf,f"– {day}",F_MED,C_SUBTXT,430,title_y)
        pt=self.gs.get_player_team(); clip_y=title_y+26; rh=38
        surf.set_clip(pygame.Rect(0,clip_y,GAME_W,GAME_H-clip_y-NEWS_H-4))
        y=clip_y-self.pscroll2
        for p in pt["players"]:
            if y>GAME_H-NEWS_H-4: break
            if y>clip_y-4:
                pygame.draw.rect(surf,C_PANEL2,(10,y,GAME_W-20,rh-2),border_radius=5)
                dt(surf,p["name"],F_SMALL,C_TEXT,18,y+4)
                dt(surf,p["position"][:16],F_TINY,C_SUBTXT,180,y+6)
                personal=p.get("personal_training","passz")
                lbl=TRAINABLE_LABELS.get(personal,personal)
                dt(surf,f"▸  {lbl}",F_SMALL,C_ACC2,360,y+4)
                val=p["skills"].get(personal,0)
                dt(surf,f"{val}",F_TINY,C_SUBTXT,560,y+7)
            y+=rh
        surf.set_clip(None)

    def _draw_taktika(self,surf):
        # Fülek balra (dropdown-ok eltávolítva)
        for i,(lbl,key) in enumerate([("Felállás","felallas"),("Rögzített helyzetek","rogzitett")]):
            bx=10+i*185; act=self.tact_tab==key
            pygame.draw.rect(surf,C_ACCENT if act else C_PANEL2,(bx,TB+8,178,30),border_radius=5)
            dtc(surf,lbl,F_TINY,C_BG if act else C_TEXT,bx+89,TB+23)
        # Formáció kijelzés
        form_str=self._get_formation_string()
        dt(surf,f"Felállás: {form_str}",F_SMALL,C_ACCENT,400,TB+14)
        
        if self.tact_tab=="felallas": self._draw_tact_f(surf)
        else: self._draw_tact_r(surf)

    def _draw_tact_f(self,surf):
        """Taktika rajzolás - előre kitett pozíciókkal."""
        sbx=582; y0=TB+46
        pr=pygame.Rect(8,y0,sbx-12,GAME_H-y0-NEWS_H-4)
        draw_tactic_pitch(surf,pr)
        
        gx, gy = game_mouse()
        slot_radius = 16
        
        # Pozíciók rajzolása
        for pos in self.tactic_positions:
            px = pr.x + pr.width * pos["x"]
            py = pr.y + pr.height * pos["y"]
            
            # Játékos keresése ezen a pozíción
            player = self.field_p.get(pos["id"])
            
            # Highlight ha fölötte van az egér
            dist = ((gx-px)**2 + (gy-py)**2)**0.5
            is_hover = dist < slot_radius + 5
            
            # Pozíció rövid neve a körben
            POS_LABELS={"GK":"GK",
                "DEF1":"DL","DEF2":"DC1","DEF3":"DC2","DEF4":"DC3","DEF5":"DR",
                "DM1":"WBL","DM2":"DMC1","DM3":"DMC2","DM4":"DMC3","DM5":"WBR",
                "MID1":"ML","MID2":"MC1","MID3":"MC2","MID4":"MC3","MID5":"MR",
                "AM1":"AML","AM2":"AMC1","AM3":"AMC2","AM4":"AMC3","AM5":"AMR",
                "ATT1":"FL","ATT2":"ST1","ATT3":"ST2","ATT4":"ST3","ATT5":"FR"}
            pos_lbl=POS_LABELS.get(pos["id"],pos["id"])
            if pos["occupied"]:
                if player:
                    pygame.draw.circle(surf,(20,80,50),(int(px),int(py)),slot_radius)
                    pygame.draw.circle(surf,C_ACCENT if is_hover else (60,140,80),(int(px),int(py)),slot_radius,2)
                    dtc(surf,player["name"].split()[-1][:8],F_TINY,C_WHITE,int(px),int(py))
                else:
                    pygame.draw.circle(surf,(35,70,50),(int(px),int(py)),slot_radius)
                    pygame.draw.circle(surf,(80,120,90) if is_hover else (60,100,70),(int(px),int(py)),slot_radius,2)
                    dtc(surf,pos_lbl,F_TINY,C_SUBTXT,int(px),int(py))
            else:
                pygame.draw.circle(surf,(25,45,35),(int(px),int(py)),slot_radius-2,1)
        
        # Játékoslista (jobb oldal)
        pygame.draw.rect(surf,C_PANEL,(sbx,TB+46,GAME_W-sbx,GAME_H-TB-NEWS_H-50))
        pygame.draw.line(surf,C_BORDER,(sbx,TB+46),(sbx,GAME_H-NEWS_H-4),1)
        dt(surf,"JÁTÉKOSOK",F_TINY,C_ACCENT,sbx+8,TB+50)
        dt(surf,"(húzd a pályára)",F_TINY,C_SUBTXT,sbx+8,TB+64)
        
        surf.set_clip(pygame.Rect(sbx,TB+80,GAME_W-sbx,GAME_H-TB-NEWS_H-86))
        pt=self.gs.get_player_team(); rh=36; y=TB+82-self.tscroll
        
        for p in pt["players"]:
            if y>GAME_H-NEWS_H-6: break
            if y>TB+78:
                # Van-e a pályán?
                in_field = any(self.field_p.get(pos["id"],{}).get("name")==p["name"] 
                              for pos in self.tactic_positions if pos["occupied"])
                r=pygame.Rect(sbx+3,y,GAME_W-sbx-6,rh-2)
                pygame.draw.rect(surf,(30,60,40) if in_field else C_PANEL2,r,border_radius=4)
                if in_field: pygame.draw.rect(surf,C_ACCENT,r,1,border_radius=4)
                dt(surf,p["name"][:18],F_TINY,C_SUBTXT if in_field else C_TEXT,sbx+10,y+4)
                dt(surf,p["position"][:14],F_TINY,C_SUBTXT,sbx+10,y+18)
            y+=rh
        surf.set_clip(None)
        
        # Húzott elem
        if self.drag_p:
            pygame.draw.circle(surf,C_ACCENT,(gx,gy),20)
            dtc(surf,self.drag_p["name"].split()[-1][:8],F_TINY,C_BG,gx,gy)
        elif self.drag_slot:
            pygame.draw.circle(surf,(100,160,120),(gx,gy),18,2)
            dtc(surf,self.drag_slot["id"],F_TINY,C_ACC2,gx,gy)
    
    def _update_tactic_hover(self,mx,my):
        """Megkeresi melyik játékos fölé viszi az egeret a listában.
        Pontosan ugyanazok a koordináták mint a _draw_tact_l-ben."""
        TB=50; pt=self.gs.get_player_team()
        if not pt: return
        players=pt.get("players",[])
        # Ugyanaz a sorrend mint a _draw_tact_l-ben (nincs rendezés!)
        rh=36
        # sbx: a jobb oldali lista x kezdete – a taktika pályarajz 580px széles
        sbx=580
        y=TB+82-self.tscroll
        self._tactic_hover_player=None
        for p in players:
            if y>GAME_H-40: break
            if y>TB+78:
                # Pontosan ugyanaz a rect mint a _draw_tact_l-ben
                r=pygame.Rect(sbx+3, y, GAME_W-sbx-6, rh-2)
                if r.collidepoint(mx,my):
                    self._tactic_hover_player=p
                    return  # megtaláltuk, kilép
            y+=rh

    def _draw_tactic_tooltip(self,surf):
        """Felugró mini-profil a hoveredelt játékoshoz."""
        p=self._tactic_hover_player
        if not p: return
        import pygame
        tw=360; th=320
        mx,my=pygame.mouse.get_pos()
        tx=mx-tw-8 if mx+tw+12>GAME_W else mx+12
        ty=max(4,min(GAME_H-th-4,my-20))
        bg=pygame.Surface((tw,th),pygame.SRCALPHA)
        bg.fill((12,18,36,235))
        surf.blit(bg,(tx,ty))
        pygame.draw.rect(surf,C_ACCENT,(tx,ty,tw,th),1,border_radius=6)
        name=p.get("name","?"); pos=p.get("position",""); age=p.get("age","?")
        # F_SMALL=14pt, F_TINY=12pt, F_NUM=10pt
        dt(surf,name,F_SMALL,C_WHITE,tx+10,ty+8)
        dt(surf,f"{pos} | {age} ev",F_TINY,C_SUBTXT,tx+10,ty+26)
        skills=p.get("skills",{})
        is_gk = "Kapus" in p.get("position","")
        # Összes skill megjelenítése a profilból
        if is_gk:
            from data_new import GK_SKILLS, GK_LABELS
            all_keys=list(GK_SKILLS)
            sections=[("KAPUS",all_keys[:9]),("FIZIKAI+MENTÁLIS",all_keys[9:])]
        else:
            from data_new import OUTFIELD_SKILLS, OUTFIELD_LABELS
            all_keys=list(OUTFIELD_SKILLS)
            n=len(all_keys)//3
            sections=[("TECHNIKAI",all_keys[:n]),
                      ("MENTÁLIS",all_keys[n:2*n]),
                      ("FIZIKAI",all_keys[2*n:])]
        # Labelek: az adatból olvassuk
        try:
            from data_new import OUTFIELD_LABELS, GK_LABELS
            col_labels={**OUTFIELD_LABELS,**GK_LABELS}
        except:
            col_labels={}
        sy=ty+46; col_w=tw//3
        for si,(sec_name,keys) in enumerate(sections):
            sx=tx+6+si*col_w
            dt(surf,sec_name,F_NUM,C_ACCENT,sx,sy)
            for ki,key in enumerate(keys):
                val=skills.get(key,0)
                lbl=col_labels.get(key,key[:9])
                ky=sy+14+ki*15
                if ky>ty+th-6: break
                val_col=(0,200,100) if val>=14 else ((255,180,0) if val>=8 else (200,60,60))
                dt(surf,lbl,F_NUM,C_SUBTXT,sx,ky)
                dt(surf,str(val),F_NUM,val_col,sx+col_w-26,ky)

    def _draw_tact_r(self,surf):
        pt=self.gs.get_player_team()
        starter_names={v["name"] for v in self.field_p.values()}
        starters=[p for p in pt["players"] if p["name"] in starter_names]
        if not starters: starters=list(pt["players"])
        names=["(nincs)"]+[p["name"] for p in starters]
        sp=pt.setdefault("set_piece_takers",{"corner":"","freekick":"","throwin":"","penalty":""})
        types=[("corner","⛳  Szöglet"),("freekick","🎯  Szabadrúgás"),
               ("throwin","🤾  Bedobás"),("penalty","⚡  Tizenegyes")]
        dt(surf,"KI VÉGEZZE EL?",F_MED,C_ACCENT,12,TB+48)
        dt(surf,"(csak a kezdőcsapatban szereplők)",F_TINY,C_SUBTXT,200,TB+52)
        bw=260; bh=32
        for i,(key,lbl) in enumerate(types):
            ly=TB+92+i*62
            pygame.draw.rect(surf,C_PANEL2,(8,ly,GAME_W-16,54),border_radius=7)
            pygame.draw.rect(surf,C_BORDER,(8,ly,GAME_W-16,54),1,border_radius=7)
            dt(surf,lbl,F_SMALL,C_ACCENT,20,ly+18)
            cur=sp.get(key,"")
            if key not in self._sp_dds:
                idx=names.index(cur) if cur in names else 0
                self._sp_dds[key]=DD(220,ly+11,bw,bh,names,idx,F_TINY)
            else:
                self._sp_dds[key].rect.y=ly+11
                self._sp_dds[key].opts=names
                if self._sp_dds[key].sel>=len(names): self._sp_dds[key].sel=0
            # draw closed state here; open list drawn after all rows
            self._sp_dds[key].draw_closed(surf)
            # ── Kiválasztott játékos képessége ──
            sel_name = self._sp_dds[key].opts[self._sp_dds[key].sel] if self._sp_dds[key].sel < len(self._sp_dds[key].opts) else ""
            if sel_name and sel_name != "(nincs)":
                sel_p = next((p for p in starters if p["name"]==sel_name), None)
                if sel_p:
                    skill_map = {"corner":"szogletek","freekick":"szabadrugas","throwin":"tavoldobas","penalty":"buntetoezes"}
                    sk_key = skill_map.get(key,"")
                    sk_val = sel_p.get("skills",{}).get(sk_key, sel_p.get("skills",{}).get("passz",0))
                    sk_label = {"corner":"Szögletek","freekick":"Szabadrúgás","throwin":"Távoldobás","penalty":"Büntető"}.get(key,"")
                    skill_x = 220 + bw + 16
                    pygame.draw.rect(surf, (25,40,60), (skill_x, ly+8, 160, 36), border_radius=5)
                    pygame.draw.rect(surf, C_BORDER, (skill_x, ly+8, 160, 36), 1, border_radius=5)
                    dt(surf, f"{sk_label}:", F_TINY, C_SUBTXT, skill_x+8, ly+11)
                    val_col = (0,200,100) if sk_val>=14 else ((255,180,0) if sk_val>=8 else (200,60,60))
                    dt(surf, str(sk_val), F_MED, val_col, skill_x+8, ly+24)
        # Draw open dropdowns on top (last, so they overlap other rows)
        for key,_ in types:
            if key in self._sp_dds:
                self._sp_dds[key].draw_open(surf)

    def _draw_post_stats(self,surf):
        """Full-screen post-match statistics."""
        surf.fill(C_BG)
        ma=self.match_anim
        # Header
        pygame.draw.rect(surf,C_NAVY,(0,0,GAME_W,56))
        dtc(surf,f"{ma.hn}  {ma.sh} : {ma.sa}  {ma.an}",F_HEAD,C_WHITE,GAME_W//2,28)
        # Tabs
        tabs=[("📋 Meccslap","match"),("📰 Többi meccs","others")]
        for i,(lbl,key) in enumerate(tabs):
            r=pygame.Rect(20+i*160,64,154,28); act=ma._stats_tab==key
            pygame.draw.rect(surf,C_ACCENT if act else C_PANEL2,r,border_radius=6)
            dtc(surf,lbl,F_SMALL,(0,0,0) if act else C_TEXT,r.centerx,r.centery)
        if ma._stats_tab=='match': ma._draw_match_report(surf)
        else: ma._draw_other_results(surf)
        # Tovabb button at bottom
        self.tovabb_btn.draw(surf)

    def _draw_meccsek(self,surf):
        """Meccsek tab: only player team's matches."""
        pt=self.gs.get_player_team(); pid=self.gs.player_team_id
        schedule=self.gs.schedule; played_md=self.gs.matchday
        teams_by_id={t['id']:t for t in self.gs.teams}
        # Build history lookup: key=(home_id, away_id)
        history_by_ids={(h['home_id'],h['away_id']):h for h in self.gs.match_stats_history}
        rh=32; y0=TB+28; visible_h=GAME_H-TB-NEWS_H-50
        # Header row
        pygame.draw.rect(surf,C_PANEL2,(0,TB,GAME_W,26))
        dt(surf,"#",F_TINY,C_SUBTXT,12,TB+6)
        dt(surf,"Hazai csapat",F_TINY,C_SUBTXT,48,TB+6)
        dtc(surf,"Eredmény",F_SMALL,C_SUBTXT,GAME_W//2,TB+12)
        dt(surf,"Vendég csapat",F_TINY,C_SUBTXT,GAME_W//2+80,TB+6)
        pygame.draw.line(surf,C_BORDER,(0,TB+26),(GAME_W,TB+26),1)
        surf.set_clip(pygame.Rect(0,y0,GAME_W,visible_h))
        y=y0-self.meccs_scroll
        match_num=0
        for rnd_idx,rnd in enumerate(schedule):
            for pair in rnd:
                h_id,a_id=pair
                if h_id is None or a_id is None: continue
                if h_id!=pid and a_id!=pid: continue  # only our matches
                match_num+=1
                ht=teams_by_id.get(h_id,{}); at=teams_by_id.get(a_id,{})
                hn=ht.get('name','?')[:20]; an=at.get('name','?')[:20]
                played=(rnd_idx<played_md)
                # Find result
                result_str='–  –'
                for r in self.gs.match_results:
                    if r.get('home_id')==h_id and r.get('away_id')==a_id:
                        result_str=f"{r['home_goals']}  :  {r['away_goals']}"; break
                if y+rh>y0 and y<y0+visible_h:
                    is_sel=self.meccs_sel==(h_id,a_id)
                    if is_sel:
                        row_col=(30,55,90)
                    elif played:
                        row_col=(20,28,46)
                    else:
                        row_col=(14,20,36)
                    pygame.draw.rect(surf,row_col,(4,y,GAME_W-8,rh-3),border_radius=4)
                    num_c=C_ACCENT if played else C_SUBTXT
                    dt(surf,str(match_num),F_TINY,num_c,12,y+9)
                    # Home team name (right-aligned to center)
                    hn_s=F_SMALL.render(hn,True,C_ACCENT if h_id==pid else C_TEXT)
                    surf.blit(hn_s,(GAME_W//2-120-hn_s.get_width(),y+8))
                    # Result
                    rc=C_ACC2 if played else C_SUBTXT
                    dtc(surf,result_str,F_MED,rc,GAME_W//2,y+rh//2)
                    # Away team name (left-aligned from center)
                    an_s=F_SMALL.render(an,True,C_ACCENT if a_id==pid else C_TEXT)
                    surf.blit(an_s,(GAME_W//2+125,y+8))
                    if played and not is_sel:
                        dt(surf,"▶ részletek",F_TINY,(80,200,80),GAME_W-100,y+9)
                y+=rh
        surf.set_clip(None)
        # Popup for selected match
        if self.meccs_sel:
            h_id,a_id=self.meccs_sel
            hist=history_by_ids.get((h_id,a_id))
            if hist: self._draw_meccs_popup(surf,hist)

    def _draw_meccs_popup(self,surf,hist):
        """Small popup with match stats."""
        pw=520; ph=240; px2=(GAME_W-pw)//2; py2=(GAME_H-ph)//2
        pygame.draw.rect(surf,C_NAVY,(px2,py2,pw,ph),border_radius=10)
        pygame.draw.rect(surf,C_ACCENT,(px2,py2,pw,ph),2,border_radius=10)
        dtc(surf,f"{hist['home']}  {hist['sh']} : {hist['sa']}  {hist['away']}",
            F_HEAD,C_WHITE,GAME_W//2,py2+24)
        y=py2+52
        # Goals
        for m,nm,side in hist.get('goal_log',[]):
            side_col=(140,170,255) if side=='home' else (255,130,130)
            dt(surf,f"⚽ {m}' {nm}",F_TINY,side_col,px2+16,y); y+=18
        # Stats
        st=hist.get('stats',{}); h_s=st.get('home',{}); a_s=st.get('away',{})
        rows2=[("Lövések",h_s.get('shots',0),a_s.get('shots',0)),
               ("Célra",h_s.get('on_target',0),a_s.get('on_target',0)),
               ("Szögletek",h_s.get('corners',0),a_s.get('corners',0))]
        for lbl,hv,av in rows2:
            dt(surf,f"{hv}",F_TINY,C_TEXT,px2+16,y)
            dtc(surf,lbl,F_TINY,C_SUBTXT,GAME_W//2,y+2)
            dt(surf,f"{av}",F_TINY,C_TEXT,GAME_W//2+100,y); y+=20
        dt(surf,"[Kattints bárhova a bezáráshoz]",F_TINY,C_SUBTXT,px2+16,py2+ph-22)

    def _handle_meccsek(self,ev,gx,gy):
        if ev.type==pygame.MOUSEBUTTONDOWN:
            if ev.button==4: self.meccs_scroll=max(0,self.meccs_scroll-40); return
            if ev.button==5: self.meccs_scroll=min(len(self.gs.schedule)*32,self.meccs_scroll+40); return
            if ev.button==1:
                if self.meccs_sel: self.meccs_sel=None; return
                pid=self.gs.player_team_id; played_md=self.gs.matchday
                rh=32; y=TB+28-self.meccs_scroll
                for rnd_idx,rnd in enumerate(self.gs.schedule):
                    for pair in rnd:
                        h_id,a_id=pair
                        if h_id is None or a_id is None: continue
                        if h_id!=pid and a_id!=pid: continue
                        if rnd_idx<played_md and pygame.Rect(4,y,GAME_W-8,rh-3).collidepoint(gx,gy):
                            self.meccs_sel=(h_id,a_id); return
                        y+=rh
        if hasattr(pygame,'MOUSEWHEEL') and ev.type==pygame.MOUSEWHEEL:
            self.meccs_scroll=max(0,min(len(self.gs.schedule)*32,
                                        self.meccs_scroll-ev.y*40))

    def _draw_tabella(self,surf):
        standings=self.gs.get_standings()
        xs=[8,38,350,394,432,470,508,590]; headers=["#","Csapat","M","Gy","D","V","Gól","Pont"]
        hy=TB+6
        pygame.draw.rect(surf,C_PANEL2,(4,hy,GAME_W-8,28),border_radius=4)
        for i,h in enumerate(headers): dt(surf,h,F_TINY,C_ACCENT,xs[i],hy+7)
        rh=28
        for rank,t in enumerate(standings):
            y=hy+32+rank*rh
            if y>GAME_H-NEWS_H-4: break
            ip=t["id"]==self.gs.player_team_id; isel=t["id"]==self.sel_tid
            bg=C_HILITE if isel else ((30,50,30) if ip else (C_PANEL if rank%2==0 else C_BG))
            pygame.draw.rect(surf,bg,(4,y,GAME_W-8,rh-1),border_radius=3)
            gd=t["goals_for"]-t["goals_against"]
            vals=[str(rank+1),t["name"][:26],str(t["wins"]+t["draws"]+t["losses"]),
                  str(t["wins"]),str(t["draws"]),str(t["losses"]),
                  f"{t['goals_for']}:{t['goals_against']}({'+' if gd>=0 else ''}{gd})",str(t["points"])]
            col=C_GOLD if ip else C_TEXT
            for i,v in enumerate(vals): dt(surf,v,F_TINY,col,xs[i],y+7)
            if rank<4: pygame.draw.rect(surf,C_ACCENT,(0,y,3,rh-1))
            elif rank>=17: pygame.draw.rect(surf,C_RED,(0,y,3,rh-1))
        dt(surf,"← kattints csapatra a részletekért",F_TINY,C_SUBTXT,8,GAME_H-NEWS_H-4)

    def _draw_team_detail(self,surf):
        self._draw_topbar(surf)
        team=next((t for t in self.gs.teams if t["id"]==self.sel_tid),None)
        if not team: self.show_td=False; return
        self._back_btn2=Btn(8,TB+4,106,30,"← Vissza",C_PANEL2,C_TEXT,F_SMALL)
        self._back_btn2.draw(surf)
        dt(surf,team["name"],F_HEAD,C_ACCENT,122,TB+6)
        dt(surf,f"{team['wins']}Gy {team['draws']}D {team['losses']}V | {team['points']}pt",F_TINY,C_SUBTXT,122,TB+28)
        lw=222; y0=TB+4; rh=42
        # Bal lista
        pygame.draw.rect(surf,C_PANEL,(0,TB,lw,GAME_H-TB-NEWS_H))
        pygame.draw.line(surf,C_BORDER,(lw,TB),(lw,GAME_H-NEWS_H),1)
        dt(surf,"KERET",F_TINY,C_ACCENT,8,TB+6)
        ly=TB+26-self.td_scroll
        for p in team["players"]:
            if ly>GAME_H-NEWS_H-4: break
            if ly>TB:
                act=self.td_sel_p and self.td_sel_p["name"]==p["name"]
                r=pygame.Rect(4,ly,lw-8,rh)
                pygame.draw.rect(surf,C_HILITE if act else C_PANEL2,r,border_radius=5)
                if act: pygame.draw.rect(surf,C_ACCENT,r,1,border_radius=5)
                dt(surf,p["name"],F_SMALL,C_TEXT,8,ly+4)
                dt(surf,p["position"][:16],F_TINY,C_SUBTXT,8,ly+22)
                dt(surf,f"{p['age']}",F_TINY,C_SUBTXT,lw-38,ly+4)
            ly+=rh+2
        # Jobb profil vagy üres
        if self.td_sel_p:
            draw_profile(surf,self.td_sel_p,lw+6,TB+4,GAME_W-lw-12,GAME_H-TB-NEWS_H-8)
        pygame.draw.rect(surf,C_NAVY,(0,GAME_H-NEWS_H,GAME_W,NEWS_H))
        if self.gs.news: dt(surf,"  ·  ".join(self.gs.news[:4]),F_TINY,C_SUBTXT,8,GAME_H-NEWS_H+6)

    def _draw_topbar(self,surf):
        pygame.draw.rect(surf,C_NAVY,(0,0,GAME_W,TB))
        pt=self.gs.get_player_team()
        dt(surf,pt["name"],F_HEAD,C_ACCENT,10,6)
        day_name=self.gs.get_day_name()
        week=self.gs.current_day//7+1
        dt(surf,f"{week}. het – {day_name}",F_TINY,C_SUBTXT,10,28)
        for btn,key in self.tab_btns:
            btn.col=C_ACCENT if self.tab==key else C_PANEL2
            btn.tc=C_BG if self.tab==key else C_TEXT
            btn.draw(surf)
        self.btn_next.draw(surf)
        self.gear.draw(surf)
        if self.save_flash>0:
            dt(surf,"Mentve!",F_SMALL,C_ACCENT,GAME_W-120,TB+8)
            self.save_flash-=1

    def draw(self,surf):
        surf.fill(C_BG)
        if self.show_match and self.match_anim:
            if self.show_post_stats:
                self._draw_post_stats(surf)
            else:
                self.match_anim.draw(surf)
                if self.match_anim.done: self.tovabb_btn.draw(surf)
                else: self.back_btn.draw(surf)
            return
        self._draw_topbar(surf)
        if self.show_td:
            self._draw_team_detail(surf)
        elif self.tab=="csapat":  self._draw_csapat(surf)
        elif self.tab=="edzés":   self._draw_edzes(surf)
        elif self.tab=="taktika":
            self._draw_taktika(surf)
            self._draw_tactic_tooltip(surf)
        elif self.tab=="tabella": self._draw_tabella(surf)
        elif self.tab=="meccsek": self._draw_meccsek(surf)
        pygame.draw.rect(surf,C_NAVY,(0,GAME_H-NEWS_H,GAME_W,NEWS_H))
        if self.gs.news: dt(surf,"  .  ".join(self.gs.news[:4]),F_TINY,C_SUBTXT,8,GAME_H-NEWS_H+6)
        # GearMenu legfelülre rajzolva, hogy a legördülő menü ne kerüljön hátra
        self.gear.draw(surf)

    def update(self,gx,gy):
        for btn,_ in self.tab_btns: btn.upd(gx,gy)
        self.btn_next.upd(gx,gy); self.gear.upd(gx,gy)
        if self.show_match and self.match_anim:
            if not self.show_post_stats:
                self.match_anim.update()
                if self.match_anim.done: self.tovabb_btn.upd(gx,gy)
                else: self.back_btn.upd(gx,gy)
        if hasattr(self,"_back_btn2"): self._back_btn2.upd(gx,gy)
        if self.tab=="taktika": self._update_tactic_hover(gx,gy)

    def handle(self,ev,gx,gy):
        if self.show_match and self.match_anim:
            if self.show_post_stats:
                if self.tovabb_btn.hit(ev,gx,gy):
                    self.show_match=False; self.show_post_stats=False
                    self.match_anim._stats_scroll=0; return
                # Scroll in others tab
                if ev.type==pygame.MOUSEBUTTONDOWN:
                    if ev.button==4: self.match_anim._stats_scroll=max(0,self.match_anim._stats_scroll-35); return
                    if ev.button==5: self.match_anim._stats_scroll=min(600,self.match_anim._stats_scroll+35); return
                if hasattr(pygame,'MOUSEWHEEL') and ev.type==pygame.MOUSEWHEEL:
                    self.match_anim._stats_scroll=max(0,min(600,self.match_anim._stats_scroll-ev.y*35)); return
                # Tab clicks ONLY on actual click (not hover)
                if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                    tabs=[("📋 Meccslap","match"),("📰 Többi meccs","others")]
                    for i,(_,key) in enumerate(tabs):
                        if pygame.Rect(20+i*160,64,154,28).collidepoint(gx,gy):
                            self.match_anim._stats_tab=key
                            self.match_anim._stats_scroll=0; return
                return
            if self.match_anim.done and self.tovabb_btn.hit(ev,gx,gy):
                # Apply result then show post-match stats
                self.gs.apply_match_result(self.match_anim.sh, self.match_anim.sa)
                self.gs.save_match_stats(self.match_anim)
                self.show_post_stats=True; return
            if not self.match_anim.done and self.back_btn.hit(ev,gx,gy):
                # Szimuláld le a hátralévő perceket és mentsd az eredményt
                ma = self.match_anim
                cur_sh, cur_sa = ma.sh, ma.sa
                max_frames = 300 * 60  # max 300 mp szimulálás
                sim_count = 0
                while not ma.done and sim_count < max_frames:
                    try: ma.update()
                    except: break
                    sim_count += 1
                # A végeredmény góljai csak több lehet, mint a kilépéskor
                final_sh = max(cur_sh, ma.sh)
                final_sa = max(cur_sa, ma.sa)
                ma.sh = final_sh; ma.sa = final_sa
                self.gs.apply_match_result(final_sh, final_sa)
                self.gs.save_match_stats(ma)
                self.show_match=False; return
            if not self.match_anim.done:
                self.match_anim.handle_event(ev,gx,gy)
            return
        gr=self.gear.handle(ev,gx,gy)
        if gr=="save": self.gs.save(SAVE_PATH); self.save_flash=90
        elif gr=="newgame":
            return "newgame"
        elif gr=="quit":
            try: self.gs.save(SAVE_PATH)
            except: pass
            pygame.quit(); sys.exit()
        if gr: return
        if self.btn_next.hit(ev,gx,gy):
            ism=self.gs.is_matchday(); self.gs.next_day()
            if ism and self.gs.last_match_events:
                pt=self.gs.get_player_team(); pid=self.gs.player_team_id
                rr=self.gs.last_round_results
                sp_takers=pt.get("set_piece_takers",{})
                if self.gs.last_match_events.get('home_id')==pid:
                    self.match_anim=MatchAnim(self.gs.last_match_events,self.gs,
                                              lineup_h=self.field_p if self.field_p else None,
                                              round_results=rr, set_piece_takers=sp_takers)
                else:
                    self.match_anim=MatchAnim(self.gs.last_match_events,self.gs,
                                              lineup_a=self.field_p if self.field_p else None,
                                              round_results=rr, set_piece_takers=sp_takers)
                self.show_match=True
            return
        for btn,key in self.tab_btns:
            if btn.hit(ev,gx,gy): self.tab=key; self.show_td=False; return
        if self.tab=="taktika" and self.tact_tab=="felallas":
            # Handle group dropdown
            rg=self.form_group_dd.handle(ev,gx,gy)
            if rg is not None:
                self._cur_group=self._fg_names[rg]
                group_forms=FORMATION_GROUPS[self._cur_group]
                self.form_dd.opts=group_forms; self.form_dd.sel=0
                self.formation=group_forms[0]
                self.gs.get_player_team()["formation"]=self.formation
                self.field_p.clear(); return
            # Handle formation dropdown
            r=self.form_dd.handle(ev,gx,gy)
            if r is not None:
                group_forms=FORMATION_GROUPS[self._cur_group]
                self.formation=group_forms[r]
                self.gs.get_player_team()["formation"]=self.formation
                self.field_p.clear(); return
        if self.tab=="tabella" and self.show_td: self._handle_team_detail(ev,gx,gy)
        elif self.tab=="csapat":  self._handle_csapat(ev,gx,gy)
        elif self.tab=="edzés":   self._handle_edzes(ev,gx,gy)
        elif self.tab=="taktika": self._handle_taktika(ev,gx,gy)
        elif self.tab=="tabella": self._handle_tabella(ev,gx,gy)
        elif self.tab=="meccsek": self._handle_meccsek(ev,gx,gy)

    def _handle_csapat(self,ev,gx,gy):
        rh=48; gap=2; lw=222
        list_y0=TB+26; vis_h=GAME_H-TB-NEWS_H-26
        pt=self.gs.get_player_team()
        total_h=len(pt["players"])*(rh+gap)
        ms=max(0,total_h-vis_h)
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and gx<lw:
            y=list_y0-self.pscroll
            for p in pt["players"]:
                if pygame.Rect(4,y,lw-8,rh).collidepoint(gx,gy):
                    self.sel_p=p; return
                y+=rh+gap
        if ev.type==pygame.MOUSEWHEEL and gx<lw:
            self.pscroll=max(0,min(ms,self.pscroll-ev.y*25))

    def _handle_edzes(self,ev,gx,gy):
        day=self.train_day; title_y=TB+46; clip_y=title_y+26; rh=38
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            for i,db in enumerate(self.day_btns):
                if db.rect.collidepoint(gx,gy): self.train_day=DAYS[i]; return
            if day=="Szombat": return
            pt=self.gs.get_player_team(); y=clip_y-self.pscroll2
            for p in pt["players"]:
                if y>GAME_H-NEWS_H-4: break
                if y>clip_y-4 and pygame.Rect(10,y,GAME_W-20,rh-2).collidepoint(gx,gy):
                    is_gk=p.get("is_gk",False)
                    tr_skills=get_trainable_skills(is_gk)
                    cur=p.get("personal_training","reflexek" if is_gk else "passz")
                    idx=tr_skills.index(cur) if cur in tr_skills else 0
                    self.gs.set_personal_training(p,tr_skills[(idx+1)%len(tr_skills)]); return
                y+=rh
        if ev.type==pygame.MOUSEWHEEL:
            pt=self.gs.get_player_team(); ms=max(0,len(pt["players"])*rh-(GAME_H-clip_y-NEWS_H-4))
            self.pscroll2=max(0,min(ms,self.pscroll2-ev.y*20))

    def _handle_taktika(self,ev,gx,gy):
        # Fül váltás
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            for i,(_,key) in enumerate([("Felállás","felallas"),("Rögzített helyzetek","rogzitett")]):
                if pygame.Rect(10+i*185,TB+8,178,30).collidepoint(gx,gy):
                    self.tact_tab=key; return
        
        if self.tact_tab=="felallas":
            sbx=582; y0=TB+46
            pr=pygame.Rect(8,y0,sbx-12,GAME_H-y0-NEWS_H-4)
            slot_radius = 16
            
            # Egérgomb lenyomás
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                # 1. Játékos listából húzás
                if gx>sbx:
                    pt=self.gs.get_player_team(); rh=36; y=TB+82-self.tscroll
                    for p in pt["players"]:
                        if y>GAME_H-NEWS_H-6: break
                        if y>TB+78 and pygame.Rect(sbx+3,y,GAME_W-sbx-6,rh-2).collidepoint(gx,gy):
                            self.drag_p=p; return
                        y+=rh
                
                # 2. Pozícióról húzás (GK nem húzható!)
                for pos in self.tactic_positions:
                    if not pos["occupied"]:
                        continue
                    if pos["row"] == "gk":  # Kapust NEM lehet húzni
                        continue
                    px = pr.x + pr.width * pos["x"]
                    py = pr.y + pr.height * pos["y"]
                    dist = ((gx-px)**2 + (gy-py)**2)**0.5
                    
                    if dist < slot_radius + 5:
                        player = self.field_p.get(pos["id"])
                        if player:
                            self.drag_p = player
                            del self.field_p[pos["id"]]
                        else:
                            self.drag_slot = pos
                        return
            
            # Egérgomb felengedés
            if ev.type==pygame.MOUSEBUTTONUP and ev.button==1:
                if self.drag_p:
                    closest_slot = None
                    min_dist = 999999
                    drag_is_gk = self.drag_p.get("is_gk", False)
                    
                    for pos in self.tactic_positions:
                        if not pos["occupied"]:
                            continue
                        # Kapus csak GK slotba, nem-kapus csak nem-GK slotba
                        if drag_is_gk and pos["row"] != "gk":
                            continue
                        if not drag_is_gk and pos["row"] == "gk":
                            continue
                        px = pr.x + pr.width * pos["x"]
                        py = pr.y + pr.height * pos["y"]
                        dist = ((gx-px)**2 + (gy-py)**2)**0.5
                        if dist < min_dist and dist < 50:
                            min_dist = dist
                            closest_slot = pos
                    
                    if closest_slot:
                        for slot_id in list(self.field_p.keys()):
                            if self.field_p.get(slot_id,{}).get("name") == self.drag_p["name"]:
                                del self.field_p[slot_id]
                        self.field_p[closest_slot["id"]] = self.drag_p
                    
                    self.drag_p = None
                
                elif self.drag_slot:
                    # Pozíció mozgatás - legközelebbi nem foglalt helyre
                    closest_empty = None
                    min_dist = 999999
                    
                    for pos in self.tactic_positions:
                        if pos["occupied"] or pos["row"] == "gk":  # Már foglalt vagy kapus
                            continue
                        px = pr.x + pr.width * pos["x"]
                        py = pr.y + pr.height * pos["y"]
                        dist = ((gx-px)**2 + (gy-py)**2)**0.5
                        
                        if dist < min_dist and dist < 50:
                            min_dist = dist
                            closest_empty = pos
                    
                    if closest_empty:
                        # Csere: régi slot nem elfoglalt, új slot elfoglalt
                        self.drag_slot["occupied"] = False
                        closest_empty["occupied"] = True
                        
                        # Ha volt játékos a régi slotban, átrakjuk
                        if self.drag_slot["id"] in self.field_p:
                            player = self.field_p[self.drag_slot["id"]]
                            del self.field_p[self.drag_slot["id"]]
                            self.field_p[closest_empty["id"]] = player
                    
                    self.drag_slot = None
            
            # Görgetés
            if ev.type==pygame.MOUSEWHEEL and gx>sbx:
                pt=self.gs.get_player_team()
                ms=max(0,len(pt["players"])*36-(GAME_H-TB-NEWS_H-120))
                self.tscroll=max(0,min(ms,self.tscroll-ev.y*20))
        
        else:
            # Rögzített helyzetek
            pt=self.gs.get_player_team()
            sp=pt.setdefault("set_piece_takers",{"corner":"","freekick":"","throwin":"","penalty":""})
            types=[("corner","Szöglet"),("freekick","Szabadrúgás"),
                   ("throwin","Bedobás"),("penalty","Tizenegyes")]
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEWHEEL):
                for key,_ in types:
                    if key in self._sp_dds:
                        res=self._sp_dds[key].handle(ev,gx,gy)
                        if res is not None:
                            chosen=self._sp_dds[key].opts[self._sp_dds[key].sel]
                            sp[key]="" if chosen=="(nincs)" else chosen
                            return
    
    def _handle_tabella(self,ev,gx,gy):
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            standings=self.gs.get_standings(); hy=TB+6; rh=28
            for rank,t in enumerate(standings):
                y=hy+32+rank*rh
                if pygame.Rect(4,y,GAME_W-8,rh-1).collidepoint(gx,gy):
                    self.sel_tid=t["id"]; self.show_td=True; self.team_sub="jatekosok"; self.td_scroll=0; return

    def _handle_team_detail(self,ev,gx,gy):
        team=next((t for t in self.gs.teams if t["id"]==self.sel_tid),None)
        if not team: return
        lw=222; rh=42
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            if hasattr(self,"_back_btn2") and self._back_btn2.rect.collidepoint(gx,gy):
                self.show_td=False; self.td_sel_p=None; return
            # Játékos kattintás a bal listában
            ly=TB+26-self.td_scroll
            for p in team["players"]:
                if ly>GAME_H-NEWS_H-4: break
                if ly>TB and pygame.Rect(4,ly,lw-8,rh).collidepoint(gx,gy):
                    self.td_sel_p=p; return
                ly+=rh+2
        if ev.type==pygame.MOUSEWHEEL and gx<lw:
            ms=max(0,len(team["players"])*(rh+2)-(GAME_H-TB-NEWS_H-60))
            self.td_scroll=max(0,min(ms,self.td_scroll-ev.y*20))

def main():
    global screen
    screen=pygame.display.set_mode((GAME_W,GAME_H),pygame.RESIZABLE)
    pygame.display.set_caption("⚽ Foci Manager")
    clock=pygame.time.Clock()
    gs=GameState(); menu=MenuScreen(); name=NameScreen(); main_s=None; cur="menu"
    while True:
        gx,gy=game_mouse()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                if main_s:
                    try: gs.save(SAVE_PATH)
                    except: pass
                pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                if main_s and main_s.show_match: main_s.show_match=False
            if cur=="menu":
                r=menu.handle(ev,gx,gy)
                if r=="new": cur="name"
                elif r=="load": gs.load(SAVE_PATH); main_s=MainScreen(gs); cur="main"
                elif r=="quit": pygame.quit(); sys.exit()
            elif cur=="name":
                r=name.handle(ev,gx,gy)
                if r:
                    if isinstance(r, tuple):
                        team_name, kit = r
                        gs.start_team_mode(team_name, kit_colors=kit)
                    else:
                        gs.start_team_mode(r)
                    main_s=MainScreen(gs); cur="main"
            elif cur=="main":
                result=main_s.handle(ev,gx,gy)
                if result=="newgame":
                    name=NameScreen(); cur="name"
        if cur=="menu": menu.upd(gx,gy)
        elif cur=="name": name.upd(gx,gy)
        elif cur=="main": main_s.update(gx,gy)
        if cur=="menu": menu.draw(GAME_SURF)
        elif cur=="name": name.draw(GAME_SURF)
        elif cur=="main": main_s.draw(GAME_SURF)
        scale_and_blit(); pygame.display.flip(); clock.tick(FPS)

if __name__=="__main__":
    main()

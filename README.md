# ⚽ Foci Manager

Egy teljes értékű foci menedzser játék Pygame alapon, Linux-on futtatható.

## Telepítés

```bash
pip install pygame
# vagy
pip3 install pygame --break-system-packages
```

## Indítás

```bash
cd focimanager
python3 main.py
# vagy
chmod +x play.sh && ./play.sh
```

## Játékmódok

### Team mód
- Add meg csapatod nevét
- Irányítsd az egész csapatot
- 20 csapatos bajnokság, 38 meccs/szezon

## Funkciók

### 📋 Csapat menü
- Minden játékos listázva
- Kattints a nevükre → skill profil megnyílik
- Zöld ↑ jelzi a fejlődést

### 🏃 Edzés menü
- 7 napos edzésprogram (hétfő-vasárnap)
- Szombat = meccsnap, nincs edzés
- Naponta 3 edzéssession
- Minden sessiont kattintással lehet váltani (8 skill + kondi)
- Személyi edzés beállítható játékosonként
- Ha a személyi edzés = csapatedzés → 1.3x gyorsabb fejlődés

### 🎯 Taktika menü
- 9 felállás választható (4-4-2, 4-3-3, stb.)
- Játékosok drag & drop-pal helyezhetők el a pályán
- Jobb oldali lista → balra a pályára húzd

### 🏆 Tabella
- Élő tabella, pontok, gólkülönbség szerint rendezve
- Saját csapat arannyal kiemelve

### ⚽ Meccsek
- Minden szombat meccs szimulálódik
- Saját meccset 7 perces animációban lehet végignézni
- Mozgó játékosok, labda, eredménytábla, eseménynapló

## Fejlődési rendszer
- Minden játékos 17 évesen indul
- 1 skillpont = 20 edzés (17 éves korban)
- +5 edzés szükséges minden életkorévvel
- Szezon végén automatikusan öregszenek a játékosok

## Pozíciók és skillek

| Pozíció | Elsődleges | Másodlagos |
|---------|-----------|-----------|
| Kapus | Kapusteljesítmény | Állóképesség, Szabadrúgás |
| Szélsőhátvéd | Védés, Szélső | Állóképesség, Passz |
| Középsőhátvéd | Védés, Állóképesség | Passz, Játékszervezés |
| Szélső | Szélső, Állóképesség | Passz, Játékszervezés |
| Véd. középpályás | Védés, Játékszervezés | Állóképesség, Passz |
| Közép. középpályás | Passz, Játékszervezés | Állóképesség, Lövés |
| Tám. középpályás | Játékszervezés, Lövés | Állóképesség, Passz |
| Csatár | Lövés, Állóképesség | Passz, Játékszervezés |

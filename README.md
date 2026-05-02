# ⚽ Foci Manager

Egy kis amatőr foci menedzser játék Pygame alapon.

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

### Alap mód
- Add meg csapatod nevét
- Mezeik színét
- 20 csapatos bajnokság, 38 meccs/szezon

## Funkciók

### 📋 Csapat menü
- Minden játékos listázva
- Kattints a nevükre → skill profil megnyílik
- Zöld ↑ jelzi a fejlődést

### 🏃 Edzés menü
- 7 napos edzésprogram (hétfő-vasárnap)
- Szombat = meccsnap, nincs edzés
- Minden sessiont kattintással lehet váltani
- Személyi edzés beállítható játékosonként

### 🎯 Taktika menü
- Dinamikus felállás
- Játékosok drag & drop-pal helyezhetők el a pályán
- Jobb oldali lista → balra a pályára húzd

### 🏆 Tabella
- Élő tabella, pontok, gólkülönbség szerint rendezve
- Saját csapat kiemelve

### ⚽ Meccsek
- Minden szombat meccs szimulálódik
- Saját meccset 7 perces animációban lehet végignézni
- Mozgó játékosok, labda, eredménytábla, eseménynapló

## Fejlődési rendszer
- Minden játékos Random generált (15-35 éves korig)
- 28 éves korukig fejlődnek a játékosok, utána lassú hanyatlás
- Szezon végén automatikusan öregszenek a játékosok

| Csatár | Lövés, Állóképesség | Passz, Játékszervezés |

#!/bin/bash

# 1. Import javítás
sed -i '3s/.*/from data import (OUTFIELD_SKILLS, OUTFIELD_LABELS, OUTFIELD_SHORT,\n                  GK_SKILLS, GK_LABELS, GK_SHORT,\n                  FORMATIONS, FORMATION_ROWS, FORMATION_GROUPS, auto_lineup)/' main.py
sed -i '4s/.*/from training import DAYS, get_trainable_skills, get_trainable_labels/' main.py

# 2. AMATŐR FOCI MANAGER törlése (csak a NameScreen-ből, 365. sor körül)
sed -i '365,370s/dtc(surf,"AMATŐR FOCI MANAGER",F_HEAD,C_TEXT,GAME_W\/\/2,100)/# Title removed/' main.py

# 3. _training_dds inicializálás a _build-ben (420. sor körül)
sed -i '/self\.tact_tab="felallas"/a\        self._training_dds={}  # Edzés dropdown-ok' main.py

echo "Alapvető javítások alkalmazva!"

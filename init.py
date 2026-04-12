import os

import database.database as db

# Create directory and parent directories if needed
os.makedirs(db.ORDNER_EINGABE, exist_ok=True)
os.makedirs(db.ORDNER_AUSGABE, exist_ok=True)
os.makedirs(os.path.join(db.ORDNER_AUSGABE, db.ORDNER_AUSGABE_GRAFIK), exist_ok=True)
os.makedirs(os.path.join(db.ORDNER_AUSGABE, db.ORDNER_JAHRESBERICHT), exist_ok=True)

import json
import sqlite3
import glob
import re

# Trouve la BDD locale
files = glob.glob(".wrangler/state/v3/d1/**/*.sqlite", recursive=True)
db_path = files[0]
print(f"BDD: {db_path}")

con = sqlite3.connect(db_path)
cur = con.cursor()

with open("scripts/vehicules_complet.json", encoding="utf-8") as f:
    fiches = json.load(f)

def normalize(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

updated = 0
not_found = 0

for fiche in fiches:
    marque = fiche["marque"]
    titre = fiche["titre"]

    # Extrait le nom du modèle depuis le titre
    # "Fiche technique Renault Megane 3 (2008-2015)" → "Megane 3"
    titre_clean = re.sub(r'Fiche technique\s*', '', titre, flags=re.I)
    titre_clean = re.sub(r'\(.*?\)', '', titre_clean).strip()
    # Retire le nom de la marque du début
    for word in marque.split("-"):
        titre_clean = re.sub(rf'^{word}\s*', '', titre_clean, flags=re.I)
    modele_name = titre_clean.strip()

    # Cherche le model_slug correspondant
    brand_row = cur.execute(
        "SELECT id FROM brands WHERE slug = ?", (marque,)
    ).fetchone()

    if not brand_row:
        # Essaie avec le nom
        brand_row = cur.execute(
            "SELECT id FROM brands WHERE LOWER(name) = LOWER(?)", (marque,)
        ).fetchone()

    if not brand_row:
        not_found += 1
        continue

    brand_id = brand_row[0]

    # Cherche le modèle (correspondance approximative)
    models = cur.execute(
        "SELECT id, name, slug FROM models WHERE brand_id = ?", (brand_id,)
    ).fetchall()

    best_model = None
    best_score = 0
    norm_titre = normalize(modele_name)

    for model_id, model_name, model_slug in models:
        norm_model = normalize(model_name)
        # Score de similarité simple
        if norm_model == norm_titre:
            best_model = model_id
            best_score = 100
            break
        elif norm_model in norm_titre or norm_titre in norm_model:
            score = len(norm_model) / max(len(norm_titre), 1) * 80
            if score > best_score:
                best_score = score
                best_model = model_id

    if best_model and best_score > 30:
        # Stocke le JSON (sans le champ distribution redondant pour économiser)
        payload = {
            "titre": fiche["titre"],
            "periode": fiche["periode"],
            "dims": fiche["dims"],
            "pneus": fiche["pneus"],
            "moteurs": fiche["moteurs"],
        }
        cur.execute(
            "UPDATE models SET fiche_json = ? WHERE id = ?",
            (json.dumps(payload, ensure_ascii=False), best_model)
        )
        updated += 1
    else:
        not_found += 1

con.commit()
con.close()

print(f"✅ {updated} modèles mis à jour")
print(f"⚠️  {not_found} non trouvés")

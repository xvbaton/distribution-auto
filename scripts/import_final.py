import json
import sqlite3
import glob
import os

# 1. Trouver la BDD locale Wrangler
files = glob.glob(".wrangler/state/v3/d1/**/*.sqlite", recursive=True)
if not files:
    print("❌ BDD locale introuvable.")
    exit(1)
db_path = files[0]
print(f"📦 Utilisation de la BDD : {db_path}")

con = sqlite3.connect(db_path)
cur = con.cursor()

# 2. Charger la base fusionnée
with open("scripts/db_finale_fusionnee.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"📖 Chargement de {len(data)} modèles fusionnés...")

# 3. Nettoyage
cur.execute("DELETE FROM engines")
cur.execute("DELETE FROM models")
cur.execute("DELETE FROM brands")
cur.execute("DELETE FROM sqlite_sequence WHERE name IN ('brands', 'models', 'engines')")

brands_cache = {}

for entry in data:
    brand_name = entry["marque"]
    # Nettoyage marque : "alfa-romeo" -> "Alfa Romeo"
    brand_display = brand_name.replace("-", " ").title()
    brand_slug = brand_name.lower()
    
    if brand_slug not in brands_cache:
        cur.execute("INSERT OR IGNORE INTO brands (slug, name) VALUES (?, ?)", (brand_slug, brand_display))
        cur.execute("SELECT id FROM brands WHERE slug = ?", (brand_slug,))
        brands_cache[brand_slug] = cur.fetchone()[0]
    
    brand_id = brands_cache[brand_slug]
    
    model_name = entry["model_name"] # Contient maintenant les années
    model_slug = entry["model_slug"]
    
    # Insert Modèle
    cur.execute("""
        INSERT INTO models (brand_id, slug, name, fiche_json) 
        VALUES (?, ?, ?, ?)
    """, (brand_id, model_slug, model_name, json.dumps(entry, ensure_ascii=False)))
    
    model_id = cur.lastrowid
    
    # Insert Moteurs
    for m in entry["moteurs"]:
        cur.execute("""
            INSERT INTO engines (model_id, periode, moteur, distribution, puissance_ch, entretien_km, entretien_ans)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            model_id, 
            entry["periode"], 
            m["Moteur"], 
            m.get("distribution") or "—", 
            m.get("Puiss.") or "—",
            m.get("entretien_km") or "—",
            m.get("entretien_ans") or "—"
        ))

con.commit()
con.close()
print("✅ Importation V3 terminée avec succès !")

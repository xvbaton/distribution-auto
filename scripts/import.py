import json, sqlite3, os, glob

# Trouve le fichier SQLite local de Wrangler
pattern = ".wrangler/state/v3/d1/**/*.sqlite"
files = glob.glob(pattern, recursive=True)
if not files:
    print("❌ BDD locale introuvable, lance 'd'abord: npx wrangler d1 execute distribution-auto --local --file=schema.sql'")
    exit(1)

db_path = files[0]
print(f"BDD trouvée : {db_path}")

con = sqlite3.connect(db_path)
cur = con.cursor()

with open("scripts/chaine_courroie_clean.json", encoding="utf-8") as f:
    data = json.load(f)

brands, models = {}, {}

for d in data:
    # Brand
    if d["brand_slug"] not in brands:
        cur.execute("INSERT OR IGNORE INTO brands (slug, name) VALUES (?,?)",
                    (d["brand_slug"], d["marque"]))
        con.commit()
        row = cur.execute("SELECT id FROM brands WHERE slug=?", (d["brand_slug"],)).fetchone()
        brands[d["brand_slug"]] = row[0]

    brand_id = brands[d["brand_slug"]]
    key = d["model_slug"]

    if key not in models:
        cur.execute("INSERT OR IGNORE INTO models (brand_id, slug, name) VALUES (?,?,?)",
                    (brand_id, d["model_slug"], d["modele"]))
        con.commit()
        row = cur.execute("SELECT id FROM models WHERE brand_id=? AND slug=?",
                          (brand_id, d["model_slug"])).fetchone()
        models[key] = row[0]

    model_id = models[key]
    cur.execute("""
        INSERT INTO engines (model_id, periode, moteur, distribution, puissance_ch, entretien_km, entretien_ans)
        VALUES (?,?,?,?,?,?,?)
    """, (model_id, d["periode"], d["moteur"], d["distribution"],
          d["puissance_ch"], d["entretien_km"], d["entretien_ans"]))

con.commit()
con.close()
print(f"✅ {len(brands)} marques, {len(models)} modèles, {len(data)} motorisations importées")

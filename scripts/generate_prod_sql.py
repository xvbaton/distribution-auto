import json

def escape_sql(text):
    if text is None: return "NULL"
    return "'" + str(text).replace("'", "''") + "'"

with open("scripts/db_finale_fusionnee.json", "r", encoding="utf-8") as f:
    data = json.load(f)

sql_commands = [
    "DELETE FROM engines;",
    "DELETE FROM models;",
    "DELETE FROM brands;",
    "DELETE FROM sqlite_sequence WHERE name IN ('brands', 'models', 'engines');"
]

brands_cache = {}
brand_id_counter = 1
model_id_counter = 1

for entry in data:
    brand_name = entry["marque"]
    brand_slug = brand_name.lower()
    brand_display = brand_name.replace("-", " ").title()
    
    if brand_slug not in brands_cache:
        sql_commands.append(f"INSERT INTO brands (id, slug, name) VALUES ({brand_id_counter}, {escape_sql(brand_slug)}, {escape_sql(brand_display)});")
        brands_cache[brand_slug] = brand_id_counter
        brand_id_counter += 1
    
    brand_id = brands_cache[brand_slug]
    model_name = entry["model_name"]
    model_slug = entry["model_slug"]
    fiche_json = json.dumps(entry, ensure_ascii=False)
    
    sql_commands.append(f"INSERT INTO models (id, brand_id, slug, name, fiche_json) VALUES ({model_id_counter}, {brand_id}, {escape_sql(model_slug)}, {escape_sql(model_name)}, {escape_sql(fiche_json)});")
    
    for m in entry["moteurs"]:
        dist = m.get("distribution") or "—"
        puiss = m.get("Puiss.") or "—"
        km = m.get("entretien_km") or "—"
        ans = m.get("entretien_ans") or "—"
        
        sql_commands.append(f"INSERT INTO engines (model_id, periode, moteur, distribution, puissance_ch, entretien_km, entretien_ans) VALUES ({model_id_counter}, {escape_sql(entry['periode'])}, {escape_sql(m['Moteur'])}, {escape_sql(dist)}, {escape_sql(puiss)}, {escape_sql(km)}, {escape_sql(ans)});")
    
    model_id_counter += 1

with open("scripts/production_update.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(sql_commands))

print(f"✅ Fichier scripts/production_update.sql généré avec {len(sql_commands)} commandes.")

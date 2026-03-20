import json
from collections import defaultdict

with open("chaine_courroie.json", encoding="utf-8") as f:
    data = json.load(f)

# 1. Vire les fausses marques
fausses_marques = {"Moteur 1.2 Dualjet Suzuki", "Moteur Fiat 1.2 69 ch", "Moteur Mercedes 220 CDI", "BMW 218d"}
data = [d for d in data if d["marque"] not in fausses_marques]

# 2. Fusionne les doublons km/années → entretien_km + entretien_ans
groupes = defaultdict(list)
for d in data:
    key = (d["marque"], d["modele"], d["periode"], d["moteur"], d["distribution"], d["puissance_ch"])
    groupes[key].append(d["entretien_km"])

clean = []
seen = set()
for d in data:
    key = (d["marque"], d["modele"], d["periode"], d["moteur"], d["distribution"], d["puissance_ch"])
    if key in seen:
        continue
    seen.add(key)

    valeurs = groupes[key]
    km  = next((v for v in valeurs if "km" in v.lower()), "-")
    ans = next((v for v in valeurs if "an" in v.lower()), "-")

    d["entretien_km"]  = km
    d["entretien_ans"] = ans
    clean.append(d)

# 3. Catégorise la distribution
for d in clean:
    dist = d["distribution"]
    if dist == "-":
        moteur = d["moteur"].lower()
        if any(x in moteur for x in ["électrique", "ev", "electric"]):
            d["distribution"] = "N/A (électrique)"
        else:
            d["distribution"] = "INCONNU"

print(f"Avant: {len(data)} → Après: {len(clean)} entrées")
print(f"Distributions: { {d['distribution'] for d in clean} }")

with open("chaine_courroie_clean.json", "w", encoding="utf-8") as f:
    json.dump(clean, f, ensure_ascii=False, indent=2)

import csv
fields = ["marque","modele","periode","moteur","distribution","puissance_ch","entretien_km","entretien_ans","brand_slug","model_slug"]
with open("chaine_courroie_clean.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(clean)

print("✅ chaine_courroie_clean.csv + .json")
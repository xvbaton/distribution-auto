import requests
from bs4 import BeautifulSoup
import csv
import json
import time

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

BASE = "https://chaine-courroie.com"

def get_brands():
    r = SESSION.get(f"{BASE}/")
    soup = BeautifulSoup(r.text, "html.parser")
    brands = []
    for a in soup.select("a[href*='/distribution-vehicules/']"):
        href = a["href"]
        slug = href.replace("/distribution-vehicules/", "").strip("/")
        if slug and "/" not in slug:
            name = a.get_text(strip=True)
            if name and (slug, name) not in [(b["slug"], b["name"]) for b in brands]:
                brands.append({"slug": slug, "name": name})
    return brands

def get_models(brand_slug):
    r = SESSION.get(f"{BASE}/distribution-vehicules/{brand_slug}")
    soup = BeautifulSoup(r.text, "html.parser")
    models = []
    for a in soup.select(f"a[href*='/distribution-vehicules/{brand_slug}/']"):
        href = a["href"]
        parts = href.strip("/").split("/")
        if len(parts) == 3:  # distribution-vehicules/brand/model
            model_slug = parts[2]
            name = a.get_text(strip=True)
            if name and model_slug not in [m["slug"] for m in models]:
                models.append({"slug": model_slug, "name": name})
    return models

def scrape_model(brand_slug, brand_name, model_slug, model_name):
    r = SESSION.get(f"{BASE}/distribution-vehicules/{brand_slug}/{model_slug}")
    soup = BeautifulSoup(r.text, "html.parser")
    rows = []

    table = soup.find("table")
    if not table:
        return []

    for tr in table.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) >= 5:
            rows.append({
                "marque":        brand_name,
                "modele":        model_name,
                "brand_slug":    brand_slug,
                "model_slug":    model_slug,
                "periode":       cells[0],
                "moteur":        cells[1],
                "distribution":  cells[2],  # CHAÎNE ou COURROIE
                "puissance_ch":  cells[3],
                "entretien_km":  cells[4],
            })
    return rows

# ============================================================
print("Récupération des marques...")
brands = get_brands()
print(f"  {len(brands)} marques : {[b['name'] for b in brands[:5]]}...")

all_data = []

for bi, brand in enumerate(brands):
    print(f"\n[{bi+1}/{len(brands)}] {brand['name']}")
    models = get_models(brand["slug"])
    print(f"  {len(models)} modèles")

    for model in models:
        print(f"    {model['name']}...", end=" ", flush=True)
        rows = scrape_model(brand["slug"], brand["name"], model["slug"], model["name"])
        all_data.extend(rows)
        print(f"✓ {len(rows)} motorisations")
        time.sleep(0.3)

    time.sleep(0.5)

# Export CSV
with open("chaine_courroie.csv", "w", newline="", encoding="utf-8-sig") as f:
    fields = ["marque","modele","periode","moteur","distribution","puissance_ch","entretien_km","brand_slug","model_slug"]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(all_data)

# Export JSON
with open("chaine_courroie.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ {len(all_data)} entrées → chaine_courroie.csv + .json")
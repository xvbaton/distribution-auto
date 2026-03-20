import requests
import json
import csv
import re
import time

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0",
    "Accept": "text/x-component",
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://www.autoestim.com",
    "Referer": "https://www.autoestim.com/",
    "next-router-state-tree": '%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
})

BASE = "https://www.autoestim.com"

ACTIONS = {
    "get_models":   "40cca03ad9b66eb94b65c8a7e54fb60c3f73dd3a8e",
    "get_years":    "40ffe767793426502d93b2213d21afba5f2d748eb2",
    "get_energies": "605d5e4190151f27ac3d59dd7d12ba6f75b9f11ec7",
    "get_versions": "7095e9d0c7a98e09aa0becb0c6a12fc5d62142e917",
    "get_trims":    "784ce8388b0000718eb2378cc35bf3678e06950f3c",
}

def call_action(action_hash, payload):
    r = SESSION.post(
        BASE,
        data=json.dumps(payload),
        headers={"next-action": action_hash},
        timeout=20
    )
    return r.text

def extract_list(rsc_text):
    """Format: 0:{...meta...}\n1:[{value, label}, ...]"""
    for line in rsc_text.splitlines():
        m = re.match(r'^\w+:(\[.*)', line)
        if m:
            try:
                data = json.loads(m.group(1))
                if isinstance(data, list) and data and "value" in data[0]:
                    return data
            except:
                pass
    return []

def get_brands():
    r = SESSION.get(BASE, params={"_rsc": "1"}, headers={"next-url": "/", "rsc": "1"})
    matches = re.findall(r'\{"value":"([a-f0-9\-]{36})","label":"([^"]+)"\}', r.text)
    seen, brands = set(), []
    for val, label in matches:
        if val not in seen:
            seen.add(val)
            brands.append({"value": val, "label": label})
    return brands

# ============================================================
print("Récupération des marques...")
brands = get_brands()
# Retire les boîtes de vitesses (Manuelle/Automatique) qui matchent aussi
brands = [b for b in brands if b["label"] not in ("Manuelle", "Automatique")]
print(f"  {len(brands)} marques : {[b['label'] for b in brands[:5]]}...")

all_data = []

for bi, brand in enumerate(brands):
    print(f"\n[{bi+1}/{len(brands)}] {brand['label']}", flush=True)

    models = extract_list(call_action(ACTIONS["get_models"], [brand["value"]]))
    print(f"  → {len(models)} modèles")

    for model in models:
        years = extract_list(call_action(ACTIONS["get_years"], [model["value"]]))
        print(f"    {model['label']} : {len(years)} années", flush=True)

        for year_opt in years:
            year = year_opt["value"]

            energies = extract_list(call_action(ACTIONS["get_energies"], [model["value"], year]))

            for energy in energies:
                versions = extract_list(call_action(ACTIONS["get_versions"], [model["value"], year, energy["value"]]))

                for version in versions:
                    trims = extract_list(call_action(ACTIONS["get_trims"], [model["value"], year, energy["value"], version["value"]]))

                    for trim in trims:
                        all_data.append({
                            "marque":    brand["label"],
                            "modele":    model["label"],
                            "annee":     year,
                            "energie":   energy["label"],
                            "version":   version["label"],
                            "finition":  trim["label"],
                            "brand_id":  brand["value"],
                            "model_id":  model["value"],
                            "energy_id": energy["value"],
                            "version_id":version["value"],
                            "trim_id":   trim["value"],
                        })

                    time.sleep(0.15)
                time.sleep(0.15)
            time.sleep(0.2)
        time.sleep(0.2)

# Export
with open("autoestim_full.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

fields = ["marque","modele","annee","energie","version","finition","brand_id","model_id","energy_id","version_id","trim_id"]
with open("autoestim_full.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(all_data)

print(f"\n✅ {len(all_data)} combinaisons exportées → autoestim_full.csv + .json")
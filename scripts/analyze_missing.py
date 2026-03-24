import json
from collections import Counter

with open('scripts/db_finale_fusionnee.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = Counter()
total = Counter()

for entry in data:
    brand = entry['marque']
    for m in entry['moteurs']:
        total[brand] += 1
        if not m.get('distribution'):
            missing[brand] += 1

print("--- TOP DES MARQUES À COMPLÉTER ---")
for brand, count in missing.most_common(15):
    pct = (count / total[brand]) * 100
    print(f"{brand:15} : {count:3} manquants ({pct:.1f}%)")

Résumé du projet : Distribution Auto
Concept
Site de référence technique automobile permettant de savoir si un véhicule est équipé d'une chaîne ou d'une courroie de distribution, enrichi de données techniques complètes (pneus, dimensions, performances). Monétisation via AdSense + affiliation (Oscaro, Mister-Auto, iDGarage). Extension prévue en polonais.

Stack technique
ComposantTechnoFrontendAstro v6 (SSR, zéro JS inutile)Adapter@astrojs/cloudflareHébergementCloudflare Pages (free tier)Base de donnéesCloudflare D1 (SQLite serverless)DéploiementGitHub → Cloudflare CI/CD autoLangageTypeScript

Base de données D1
3 tables :
sqlbrands   (id, slug, name)
models   (id, brand_id, slug, name, fiche_json)
engines  (id, model_id, periode, moteur, distribution,
          puissance_ch, entretien_km, entretien_ans)
```

`fiche_json` stocke un blob JSON complet par modèle contenant dims, pneus, moteurs depuis fiches-auto.fr.

---

### Sources de données scrapées

**1. chaine-courroie.com** → table `engines`
- 2 679 entrées
- 37 marques, 795 modèles
- Champs : période, moteur, chaîne/courroie/courroie humide, entretien km + ans
- ⚠️ Qualité moyenne — slugs diesel séparés, puissances groupées en fourchettes aberrantes

**2. fiches-auto.fr** → colonne `fiche_json`
- 631 fiches techniques
- 38 marques
- Champs : dimensions (longueur, largeur, hauteur, empattement, poids, coffre), pneus avec scores confort/efficacité, moteurs avec puissance exacte / couple / Vmax / 0-100
- ✅ Qualité excellente, données structurées

**Taux de fusion entre les deux sources : 409/631 modèles (65%)**

---

### Pages existantes
```
/                              → Homepage avec grille des 37 marques
/distribution                  → Liste toutes les marques
/distribution/[marque]         → Modèles d'une marque
/distribution/[marque]/[modele] → Page principale (tableau distribution
                                  + pneus + dimensions + performances)
Contenu de la page modèle :

Badges chaîne/courroie
Tableau motorisations : moteur propre (depuis fiches-auto), boîte auto/manuelle, distribution, puissance exacte, 0-100, entretien
Tableau dimensions
Tableau pneus avec scores confort/efficacité
Trié par puissance croissante, dédoublonné


Logique de croisement des données
Sur la page modèle, les moteurs de fiches-auto (propres, puissance exacte, boîte) sont croisés avec les engines de chaine-courroie (distribution, entretien) via :

Correspondance cylindrée (1.2 dans les deux)
Correspondance puissance dans la fourchette ±5ch
Déduplication par clé (nom + puissance + boîte)
Détection électrique → colonnes décalées corrigées automatiquement


État actuel

✅ Site en ligne : distribution-auto.thomas-bruckert68.workers.dev
✅ BDD locale + remote synchronisées
✅ Pages fonctionnelles
✅ Données pneus et dimensions intégrées
⚠️ Qualité données distribution à améliorer — en cours d'investigation sur /moteurs/ de chaine-courroie.com (fiches par code moteur : K9K, R9M...) comme source de remplacement
❌ Sitemap / SEO non encore fait
❌ Pneus phase 2 (wheel-size payant, Kaggle non pertinent)
❌ Version polonaise
❌ Monétisation non configurée
❌ Nom de domaine non choisi


Prochaines étapes prioritaires

Scraper /moteurs/ de chaine-courroie.com → base propre par code moteur
Création d'une base de donnée complète par modèle
Sitemap + SEO (meta, schema.org, canonical)
Nom de domaine + config Cloudflare
AdSense + liens affiliés pièces détachées

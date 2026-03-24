import { env } from "cloudflare:workers";

export function getDB() {
  return (env as any).DB;
}

export async function getBrands(db: any) {
  const { results } = await db.prepare(
    "SELECT id, slug, name FROM brands ORDER BY name"
  ).all();
  return results;
}

export async function getBrand(db: any, slug: string) {
  return db.prepare(
    "SELECT id, slug, name FROM brands WHERE slug = ?"
  ).bind(slug).first();
}

export async function getModelsByBrand(db: any, brandId: number) {
  // Exclut les variantes diesel/rs/rs-diesel qui ont un modèle parent
  const { results } = await db.prepare(`
    SELECT id, slug, name FROM models
    WHERE brand_id = ?
    AND slug NOT LIKE '%-diesel'
    AND slug NOT LIKE '%-diesel-%'
    ORDER BY name
  `).bind(brandId).all();
  return results;
}

export async function getModel(db: any, brandId: number, slug: string) {
  return db.prepare(
    "SELECT id, slug, name, fiche_json FROM models WHERE brand_id = ? AND slug = ?"
  ).bind(brandId, slug).first();
}

export async function getEnginesByModel(db: any, modelId: number) {
  const { results } = await db.prepare(
    "SELECT * FROM engines WHERE model_id = ? ORDER BY periode"
  ).bind(modelId).all();
  return results;
}

// Récupère aussi les engines de la variante diesel si elle existe
export async function getAllEnginesForModel(db: any, brandId: number, slug: string) {
  // Slugs à chercher : le slug principal + éventuellement slug-diesel
  const slugs = [slug, `${slug}-diesel`];
  const placeholders = slugs.map(() => '?').join(',');
  
  const { results: models } = await db.prepare(
    `SELECT id FROM models WHERE brand_id = ? AND slug IN (${placeholders})`
  ).bind(brandId, ...slugs).all();
  
  if (!models.length) return [];
  
  const modelIds = models.map((m: any) => m.id);
  const idPlaceholders = modelIds.map(() => '?').join(',');
  
  const { results } = await db.prepare(
    `SELECT * FROM engines WHERE model_id IN (${idPlaceholders}) ORDER BY periode`
  ).bind(...modelIds).all();
  
  return results;
}

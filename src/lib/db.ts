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
  const { results } = await db.prepare(
    "SELECT id, slug, name FROM models WHERE brand_id = ? ORDER BY name"
  ).bind(brandId).all();
  return results;
}

export async function getModel(db: any, brandId: number, slug: string) {
  return db.prepare(
    "SELECT id, slug, name FROM models WHERE brand_id = ? AND slug = ?"
  ).bind(brandId, slug).first();
}

export async function getEnginesByModel(db: any, modelId: number) {
  const { results } = await db.prepare(
    "SELECT * FROM engines WHERE model_id = ? ORDER BY periode"
  ).bind(modelId).all();
  return results;
}

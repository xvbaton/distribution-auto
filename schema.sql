CREATE TABLE IF NOT EXISTS brands (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  slug  TEXT UNIQUE NOT NULL,
  name  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS models (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  brand_id INTEGER NOT NULL REFERENCES brands(id),
  slug     TEXT NOT NULL,
  name     TEXT NOT NULL,
  UNIQUE(brand_id, slug)
);

CREATE TABLE IF NOT EXISTS engines (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  model_id      INTEGER NOT NULL REFERENCES models(id),
  periode       TEXT,
  moteur        TEXT,
  distribution  TEXT,
  puissance_ch  TEXT,
  entretien_km  TEXT,
  entretien_ans TEXT
);

CREATE INDEX IF NOT EXISTS idx_engines_model ON engines(model_id);
CREATE INDEX IF NOT EXISTS idx_models_brand  ON models(brand_id);
CREATE INDEX IF NOT EXISTS idx_models_slug   ON models(slug);
CREATE INDEX IF NOT EXISTS idx_brands_slug   ON brands(slug);

import type { APIRoute } from 'astro';
import { getDB } from '../../lib/db';

export const GET: APIRoute = async ({ url }) => {
  let query = url.searchParams.get('q')?.trim().toLowerCase() || '';

  if (query.length < 3) {
    return new Response(JSON.stringify([]), { status: 200 });
  }

  // Roman Numeral processing (e.g. Golf 5 -> Golf V)
  const romanMapping: Record<string, string> = {
    '1': 'i', '2': 'ii', '3': 'iii', '4': 'iv', '5': 'v', '6': 'vi', '7': 'vii', '8': 'viii',
    'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5', 'vi': '6', 'vii': '7', 'viii': '8'
  };

  let queryVariant = query;
  for (const [key, value] of Object.entries(romanMapping)) {
    const regex = new RegExp(`\\b${key}\\b`, 'g');
    if (regex.test(query)) {
      queryVariant = query.replace(regex, value);
      break; 
    }
  }

  const db = getDB();
  
  const searchTerm = `%${query.toUpperCase()}%`;
  const searchVariantTerm = `%${queryVariant.toUpperCase()}%`;

  // Search by brand, model, or searching raw fiche_json which contains "Moteurs" objects (engine search).
  const stmt = db.prepare(`
    SELECT DISTINCT
      b.name as brand_name, 
      b.slug as brand_slug, 
      m.name as model_name, 
      m.slug as model_slug
    FROM models m
    JOIN brands b ON m.brand_id = b.id
    WHERE 
      UPPER(b.name || ' ' || m.name) LIKE ?
      OR UPPER(b.name || ' ' || m.name) LIKE ?
      OR UPPER(m.fiche_json) LIKE ?
    LIMIT 6
  `).bind(searchTerm, searchVariantTerm, searchTerm);

  const results = await stmt.all();

  return new Response(JSON.stringify(results.results), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=3600'
    }
  });
};

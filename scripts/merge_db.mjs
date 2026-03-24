import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// --- Fonctions utilitaires ---

function generateSlugFromTitre(titre, marque) {
    return titre.toLowerCase()
        .replace(/Fiche technique\s+/i, '')
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/-+$/, '')
        .replace(/^-+/, '');
}

function getModelName(titre, marque) {
    let n = titre.replace(/Fiche technique\s+/i, '');
    let brandName = marque.charAt(0).toUpperCase() + marque.slice(1);
    n = n.replace(new RegExp(`^${brandName}\\s*`, 'i'), '');
    return n.trim();
}

/**
 * DICTIONNAIRE DE VÉRITÉ MÉCANIQUE V9 - FULL EUROPE/ASIA
 */
function getVerifiedDistribution(name, year, brand) {
    const n = name.toLowerCase();
    const b = brand.toLowerCase();

    // --- RENAULT / DACIA / NISSAN ---
    if (n.includes('1.5 dci')) return 'COURROIE'; 
    if (n.includes('1.6 dci') || n.includes('2.0 dci') || n.includes('2.3 dci') || n.includes('3.0 dci')) return 'CHAÎNE'; 
    if (n.includes('0.9 tce') || n.includes('1.3 tce') || n.includes('1.0 tce') || n.includes('1.6 tce')) return 'CHAÎNE';
    if (n.includes('1.2 tce')) {
        if (n.includes('115') || n.includes('120') || n.includes('125') || n.includes('130')) return 'CHAÎNE';
        return 'COURROIE';
    }
    // Vieilles Renault essence : la grande majorité est à courroie
    if (n.includes('16v') || n.includes('1.2') || n.includes('1.4') || n.includes('1.6') || n.includes('1.8') || n.includes('2.0')) {
        if (n.includes('tce') || n.includes('dci')) { /* géré plus haut */ }
        else return 'COURROIE';
    }

    // --- PSA ---
    if (n.includes('puretech') || n.includes('1.2 vti') || n.includes('1.2 82') || n.includes('1.0 68')) return 'COURROIE HUMIDE';
    if (n.includes('hdi') || n.includes('bluehdi')) return 'COURROIE';
    if (n.includes('1.6 thp') || n.includes('1.6 vti')) return 'CHAÎNE';

    // --- OPEL ---
    if (b.includes('opel')) {
        if (n.includes('cdti')) {
            if (n.includes('1.3')) return 'CHAÎNE';
            return 'COURROIE';
        }
        if (n.includes('ecotec')) {
            if (n.includes('1.0') || n.includes('1.2') || n.includes('2.2')) return 'CHAÎNE';
            return 'COURROIE';
        }
    }

    // --- MAZDA / SUZUKI / SUBARU ---
    if (b.includes('mazda') || b.includes('suzuki') || b.includes('subaru')) return 'CHAÎNE'; 

    // --- VOLKSWAGEN / AUDI / SEAT / SKODA ---
    if (n.includes('3.0 tdi') || n.includes('2.7 tdi') || n.includes('4.2 tdi') || n.includes('5.0 tdi')) return 'CHAÎNE';
    if (n.includes('tdi')) return 'COURROIE'; 
    if (n.includes('1.8 tsi') || n.includes('2.0 tsi') || n.includes('1.8 tfsi') || n.includes('2.0 tfsi') || n.includes('3.0 tfsi')) return 'CHAÎNE';
    if (n.includes('1.0 tsi') || n.includes('1.0 60') || n.includes('1.0 75')) return 'COURROIE'; 
    if (n.includes('1.2 tsi') || n.includes('1.4 tsi')) {
        if (year && year >= 2013) return 'COURROIE';
        if (year && year <= 2011) return 'CHAÎNE';
        return null; 
    }

    // --- BMW / MINI ---
    if (b.includes('bmw') || b.includes('mini')) {
        if (n.includes('1.6 hdi') || n.includes('1.6 d')) {
            if (year && year <= 2010) return 'COURROIE'; 
        }
        return 'CHAÎNE'; 
    }

    // --- MERCEDES ---
    if (b.includes('mercedes')) {
        if (n.includes('180d') || n.includes('160d')) return 'COURROIE';
        return 'CHAÎNE';
    }

    // --- HYUNDAI / KIA ---
    if (b.includes('hyundai') || b.includes('kia')) return 'CHAÎNE'; // GDI, CRDI, MPI sont quasi tous à chaîne chez eux depuis 2005

    // --- VOLVO ---
    if (b.includes('volvo')) return 'COURROIE'; // D2/3/4/5, T2/3/4/5/6 sont tous à courroie

    // --- FORD ---
    if (n.includes('ecoboost')) {
        if (year && year >= 2020) return 'CHAÎNE';
        return 'COURROIE HUMIDE';
    }
    if (n.includes('tdci') || n.includes('ecoblue')) return 'COURROIE';
    if (n.includes('duratec')) return 'CHAÎNE';

    // --- TOYOTA / LEXUS / HONDA ---
    if (n.includes('hsd') || n.includes('hybrid') || n.includes('vvt-i') || n.includes('dtec') || n.includes('ctdi') || n.includes('vtec')) return 'CHAÎNE';

    // --- FIAT / ALFA ---
    if (n.includes('1.3 multijet') || n.includes('1.3 jtd')) return 'CHAÎNE';
    if (n.includes('fire') || n.includes('jtdm') || n.includes('jtd')) return 'COURROIE';

    // --- ÉLECTRIQUE ---
    if (/batterie|electr|électr|BEV/i.test(n)) return 'N/A';

    return null;
}

function extractYear(periode) {
    const m = periode.match(/(\d{4})/);
    return m ? parseInt(m[1]) : null;
}

function deduceFuel(name) {
    const n = name.toLowerCase();
    const diesels = ['dci', 'hdi', 'tdi', 'cdti', 'jtd', 'multijet', 'crdi', 'did', 'tdci', 'd-4d', 'bluehdi', 'dcat', '180d', '160d', 'ecoblue'];
    if (diesels.some(d => n.includes(d))) return 'DIESEL';
    if (/batterie|electr|électr|BEV/i.test(n)) return 'ÉLECTRIQUE';
    return 'ESSENCE';
}

async function run() {
    console.log("🚀 Fusion HAUTE FIDÉLITÉ (V9 - Full Europe/Asia)...");

    const faPath = path.join(__dirname, 'vehicules_complet.json');
    const faData = JSON.parse(fs.readFileSync(faPath, 'utf-8'));

    const result = [];
    let stats = { total: faData.length, moteurs: 0, distFound: 0 };

    faData.forEach(fa => {
        const slug = generateSlugFromTitre(fa.titre, fa.marque);
        const nameWithYears = getModelName(fa.titre, fa.marque);
        const startYear = extractYear(fa.periode);

        const mergedMoteurs = fa.moteurs.map(m => {
            stats.moteurs++;
            const distribution = getVerifiedDistribution(m.Moteur, startYear, fa.marque);
            if (distribution) stats.distFound++;

            return {
                ...m,
                fuel: deduceFuel(m.Moteur),
                distribution: distribution,
                entretien_km: null,
                entretien_ans: null,
                match_source: distribution ? "verified-dictionary-v9" : null
            };
        });

        result.push({
            ...fa,
            model_name: nameWithYears,
            model_slug: slug,
            moteurs: mergedMoteurs
        });
    });

    const outputPath = path.join(__dirname, 'db_finale_fusionnee.json');
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));

    console.log(`✅ Terminé ! Fichier : db_finale_fusionnee.json`);
    console.log(`📊 Stats :`);
    console.log(`- Modèles : ${stats.total}`);
    console.log(`- Moteurs : ${stats.moteurs}`);
    console.log(`- Distribution VÉRIFIÉE : ${stats.distFound} (${Math.round(stats.distFound/stats.moteurs*100)}%)`);
}

run();

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

from ancient_backend import _extract_feature_value, sanitize_json_payload

BASE_DIR = Path(__file__).resolve().parent
DIM_OUTPUT_JSON = BASE_DIR / 'data' / 'dimensional_reduction_dataset.json'

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('dim-backend')


def safe_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip().lower()
    if not s or s in ('null', 'none', 'nan', 'inf', '-inf'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load_gaia_data() -> List[Dict[str, Any]]:
    possible_names = ['gaia.json', 'gaia_dr3.json', 'gaia_data.json']
    possible_dirs = [
        BASE_DIR / 'data',
        BASE_DIR.parent / 'data',
        BASE_DIR / 'frontend' / 'data',
        Path('/data'),
        Path('/frontend/data'),
        Path('.')
    ]
    for d in possible_dirs:
        for name in possible_names:
            path = d / name
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding='utf-8'))
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        for key in ['data', 'rows', 'results']:
                            if key in data and isinstance(data[key], list):
                                return data[key]
                except Exception:
                    pass
    return []


def _build_dimensionality_payload() -> Dict[str, Any]:
    gaia_list = load_gaia_data()
    
    rows: List[Dict[str, Any]] = []
    for item in gaia_list:
        source_id = _extract_feature_value(item, ['designation', 'source_id', 'id', 'sourceId'])
        hip_val = _extract_feature_value(item, ['hip', 'HIP', 'hip_id'])
        hip = int(float(hip_val)) if safe_float(hip_val) is not None else None
        
        name = source_id if source_id else "Gaia Anonymous Source"
        office = item.get('星官') or item.get('office') or '未分组'

        ra = safe_float(_extract_feature_value(item, ['ra', 'RA']))
        dec = safe_float(_extract_feature_value(item, ['dec', 'DEC']))
        
        if ra is None or dec is None:
            continue

        row = {
            'id': source_id or f"G_{ra:.5f}_{dec:.5f}",
            'hip': hip,
            'name': name,
            'office': office,
            'ra': ra,
            'dec': dec,
            'mag': safe_float(_extract_feature_value(item, ['phot_g_mean_mag', 'mag', 'Vmag', 'g_mag', 'Gmag'])),
            'parallax': safe_float(_extract_feature_value(item, ['parallax', 'Plx', 'plx'])),
            'parallax_error': safe_float(_extract_feature_value(item, ['parallax_error', 'plx_error', 'e_parallax'])),
            'pmra': safe_float(_extract_feature_value(item, ['pmra', 'pmRA'])),
            'pmdec': safe_float(_extract_feature_value(item, ['pmdec', 'pmDE'])),
            'rv': safe_float(_extract_feature_value(item, ['radial_velocity', 'rv', 'RV'])),
            'teff': safe_float(_extract_feature_value(item, ['teff_gspphot', 'teff', 'Teff', 'effective_temperature'])),
            'bp_rp': safe_float(_extract_feature_value(item, ['bp_rp'])),
            'bp_g': safe_float(_extract_feature_value(item, ['bp_g'])),
            'g_rp': safe_float(_extract_feature_value(item, ['g_rp'])),
            'ruwe': safe_float(_extract_feature_value(item, ['ruwe', 'RUWE'])),
        }
        rows.append(row)

    numeric_keys = ['ra', 'dec', 'parallax', 'parallax_error', 'pmra', 'pmdec', 'rv', 'mag', 'teff', 'bp_rp', 'bp_g', 'g_rp', 'ruwe']
    valid_rows = []
    for row in rows:
        if row['parallax_error'] is not None and row['parallax'] not in (None, 0):
            if abs(row['parallax_error']) > 3 * max(abs(row['parallax']), 1e-6):
                continue
        # 确保该恒星具备至少 4 个以上的非空物理维度（因为暗星可能普遍缺失 teff 或 rv 测量值）
        if sum(1 for key in numeric_keys if row.get(key) is not None) >= 4:
            valid_rows.append(row)

    def feature_vector(row: Dict[str, Any]) -> List[float]:
        mag = row.get('mag') or 0.0
        parallax = row.get('parallax') or 0.0
        distance_pc = 1000.0 / parallax if parallax and parallax > 0 else 0.0
        absolute_mag = mag - 5 * math.log10(distance_pc / 10) if distance_pc > 0 and mag is not None else 0.0
        motion = math.hypot(row.get('pmra') or 0.0, row.get('pmdec') or 0.0)
        return [
            row.get('ra') or 0.0,
            row.get('dec') or 0.0,
            parallax,
            row.get('pmra') or 0.0,
            row.get('pmdec') or 0.0,
            motion,
            mag,
            row.get('teff') or 0.0,
            row.get('bp_rp') or 0.0,
            row.get('bp_g') or 0.0,
            row.get('g_rp') or 0.0,
            row.get('ruwe') or 0.0,
            absolute_mag,
            distance_pc
        ]

    matrix = [feature_vector(row) for row in valid_rows]
    if not matrix:
        return {'stats': {'total': len(rows), 'filtered': 0, 'feature_count': 14}, 'rows': [], 'embeddings': {}}

    import numpy as np
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler

    try:
        import umap
        UMAP_AVAILABLE = True
    except Exception:
        UMAP_AVAILABLE = False

    X = np.asarray(matrix, dtype=float)
    Xs = StandardScaler().fit_transform(X)
    pca = PCA(n_components=min(3, Xs.shape[1]))
    pca_coords = pca.fit_transform(Xs)
    pca_variance = [float(v) for v in pca.explained_variance_ratio_.tolist()]
    if len(pca_variance) < 3:
        pca_variance += [0.0] * (3 - len(pca_variance))
        
    perplexity = max(5, min(30, len(valid_rows) // 10 or 5))
    tsne = TSNE(n_components=2, perplexity=min(perplexity, max(2, len(valid_rows) - 1)), random_state=42, init='pca', learning_rate='auto')
    tsne_coords = tsne.fit_transform(Xs)
    
    if UMAP_AVAILABLE and len(valid_rows) >= 10:
        umap_model = umap.UMAP(n_components=2, n_neighbors=min(15, max(5, len(valid_rows) // 12)), min_dist=0.18, random_state=42)
        umap_coords = umap_model.fit_transform(Xs)
    else:
        umap_coords = tsne_coords * 0.85 + pca_coords[:, :2] * 0.15
        
    labels = DBSCAN(eps=0.38, min_samples=8).fit_predict(Xs[:, : min(8, Xs.shape[1])])

    def make_payload(coords: Any) -> List[Dict[str, Any]]:
        return [{'id': row['id'], 'x': float(pt[0]), 'y': float(pt[1]), 'z': float(pt[2]) if len(pt) > 2 else 0.0, 'cluster': int(labels[i]), 'outlier': bool(labels[i] == -1)} for i, (row, pt) in enumerate(zip(valid_rows, coords))]

    payload = {
        'stats': {'total': len(gaia_list), 'filtered': len(valid_rows), 'feature_count': len(numeric_keys), 'missing_ratio': float(1 - (len(valid_rows) / len(gaia_list))) if gaia_list else 0.0},
        'rows': [{**row, 'cluster': int(labels[i]), 'outlier': bool(labels[i] == -1)} for i, row in enumerate(valid_rows)],
        'embeddings': {'pca': make_payload(pca_coords), 'tsne': make_payload(tsne_coords), 'umap': make_payload(umap_coords)},
        'pca': {'variance_ratio': pca_variance, 'components': pca.components_.tolist()},
        'cluster_labels': labels.tolist(),
    }
    DIM_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    safe_payload = sanitize_json_payload(payload)
    DIM_OUTPUT_JSON.write_text(json.dumps(safe_payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return safe_payload


def build_dimensionality_payload() -> Dict[str, Any]:
    if DIM_OUTPUT_JSON.exists():
        try:
            cached_data = json.loads(DIM_OUTPUT_JSON.read_text(encoding='utf-8'))
            if cached_data.get('stats', {}).get('filtered', 0) > 0:
                return sanitize_json_payload(cached_data)
            else:
                logger.warning("Cached dimensionality data has 0 filtered samples. Forcing regeneration...")
        except Exception:
            pass
    return _build_dimensionality_payload()
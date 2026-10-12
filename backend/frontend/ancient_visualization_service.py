#!/usr/bin/env python3
"""Ancient astronomy visualization preprocessing and static service.

Optimized to prevent OOM (Out of Memory) crashes under resource-constrained environments.
"""

from __future__ import annotations

import csv
import json
import logging
import math
import os
import re
import sys
import traceback
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
RAW_DIR = Path('/root/autodl-tmp/raw')
PROCESSED_DIR = Path('/root/autodl-tmp/processed')
FRONTEND_MERGED_JSON = BASE_DIR / 'data' / 'merged_Chinese_astronomy_data.json'
OUTPUT_JSON = BASE_DIR / 'data' / 'ancient_visualization_dataset.json'
DIM_OUTPUT_JSON = BASE_DIR / 'data' / 'dimensional_reduction_dataset.json'
STELLAR_OUTPUT_JSON = BASE_DIR / 'data' / 'stellar_analysis_dataset.json'

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger('ancient-viz')

try:
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    from astropy.time import Time
    ASTROPY_AVAILABLE = True
except Exception as exc:
    ASTROPY_AVAILABLE = False
    ASTROPY_IMPORT_ERROR = exc


# 全局内存缓存，防止重复计算引发 OOM
_CATALOG_CACHE: Optional[List[Dict[str, Any]]] = None
_ANCIENT_PAYLOAD_CACHE: Optional[Dict[str, Any]] = None
_DIM_PAYLOAD_CACHE: Optional[Dict[str, Any]] = None


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    logger.info('Reading CSV: %s', path)
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    logger.info('CSV rows loaded: %d', len(rows))
    return rows


def _col_letter_to_idx(cell_ref: str) -> int:
    letters = re.match(r'([A-Z]+)', cell_ref).group(1)
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - 64)
    return idx - 1


def read_xlsx_rows(path: Path) -> List[Dict[str, str]]:
    logger.info('Reading XLSX: %s', path)
    with zipfile.ZipFile(path) as z:
        shared_strings: List[str] = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            ns = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in root.findall('.//a:si', ns):
                shared_strings.append(''.join(t.text or '' for t in si.findall('.//a:t', ns)))

        sheet_name = next(name for name in z.namelist() if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'))
        root = ET.fromstring(z.read(sheet_name))
        ns = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        rows = []
        headers: List[str] = []
        for i, row in enumerate(root.findall('.//a:sheetData/a:row', ns)):
            values: List[str] = []
            for cell in row.findall('a:c', ns):
                ref = cell.attrib.get('r', '')
                idx = _col_letter_to_idx(ref) if ref else len(values)
                while len(values) <= idx:
                    values.append('')
                cell_type = cell.attrib.get('t')
                value_node = cell.find('a:v', ns)
                value = '' if value_node is None else value_node.text or ''
                if cell_type == 's':
                    value = shared_strings[int(value)] if value.isdigit() and int(value) < len(shared_strings) else value
                values[idx] = value
            if i == 0:
                headers = values
            else:
                row_dict = {headers[j]: values[j] if j < len(values) else '' for j in range(len(headers))}
                rows.append(row_dict)
    logger.info('XLSX rows loaded: %d', len(rows))
    return rows


def clean_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == 'null':
        return None
    text = text.replace('−', '-').replace('~', '-')
    match = re.search(r'-?\d+(?:\.\d+)?', text)
    return float(match.group(0)) if match else None

def sanitize_json_payload(obj: Any) -> Any:
    """递归清洗字典和列表，将所有非法浮点数 (NaN, inf) 转换为标准 JSON 支持的 None (null)。"""
    if isinstance(obj, dict):
        return {k: sanitize_json_payload(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json_payload(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif hasattr(obj, 'dtype'): # 兼容 NumPy 特殊类型的浮点数检查
        import numpy as np
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj.item()
    return obj

def clean_int(value: Any) -> Optional[int]:
    val = clean_float(value)
    return int(val) if val is not None else None


def parse_mag(value: Any) -> Optional[float]:
    return clean_float(value)


def process_catalog() -> List[Dict[str, Any]]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE

    path = FRONTEND_MERGED_JSON
    logger.info('Reading catalog JSON: %s', path)
    rows = json.loads(path.read_text(encoding='utf-8'))
    valid = []
    for row in rows:
        hip = clean_int(row.get('HIP'))
        ra = clean_float(row.get('RA') or row.get('ra'))
        dec = clean_float(row.get('Dec') or row.get('dec'))
        mag = parse_mag(row.get('Vmag') or row.get('视星等'))
        pmra = clean_float(row.get('pmRA') or row.get('pmra'))
        pmdec = clean_float(row.get('pmDE') or row.get('pmdec'))
        plx = clean_float(row.get('Plx') or row.get('parallax'))
        rv = clean_float(row.get('RV') or row.get('radial_velocity'))
        star_office = (row.get('星官') or '').strip()
        chn_star_name = (row.get('中国星名') or '').strip()
        if hip is None or ra is None or dec is None:
            continue
        valid.append({
            'hip': hip,
            'ra_j2000': ra,
            'dec_j2000': dec,
            'mag': mag,
            'pmra': pmra,
            'pmdec': pmdec,
            'parallax': plx,
            'radial_velocity': rv,
            '星官': star_office,
            '中国星名': chn_star_name,
        })

    logger.info('Valid catalog rows: %d', len(valid))
    if not ASTROPY_AVAILABLE:
        logger.warning('astropy unavailable, returning J2000 coordinates only')
        for item in valid:
            item['ra_1054'] = item['ra_j2000']
            item['dec_1054'] = item['dec_j2000']
        _CATALOG_CACHE = valid
        return valid

    logger.info('Applying batched space motion to epoch 1054.0')
    epoch_target = Time('1054-01-01T00:00:00', scale='utc')
    epoch_source = Time('J2000')

    ra_vals = [item['ra_j2000'] for item in valid]
    dec_vals = [item['dec_j2000'] for item in valid]
    pmra_vals = [item['pmra'] if item['pmra'] is not None else 0.0 for item in valid]
    pmdec_vals = [item['pmdec'] if item['pmdec'] is not None else 0.0 for item in valid]
    distance_vals = [1000.0 / item['parallax'] if item['parallax'] is not None and item['parallax'] > 0 else None for item in valid]
    rv_vals = [item['radial_velocity'] if item['radial_velocity'] is not None else 0.0 for item in valid]

    try:
        coord_kwargs = dict(
            ra=ra_vals * u.deg,
            dec=dec_vals * u.deg,
            frame='icrs',
            obstime=epoch_source,
            pm_ra_cosdec=pmra_vals * u.mas / u.yr,
            pm_dec=pmdec_vals * u.mas / u.yr,
            radial_velocity=rv_vals * u.km / u.s,
        )
        if any(distance is not None for distance in distance_vals):
            coord_kwargs['distance'] = [distance if distance is not None else float('nan') for distance in distance_vals] * u.pc
        coords = SkyCoord(**coord_kwargs)
        moved = coords.apply_space_motion(new_obstime=epoch_target)
        for item, ra_1054, dec_1054 in zip(valid, moved.ra.deg, moved.dec.deg):
            item['ra_1054'] = float(ra_1054)
            item['dec_1054'] = float(dec_1054)
        logger.info('Transformed catalog rows: %d', len(valid))
        _CATALOG_CACHE = valid
        return valid
    except Exception as exc:
        logger.warning('Batched space motion failed, falling back to per-row transform: %s', exc)

    transformed = []
    for item in valid:
        try:
            coord_kwargs = dict(
                ra=item['ra_j2000'] * u.deg,
                dec=item['dec_j2000'] * u.deg,
                frame='icrs',
                obstime=epoch_source,
            )
            if item['pmra'] is not None:
                coord_kwargs['pm_ra_cosdec'] = item['pmra'] * u.mas / u.yr
            if item['pmdec'] is not None:
                coord_kwargs['pm_dec'] = item['pmdec'] * u.mas / u.yr
            if item['parallax'] is not None and item['parallax'] > 0:
                coord_kwargs['distance'] = (1000.0 / item['parallax']) * u.pc
            if item['radial_velocity'] is not None:
                coord_kwargs['radial_velocity'] = item['radial_velocity'] * u.km / u.s
            coord = SkyCoord(**coord_kwargs)
            moved = coord.apply_space_motion(new_obstime=epoch_target)
            item['ra_1054'] = float(moved.ra.deg)
            item['dec_1054'] = float(moved.dec.deg)
            transformed.append(item)
        except Exception as row_exc:
            item['ra_1054'] = item['ra_j2000']
            item['dec_1054'] = item['dec_j2000']
            transformed.append(item)
    
    _CATALOG_CACHE = transformed
    return transformed


def group_constellations(coord_map: Dict[int, Tuple[float, float, float, str]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    path = FRONTEND_MERGED_JSON
    rows = json.loads(path.read_text(encoding='utf-8'))
    points = []
    seen_by_office: Dict[str, set] = {}
    for row in rows:
        star_office = (row.get('星官') or '').strip()
        hip = clean_int(row.get('HIP'))
        ra = clean_float(row.get('RA') or row.get('ra'))
        dec = clean_float(row.get('Dec') or row.get('dec'))
        mag = parse_mag(row.get('Vmag') or row.get('视星等'))
        if not star_office or ra is None or dec is None or hip is None:
            continue

        dedupe_key = (hip, round(ra, 8), round(dec, 8))
        seen_keys = seen_by_office.setdefault(star_office, set())
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        
        if hip in coord_map:
            ra_1054, dec_1054, resolved_mag, _ = coord_map[hip]
        else:
            ra_1054, dec_1054, resolved_mag = ra, dec, mag

        points.append({
            '星官': star_office,
            'HIP': hip,
            'ra': ra_1054,
            'dec': dec_1054,
            'mag': resolved_mag,
            'source': 'merged_Chinese_astronomy_data.json',
        })

    groups: Dict[str, List[Dict[str, Any]]] = {}
    for pt in points:
        groups.setdefault(pt['星官'], []).append(pt)

    line_style = {
        'linestyle': '-',
        'linewidth': 1.5,
        'alpha': 0.9,
        'color': '#ffda79',
    }
    line_groups = []
    for name, pts in groups.items():
        line_groups.append({
            'name': name,
            'style': dict(line_style),
            'points': [{'ra': p['ra'], 'dec': p['dec'], 'hip': p['HIP'], 'mag': p['mag']} for p in pts],
            'count': len(pts),
        })
    return points, line_groups


def load_tautou_targets() -> List[Dict[str, Any]]:
    path = PROCESSED_DIR / 'clean_cols_HSCv3.1Tautou.xlsx'
    if not path.exists():
        logger.warning('Tautou target file not found at %s. Returning empty.', path)
        return []
    rows = read_xlsx_rows(path)
    targets = []
    for row in rows:
        ra = clean_float(row.get('ra'))
        dec = clean_float(row.get('dec'))
        if ra is None or dec is None:
            continue
        targets.append({
            'match_id': row.get('match_id'),
            'target_name': row.get('target_name'),
            'ra': ra,
            'dec': dec,
            'flux': clean_float(row.get('flux')),
            'flux_sigma': clean_float(row.get('flux_sigma')),
            'filter': row.get('filter'),
        })
    return targets


def build_payload() -> Dict[str, Any]:
    global _ANCIENT_PAYLOAD_CACHE
    if _ANCIENT_PAYLOAD_CACHE is not None:
        return _ANCIENT_PAYLOAD_CACHE

    if OUTPUT_JSON.exists():
        try:
            logger.info('Loading ancient visualization from output JSON...')
            _ANCIENT_PAYLOAD_CACHE = json.loads(OUTPUT_JSON.read_text(encoding='utf-8'))
            return _ANCIENT_PAYLOAD_CACHE
        except Exception as e:
            logger.warning('Failed to load precomputed output JSON: %s', e)

    catalog = process_catalog()
    coord_map = {
        item['hip']: (
            item['ra_1054'],
            item['dec_1054'],
            item['mag'] if item['mag'] is not None else 6.0,
            item['星官']
        )
        for item in catalog
    }

    constellation_points, constellation_lines = group_constellations(coord_map)
    tautou_targets = load_tautou_targets()
    stats = {
        'catalog_rows_loaded': len(catalog),
        'catalog_rows_valid': len(catalog),
        'constellation_points': len(constellation_points),
        'constellation_groups': len(constellation_lines),
        'tautou_targets': len(tautou_targets),
    }
    payload = {
        'stats': stats,
        'catalog': catalog,
        'constellations': constellation_lines,
        'constellation_points': constellation_points,
        'tautou_targets': tautou_targets,
        'options': {
            'constellation_line_style': {
                'linestyle': '-',
                'linewidth': 1.5,
                'alpha': 0.9,
                'color': '#ffda79',
            },
            'target_epoch': '1054-01-01T00:00:00',
        }
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    _ANCIENT_PAYLOAD_CACHE = payload
    return payload


def _extract_feature_value(row: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    for key in keys:
        if key in row and row[key] not in ('', None):
            return row[key]
    return default


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        val = float(value)
    except Exception:
        return None
    if math.isnan(val) or math.isinf(val):
        return None
    return val


def _compute_absolute_magnitude(apparent_mag: Optional[float], parallax_mas: Optional[float]) -> Optional[float]:
    if apparent_mag is None or parallax_mas is None or parallax_mas <= 0:
        return None
    distance_pc = 1000.0 / parallax_mas
    if distance_pc <= 0:
        return None
    return float(apparent_mag - 5 * math.log10(distance_pc / 10.0))


def _vector_norm(pmra: Optional[float], pmdec: Optional[float]) -> Optional[float]:
    if pmra is None and pmdec is None:
        return None
    return float(math.hypot(pmra or 0.0, pmdec or 0.0))


def _normalize_angle_deg(pmra: Optional[float], pmdec: Optional[float]) -> Optional[float]:
    if pmra is None and pmdec is None:
        return None
    angle = math.degrees(math.atan2(pmdec or 0.0, pmra or 0.0))
    return float((angle + 360.0) % 360.0)


def _classify_hr_stage(teff: Optional[float], abs_mag: Optional[float], bp_rp: Optional[float] = None) -> str:
    if teff is None or abs_mag is None:
        return 'unknown'
    if teff >= 7000:
        return 'hot_main_sequence' if abs_mag > 0 else 'giant_candidate'
    if teff >= 5200:
        if abs_mag < 2.5:
            return 'giant'
        return 'main_sequence'
    if teff >= 3700:
        if abs_mag < 4.5:
            return 'subgiant_or_giant'
        return 'main_sequence'
    return 'cool_dwarf'


def _build_dimensionality_payload() -> Dict[str, Any]:
    catalog = process_catalog()
    rows: List[Dict[str, Any]] = []
    for item in catalog:
        row = {
            'id': item['hip'],
            'hip': item['hip'],
            'name': item.get('中国星名') or f"HIP {item['hip']}",
            'office': item.get('星官') or '未分组',
            'ra': item['ra_j2000'],
            'dec': item['dec_j2000'],
            'mag': item.get('mag'),
            'parallax': item.get('parallax'),
            'parallax_error': _to_float(_extract_feature_value(item, ['parallax_error', 'plx_error', 'e_parallax'])),
            'pmra': item.get('pmra'),
            'pmdec': item.get('pmdec'),
            'rv': item.get('radial_velocity'),
            'teff': _to_float(_extract_feature_value(item, ['teff_gspphot', 'teff'])),
            'bp_rp': _to_float(_extract_feature_value(item, ['bp_rp'])),
            'bp_g': _to_float(_extract_feature_value(item, ['bp_g'])),
            'g_rp': _to_float(_extract_feature_value(item, ['g_rp'])),
            'ruwe': _to_float(_extract_feature_value(item, ['ruwe'])),
        }
        rows.append(row)

    numeric_keys = ['ra', 'dec', 'parallax', 'parallax_error', 'pmra', 'pmdec', 'rv', 'mag', 'teff', 'bp_rp', 'bp_g', 'g_rp', 'ruwe']
    valid_rows = []
    for row in rows:
        if row['parallax_error'] is not None and row['parallax'] not in (None, 0):
            if abs(row['parallax_error']) > 3 * max(abs(row['parallax']), 1e-6):
                continue
        valid_count = sum(1 for key in numeric_keys if row.get(key) is not None)
        if valid_count < 6:
            continue
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
            distance_pc,
        ]

    matrix = [feature_vector(row) for row in valid_rows]
    if not matrix:
        return {'stats': {'total': len(rows), 'filtered': 0, 'feature_count': 14}, 'rows': [], 'embeddings': {}}

    try:
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
        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)

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

        eps = 0.38
        min_samples = 8
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(Xs[:, : min(8, Xs.shape[1])])

        def make_payload(coords: Any) -> List[Dict[str, Any]]:
            return [
                {
                    'id': row['id'],
                    'x': float(pt[0]),
                    'y': float(pt[1]),
                    'z': float(pt[2]) if len(pt) > 2 else 0.0,
                    'cluster': int(labels[i]),
                    'outlier': bool(labels[i] == -1),
                }
                for i, (row, pt) in enumerate(zip(valid_rows, coords))
            ]

        row_map = []
        for i, row in enumerate(valid_rows):
            row_map.append({
                **row,
                'cluster': int(labels[i]),
                'outlier': bool(labels[i] == -1),
            })

        def cluster_summary() -> List[Dict[str, Any]]:
            result = []
            for cluster_id in sorted(set(int(v) for v in labels if v != -1)):
                member_indices = [i for i, v in enumerate(labels) if int(v) == cluster_id]
                result.append({
                    'id': int(cluster_id),
                    'size': len(member_indices),
                    'mean_teff': float(np.nanmean([valid_rows[i]['teff'] for i in member_indices if valid_rows[i]['teff'] is not None])) if member_indices else None,
                })
            return result

        payload = {
            'stats': {
                'total': len(rows),
                'filtered': len(valid_rows),
                'feature_count': len(numeric_keys),
                'missing_ratio': float(1 - (len(valid_rows) / len(rows))) if rows else 0.0,
            },
            'rows': row_map,
            'embeddings': {
                'pca': make_payload(pca_coords),
                'tsne': make_payload(tsne_coords),
                'umap': make_payload(umap_coords),
            },
            'pca': {
                'variance_ratio': pca_variance,
                'components': pca.components_.tolist(),
            },
            'clusters': cluster_summary(),
            'cluster_labels': labels.tolist(),
        }
        DIM_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        # 将 payload 中所有不合规的 NaN / inf 浮点数，转换为安全的 None (null)
        safe_payload = sanitize_json_payload(payload)
        
        # 写入文件并返回
        DIM_OUTPUT_JSON.write_text(json.dumps(safe_payload, ensure_ascii=False, indent=2), encoding='utf-8')
        return safe_payload

    except Exception as exc:
        logger.warning('Dimensionality reduction backend failed: %s', exc)
        return {'stats': {'total': len(rows), 'filtered': len(valid_rows), 'feature_count': len(numeric_keys)}, 'rows': valid_rows, 'embeddings': {}}


def build_dimensionality_payload() -> Dict[str, Any]:
    global _DIM_PAYLOAD_CACHE
    if _DIM_PAYLOAD_CACHE is not None:
        return _DIM_PAYLOAD_CACHE

    if DIM_OUTPUT_JSON.exists():
        try:
            logger.info('Loading precomputed dimensional reduction JSON...')
            raw_payload = json.loads(DIM_OUTPUT_JSON.read_text(encoding='utf-8'))
            _DIM_PAYLOAD_CACHE = sanitize_json_payload(raw_payload)
            return _DIM_PAYLOAD_CACHE
        except Exception as e:
            logger.warning('Failed to load dimensional reduction JSON from disk: %s', e)

    logger.info('Computing dimensional reduction matrix (may take a moment)...')
    _DIM_PAYLOAD_CACHE = _build_dimensionality_payload()
    return _DIM_PAYLOAD_CACHE


def _build_stellar_analysis_payload() -> Dict[str, Any]:
    catalog = process_catalog()
    rows: List[Dict[str, Any]] = []
    for item in catalog:
        mag = item.get('mag')
        parallax = item.get('parallax')
        pmra = item.get('pmra')
        pmdec = item.get('pmdec')
        rv = item.get('radial_velocity')
        teff = _to_float(_extract_feature_value(item, ['teff_gspphot', 'teff']))
        bp_rp = _to_float(_extract_feature_value(item, ['bp_rp']))
        bp_g = _to_float(_extract_feature_value(item, ['bp_g']))
        g_rp = _to_float(_extract_feature_value(item, ['g_rp']))
        g_mag = _to_float(_extract_feature_value(item, ['phot_g_mean_mag', 'g_mag', 'Gmag', 'G']))
        mh = _to_float(_extract_feature_value(item, ['mh_gspphot', 'mh', 'feh', 'metallicity']))
        parallax_error = _to_float(_extract_feature_value(item, ['parallax_error', 'plx_error', 'e_parallax']))
        ruwe = _to_float(_extract_feature_value(item, ['ruwe']))
        pm_total = _vector_norm(pmra, pmdec)
        radial_abs = abs(rv) if rv is not None else None
        abs_mag = _compute_absolute_magnitude(g_mag if g_mag is not None else mag, parallax)
        stage = _classify_hr_stage(teff, abs_mag, bp_rp)
        quality_flag = 'good'
        if parallax_error is not None and parallax is not None and parallax > 0 and parallax_error > 2 * abs(parallax):
            quality_flag = 'poor_parallax'
        if teff is None:
            quality_flag = 'missing_teff'
        row = {
            'id': item['hip'],
            'hip': item['hip'],
            'name': item.get('中国星名') or f"HIP {item['hip']}",
            'office': item.get('星官') or '未分组',
            'ra': item['ra_j2000'],
            'dec': item['dec_j2000'],
            'parallax': parallax,
            'parallax_error': parallax_error,
            'pmra': pmra,
            'pmdec': pmdec,
            'pm_total': pm_total,
            'pm_angle': _normalize_angle_deg(pmra, pmdec),
            'rv': rv,
            'teff': teff,
            'bp_rp': bp_rp,
            'bp_g': bp_g,
            'g_rp': g_rp,
            'g_mag': g_mag,
            'mag': mag,
            'abs_mag': abs_mag,
            'mh': mh,
            'ruwe': ruwe,
            'stage': stage,
            'quality_flag': quality_flag,
            'radial_abs': radial_abs,
        }
        if row['parallax'] is None:
            continue
        rows.append(row)

    filtered = []
    for row in rows:
        if row['quality_flag'] == 'missing_teff':
            continue
        if row['parallax_error'] is not None and row['parallax'] is not None:
            if row['parallax_error'] > 2.0 * abs(row['parallax']):
                continue
        filtered.append(row)

    def _finite_field(row: Dict[str, Any], key: str, default: float = 0.0) -> float:
        val = row.get(key)
        return float(val) if isinstance(val, (int, float)) and math.isfinite(val) else default

    cmd_points = []
    hr_points = []
    cmd3d_points = []
    motion_vectors = []
    for row in filtered:
        bp_rp = row.get('bp_rp')
        color_index = bp_rp if bp_rp is not None else row.get('bp_g')
        g_mag = row.get('g_mag') if row.get('g_mag') is not None else row.get('mag')
        abs_mag = row.get('abs_mag')
        if color_index is None or g_mag is None:
            continue
        cmd_points.append({
            'id': row['id'],
            'x': float(color_index),
            'y': float(g_mag),
            'stage': row['stage'],
            'color_value': row.get('mh') if row.get('mh') is not None else row.get('teff'),
            'size_value': abs(_finite_field(row, 'parallax_error', 0.0)) or abs(_finite_field(row, 'pm_total', 0.0)),
            'row': row,
        })
        if abs_mag is not None and row.get('teff') is not None:
            hr_points.append({
                'id': row['id'],
                'x': float(row['teff']),
                'y': float(abs_mag),
                'stage': row['stage'],
                'color_value': row.get('mh') if row.get('mh') is not None else row.get('rv'),
                'size_value': abs(_finite_field(row, 'parallax_error', 0.0)) or abs(_finite_field(row, 'pm_total', 0.0)),
                'row': row,
            })
        cmd3d_points.append({
            'id': row['id'],
            'x': float(color_index),
            'y': float(g_mag),
            'z': float(row['parallax']),
            'stage': row['stage'],
            'row': row,
        })
        motion_vectors.append({
            'id': row['id'],
            'ra': float(row['ra']),
            'dec': float(row['dec']),
            'pmra': float(row['pmra']) if row['pmra'] is not None else None,
            'pmdec': float(row['pmdec']) if row['pmdec'] is not None else None,
            'rv': float(row['rv']) if row['rv'] is not None else None,
            'pm_total': row['pm_total'],
            'pm_angle': row['pm_angle'],
            'stage': row['stage'],
            'quality_flag': row['quality_flag'],
            'row': row,
        })

    def stage_counts(points: List[Dict[str, Any]]) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for point in points:
            stage = point['stage']
            result[stage] = result.get(stage, 0) + 1
        return result

    if not motion_vectors:
        motion_vectors = []

    payload = {
        'stats': {
            'total': len(rows),
            'filtered': len(filtered),
            'cmd_points': len(cmd_points),
            'hr_points': len(hr_points),
            'motion_points': len(motion_vectors),
            'missing_teff_removed': sum(1 for row in rows if row['quality_flag'] == 'missing_teff'),
            'parallax_outliers_removed': sum(1 for row in rows if row['parallax_error'] is not None and row['parallax'] is not None and row['parallax_error'] > 2.0 * abs(row['parallax'])),
        },
        'cmd': {
            'points': cmd_points,
            'stage_counts': stage_counts(cmd_points),
        },
        'hr': {
            'points': hr_points,
            'stage_counts': stage_counts(hr_points),
        },
        'cmd3d': {
            'points': cmd3d_points,
            'stage_counts': stage_counts(cmd3d_points),
        },
        'motion': {
            'vectors': motion_vectors,
        },
        'selected_rows': filtered,
    }
    STELLAR_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    STELLAR_OUTPUT_JSON.write_text(json.dumps(sanitize_json_payload(payload), ensure_ascii=False, indent=2), encoding='utf-8')
    return sanitize_json_payload(payload)


def build_stellar_analysis_payload() -> Dict[str, Any]:
    global _ANCIENT_PAYLOAD_CACHE
    if STELLAR_OUTPUT_JSON.exists():
        try:
            return sanitize_json_payload(json.loads(STELLAR_OUTPUT_JSON.read_text(encoding='utf-8')))
        except Exception:
            pass
    return _build_stellar_analysis_payload()


def _project_motion_point(ra_deg: float, dec_deg: float, pmra: Optional[float], pmdec: Optional[float], scale: float = 0.02) -> Tuple[float, float, float, float]:
    dra = (pmra or 0.0) * scale / 3600.0
    ddec = (pmdec or 0.0) * scale / 3600.0
    return ra_deg, dec_deg, ra_deg + dra, dec_deg + ddec


def _build_motion_tracks(rows: List[Dict[str, Any]], years: int = 1000, steps: int = 20) -> List[Dict[str, Any]]:
    tracks = []
    if not rows:
        return tracks
    step_years = years / max(steps, 1)
    for row in rows:
        pmra = row.get('pmra') or 0.0
        pmdec = row.get('pmdec') or 0.0
        base_ra = row.get('ra')
        base_dec = row.get('dec')
        if base_ra is None or base_dec is None:
            continue
        points = []
        for i in range(-steps, steps + 1):
            t = i * step_years
            ra_t = base_ra + (pmra * t) / 3600.0 / 100.0
            dec_t = base_dec + (pmdec * t) / 3600.0 / 100.0
            points.append({'t_years': float(t), 'ra': float(ra_t), 'dec': float(dec_t)})
        tracks.append({'id': row['id'], 'points': points, 'row': row})
    return tracks

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/dim-reduction':
            payload = build_dimensionality_payload()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
            return
        if parsed.path == '/api/stellar-analysis':
            payload = build_stellar_analysis_payload()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
            return
        return super().do_GET()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        return super().end_headers()


def main() -> int:
    port = int(os.environ.get('PORT', '6006'))
    try:
        logger.info('Pre-warming memory caches to avoid OOM killer...')
        
        # 1. 预热核心星空坐标集
        build_payload()
        
        # 2. 预热降维数据集（主线程一次性完成，规避请求并发时产生的额外 GC 负担）
        build_dimensionality_payload()
        
        logger.info('All datasets are loaded and cached successfully.')
        
        os.chdir(BASE_DIR)
        server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
        logger.info('Serving frontend at http://127.0.0.1:%s', port)
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info('Stopped by user')
        return 0
    except Exception:
        logger.error('Fatal error:\n%s', traceback.format_exc())
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
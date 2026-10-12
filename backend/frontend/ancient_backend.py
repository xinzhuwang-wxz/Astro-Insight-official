from __future__ import annotations

import json
import logging
import math
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_MERGED_JSON = BASE_DIR / 'data' / 'merged_Chinese_astronomy_data.json'
OUTPUT_JSON = BASE_DIR / 'data' / 'ancient_visualization_dataset.json'

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('ancient-backend')

try:
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    from astropy.time import Time
    ASTROPY_AVAILABLE = True
except Exception as exc:
    ASTROPY_AVAILABLE = False
    ASTROPY_IMPORT_ERROR = exc

_CATALOG_CACHE: Optional[List[Dict[str, Any]]] = None
_ANCIENT_PAYLOAD_CACHE: Optional[Dict[str, Any]] = None


def _col_letter_to_idx(cell_ref: str) -> int:
    letters = re.match(r'([A-Z]+)', cell_ref).group(1)
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - 64)
    return idx - 1


def read_xlsx_rows(path: Path) -> List[Dict[str, str]]:
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
                if cell_type == 's' and value.isdigit() and int(value) < len(shared_strings):
                    value = shared_strings[int(value)]
                values[idx] = value
            if i == 0:
                headers = values
            else:
                rows.append({headers[j]: values[j] if j < len(values) else '' for j in range(len(headers))})
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


def clean_int(value: Any) -> Optional[int]:
    val = clean_float(value)
    return int(val) if val is not None else None


def _extract_feature_value(row: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    for key in keys:
        if key in row and row[key] not in ('', None):
            return row[key]
    return default


def sanitize_json_payload(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: sanitize_json_payload(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_json_payload(v) for v in obj]
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    return obj


def process_catalog() -> List[Dict[str, Any]]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE
    rows = json.loads(FRONTEND_MERGED_JSON.read_text(encoding='utf-8'))
    valid = []
    for row in rows:
        hip = clean_int(row.get('HIP'))
        ra = clean_float(row.get('RA') or row.get('ra'))
        dec = clean_float(row.get('Dec') or row.get('dec'))
        if hip is None or ra is None or dec is None:
            continue
        valid.append({
            'hip': hip,
            'ra_j2000': ra,
            'dec_j2000': dec,
            'mag': clean_float(row.get('Vmag') or row.get('视星等')),
            'pmra': clean_float(row.get('pmRA') or row.get('pmra')),
            'pmdec': clean_float(row.get('pmDE') or row.get('pmdec')),
            'parallax': clean_float(row.get('Plx') or row.get('parallax')),
            'radial_velocity': clean_float(row.get('RV') or row.get('radial_velocity')),
            '星官': (row.get('星官') or '').strip(),
            '中国星名': (row.get('中国星名') or '').strip(),
        })
    if not ASTROPY_AVAILABLE:
        for item in valid:
            item['ra_1054'] = item['ra_j2000']
            item['dec_1054'] = item['dec_j2000']
        _CATALOG_CACHE = valid
        return valid
    epoch_target = Time('1054-01-01T00:00:00', scale='utc')
    epoch_source = Time('J2000')
    coords = SkyCoord(
        ra=[x['ra_j2000'] for x in valid] * u.deg,
        dec=[x['dec_j2000'] for x in valid] * u.deg,
        frame='icrs',
        obstime=epoch_source,
        pm_ra_cosdec=[(x['pmra'] or 0.0) for x in valid] * u.mas / u.yr,
        pm_dec=[(x['pmdec'] or 0.0) for x in valid] * u.mas / u.yr,
        radial_velocity=[(x['radial_velocity'] or 0.0) for x in valid] * u.km / u.s,
    )
    moved = coords.apply_space_motion(new_obstime=epoch_target)
    for item, ra_1054, dec_1054 in zip(valid, moved.ra.deg, moved.dec.deg):
        item['ra_1054'] = float(ra_1054)
        item['dec_1054'] = float(dec_1054)
    _CATALOG_CACHE = valid
    return valid


def group_constellations(coord_map: Dict[int, Tuple[float, float, float, str]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rows = json.loads(FRONTEND_MERGED_JSON.read_text(encoding='utf-8'))
    points = []
    seen_by_office: Dict[str, set] = {}
    for row in rows:
        star_office = (row.get('星官') or '').strip()
        hip = clean_int(row.get('HIP'))
        ra = clean_float(row.get('RA') or row.get('ra'))
        dec = clean_float(row.get('Dec') or row.get('dec'))
        mag = clean_float(row.get('Vmag') or row.get('视星等'))
        if not star_office or ra is None or dec is None or hip is None:
            continue
        dedupe_key = (hip, round(ra, 8), round(dec, 8))
        seen_keys = seen_by_office.setdefault(star_office, set())
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        ra_1054, dec_1054, resolved_mag = coord_map.get(hip, (ra, dec, mag, star_office))[:3]
        points.append({'星官': star_office, 'HIP': hip, 'ra': ra_1054, 'dec': dec_1054, 'mag': resolved_mag})
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for pt in points:
        groups.setdefault(pt['星官'], []).append(pt)
    line_groups = []
    for name, pts in groups.items():
        line_groups.append({'name': name, 'style': {'linestyle': '-', 'linewidth': 1.5, 'alpha': 0.9, 'color': '#ffda79'}, 'points': [{'ra': p['ra'], 'dec': p['dec'], 'hip': p['HIP'], 'mag': p['mag']} for p in pts], 'count': len(pts)})
    return points, line_groups


def build_payload() -> Dict[str, Any]:
    global _ANCIENT_PAYLOAD_CACHE
    if _ANCIENT_PAYLOAD_CACHE is not None:
        return _ANCIENT_PAYLOAD_CACHE
    if OUTPUT_JSON.exists():
        try:
            _ANCIENT_PAYLOAD_CACHE = json.loads(OUTPUT_JSON.read_text(encoding='utf-8'))
            return _ANCIENT_PAYLOAD_CACHE
        except Exception:
            pass
    catalog = process_catalog()
    coord_map = {item['hip']: (item['ra_1054'], item['dec_1054'], item['mag'] if item['mag'] is not None else 6.0, item['星官']) for item in catalog}
    constellation_points, constellation_lines = group_constellations(coord_map)
    payload = {'stats': {'catalog_rows_loaded': len(catalog), 'catalog_rows_valid': len(catalog), 'constellation_points': len(constellation_points), 'constellation_groups': len(constellation_lines)}, 'catalog': catalog, 'constellations': constellation_lines, 'constellation_points': constellation_points, 'options': {'target_epoch': '1054-01-01T00:00:00'}}
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    _ANCIENT_PAYLOAD_CACHE = payload
    return payload

#!/usr/bin/env python3
"""Ancient astronomy visualization preprocessing and static service.

This script:
1. Reads the processed merged Chinese astronomy dataset from JSON.
2. Applies astropy SkyCoord.apply_space_motion to shift J2000 stars to epoch 1054.
3. Groups constellation lines by 星官.
4. Matches Tautou SN1054/Crab sources by RA/Dec tolerance (0.1 deg).
5. Exports a structured JSON payload consumed by the frontend.
6. Serves the frontend on the requested mapped port.
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

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
RAW_DIR = Path('/root/autodl-tmp/raw')
PROCESSED_DIR = Path('/root/autodl-tmp/processed')
OUTPUT_JSON = BASE_DIR / 'data' / 'ancient_visualization_dataset.json'

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
except Exception as exc:  # pragma: no cover
    ASTROPY_AVAILABLE = False
    ASTROPY_IMPORT_ERROR = exc


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


def clean_int(value: Any) -> Optional[int]:
    val = clean_float(value)
    return int(val) if val is not None else None


def parse_mag(value: Any) -> Optional[float]:
    return clean_float(value)


def process_catalog() -> List[Dict[str, Any]]:
    path = PROCESSED_DIR / 'merged_Chinese_astronomy_data.json'
    logger.info('Reading catalog JSON: %s', path)
    rows = json.loads(path.read_text(encoding='utf-8'))
    valid = []
    for row in rows:
        hip = clean_int(row.get('HIP'))
        ra = clean_float(row.get('RA') or row.get('ra'))
        dec = clean_float(row.get('Dec') or row.get('dec'))
        mag = parse_mag(row.get('Vmag') or row.get('视星等'))
        pmra = clean_float(row.get('pmRA') or row.get('pmra'))
        pmde = clean_float(row.get('pmDE') or row.get('pmdec'))
        plx = clean_float(row.get('Plx') or row.get('parallax'))
        rv = clean_float(row.get('RV') or row.get('radial_velocity'))
        if hip is None or ra is None or dec is None:
            continue
        valid.append({
            'hip': hip,
            'ra_j2000': ra,
            'dec_j2000': dec,
            'mag': mag,
            'pmra': pmra,
            'pmdec': pmde,
            'parallax': plx,
            'radial_velocity': rv,
        })

    logger.info('Valid catalog rows: %d', len(valid))
    if not ASTROPY_AVAILABLE:
        logger.warning('astropy unavailable, returning J2000 coordinates only: %s', ASTROPY_IMPORT_ERROR)
        for item in valid:
            item['ra_1054'] = item['ra_j2000']
            item['dec_1054'] = item['dec_j2000']
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
            logger.warning('Space motion failed for HIP %s: %s', item['hip'], row_exc)
            item['ra_1054'] = item['ra_j2000']
            item['dec_1054'] = item['dec_j2000']
            transformed.append(item)
    logger.info('Transformed catalog rows: %d', len(transformed))
    return transformed


def group_constellations() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    path = PROCESSED_DIR / 'merged_Chinese_astronomy_data.json'
    logger.info('Reading constellation JSON: %s', path)
    rows = json.loads(path.read_text(encoding='utf-8'))
    points = []
    for row in rows:
        star_office = (row.get('星官') or '').strip()
        hip = clean_int(row.get('HIP'))
        ra = clean_float(row.get('RA') or row.get('ra'))
        dec = clean_float(row.get('Dec') or row.get('dec'))
        mag = parse_mag(row.get('Vmag') or row.get('视星等'))
        if not star_office or ra is None or dec is None or hip is None:
            continue
        points.append({
            '星官': star_office,
            'HIP': hip,
            'ra': ra,
            'dec': dec,
            'mag': mag,
            'source': 'merged_Chinese_astronomy_data.json',
        })

    groups: Dict[str, List[Dict[str, Any]]] = {}
    for pt in points:
        groups.setdefault(pt['星官'], []).append(pt)

    line_style = {
        'linestyle': '-',
        'linewidth': 1.2,
        'alpha': 0.85,
        'color': '#8ea2ff',
    }
    line_groups = []
    for name, pts in groups.items():
        line_groups.append({
            'name': name,
            'style': dict(line_style),
            'points': [{'ra': p['ra'], 'dec': p['dec'], 'hip': p['HIP'], 'mag': p['mag']} for p in pts],
            'count': len(pts),
        })
    logger.info('Constellation groups built from JSON: %d', len(line_groups))
    return points, line_groups


def process_tautou_matches(catalog: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    path = PROCESSED_DIR / 'clean_cols_HSCv3.1Tautou.xlsx'
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

    logger.info('Tautou targets loaded: %d', len(targets))

    '''
    matches = []
    matched_points = []
    for target in targets:
        best = None
        for star in catalog:
            dist = angular_distance_deg(target['ra'], target['dec'], star['ra_1054'], star['dec_1054'])
            if dist <= 0.1 and (best is None or dist < best['distance_deg']):
                best = {
                    'target_name': target['target_name'],
                    'target_ra': target['ra'],
                    'target_dec': target['dec'],
                    'matched_hip': star['hip'],
                    'matched_ra_1054': star['ra_1054'],
                    'matched_dec_1054': star['dec_1054'],
                    'distance_deg': round(dist, 6),
                    'mag': star['mag'],
                    'source': 'caafrc',
                }
        if best:
            matches.append(best)
            matched_points.append({
                'hip': best['matched_hip'],
                'ra': best['matched_ra_1054'],
                'dec': best['matched_dec_1054'],
                'label': target['target_name'],
                'distance_deg': best['distance_deg'],
            })

    logger.info('SN1054 matches found: %d', len(matches))
    return targets, matches, matched_points
    '''

    matches: List[Dict[str, Any]] = []
    matched_points: List[Dict[str, Any]] = []
    return targets, matches, matched_points

def angular_distance_deg(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    if ASTROPY_AVAILABLE:
        c1 = SkyCoord(ra=ra1 * u.deg, dec=dec1 * u.deg, frame='icrs')
        c2 = SkyCoord(ra=ra2 * u.deg, dec=dec2 * u.deg, frame='icrs')
        return float(c1.separation(c2).deg)
    # fallback
    r1, d1, r2, d2 = map(math.radians, [ra1, dec1, ra2, dec2])
    s = math.sin((d2 - d1) / 2) ** 2 + math.cos(d1) * math.cos(d2) * math.sin((r2 - r1) / 2) ** 2
    return math.degrees(2 * math.asin(min(1.0, math.sqrt(s))))


def build_payload() -> Dict[str, Any]:
    catalog = process_catalog()
    constellation_points, constellation_lines = group_constellations()
    tautou_targets, matches, matched_points = process_tautou_matches(catalog)
    stats = {
        'catalog_rows_loaded': len(json.loads((PROCESSED_DIR / 'merged_Chinese_astronomy_data.json').read_text(encoding='utf-8'))),
        'catalog_rows_valid': len(catalog),
        'constellation_points': len(constellation_points),
        'constellation_groups': len(constellation_lines),
        'tautou_targets': len(tautou_targets),
        'sn1054_matches': len(matches),
    }
    payload = {
        'stats': stats,
        'catalog': catalog,
        'constellations': constellation_lines,
        'constellation_points': constellation_points,
        'tautou_targets': tautou_targets,
        'sn1054_matches': matches,
        'sn1054_points': matched_points,
        'options': {
            'constellation_line_style': {
                'linestyle': '-',
                'linewidth': 1.2,
                'alpha': 0.85,
                'color': '#8ea2ff',
            },
            'match_tolerance_deg': 0.1,
            'target_epoch': '1054-01-01T00:00:00',
        }
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info('Exported dataset JSON: %s', OUTPUT_JSON)
    return payload


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        return super().end_headers()


def main() -> int:
    port = int(os.environ.get('PORT', '6006'))
    try:
        logger.info('Building ancient visualization payload...')
        build_payload()
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

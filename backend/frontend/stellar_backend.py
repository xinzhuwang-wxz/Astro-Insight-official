from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

import numpy as np

# 从 ancient_backend 仅导入基础字段提取和目录处理函数，去掉了 sanitize_json_payload 的导入
from ancient_backend import _extract_feature_value, process_catalog

BASE_DIR = Path(__file__).resolve().parent
GAIA_INPUT_JSON = BASE_DIR / 'data' / 'gaia.json'
STELLAR_OUTPUT_JSON = BASE_DIR / 'data' / 'stellar_analysis_dataset.json'

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('stellar-backend')


def sanitize_json_payload(obj: Any) -> Any:
    """
    本地实现的 JSON 净化函数。
    递归清洗 Python 数据结构，将标准 JSON 不支持的 float('nan') 或无穷大（inf）转换为 None，
    确保生成的 JSON 能够被标准前端解析器正确读取。
    """
    if isinstance(obj, dict):
        return {k: sanitize_json_payload(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json_payload(x) for x in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


def _clean_to_float(val: Any) -> Optional[float]:
    """安全地将任何类型转换为 float，过滤掉 NaN、Inf、空字符及特定占位符"""
    if val is None:
        return None
    if isinstance(val, str):
        val_str = val.strip().lower()
        if val_str in ('', 'null', 'none', 'nan', 'undefined', '—', '-'):
            return None
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (ValueError, TypeError):
        return None


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
    return float((math.degrees(math.atan2(pmdec or 0.0, pmra or 0.0)) + 360.0) % 360.0)


def _classify_hr_stage(teff: Optional[float], abs_mag: Optional[float]) -> str:
    if teff is None or abs_mag is None:
        return 'unknown'
    if teff >= 7000:
        return 'hot_main_sequence' if abs_mag > 0 else 'giant_candidate'
    if teff >= 5200:
        return 'giant' if abs_mag < 2.5 else 'main_sequence'
    if teff >= 3700:
        return 'subgiant_or_giant' if abs_mag < 4.5 else 'main_sequence'
    return 'cool_dwarf'


def _ballesteros_teff(bp_rp: float) -> float:
    """
    学术通用的 Ballesteros 经验公式，利用 G_BP - G_RP 估算有效温度 Teff
    """
    try:
        val = max(-0.5, min(4.0, bp_rp))
        term1 = 1.0 / (0.92 * val + 1.7)
        term2 = 1.0 / (0.92 * val + 0.62)
        teff = 4600.0 * ((term1 + term2) ** 0.9)
        return float(teff)
    except Exception:
        return 4000.0


def _fit_color_temp_relation(catalog: List[Dict[str, Any]]) -> Callable[[float], float]:
    """
    自适应颜色-温度转换器。
    """
    bp_rp_list = []
    teff_list = []
    
    total_items = len(catalog)
    has_teff_count = 0
    has_bp_rp_count = 0
    both_count = 0
    
    for item in catalog:
        raw_teff = item.get('teff_gspphot')
        raw_bp_rp = item.get('bp_rp')
        
        t = _clean_to_float(raw_teff)
        idx = _clean_to_float(raw_bp_rp)
        
        if t is not None:
            has_teff_count += 1
        if idx is not None:
            has_bp_rp_count += 1
            
        if t is not None and idx is not None:
            both_count += 1
            if 2500.0 <= t <= 12000.0 and -0.5 <= idx <= 4.0:
                bp_rp_list.append(idx)
                teff_list.append(t)
                
    logger.info(
        f"[数据诊断] 星表总数: {total_items} | "
        f"含有效温度: {has_teff_count} | "
        f"含颜色指数: {has_bp_rp_count} | "
        f"两者完备: {both_count}"
    )
    
    if len(bp_rp_list) >= 15:
        try:
            coefs = np.polyfit(bp_rp_list, teff_list, deg=3)
            poly_model = np.poly1d(coefs)
            logger.info(f"成功构建自适应 3 阶多项式温度拟合模型（参与拟合点数: {len(bp_rp_list)}）")
            return lambda x: float(np.clip(poly_model(max(-0.5, min(4.0, x))), 3000.0, 12000.0))
        except Exception as e:
            logger.error(f"自适应拟合失败 ({e})，将回退至物理公式。")
            
    logger.info("采用 Ballesteros 经典物理公式进行颜色-温度转换。")
    return _ballesteros_teff


def _build_stellar_analysis_payload() -> Dict[str, Any]:
    if not GAIA_INPUT_JSON.exists():
        logger.error(f"未找到 gaia.json 输入文件: {GAIA_INPUT_JSON}")
        return {"error": "gaia.json not found"}
        
    try:
        raw_data = json.loads(GAIA_INPUT_JSON.read_text(encoding='utf-8'))
        logger.info(f"成功读取 gaia.json，共加载 {len(raw_data)} 条原始恒星记录。")
    except Exception as e:
        logger.error(f"读取 gaia.json 失败: {e}")
        return {"error": str(e)}

    teff_converter = _fit_color_temp_relation(raw_data)
    rows: List[Dict[str, Any]] = []
    
    for item in raw_data:
        ra_deg = _clean_to_float(item.get('ra'))
        dec_deg = _clean_to_float(item.get('dec'))
        parallax = _clean_to_float(item.get('parallax'))
        parallax_err = _clean_to_float(item.get('parallax_error'))
        
        g_mag = _clean_to_float(item.get('phot_g_mean_mag'))
        bp_rp = _clean_to_float(item.get('bp_rp'))
        bp_g = _clean_to_float(item.get('bp_g'))
        g_rp = _clean_to_float(item.get('g_rp'))
        
        pmra = _clean_to_float(item.get('pmra'))
        pmdec = _clean_to_float(item.get('pmdec'))
        rv = _clean_to_float(item.get('radial_velocity'))
        ruwe = _clean_to_float(item.get('ruwe'))
        
        teff = _clean_to_float(item.get('teff_gspphot'))
        ag = _clean_to_float(item.get('ag_gspphot')) or 0.0
        ebpminrp = _clean_to_float(item.get('ebpminrp_gspphot')) or 0.0
        distance_gspphot = _clean_to_float(item.get('distance_gspphot'))

        if ra_deg is None or dec_deg is None:
            continue

        if distance_gspphot is not None and distance_gspphot > 0:
            dist_pc = distance_gspphot
            dist_source = 'gspphot'
        elif parallax is not None and parallax > 0:
            dist_pc = 1000.0 / parallax
            dist_source = 'geometry'
        else:
            dist_pc = None
            dist_source = 'unknown'

        x_space, y_space, z_space = None, None, None
        if dist_pc is not None:
            ra_rad = math.radians(ra_deg)
            dec_rad = math.radians(dec_deg)
            x_space = float(dist_pc * math.cos(dec_rad) * math.cos(ra_rad))
            y_space = float(dist_pc * math.cos(dec_rad) * math.sin(ra_rad))
            z_space = float(dist_pc * math.sin(dec_rad))

        bp_rp_corrected = bp_rp - ebpminrp if bp_rp is not None else None
        
        abs_mag = None
        if g_mag is not None and dist_pc is not None and dist_pc > 0:
            abs_mag = float(g_mag - 5 * math.log10(dist_pc / 10.0) - ag)

        is_estimated = False
        if teff is None and bp_rp is not None and teff_converter is not None:
            try:
                teff = teff_converter(bp_rp)
                is_estimated = True
            except Exception:
                pass

        stage = _classify_hr_stage(teff, abs_mag)
        
        quality_flag = 'good'
        if parallax_err is not None and parallax is not None and parallax > 0:
            if parallax_err > 2 * parallax:
                quality_flag = 'poor_parallax'
                
        if is_estimated:
            quality_flag = 'estimated_teff'
        elif teff is None:
            quality_flag = 'missing_teff'

        pm_total = math.hypot(pmra or 0.0, pmdec or 0.0) if (pmra or pmdec) else None

        row = {
            'id': item['designation'],
            'hip': '—',
            'name': item['designation'].replace("Gaia DR3 ", "DR3 "),
            'office': '蟹状星云天区',
            'ra': ra_deg,
            'dec': dec_deg,
            'parallax': parallax,
            'parallax_error': parallax_err,
            'pmra': pmra,
            'pmdec': pmdec,
            'pm_total': pm_total,
            'pm_angle': float((math.degrees(math.atan2(pmdec or 0.0, pmra or 0.0)) + 360.0) % 360.0) if (pmra or pmdec) else None,
            'rv': rv,
            'teff': teff,
            'bp_rp': bp_rp,
            'bp_rp_corrected': bp_rp_corrected,
            'bp_g': bp_g,
            'g_rp': g_rp,
            'g_mag': g_mag,
            'mag': g_mag,
            'abs_mag': abs_mag,
            'mh': _clean_to_float(item.get('mh_gspphot')),
            'ruwe': ruwe,
            'stage': stage,
            'quality_flag': quality_flag,
            'radial_abs': abs(rv) if rv is not None else None,
            'x_space': x_space,
            'y_space': y_space,
            'z_space': z_space,
            'dist_pc': dist_pc,
            'dist_source': dist_source,
        }
        rows.append(row)

    cmd_points = []
    hr_points = []
    cmd3d_points = []
    motion_vectors = []

    for r in rows:
        color_index = r['bp_rp'] if r['bp_rp'] is not None else r['bp_g']
        if color_index is None or r['g_mag'] is None:
            continue
        
        cmd_points.append({'id': r['id'], 'x': float(color_index), 'y': float(r['g_mag']), 'stage': r['stage'], 'row': r})
        
        if r['teff'] is not None and r['abs_mag'] is not None:
            hr_points.append({'id': r['id'], 'x': float(r['teff']), 'y': float(r['abs_mag']), 'stage': r['stage'], 'row': r})
            
        if r['x_space'] is not None:
            cmd3d_points.append({
                'id': r['id'],
                'x': float(r['x_space']),
                'y': float(r['y_space']),
                'z': float(r['z_space']),
                'stage': r['stage'],
                'row': r
            })
        else:
            cmd3d_points.append({
                'id': r['id'],
                'x': float(color_index),
                'y': float(r['g_mag']),
                'z': float(r['parallax'] or 0.0),
                'stage': r['stage'],
                'row': r
            })

        motion_vectors.append({
            'id': r['id'],
            'ra': float(r['ra']),
            'dec': float(r['dec']),
            'pmra': float(r['pmra']) if r['pmra'] is not None else None,
            'pmdec': float(r['pmdec']) if r['pmdec'] is not None else None,
            'rv': float(r['rv']) if r['rv'] is not None else None,
            'pm_total': r['pm_total'],
            'pm_angle': r['pm_angle'],
            'stage': r['stage'],
            'quality_flag': r['quality_flag'],
            'row': r
        })

    def stage_counts(points: List[Dict[str, Any]]) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for p in points:
            result[p['stage']] = result.get(p['stage'], 0) + 1
        return result

    payload = {
        'stats': {
            'total': len(raw_data),
            'filtered': len(rows),
            'cmd_points': len(cmd_points),
            'hr_points': len(hr_points),
            'motion_points': len(motion_vectors),
            'missing_teff_removed': sum(1 for item in raw_data if _clean_to_float(item.get('teff_gspphot')) is None and _clean_to_float(item.get('bp_rp')) is None),
            'parallax_outliers_removed': sum(1 for item in raw_data if (_clean_to_float(item.get('parallax_error')) is not None and _clean_to_float(item.get('parallax')) is not None and float(_clean_to_float(item.get('parallax_error'))) > 2.0 * abs(float(_clean_to_float(item.get('parallax')))))),
        },
        'cmd': {'points': cmd_points, 'stage_counts': stage_counts(cmd_points)},
        'hr': {'points': hr_points, 'stage_counts': stage_counts(hr_points)},
        'cmd3d': {'points': cmd3d_points, 'stage_counts': stage_counts(cmd3d_points)},
        'motion': {'vectors': motion_vectors},
        'selected_rows': rows,
    }
    
    STELLAR_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    
    # 使用本地编写的净化逻辑
    safe_payload = sanitize_json_payload(payload)
    STELLAR_OUTPUT_JSON.write_text(json.dumps(safe_payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return safe_payload


def build_stellar_analysis_payload() -> Dict[str, Any]:
    logger.info("正在强制读取 gaia.json 重新计算蟹状星云天区恒星空间分布...")
    return _build_stellar_analysis_payload()
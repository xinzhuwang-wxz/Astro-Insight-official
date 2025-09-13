#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天文代码模板管理器
提供各种天文分析任务的代码模板
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


class AnalysisType(Enum):
    """分析类型枚举"""
    PHOTOMETRY = "photometry"
    SPECTROSCOPY = "spectroscopy"
    ASTROMETRY = "astrometry"
    CLASSIFICATION = "classification"
    VARIABLE_STAR = "variable_star"
    EXOPLANET = "exoplanet"
    GALAXY = "galaxy"
    NEBULA = "nebula"


class ObjectType(Enum):
    """天体类型枚举"""
    STAR = "star"
    GALAXY = "galaxy"
    NEBULA = "nebula"
    PLANET = "planet"
    ASTEROID = "asteroid"
    COMET = "comet"
    SUPERNOVA = "supernova"
    QUASAR = "quasar"
    EXOPLANET = "exoplanet"
    VARIABLE_STAR = "variable_star"
    BINARY_STAR = "binary_star"
    CLUSTER = "cluster"


@dataclass
class CodeTemplate:
    """代码模板数据类"""
    name: str
    description: str
    analysis_type: AnalysisType
    object_types: List[ObjectType]
    required_libraries: List[str]
    template_code: str
    parameters: Dict[str, str]
    example_usage: str


def parse_hms_to_degrees(hms_str: str) -> float:
    """将HMS格式（时:分:秒）转换为度数"""
    parts = hms_str.strip().split()
    if len(parts) >= 3:
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return (hours + minutes/60 + seconds/3600) * 15  # 1小时 = 15度
    return None

def parse_dms_to_degrees(dms_str: str) -> float:
    """将DMS格式（度:分:秒）转换为度数"""
    parts = dms_str.strip().replace('+', '').split()
    if len(parts) >= 3:
        degrees = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        result = abs(degrees) + minutes/60 + seconds/3600
        return result if degrees >= 0 else -result
    return None

def query_simbad_by_name(object_name: str) -> Dict[str, Any]:
    """通过名称查询SIMBAD数据库"""
    result = {
        'found': False,
        'object_name': object_name,
        'main_category': 'Unknown',
        'sub_category': 'Unknown',
        'detailed_classification': 'No data available',
        'confidence': 'Low',
        'key_features': 'No features available',
        'data_source': 'SIMBAD',
        'coordinates': {'ra': None, 'dec': None},
        'magnitude': None,
        'object_type': None
    }
    
    try:
        from astroquery.simbad import Simbad
        import numpy as np
        
        
        # 配置SIMBAD查询，添加更多字段
        custom_simbad = Simbad()
        custom_simbad.add_votable_fields('otype', 'ra', 'dec', 'plx', 'flux(V)', 'flux(B)', 'flux(R)')
        
        # 执行查询
        query_result = custom_simbad.query_object(object_name)
        
        if query_result is not None and len(query_result) > 0:
            row = query_result[0]
            
            # 获取对象类型 - 检查字段是否存在
            object_type = "Unknown"
            if 'OTYPE' in row.colnames:
                object_type = row['OTYPE'].decode('utf-8') if hasattr(row['OTYPE'], 'decode') else str(row['OTYPE'])
            elif 'otype' in row.colnames:
                object_type = row['otype'].decode('utf-8') if hasattr(row['otype'], 'decode') else str(row['otype'])
            
            # 获取坐标 - 转换为度数
            ra_deg = None
            dec_deg = None
            
            if 'ra' in row.colnames and row['ra'] is not None and not np.ma.is_masked(row['ra']):
                try:
                    from astropy.coordinates import SkyCoord
                    import astropy.units as u
                    
                    # 使用astropy解析坐标字符串
                    ra_str = str(row['ra']).strip()
                    dec_str = str(row['dec']).strip() if 'dec' in row.colnames else None
                    
                    # 创建SkyCoord对象来解析坐标
                    coord = SkyCoord(ra=ra_str, dec=dec_str, unit=(u.hourangle, u.deg))
                    ra_deg = coord.ra.degree
                    dec_deg = coord.dec.degree
                    
                except Exception as coord_error:
                    print(f"坐标解析错误: {coord_error}")
                    # 备用方法：手动解析HMS和DMS格式
                    try:
                        ra_deg = parse_hms_to_degrees(str(row['RA']))
                        dec_deg = parse_dms_to_degrees(str(row['DEC']))
                    except Exception as manual_error:
                        print(f"手动坐标解析也失败: {manual_error}")
                        ra_deg = None
                        dec_deg = None
            
            
            # 获取星等信息
            magnitude = None
            for mag_field in ['FLUX_V', 'FLUX_B', 'FLUX_R']:
                if mag_field in row.colnames:
                    mag_value = row[mag_field]
                    if mag_value is not None and not np.ma.is_masked(mag_value):
                        magnitude = float(mag_value)
                        break
            
            # 分类天体类型
            classification = classify_simbad_type(object_type)
            
            result.update({
                'found': True,
                'object_type': object_type,
                'coordinates': {'ra': ra_deg, 'dec': dec_deg},
                'magnitude': magnitude,
                **classification
            })
            
        else:
            pass  # 未找到天体
    except ImportError:
        print("Warning: astroquery not available. Install with: pip install astroquery")
    except Exception as e:
        import traceback
        traceback.print_exc()
    
    return result


def classify_simbad_type(object_type: str, object_name: str = None) -> Dict[str, str]:
    """完全动态分类SIMBAD对象类型 - 完全基于LLM智能分析"""
    
    if not object_type or not object_type.strip():
        return {
            'hierarchy': ['天体', '未知类型'],
            'main_category': '未知类型',
            'sub_category': '未知类型',
            'detailed_classification': '未知类型',
            'key_features': '无法识别',
            'confidence': 'Low',
            'similar_objects': [],
            'object_properties': [],
            'formation_mechanism': '需要进一步研究',
            'observational_features': [],
            'evolutionary_stage': '需要进一步研究'
        }
    
    obj_type = object_type.strip()
    
    # 完全使用LLM进行动态分类
    return _classify_with_llm(obj_type, object_name)


def _classify_with_llm(obj_type: str, object_name: str = None) -> Dict[str, str]:
    """使用LLM完全动态分类天体类型"""
    
    try:
        from src.llms.llm import get_llm_by_type
        
        # 获取LLM实例
        llm = get_llm_by_type("basic")
        
        # 构建LLM提示 - 完全动态分类
        prompt = f"""作为专业天文学家，请分析以下SIMBAD天体类型代码并提供完整的分类信息：

SIMBAD类型代码: {obj_type}
天体名称: {object_name or '未知'}

重要：请基于SIMBAD官方分类系统理解这些代码：
- rG = 射电星系 (Radio Galaxy)
- G = 星系 (Galaxy) 
- S = 旋涡星系 (Spiral Galaxy)
- E = 椭圆星系 (Elliptical Galaxy)
- * = 恒星 (Star)
- SB* = 分光双星 (Spectroscopic Binary)
- V* = 变星 (Variable Star)
- QSO = 类星体 (Quasar)
- BLL = Blazar
- WD = 白矮星 (White Dwarf)
- NS = 中子星 (Neutron Star)
- BH = 黑洞 (Black Hole)

请提供以下完整信息（用JSON格式返回）：
1. 分类层次结构（从大类到具体类型）
2. 主要分类类别
3. 子分类类别
4. 详细分类
5. 关键特征描述
6. 置信度评估

返回格式：
{{
    "hierarchy": ["大类", "中类", "小类", "具体类型"],
    "main_category": "主要分类",
    "sub_category": "子分类",
    "detailed_classification": "详细分类",
    "key_features": "关键特征描述",
    "confidence": "High/Medium/Low"
}}"""

        # 调用LLM
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        response_text = response.content
        
        # 尝试解析LLM响应
        import json
        try:
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                enhanced_data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            # 如果JSON解析失败，使用默认值
            enhanced_data = {
                "hierarchy": ['天体', '未知类型', obj_type],
                "main_category": "未知类型",
                "sub_category": obj_type,
                "detailed_classification": obj_type,
                "key_features": "需要进一步分析",
                "confidence": "Low",
                "similar_objects": [],
                "object_properties": [],
                "formation_mechanism": "需要进一步研究",
                "observational_features": [],
                "evolutionary_stage": "需要进一步研究"
            }
        
        return enhanced_data
        
    except Exception as e:
        # 如果LLM调用失败，返回最基本的分类
        return {
            'hierarchy': ['天体', '未知类型', obj_type],
            'main_category': '未知类型',
            'sub_category': obj_type,
            'detailed_classification': obj_type,
            'key_features': '需要进一步分析',
            'confidence': 'Low',
            'similar_objects': [],
            'object_properties': [],
            'formation_mechanism': '需要进一步研究',
            'observational_features': [],
            'evolutionary_stage': '需要进一步研究'
        }


class AstronomyCodeTemplates:
    """天文代码模板管理器"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, CodeTemplate]:
        """初始化所有模板"""
        templates = {}
        
        # 天体分类检索模板
        templates["simple_classification"] = CodeTemplate(
            name="天体分类检索",
            description="从天文数据库检索天体分类信息",
            analysis_type=AnalysisType.CLASSIFICATION,
            object_types=[
                ObjectType.STAR,
                ObjectType.GALAXY,
                ObjectType.NEBULA,
                ObjectType.SUPERNOVA,
                ObjectType.QUASAR,
                ObjectType.ASTEROID,
                ObjectType.COMET,
                ObjectType.EXOPLANET,
            ],
            required_libraries=["astropy", "astroquery", "pandas"],
            template_code="""#!/usr/bin/env python3
# 天体分类检索代码
# 生成时间: {timestamp}
# 查询目标: {target_name}

import pandas as pd
from astropy.coordinates import SkyCoord
from astropy import units as u
try:
    from astroquery.simbad import Simbad
    ASTROQUERY_AVAILABLE = True
except ImportError:
    ASTROQUERY_AVAILABLE = False
    print("Warning: astroquery not available. Install with: pip install astroquery")
import warnings
warnings.filterwarnings('ignore')

def query_object_classification(object_name=None, coordinates=None):
    \"\"\"查询天体分类信息\"\"\"
    results = {{
        'object_name': object_name or 'Unknown',
        'main_category': 'Unknown',
        'sub_category': 'Unknown',
        'detailed_classification': 'No data available',
        'confidence': 'Low',
        'key_features': 'No features available',
        'data_source': 'None'
    }}
    
    try:
        if object_name:
            # 使用SIMBAD查询
            from src.code_generation.templates import query_simbad_by_name
            simbad_result = query_simbad_by_name(object_name)
            if simbad_result['found']:
                results.update(simbad_result)
                return results
        
        print(f"未找到天体信息: {{object_name or coordinates}}")
        
    except Exception as e:
        print(f"查询过程中出现错误: {{e}}")
    
    return results

# 主程序
if __name__ == "__main__":
    target_name = "{target_name}"
    result = query_object_classification(target_name)
    
    print(f"\\n=== 天体分类结果 ===")
    print(f"天体名称: {{result['object_name']}}")
    print(f"主要类别: {{result['main_category']}}")
    print(f"子类别: {{result['sub_category']}}")
    print(f"详细分类: {{result['detailed_classification']}}")
    print(f"关键特征: {{result['key_features']}}")
    print(f"置信度: {{result['confidence']}}")
    print(f"数据源: {{result['data_source']}}")
""",
            parameters={
                "target_name": "目标天体名称",
                "timestamp": "代码生成时间戳"
            },
            example_usage="""# 使用示例
from src.code_generation.templates import AstronomyCodeTemplates

templates = AstronomyCodeTemplates()
template = templates.get_template("simple_classification")
code = templates.generate_code("simple_classification", {"target_name": "M31"})
print(code)
"""
        )
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[CodeTemplate]:
        """获取指定模板"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """列出所有可用模板"""
        return list(self.templates.keys())
    
    def generate_code(self, template_name: str, parameters: Dict[str, str]) -> str:
        """生成代码"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"模板 '{template_name}' 不存在")
        
        # 添加默认参数
        from datetime import datetime
        default_params = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_name": "Unknown"
        }
        default_params.update(parameters)
        
        try:
            return template.template_code.format(**default_params)
        except KeyError as e:
            raise ValueError(f"缺少必需参数: {e}")
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """获取模板信息"""
        template = self.get_template(template_name)
        if not template:
            return {}
        
        return {
            "name": template.name,
            "description": template.description,
            "analysis_type": template.analysis_type.value,
            "object_types": [obj_type.value for obj_type in template.object_types],
            "required_libraries": template.required_libraries,
            "parameters": template.parameters
        }


# 导出的主要函数和类
__all__ = [
    'AstronomyCodeTemplates',
    'CodeTemplate',
    'AnalysisType',
    'ObjectType',
    'query_simbad_by_name',
    'classify_simbad_type'
]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simbad天体数据库客户端
提供天体分类和基本信息查询功能
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
import time
import re

class SimbadClient:
    """Simbad天体数据库客户端"""
    
    def __init__(self):
        self.base_url = "http://simbad.u-strasbg.fr/simbad/sim-id"
        self.search_url = "http://simbad.u-strasbg.fr/simbad/sim-sam"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Astro-Insight/1.0 (astronomical research assistant)'
        })
        # 禁用代理，直接访问Simbad
        self.session.proxies = {
            'http': None,
            'https': None
        }
        
    def search_object(self, object_name: str) -> Dict[str, Any]:
        """
        搜索天体对象
        
        Args:
            object_name: 天体名称
            
        Returns:
            包含天体信息的字典
        """
        try:
            # 清理天体名称
            clean_name = self._clean_object_name(object_name)
            
            # 构建查询参数 - 使用ASCII格式
            params = {
                'Ident': clean_name,
                'output.format': 'ASCII'
            }
            
            # 执行查询
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析ASCII结果
            return self._parse_ascii(response.text, clean_name)
                
        except Exception as e:
            print(f"Simbad查询失败: {e}")
            return self._create_error_result(object_name, str(e))
    
    def get_object_classification(self, object_name: str) -> Dict[str, Any]:
        """
        获取天体分类信息
        
        Args:
            object_name: 天体名称
            
        Returns:
            包含分类信息的字典
        """
        try:
            # 清理天体名称
            clean_name = self._clean_object_name(object_name)
            
            # 构建分类查询参数 - 使用ASCII格式，获取更多信息
            params = {
                'Ident': clean_name,
                'output.format': 'ASCII',
                'output.script': 'o',
                'output.params': '2'  # 获取更多参数信息
            }
            
            # 执行查询
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析分类信息
            classification_info = self._extract_classification_info(response.text, clean_name)
            return classification_info
            
        except Exception as e:
            print(f"Simbad分类查询失败: {e}")
            return self._create_error_result(object_name, str(e))
    
    def _clean_object_name(self, object_name: str) -> str:
        """清理天体名称"""
        # 移除常见的前缀和后缀
        clean_name = object_name.strip()
        
        # 移除中文描述
        clean_name = re.sub(r'[星系|恒星|行星|星云|黑洞|脉冲星|类星体]', '', clean_name)
        
        # 移除常见的英文描述
        clean_name = re.sub(r'\b(galaxy|star|planet|nebula|black hole|pulsar|quasar)\b', '', clean_name, flags=re.IGNORECASE)
        
        # 移除多余空格
        clean_name = ' '.join(clean_name.split())
        
        return clean_name
    
    def _parse_votable(self, content: str, object_name: str) -> Dict[str, Any]:
        """解析VOTable格式的结果"""
        try:
            root = ET.fromstring(content)
            
            # 查找RESOURCE元素
            resource = root.find('.//RESOURCE')
            if resource is None:
                return self._create_error_result(object_name, "未找到天体信息")
            
            # 查找TABLE元素
            table = resource.find('.//TABLE')
            if table is None:
                return self._create_error_result(object_name, "未找到天体数据表")
            
            # 解析数据
            result = {
                "object_name": object_name,
                "found": True,
                "source": "Simbad",
                "classification": "unknown",
                "object_type": "unknown",
                "coordinates": None,
                "magnitude": None,
                "distance": None,
                "raw_data": content[:500] + "..." if len(content) > 500 else content
            }
            
            # 这里可以添加更详细的VOTable解析逻辑
            # 由于VOTable格式复杂，我们先用基础解析
            
            return result
            
        except ET.ParseError as e:
            print(f"VOTable解析失败: {e}")
            return self._create_error_result(object_name, f"VOTable解析失败: {e}")
    
    def _parse_ascii(self, content: str, object_name: str) -> Dict[str, Any]:
        """解析ASCII格式的结果"""
        lines = content.split('\n')
        
        result = {
            "object_name": object_name,
            "found": False,
            "source": "Simbad",
            "classification": "unknown",
            "object_type": "unknown",
            "coordinates": None,
            "magnitude": None,
            "distance": None,
            "raw_data": content[:500] + "..." if len(content) > 500 else content
        }
        
        # 检查是否找到天体
        if "not found" in content.lower() or "no object" in content.lower():
            result["found"] = False
            result["error"] = "天体未找到"
            return result
        
        # 如果内容不为空且包含天体信息，认为找到了天体
        if content.strip() and ("Object" in content or "Coordinates" in content):
            result["found"] = True
        
        for line in lines:
            line = line.strip()
            
            # 解析天体类型 - 从Object行中提取
            if line.startswith("Object") and "---" in line:
                # 提取天体类型标识符
                parts = line.split("---")
                if len(parts) > 1:
                    type_part = parts[1].strip()
                    # 查找类型标识符
                    if "rG" in type_part:
                        result["object_type"] = "Radio Galaxy"
                        result["classification"] = "radio_galaxy"
                    elif "G" in type_part:
                        result["object_type"] = "Galaxy"
                        result["classification"] = "galaxy"
                    elif "S*" in type_part:
                        result["object_type"] = "Star"
                        result["classification"] = "star"
                    elif "Pl" in type_part:
                        result["object_type"] = "Planet"
                        result["classification"] = "planet"
                    elif "PN" in type_part:
                        result["object_type"] = "Planetary Nebula"
                        result["classification"] = "planetary_nebula"
                    elif "HII" in type_part:
                        result["object_type"] = "HII Region"
                        result["classification"] = "emission_nebula"
                    elif "Cl" in type_part:
                        result["object_type"] = "Cluster"
                        result["classification"] = "cluster"
                    else:
                        result["object_type"] = type_part
                        result["classification"] = self._classify_object_type(type_part)
            
            # 解析坐标
            if "Coordinates(ICRS" in line:
                coord_match = re.search(r'(\d+\s+\d+\s+[\d.]+)\s+([+-]\d+\s+\d+\s+[\d.]+)', line)
                if coord_match:
                    ra = coord_match.group(1)
                    dec = coord_match.group(2)
                    result["coordinates"] = f"RA: {ra}, Dec: {dec}"
            
            # 解析星等
            if "mag" in line.lower() and "V" in line:
                mag_match = re.search(r'V\s*=\s*([\d.+-]+)', line)
                if mag_match:
                    try:
                        result["magnitude"] = float(mag_match.group(1))
                    except ValueError:
                        pass
        
        return result
    
    def _extract_classification_info(self, content: str, object_name: str) -> Dict[str, Any]:
        """提取分类信息"""
        lines = content.split('\n')
        
        result = {
            "object_name": object_name,
            "found": False,
            "source": "Simbad",
            "classification": "unknown",
            "object_type": "unknown",
            "object_subtype": "unknown",
            "morphology": "unknown",
            "spectral_type": "unknown",
            "hierarchy": {
                "parents": 0,
                "children": 0,
                "siblings": 0
            },
            "raw_data": content[:500] + "..." if len(content) > 500 else content
        }
        
        for line in lines:
            line = line.strip()
            
            # 检查是否找到天体
            if "Object" in line and "not found" in line.lower():
                result["found"] = False
                result["error"] = "天体未找到"
                return result
            
            # 解析天体类型 - 从Object行中提取类型代码
            if "Object" in line and "---" in line:
                result["found"] = True
                # 匹配格式: Object M 13  ---  GlC  ---  OID=...
                type_match = re.search(r'---\s+([A-Za-z\*]+)\s+---', line)
                if type_match:
                    result["object_type"] = type_match.group(1).strip()
                    result["classification"] = self._classify_object_type(result["object_type"])
            
            # 备用解析：查找Object type行
            elif "Object type" in line or "Type" in line:
                result["found"] = True
                type_match = re.search(r'[A-Za-z\s]+', line)
                if type_match:
                    result["object_type"] = type_match.group().strip()
                    result["classification"] = self._classify_object_type(result["object_type"])
            
            # 解析形态学信息
            if "Morphology" in line or "Morph" in line:
                morph_match = re.search(r'[A-Za-z\s]+', line)
                if morph_match:
                    result["morphology"] = morph_match.group().strip()
            
            # 解析光谱类型
            if "Spectral type" in line or "SpType" in line:
                spec_match = re.search(r'[A-Za-z0-9\s]+', line)
                if spec_match:
                    result["spectral_type"] = spec_match.group().strip()
            
            # 解析层级信息
            if "hierarchy counts" in line.lower():
                # 解析格式: hierarchy counts: #parents=9, #children=2867, #siblings=0
                parents_match = re.search(r'#parents=(\d+)', line)
                children_match = re.search(r'#children=(\d+)', line)
                siblings_match = re.search(r'#siblings=(\d+)', line)
                
                if parents_match:
                    result["hierarchy"]["parents"] = int(parents_match.group(1))
                if children_match:
                    result["hierarchy"]["children"] = int(children_match.group(1))
                if siblings_match:
                    result["hierarchy"]["siblings"] = int(siblings_match.group(1))
        
        return result
    
    def _classify_object_type(self, object_type: str) -> str:
        """根据天体类型进行分类"""
        if not object_type or object_type.lower() == "unknown":
            return "unknown"
        
        object_type_lower = object_type.lower()
        
        # 星系分类
        if any(keyword in object_type_lower for keyword in ["galaxy", "gal", "星系", "rg"]):
            if "elliptical" in object_type_lower or "椭圆" in object_type_lower or "rg" in object_type_lower:
                return "elliptical_galaxy"
            elif "spiral" in object_type_lower or "螺旋" in object_type_lower:
                return "spiral_galaxy"
            elif "irregular" in object_type_lower or "不规则" in object_type_lower:
                return "irregular_galaxy"
            else:
                return "galaxy"
        
        # 星团分类
        elif any(keyword in object_type_lower for keyword in ["glc", "opc", "cluster", "星团"]):
            if "glc" in object_type_lower:
                return "globular_cluster"
            elif "opc" in object_type_lower:
                return "open_cluster"
            else:
                return "star_cluster"
        
        # 星云分类
        elif any(keyword in object_type_lower for keyword in ["snr", "hii", "nebula", "星云"]):
            if "snr" in object_type_lower:
                return "supernova_remnant"
            elif "hii" in object_type_lower:
                return "emission_nebula"
            else:
                return "nebula"
        
        # 双星分类
        elif any(keyword in object_type_lower for keyword in ["sb*", "binary", "双星"]):
            if "sb*" in object_type_lower:
                return "spectroscopic_binary"
            else:
                return "binary_star"
        
        # 恒星分类
        elif any(keyword in object_type_lower for keyword in ["star", "恒星", "dwarf", "giant", "supergiant"]):
            if "dwarf" in object_type_lower or "矮星" in object_type_lower:
                return "dwarf_star"
            elif "giant" in object_type_lower or "巨星" in object_type_lower:
                return "giant_star"
            elif "supergiant" in object_type_lower or "超巨星" in object_type_lower:
                return "supergiant_star"
            else:
                return "star"
        
        # 行星分类
        elif any(keyword in object_type_lower for keyword in ["planet", "行星", "exoplanet", "系外行星"]):
            return "planet"
        
        # 星云分类
        elif any(keyword in object_type_lower for keyword in ["nebula", "星云", "cloud"]):
            if "planetary" in object_type_lower or "行星状" in object_type_lower:
                return "planetary_nebula"
            elif "emission" in object_type_lower or "发射" in object_type_lower:
                return "emission_nebula"
            elif "reflection" in object_type_lower or "反射" in object_type_lower:
                return "reflection_nebula"
            else:
                return "nebula"
        
        # 黑洞分类
        elif any(keyword in object_type_lower for keyword in ["black hole", "黑洞", "bh"]):
            return "black_hole"
        
        # 脉冲星分类
        elif any(keyword in object_type_lower for keyword in ["pulsar", "脉冲星", "neutron star", "中子星"]):
            return "pulsar"
        
        # 类星体分类
        elif any(keyword in object_type_lower for keyword in ["quasar", "类星体", "qso"]):
            return "quasar"
        
        # 星团分类
        elif any(keyword in object_type_lower for keyword in ["cluster", "星团", "globular", "球状"]):
            if "globular" in object_type_lower or "球状" in object_type_lower:
                return "globular_cluster"
            else:
                return "open_cluster"
        
        else:
            return "unknown"
    
    def _create_error_result(self, object_name: str, error_message: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            "object_name": object_name,
            "found": False,
            "source": "Simbad",
            "error": error_message,
            "classification": "unknown",
            "object_type": "unknown"
        }
    
    def test_connection(self) -> bool:
        """测试Simbad连接"""
        try:
            # 测试查询一个已知天体
            result = self.search_object("M87")
            return result.get("found", False) or "error" not in result
        except Exception as e:
            print(f"Simbad连接测试失败: {e}")
            return False

# 测试函数
def test_simbad_client():
    """测试Simbad客户端"""
    client = SimbadClient()
    
    print("🔍 测试Simbad客户端")
    print("=" * 40)
    
    # 测试连接
    if client.test_connection():
        print("✅ Simbad连接正常")
    else:
        print("❌ Simbad连接失败")
        return
    
    # 测试天体查询
    test_objects = ["M87", "Sun", "Jupiter", "Crab Nebula", "Sgr A*"]
    
    for obj in test_objects:
        print(f"\n📝 查询天体: {obj}")
        result = client.get_object_classification(obj)
        
        if result.get("found"):
            print(f"✅ 找到天体: {result.get('object_type', 'unknown')}")
            print(f"   分类: {result.get('classification', 'unknown')}")
            if result.get("morphology"):
                print(f"   形态: {result.get('morphology')}")
            if result.get("spectral_type"):
                print(f"   光谱类型: {result.get('spectral_type')}")
        else:
            print(f"❌ 未找到天体: {result.get('error', 'unknown error')}")

if __name__ == "__main__":
    test_simbad_client()

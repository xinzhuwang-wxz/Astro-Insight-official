import sys
import os
sys.path.append(os.path.dirname(__file__))

from tap_client import run_adql
import logging
from typing import Dict, Any

# 配置日志
logger = logging.getLogger(__name__)

def get_object_by_identifier(object_id: str) -> Dict[str, Any]:
    """
    根据天体标识符获取基础天文数据
    
    Args:
        object_id: 天体标识符，如 'M13', 'NGC6205' 等
        
    Returns:
        包含天体基础信息的字典
    """
    # 清理输入参数
    object_id = object_id.strip().replace('\n', '').replace('\r', '')
    
    # 查询天体基础信息
    
    # 构建ADQL查询语句 - 使用简单的搜索方式
    query = f"""
    SELECT basic.oid,
           basic.RA,
           basic.DEC,
           basic.main_id AS "Main identifier",
           basic.coo_bibcode AS "Coord Reference",
           basic.nbref AS "NbReferences",
           basic.plx_value AS "Parallax",
           basic.rvz_radvel AS "Radial velocity",
           basic.galdim_majaxis,
           basic.galdim_minaxis,
           basic.galdim_angle AS "Galaxy ellipse angle"
    FROM basic
    WHERE basic.main_id = '{object_id.upper()}'
    """
    
    try:
        result = run_adql(query)
        
        if "error" in result:
            logger.error(f"Failed to query object {object_id}: {result['error']}")
            return {
                "success": False,
                "error": result["error"],
                "details": result.get("details", "")
            }
        
        # 格式化结果
        formatted_result = {
            "success": True,
            "object_id": object_id,
            "total_records": result.get("total_rows", 0),
            "data": []
        }
        
        # 处理查询结果
        if result.get("rows"):
            columns = result.get("columns", [])
            column_names = [col.get("name", f"col_{i}") for i, col in enumerate(columns)]
            
            for row in result["rows"]:
                record = {}
                for i, value in enumerate(row):
                    col_name = column_names[i] if i < len(column_names) else f"col_{i}"
                    record[col_name] = value
                formatted_result["data"].append(record)
            
            # 更新总记录数
            formatted_result["total_records"] = len(formatted_result["data"])
        else:
            # TAP服务没有返回数据
            logger.warning(f"TAP service returned no data, query object: {object_id}")
            logger.debug(f"TAP query result: {result}")
            formatted_result["data"] = []
            formatted_result["total_records"] = 0
        
        # 成功查询到记录
        return formatted_result
        
    except Exception as e:
        logger.error(f"Exception occurred while querying object {object_id}: {str(e)}")
        logger.debug(f"Query parameters: object_id={object_id}")
        import traceback
        logger.debug(f"Error stack trace: {traceback.format_exc()}")
        return {
            "success": False,
            "error": "查询执行异常",
            "details": str(e),
            "debug_info": {
                "object_id": object_id,
                "error_type": type(e).__name__,
                "query": query
            }
        }

def get_bibliographic_data(object_id: str) -> Dict[str, Any]:
    """
    根据天体标识符获取参考文献数据
    
    Args:
        object_id: 天体标识符，如 'M13', 'NGC6205' 等
        
    Returns:
        包含参考文献信息的字典
    """
    # 清理输入参数
    object_id = object_id.strip().replace('\n', '').replace('\r', '')
    
    # 查询天体参考文献
    
    # 构建ADQL查询语句 - 使用正确的语法，限制返回前5条
    query = f"""
    SELECT TOP 5 BIBCode,
           Journal,
           Title,
           "year",
           Volume,
           Page || '-' || Last_Page AS "Pages",
           DOI
    FROM ref
         JOIN has_ref ON oidbibref = oidbib
         JOIN ident ON has_ref.oidref = ident.oidref
    WHERE id = '{object_id.lower()}'
    ORDER BY "year" DESC
    """
    
    try:
        result = run_adql(query)
        
        if "error" in result:
            logger.error(f"Failed to query bibliographic data for object {object_id}: {result['error']}")
            return {
                "success": False,
                "error": result["error"],
                "details": result.get("details", "")
            }
        
        # 格式化结果
        formatted_result = {
            "success": True,
            "object_id": object_id,
            "total_references": result.get("total_rows", 0),
            "references": []
        }
        
        # 处理查询结果
        if result.get("rows"):
            columns = result.get("columns", [])
            column_names = [col.get("name", f"col_{i}") for i, col in enumerate(columns)]
            
            for row in result["rows"]:
                reference = {}
                for i, value in enumerate(row):
                    col_name = column_names[i] if i < len(column_names) else f"col_{i}"
                    reference[col_name] = value
                formatted_result["references"].append(reference)
        
        # 更新总记录数
        formatted_result["total_references"] = len(formatted_result["references"])
        
        # 成功查询到参考文献
        return formatted_result
        
    except Exception as e:
        logger.error(f"Exception occurred while querying bibliographic data for object {object_id}: {str(e)}")
        logger.debug(f"Query parameters: object_id={object_id}")
        import traceback
        logger.debug(f"Error stack trace: {traceback.format_exc()}")
        return {
            "success": False,
            "error": "查询执行异常",
            "details": str(e),
            "debug_info": {
                "object_id": object_id,
                "error_type": type(e).__name__,
                "query": query
            }
        }

def search_objects_by_coordinates(ra: float, dec: float, radius: float = 0.1) -> Dict[str, Any]:
    """
    根据坐标搜索附近的天体
    
    Args:
        ra: 赤经 (度)
        dec: 赤纬 (度)
        radius: 搜索半径 (度，默认0.1度)
        
    Returns:
        包含搜索结果的字典
    """
    # 坐标搜索天体
    
    # 构建ADQL查询语句 - 使用正确的几何函数
    query = f"""
    SELECT TOP 20
           basic.OID,
           RA,
           DEC,
           main_id,
           otype_txt AS "Object Type",
           DISTANCE(POINT('ICRS', RA, DEC), POINT('ICRS', {ra}, {dec})) AS "distance"
    FROM basic
    WHERE CONTAINS(POINT('ICRS', RA, DEC), CIRCLE('ICRS', {ra}, {dec}, {radius})) = 1
      AND RA IS NOT NULL
      AND DEC IS NOT NULL
    ORDER BY "distance"
    """
    
    try:
        result = run_adql(query)
        
        if "error" in result:
            logger.error(f"Coordinate search failed: {result['error']}")
            return {
                "success": False,
                "error": result["error"],
                "details": result.get("details", "")
            }
        
        # 格式化结果
        formatted_result = {
            "success": True,
            "search_center": {"ra": ra, "dec": dec},
            "search_radius": radius,
            "total_objects": result.get("total_rows", 0),
            "objects": []
        }
        
        # 处理查询结果
        if result.get("rows"):
            columns = result.get("columns", [])
            column_names = [col.get("name", f"col_{i}") for i, col in enumerate(columns)]
            
            for row in result["rows"]:
                obj = {}
                for i, value in enumerate(row):
                    col_name = column_names[i] if i < len(column_names) else f"col_{i}"
                    obj[col_name] = value
                formatted_result["objects"].append(obj)
        
        # 坐标搜索完成
        return formatted_result
        
    except Exception as e:
        logger.error(f"Exception occurred during coordinate search: {str(e)}")
        logger.debug(f"Search parameters: ra={ra}, dec={dec}, radius={radius}")
        import traceback
        logger.debug(f"Error stack trace: {traceback.format_exc()}")
        return {
            "success": False,
            "error": "搜索执行异常",
            "details": str(e),
            "debug_info": {
                "ra": ra,
                "dec": dec,
                "radius": radius,
                "error_type": type(e).__name__,
                "query": query
            }
        }

if __name__ == "__main__":
    # 测试工具函数
    print("测试天体查询工具...")
    
    # 测试基础信息查询
    print("\n1. 测试基础信息查询 (M13):")
    result1 = get_object_by_identifier("M13")
    if result1["success"]:
        print(f"✓ 查询成功，找到 {result1['total_records']} 条记录")
        if result1["data"]:
            print("示例数据:")
            for key, value in list(result1["data"][0].items())[:5]:
                print(f"  {key}: {value}")
    else:
        print(f"✗ 查询失败: {result1['error']}")
    
    # 测试参考文献查询
    print("\n2. 测试参考文献查询 (M13):")
    result2 = get_bibliographic_data("M13")
    if result2["success"]:
        print(f"✓ 查询成功，找到 {result2['total_references']} 条参考文献")
        if result2["references"]:
            print("示例文献:")
            ref = result2["references"][0]
            for key, value in ref.items():
                print(f"  {key}: {value}")
    else:
        print(f"✗ 查询失败: {result2['error']}")
    
    # 测试坐标搜索
    print("\n3. 测试坐标搜索 (M13附近):")
    result3 = search_objects_by_coordinates(250.421, 36.460, 0.05)
    if result3["success"]:
        print(f"✓ 搜索成功，找到 {result3['total_objects']} 个天体")
        if result3["objects"]:
            print("示例天体:")
            obj = result3["objects"][0]
            for key, value in list(obj.items())[:4]:
                print(f"  {key}: {value}")
    else:
        print(f"✗ 搜索失败: {result3['error']}")
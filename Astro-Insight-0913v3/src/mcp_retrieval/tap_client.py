import httpx
import xmltodict
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simbad TAP服务端点
TAP_URL = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"

def run_adql(query: str) -> Dict[str, Any]:
    """
    执行ADQL查询并返回结果
    
    Args:
        query: ADQL查询语句
        
    Returns:
        包含查询结果的字典
    """
    try:
        # 准备请求参数
        payload = {
            "REQUEST": "doQuery",
            "LANG": "ADQL",
            "FORMAT": "csv",
            "MAXREC": "100",
            "QUERY": query,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Astrophysics-TAP-Client/1.0"
        }
        
        # 执行ADQL查询
        
        # 发送HTTP请求（带重试机制）
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(TAP_URL, data=payload, headers=headers)
                    response.raise_for_status()
                break
            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    logger.warning(f"Request timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                    continue
                else:
                    raise
            
        # TAP查询成功
        
        # 调试：打印响应内容的前1000个字符
        logger.info(f"Response content preview: {response.text[:1000]}")
        logger.info(f"Response Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        # 检查响应格式
        content_type = response.headers.get('content-type', '').lower()
        
        if 'text/csv' in content_type or response.text.strip().startswith('bibcode'):
            # CSV格式
            return _parse_csv_text(response.text)
        elif 'text/plain' in content_type:
            # 固定宽度文本格式
            return _parse_fixed_width_text(response.text)
        else:
            # VOTable XML格式
            data = xmltodict.parse(response.text)
            return _extract_table_data(data)
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP请求失败: {e.response.status_code} - {e.response.text}")
        return {"error": f"HTTP错误: {e.response.status_code}", "details": str(e)}
    except httpx.TimeoutException:
        logger.error("请求超时")
        return {"error": "请求超时", "details": "TAP服务响应超时"}
    except Exception as e:
        logger.error(f"查询执行失败: {str(e)}")
        return {"error": "查询执行失败", "details": str(e)}

def _parse_fixed_width_text(text: str) -> Dict[str, Any]:
    """
    解析固定宽度的文本格式响应
    
    Args:
        text: 固定宽度的文本响应
        
    Returns:
        包含行数据和列信息的字典
    """
    try:
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return {"rows": [], "columns": [], "raw": text}
        
        # 第一行是列标题
        header_line = lines[0]
        # 第二行是分隔线（包含|和-字符）
        separator_line = lines[1]
        
        # 解析列分隔符位置
        column_positions = []
        in_column = False
        start_pos = 0
        
        for i, char in enumerate(separator_line):
            if char == '|' and not in_column:
                column_positions.append(i)
                in_column = True
            elif char != '|' and char != '-' and in_column:
                in_column = False
        
        # 添加最后一个位置
        column_positions.append(len(separator_line))
        
        # 解析列名
        columns = []
        for i in range(len(column_positions) - 1):
            start = column_positions[i] + 1 if i > 0 else 0
            end = column_positions[i + 1]
            col_name = header_line[start:end].strip()
            columns.append({
                "name": col_name,
                "datatype": "char",
                "description": ""
            })
        
        # 解析数据行
        rows = []
        for line in lines[2:]:  # 跳过标题和分隔线
            if not line.strip():
                continue
                
            row = []
            for i in range(len(column_positions) - 1):
                start = column_positions[i] + 1 if i > 0 else 0
                end = column_positions[i + 1]
                cell_value = line[start:end].strip()
                
                # 移除引号
                if cell_value.startswith('"') and cell_value.endswith('"'):
                    cell_value = cell_value[1:-1]
                
                row.append(cell_value)
            
            if any(cell.strip() for cell in row):  # 只添加非空行
                rows.append(row)
        
        return {
            "rows": rows,
            "columns": columns,
            "raw": text
        }
        
    except Exception as e:
        logger.error(f"固定宽度文本解析失败: {e}")
        return {"error": "文本解析失败", "details": str(e)}

def _parse_csv_text(text: str) -> Dict[str, Any]:
    """
    解析CSV格式的响应
    
    Args:
        text: CSV格式的文本响应
        
    Returns:
        包含行数据和列信息的字典
    """
    try:
        import csv
        from io import StringIO
        
        # 使用StringIO和csv模块解析
        csv_reader = csv.reader(StringIO(text))
        rows = list(csv_reader)
        
        if not rows:
            return {"rows": [], "columns": [], "raw": text}
        
        # 第一行是列标题
        headers = rows[0]
        columns = []
        for header in headers:
            columns.append({
                "name": header.strip(),
                "datatype": "char",
                "description": ""
            })
        
        # 数据行（跳过标题行）
        data_rows = rows[1:] if len(rows) > 1 else []
        
        return {
            "rows": data_rows,
            "columns": columns,
            "raw": text
        }
        
    except Exception as e:
        logger.error(f"CSV解析失败: {e}")
        return {"error": "CSV解析失败", "details": str(e)}

def _extract_table_data(votable_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    从VOTable数据中提取表格数据
    
    Args:
        votable_data: 解析后的VOTable数据
        
    Returns:
        包含行数据和列信息的字典
    """
    try:
        # 检查是否有错误信息
        resource = votable_data.get("VOTABLE", {}).get("RESOURCE", {})
        
        # 检查查询状态
        if isinstance(resource, dict):
            info_list = resource.get("INFO", [])
            if not isinstance(info_list, list):
                info_list = [info_list]
                
            for info in info_list:
                if isinstance(info, dict) and info.get("@name") == "QUERY_STATUS":
                    if info.get("@value") == "ERROR":
                        error_msg = info.get("#text", "未知错误")
                        logger.error(f"TAP查询错误: {error_msg}")
                        return {"error": "TAP查询错误", "details": error_msg}
        
        # 提取表格数据
        table = resource.get("TABLE", {})
        if not table:
            logger.warning("响应中未找到TABLE元素")
            return {"rows": [], "columns": [], "raw": votable_data}
            
        # 提取列信息
        fields = table.get("FIELD", [])
        if not isinstance(fields, list):
            fields = [fields]
            
        columns = []
        for field in fields:
            if isinstance(field, dict):
                columns.append({
                    "name": field.get("@name", ""),
                    "datatype": field.get("@datatype", ""),
                    "description": field.get("@description", "")
                })
        
        # 提取行数据 - 支持BINARY和TABLEDATA格式
        data_element = table.get("DATA", {})
        
        # 检查是否是BINARY格式
        if "BINARY" in data_element:
            # 对于BINARY格式，我们需要解码base64数据
            binary_data = data_element.get("BINARY", {})
            stream_data = binary_data.get("STREAM", {})
            if isinstance(stream_data, dict) and stream_data.get("@encoding") == "base64":
                import base64
                encoded_data = stream_data.get("#text", "")
                try:
                    decoded_data = base64.b64decode(encoded_data)
                    # Simbad TAP的BINARY格式：固定长度字段
                    rows = []
                    offset = 0
                    row = []
                    
                    # 根据列定义解析数据
                    for col_idx, column in enumerate(columns):
                        if offset >= len(decoded_data):
                            break
                            
                        datatype = column.get("datatype", "char")
                        
                        if datatype in ["long"]:
                            # long类型：8字节
                            if offset + 8 <= len(decoded_data):
                                data_bytes = decoded_data[offset:offset+8]
                                value = int.from_bytes(data_bytes, byteorder='little', signed=True)
                                offset += 8
                            else:
                                value = 0
                        elif datatype in ["int"]:
                            # int类型：4字节
                            if offset + 4 <= len(decoded_data):
                                data_bytes = decoded_data[offset:offset+4]
                                value = int.from_bytes(data_bytes, byteorder='little', signed=True)
                                offset += 4
                            else:
                                value = 0
                        elif datatype in ["short"]:
                            # short类型：2字节
                            if offset + 2 <= len(decoded_data):
                                data_bytes = decoded_data[offset:offset+2]
                                value = int.from_bytes(data_bytes, byteorder='little', signed=True)
                                offset += 2
                            else:
                                value = 0
                        elif datatype in ["double"]:
                            # double类型：8字节
                            if offset + 8 <= len(decoded_data):
                                data_bytes = decoded_data[offset:offset+8]
                                import struct
                                value = struct.unpack('<d', data_bytes)[0]
                                offset += 8
                            else:
                                value = 0.0
                        elif datatype in ["float"]:
                            # float类型：4字节
                            if offset + 4 <= len(decoded_data):
                                data_bytes = decoded_data[offset:offset+4]
                                import struct
                                value = struct.unpack('<f', data_bytes)[0]
                                offset += 4
                            else:
                                value = 0.0
                        elif datatype in ["unicodeChar"]:
                            # Unicode字符串类型：需要根据长度前缀解析，每个字符2字节
                            if offset + 4 <= len(decoded_data):
                                # 读取长度前缀
                                length = int.from_bytes(decoded_data[offset:offset+4], byteorder='little')
                                offset += 4
                                
                                if length > 0 and offset + length <= len(decoded_data):
                                    data_bytes = decoded_data[offset:offset+length]
                                    # UTF-16解码
                                    value = data_bytes.decode('utf-16be', errors='ignore').strip()
                                    offset += length
                                else:
                                    value = ""
                            else:
                                value = ""
                        else:
                            # 普通字符串类型：需要根据长度前缀解析
                            if offset + 4 <= len(decoded_data):
                                # 读取长度前缀
                                length = int.from_bytes(decoded_data[offset:offset+4], byteorder='little')
                                offset += 4
                                
                                if length > 0 and offset + length <= len(decoded_data):
                                    data_bytes = decoded_data[offset:offset+length]
                                    value = data_bytes.decode('utf-8', errors='ignore').strip()
                                    offset += length
                                else:
                                    value = ""
                            else:
                                value = ""
                        
                        row.append(value)
                    
                    if row:
                        rows.append(row)
                        
                except Exception as e:
                    logger.error(f"BINARY数据解码失败: {e}")
                    logger.debug(f"解码数据: {decoded_data}")
                    rows = []
            else:
                rows = []
        else:
            # 处理TABLEDATA格式
            tabledata = data_element.get("TABLEDATA", {})
            rows_data = tabledata.get("TR", [])
            
            if not isinstance(rows_data, list):
                rows_data = [rows_data] if rows_data else []
                
            rows = []
            for tr in rows_data:
                if isinstance(tr, dict):
                    td_data = tr.get("TD", [])
                    if not isinstance(td_data, list):
                        td_data = [td_data] if td_data else []
                        
                    # 处理每个单元格的数据
                    row = []
                    for td in td_data:
                        if isinstance(td, dict):
                            # 如果TD是字典，提取文本内容
                            cell_value = td.get("#text", td.get("@value", ""))
                        else:
                            # 如果TD直接是值
                            cell_value = td if td is not None else ""
                        row.append(cell_value)
                    rows.append(row)
        
        # 成功提取数据
        
        # 调试信息：打印列定义
        logger.info("列定义:")
        for i, col in enumerate(columns):
            logger.info(f"  列 {i}: {col}")
        
        return {
            "rows": rows,
            "columns": columns,
            "total_rows": len(rows)
        }
        
    except Exception as e:
        logger.error(f"数据提取失败: {str(e)}")
        return {
            "error": "数据提取失败",
            "details": str(e),
            "raw": votable_data
        }

def test_connection() -> bool:
    """
    测试TAP服务连接
    
    Returns:
        连接是否成功
    """
    test_query = "SELECT TOP 1 main_id FROM basic"
    result = run_adql(test_query)
    
    if "error" in result:
        logger.error(f"连接测试失败: {result['error']}")
        return False
    else:
        # TAP服务连接测试成功
        return True

if __name__ == "__main__":
    # 测试连接
    print("测试TAP服务连接...")
    if test_connection():
        print("✓ TAP服务连接正常")
        
        # 测试查询
        print("\n测试查询M13...")
        test_query = """
        SELECT TOP 5 basic.OID, RA, DEC, main_id
        FROM basic JOIN ident ON oidref = oid
        WHERE id = 'M13'
        """
        result = run_adql(test_query)
        
        if "error" in result:
            print(f"✗ 查询失败: {result['error']}")
        else:
            print(f"✓ 查询成功，返回 {result['total_rows']} 行数据")
            if result['rows']:
                print("示例数据:")
                for i, row in enumerate(result['rows'][:3]):
                    print(f"  行 {i+1}: {row}")
    else:
        print("✗ TAP服务连接失败")
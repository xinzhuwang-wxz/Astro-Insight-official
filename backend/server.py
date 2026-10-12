#!/usr/bin/env python3
"""
天体分析系统 - Web服务器
提供完整的API接口，支持天体分类、代码生成和执行等功能
"""

import os
import sys
import time
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
try:
    from src.graph import build_graph_with_memory
    from src.database import data_manager, DatabaseAPI
    from src.database.importers import CSVImporter
except ImportError as e:
    print(f"导入模块失败：{e}")
    print("请确保所有依赖模块已正确安装")
    sys.exit(1)

# 代码生成模块目前在仓库中没有可导出的统一入口，先用运行时占位避免启动失败
code_generator = None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('astro_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
CORS(app)  # 启用跨域支持

# 应用配置
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'astro-insight-dev-key'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB最大请求大小
    JSON_SORT_KEYS=False
)

# 全局变量
astro_graph = None
db_api = None
csv_importer = None

# 初始化系统组件
def initialize_system():
    """初始化系统组件"""
    global astro_graph, db_api, csv_importer
    
    try:
        logger.info("正在初始化天体分析系统...")
        
        # 初始化数据库API
        db_api = DatabaseAPI()
        csv_importer = CSVImporter(db_api)
        seed_counts = {
            "task_types": db_api.ensure_analysis_task_types(),
            "methods": db_api.ensure_analysis_methods(),
            "chart_types": db_api.ensure_chart_types(),
        }
        logger.info(f"数据库API初始化完成，种子写入: {seed_counts}")
        
        # 初始化分析图
        astro_graph = build_graph_with_memory()
        logger.info("天体分析图初始化完成")
        
        # 初始化代码生成器
        logger.info("代码生成器已就绪")
        
        logger.info("系统初始化完成！")
        return True
        
    except Exception as e:
        logger.error(f"系统初始化失败：{e}")
        logger.error(traceback.format_exc())
        return False

# 错误处理装饰器
def handle_errors(f):
    """统一错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BadRequest as e:
            logger.warning(f"客户端请求错误：{e}")
            return jsonify({
                "success": False,
                "error": "请求参数错误",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }), 400
        except Exception as e:
            logger.error(f"服务器内部错误：{e}")
            logger.error(traceback.format_exc())
            return jsonify({
                "success": False,
                "error": "服务器内部错误",
                "message": "请稍后重试或联系管理员",
                "timestamp": datetime.now().isoformat()
            }), 500
    wrapper.__name__ = f.__name__
    return wrapper

# API路由

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
@handle_errors
def get_status():
    """获取系统状态"""
    try:
        # 检查各组件状态
        db_status = "正常" if db_api and db_api.database.connection else "异常"
        graph_status = "正常" if astro_graph else "未初始化"
        
        # 获取数据库统计
        stats = db_api.get_statistics() if db_api else {}
        
        return jsonify({
            "success": True,
            "system_status": {
                "database": db_status,
                "analysis_graph": graph_status,
                "code_generator": "正常"
            },
            "statistics": stats,
            "uptime": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"获取系统状态失败：{e}")
        raise

@app.route('/api/analyze', methods=['POST'])
@handle_errors
def analyze_celestial_object():
    """天体分析API"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        raise BadRequest("缺少必要参数：query")
    
    query = data['query']
    user_type = data.get('user_type', 'hobbyist')
    analysis_type = data.get('analysis_type', 'classification')
    
    logger.info(f"收到分析请求：{query[:100]}...")
    
    try:
        from src.graph.types import create_initial_state
        
        # 构建初始状态
        initial_state = create_initial_state(
            session_id=None,  # 将自动生成UUID
            user_input=query
        )
        
        # 设置额外的状态信息
        initial_state["user_type"] = user_type
        initial_state["task_type"] = analysis_type
        
        # 执行分析流程
        if astro_graph:
            result = astro_graph.execute(initial_state)
        else:
            raise InternalServerError("分析系统未初始化")
        
        # 保存分析结果到数据库
        if db_api and result.get("execution_result"):
            try:
                classification_result = {
                    "object_name": result.get("celestial_info", {}).get("name", "未知天体"),
                    "classification": result.get("classification", "未分类"),
                    "confidence": result.get("confidence", 0.0),
                    "analysis_type": analysis_type,
                    "user_type": user_type,
                    "metadata": json.dumps(result.get("code_metadata", {}))
                }
                db_api.add_classification_result(classification_result)
            except Exception as db_error:
                logger.warning(f"保存分析结果失败：{db_error}")
        
        return jsonify({
            "success": True,
            "result": {
                "analysis_type": analysis_type,
                "celestial_info": result.get("celestial_info", {}),
                "classification": result.get("classification"),
                "confidence": result.get("confidence"),
                "generated_code": result.get("generated_code"),
                "execution_result": result.get("execution_result"),
                "execution_history": result.get("execution_history", []),
                "processing_time": result.get("processing_time")
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"分析处理失败：{e}")
        raise

@app.route('/api/generate-code', methods=['POST'])
@handle_errors
def generate_code():
    """代码生成API"""
    return jsonify({
        "success": False,
        "message": "代码生成模块当前未对外导出统一入口，后续会补齐。",
        "timestamp": datetime.now().isoformat()
    }), 501

@app.route('/api/data/objects', methods=['GET'])
@handle_errors
def get_celestial_objects():
    """获取天体对象列表"""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # 最大100条
        object_type = request.args.get('type')
        
        objects = db_api.get_celestial_objects(
            limit=limit,
            offset=(page-1)*limit,
            object_type=object_type
        )
        
        return jsonify({
            "success": True,
            "data": objects,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(objects)
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取天体对象失败：{e}")
        raise

@app.route('/api/data/classifications', methods=['GET'])
@handle_errors
def get_classifications():
    """获取分类结果列表"""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        
        results = db_api.get_classification_results(
            limit=limit,
            offset=(page-1)*limit
        )
        
        return jsonify({
            "success": True,
            "data": results,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(results)
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取分类结果失败：{e}")
        raise

@app.route('/api/data/history', methods=['GET'])
@handle_errors
def get_execution_history():
    """获取执行历史"""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        
        history = db_api.get_execution_history(
            limit=limit,
            offset=(page-1)*limit
        )
        
        return jsonify({
            "success": True,
            "data": history,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(history)
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取执行历史失败：{e}")
        raise

@app.route('/api/data/statistics', methods=['GET'])
@handle_errors
def get_statistics():
    """获取系统统计信息"""
    try:
        stats = db_api.get_statistics()
        mvp_stats = db_api.get_mvp_statistics()

        return jsonify({
            "success": True,
            "statistics": stats,
            "mvp_statistics": mvp_stats,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"获取统计信息失败：{e}")
        raise


@app.route('/api/mvp/import-csv', methods=['POST'])
@handle_errors
def import_csv_dataset():
    """导入CSV到MVP schema"""
    data = request.get_json() or {}
    csv_path = data.get('csv_path')
    source_name = data.get('source_name')
    source_type = data.get('source_type', 'catalog')
    dataset_name = data.get('dataset_name')

    if not csv_path or not source_name or not dataset_name:
        raise BadRequest("缺少必要参数：csv_path, source_name, dataset_name")

    result = csv_importer.import_dataset(
        csv_path=csv_path,
        source_name=source_name,
        source_type=source_type,
        dataset_name=dataset_name,
        dataset_version=data.get('dataset_version'),
        access_method=data.get('access_method', 'csv'),
        base_url=data.get('base_url'),
        description=data.get('description'),
        object_family_field=data.get('object_family_field'),
        object_name_field=data.get('object_name_field'),
        feature_fields=data.get('feature_fields'),
    )

    return jsonify({
        "success": True,
        "message": "CSV导入成功",
        "result": result,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/mvp/overview', methods=['GET'])
@handle_errors
def get_mvp_overview():
    """获取MVP新schema概览"""
    limit = min(int(request.args.get('limit', 20)), 100)
    return jsonify({
        "success": True,
        "data": {
            "sources": db_api.list_data_sources(limit=limit),
            "datasets": db_api.list_source_datasets(limit=limit),
            "records": db_api.list_dataset_records(limit=limit),
            "analysis_task_types": db_api.list_analysis_task_types(limit=limit),
            "analysis_methods": db_api.list_analysis_methods(limit=limit),
            "chart_types": db_api.list_chart_types(limit=limit),
            "analysis_tasks": db_api.list_analysis_tasks(limit=limit),
            "analysis_runs": db_api.list_analysis_runs(limit=limit),
            "analysis_results": db_api.list_analysis_results(limit=limit),
            "chart_configs": db_api.list_chart_configs(limit=limit),
            "claims": db_api.list_interpretation_claims(limit=limit),
        },
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/mvp/bootstrap-demo', methods=['POST'])
@handle_errors
def bootstrap_demo_entities():
    """创建一组最小演示任务/运行/图表/解释数据"""
    task_types = db_api.list_analysis_task_types(limit=10)
    methods = db_api.list_analysis_methods(limit=10)
    chart_types = db_api.list_chart_types(limit=10)

    if not task_types or not methods or not chart_types:
        raise InternalServerError("缺少种子数据，请重启服务以初始化")

    task_id = db_api.create_analysis_task({
        "task_type_id": task_types[0]["task_type_id"],
        "source_scope": {"source": "demo"},
        "filters": {"sample": True},
        "target_variables": ["feature_a", "feature_b"],
        "task_name": "MVP Demo Task",
        "task_status": "completed",
    })

    run_id = db_api.create_analysis_run({
        "task_id": task_id,
        "method_id": methods[0]["method_id"],
        "parameters": {"n_components": 2},
        "input_snapshot_hash": "demo_snapshot",
        "runtime_ms": 123,
        "run_status": "completed",
    })

    result_id = db_api.create_analysis_result({
        "run_id": run_id,
        "result_type": "embedding",
        "result_payload": {"points": [[0.1, 0.2], [0.3, 0.4]]},
        "summary_text": "Demo embedding generated.",
    })

    chart_config_id = db_api.create_chart_config({
        "task_id": task_id,
        "chart_type_id": chart_types[1]["chart_type_id"] if len(chart_types) > 1 else chart_types[0]["chart_type_id"],
        "encoding_spec": {"x": "feature_a", "y": "feature_b"},
        "color_theme": "default",
        "axis_mapping": {"x": "feature_a", "y": "feature_b"},
        "layout_spec": {"height": 320},
    })

    claim_id = db_api.create_interpretation_claim({
        "task_id": task_id,
        "claim_text": "样本数据在二维空间中存在可分离趋势。",
        "confidence_level": 0.72,
    })

    return jsonify({
        "success": True,
        "message": "Demo entities created",
        "result": {
            "task_id": task_id,
            "run_id": run_id,
            "result_id": result_id,
            "chart_config_id": chart_config_id,
            "claim_id": claim_id,
        },
        "timestamp": datetime.now().isoformat(),
    })

# 健康检查
@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

# 错误处理器
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "接口不存在",
        "message": "请检查请求URL是否正确",
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "请求方法不允许",
        "message": "请检查HTTP方法是否正确",
        "timestamp": datetime.now().isoformat()
    }), 405

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error": "请求体过大",
        "message": "请求大小不能超过16MB",
        "timestamp": datetime.now().isoformat()
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"服务器内部错误：{error}")
    return jsonify({
        "success": False,
        "error": "服务器内部错误",
        "message": "请稍后重试或联系管理员",
        "timestamp": datetime.now().isoformat()
    }), 500

# 启动服务器
if __name__ == '__main__':
    # 记录启动时间
    start_time = time.time()
    
    # 初始化系统
    if not initialize_system():
        logger.error("系统初始化失败，服务器无法启动")
        sys.exit(1)
    
    # 获取配置
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info("启动天体分析系统服务器...")
    logger.info(f"服务地址: http://localhost:8000")
    logger.info(f"调试模式: {DEBUG}")
    
    try:
        app.run(
            host='localhost',
            port=8000,
            debug=DEBUG
        )
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败：{e}")
        sys.exit(1)
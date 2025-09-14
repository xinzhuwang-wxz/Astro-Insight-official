# 🌌 Astro-Insight API服务

专注于核心功能的天文科研助手API，便于学习和前端对接。

## ✨ 特性

- 🚀 **简单易用**: 专注于核心查询功能
- 🌐 **标准输出**: 统一的JSON响应格式
- 🔗 **前端友好**: 支持CORS，便于前端对接
- 📚 **学习导向**: 清晰的代码示例和文档
- 🧪 **测试支持**: 内置测试脚本

## 🚀 快速开始

### 1. 安装依赖

```bash
# 确保已安装项目依赖
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 使用启动脚

# 或者指定端口
python api_service/start_api.py --port 8001

# 开发模式（自动重载）
python api_service/start_api.py --reload --log-level DEBUG
```

### 3. 验证服务

```bash
# 检查服务状态
curl http://localhost:8000/status

# 查看API文档
# 浏览器访问: http://localhost:8000/docs
```

## 📡 API接口

### 基础信息

- **基础URL**: `http://localhost:8000`
- **数据格式**: JSON
- **支持CORS**: 是

### 端点列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/status` | GET | 系统状态 |
| `/health` | GET | 健康检查 |
| `/query` | POST | 天文查询 |
| `/docs` | GET | API文档 |

### 查询接口

**POST /query**

请求体：
```json
{
  "query": "什么是黑洞？",
  "user_type": "amateur"
}
```

响应：
```json
{
  "success": true,
  "message": "查询处理成功",
  "data": {
    "query": "什么是黑洞？",
    "session_id": "api_20240101_120000_123456",
    "user_type": "amateur",
    "task_type": "qa",
    "current_step": "qa_completed",
    "is_complete": true,
    "answer": "黑洞是宇宙中一种极其致密的天体...",
    "generated_code": null,
    "execution_history": [...],
    "error_info": null
  },
  "timestamp": "2024-01-01T12:00:00.000Z",
  "execution_time": 2.34
}
```

## 💻 前端对接示例

### JavaScript

```javascript
// 基础查询函数
async function queryAstro(query, userType = null) {
    try {
        const response = await fetch('http://localhost:8000/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                user_type: userType
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('查询失败:', error);
        throw error;
    }
}

// 使用示例
queryAstro('什么是黑洞？', 'amateur')
    .then(result => {
        if (result.success) {
            console.log('回答:', result.data.answer);
            console.log('执行时间:', result.execution_time + '秒');
        }
    });
```

### Python

```python
import requests

def query_astro(query, user_type=None):
    """查询天文问题"""
    url = "http://localhost:8000/query"
    payload = {
        "query": query,
        "user_type": user_type
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

# 使用示例
result = query_astro("什么是黑洞？", "amateur")
if result and result['success']:
    print(f"回答: {result['data']['answer']}")
    print(f"执行时间: {result['execution_time']:.2f}秒")
```

### React组件

```jsx
import React, { useState } from 'react';

function AstroQuery() {
    const [query, setQuery] = useState('');
    const [userType, setUserType] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const response = await fetch('http://localhost:8000/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, user_type: userType })
            });
            
            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error('查询失败:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <textarea 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="请输入天文问题"
                />
                <select 
                    value={userType}
                    onChange={(e) => setUserType(e.target.value)}
                >
                    <option value="">自动识别</option>
                    <option value="amateur">业余爱好者</option>
                    <option value="professional">专业研究人员</option>
                </select>
                <button type="submit" disabled={loading}>
                    {loading ? '查询中...' : '提交查询'}
                </button>
            </form>
            
            {result && (
                <div>
                    <h3>查询结果</h3>
                    <p>{result.data.answer}</p>
                    <p>执行时间: {result.execution_time}秒</p>
                </div>
            )}
        </div>
    );
}
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python api_service/test_api.py

# 运行特定测试
python api_service/test_api.py --test health
python api_service/test_api.py --test status
python api_service/test_api.py --test query
python api_service/test_api.py --test multiple
```

### 测试覆盖

- ✅ 健康检查测试
- ✅ 系统状态测试
- ✅ 单次查询测试
- ✅ 批量查询测试

## 🌐 前端演示

打开 `frontend_examples.html` 文件，在浏览器中查看完整的前端对接示例：

```bash
# 在浏览器中打开
open api_service/frontend_examples.html
```

该文件包含：
- 在线演示界面
- 代码示例
- API文档
- 实时测试功能

## ⚙️ 配置

### 环境变量

```bash
# 服务器配置
export API_HOST=0.0.0.0
export API_PORT=8000
export API_DEBUG=False
```

### 启动参数

```bash
python api_service/start_api.py \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level INFO
```

## 📁 文件结构

```
api_service/
├── main.py                 # 主应用
├── start_api.py            # 启动脚本
├── test_api.py             # 测试脚本
├── frontend_examples.html  # 前端对接示例
├── README.md               # 说明文档
└── api_service.log         # 日志文件
```

## 🔧 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口使用情况
   lsof -i :8000
   
# 使用其他端口
python api_service/start_api.py --port 8001
   ```

2. **CORS错误**
   - 确保API服务正在运行
   - 检查请求URL是否正确
   - 确认Content-Type设置为application/json

3. **查询失败**
   - 检查系统状态：`curl http://localhost:8000/status`
   - 查看日志文件：`tail -f api_service.log`
   - 确认LLM服务正常运行

### 调试技巧

```bash
# 查看实时日志
tail -f api_service.log

# 检查API响应
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "测试查询"}'

# 检查系统状态
curl http://localhost:8000/status
```

## 📚 学习资源

- **API文档**: http://localhost:8000/docs
- **可读文档**: http://localhost:8000/redoc
- **前端示例**: `frontend_examples.html`
- **测试脚本**: `test_simple.py`

## 🎯 下一步

1. 熟悉API接口和响应格式
2. 尝试不同的查询类型
3. 集成到你的前端项目中
4. 根据需要扩展功能

## 💡 提示

- 建议先运行测试脚本确保服务正常
- 使用前端示例页面进行交互式测试
- 查看API文档了解完整的接口规范
- 根据需要调整用户类型和查询内容

---

**开始你的天文科研助手API之旅吧！** 🚀

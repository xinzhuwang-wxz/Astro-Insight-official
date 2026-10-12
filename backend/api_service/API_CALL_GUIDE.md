# API服务调用完整指南

## 概述

这个文档将详细解释API服务的完整调用流程，从前端输入到后端处理，再到前端显示的整个过程。适合初学者理解整个系统的数据流向。

## 系统架构图

```
前端 (HTML/JavaScript) 
    ↓ HTTP请求
API服务 (FastAPI)
    ↓ 调用
LangGraph工作流
    ↓ 处理
LLM + 各种工具
    ↓ 返回结果
API服务 (FastAPI)
    ↓ HTTP响应
前端 (HTML/JavaScript)
```

## 1. 前端输入处理

### 1.1 前端输入位置
**文件**: `api_service/frontend_examples.html`

**输入表单**:
```html
<!-- 第47-60行 -->
<form id="queryForm">
    <div class="form-group">
        <label for="queryInput">请输入您的天文问题：</label>
        <textarea id="queryInput" name="query" placeholder="例如：什么是黑洞？" required></textarea>
    </div>
    <div class="form-group">
        <label for="userType">用户类型：</label>
        <select id="userType" name="user_type">
            <option value="amateur">业余爱好者</option>
            <option value="professional">专业研究人员</option>
        </select>
    </div>
    <button type="submit">提交查询</button>
</form>
```

### 1.2 前端JavaScript处理
**文件**: `api_service/frontend_examples.html`

**JavaScript函数** (第400-450行):
```javascript
// 处理表单提交
document.getElementById('queryForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const query = document.getElementById('queryInput').value;
    const userType = document.getElementById('userType').value;
    
    // 显示加载状态
    showLoading();
    
    try {
        // 发送HTTP请求到后端API
        const response = await fetch('/query', {
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
        displayResult(data);
    } catch (error) {
        displayError(error);
    }
});
```

## 2. 后端API处理

### 2.1 API端点定义
**文件**: `api_service/main.py`

**查询端点** (第80-120行):
```python
@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """处理查询请求"""
    start_time = time.time()
    session_id = f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    try:
        logger.info(f"处理查询: {request.query[:50]}...")
        
        # 调用LangGraph工作流
        result_state = workflow.execute_workflow(
            session_id=session_id,
            user_input=request.query,
            user_context={"user_type": request.user_type}
        )
        
        # 构建响应
        response_data = {
            "query": request.query,
            "session_id": session_id,
            "user_type": result_state.get("user_type", "unknown"),
            "task_type": result_state.get("task_type", "unknown"),
            "current_step": result_state.get("current_step", "unknown"),
            "is_complete": result_state.get("is_complete", False),
            "answer": result_state.get("final_answer", "未找到答案"),
            "generated_code": result_state.get("generated_code"),
            "execution_history": result_state.get("execution_history", []),
            "error_info": result_state.get("error_info")
        }
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            success=True,
            message="查询处理成功",
            data=response_data,
            timestamp=datetime.now().isoformat(),
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"查询处理失败: {str(e)}")
        return QueryResponse(
            success=False,
            message=f"查询处理失败: {str(e)}",
            data={"error": str(e)},
            timestamp=datetime.now().isoformat(),
            execution_time=time.time() - start_time
        )
```

### 2.2 数据模型定义
**文件**: `api_service/main.py`

**请求模型** (第30-40行):
```python
class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str = Field(..., description="用户查询内容")
    user_type: str = Field(..., description="用户类型")
```

**响应模型** (第42-55行):
```python
class QueryResponse(BaseModel):
    """查询响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Dict[str, Any] = Field(..., description="响应数据")
    timestamp: str = Field(..., description="响应时间戳")
    execution_time: float = Field(..., description="执行时间（秒）")
```

## 3. LangGraph工作流处理

### 3.1 工作流入口
**文件**: `src/workflow.py`

**工作流执行** (第101-153行):
```python
def execute_workflow(
    self,
    session_id: str,
    user_input: str,
    user_context: Optional[Dict[str, Any]] = None,
) -> AstroAgentState:
    """执行完整的工作流程"""
    start_time = time.time()
    logger.info(f"开始执行工作流 - 会话: {session_id}")
    
    try:
        # 创建或获取会话
        if session_id not in self.sessions:
            initial_state = self.create_session(
                session_id, user_input, user_context
            )
        else:
            # 更新现有会话
            session = self.sessions[session_id]
            initial_state = session["current_state"].copy()
            initial_state["user_input"] = user_input
            if user_context:
                for key, value in user_context.items():
                    if key != "session_id":
                        initial_state[key] = value
                session["last_updated"] = datetime.now()
        
        # 执行图
        logger.info(f"执行图处理 - 输入: {user_input[:50]}...")
        final_state = self.graph.invoke(initial_state)
        
        # 更新会话状态
        self.sessions[session_id]["current_state"] = final_state
        
        # 记录执行时间
        execution_time = time.time() - start_time
        logger.info(f"工作流执行完成 - 耗时: {execution_time:.2f}秒")
        
        # 记录执行结果
        self._log_execution_result(session_id, final_state, execution_time)
        
        return final_state
        
    except Exception as e:
        logger.error(f"工作流执行失败 - 会话: {session_id}, 错误: {str(e)}")
        # 记录错误信息到状态中
        if session_id in self.sessions:
            error_state = self.sessions[session_id]["current_state"].copy()
            error_state["error_info"] = {
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
            }
            self.sessions[session_id]["current_state"] = error_state
            return error_state
        raise
```

### 3.2 节点处理流程
**文件**: `src/graph/nodes.py`

**身份检查节点** (第320-380行):
```python
@track_node_execution("identity_check")
def identity_check_command_node(state: AstroAgentState) -> Command[AstroAgentState]:
    """身份检查节点 - 判断用户是业余爱好者还是专业研究人员"""
    try:
        user_input = state["user_input"]
        
        # 获取LLM实例
        llm = get_llm_by_type("basic")
        
        if llm:
            # 构建身份识别提示词
            identity_prompt = f"""请分析以下用户查询，判断用户是业余爱好者还是专业研究人员：

用户查询: {user_input}

判断标准:
- 业余爱好者 (amateur): 使用简单语言，问基础概念，如"什么是"、"为什么"、"如何理解"
- 专业研究人员 (professional): 使用专业术语，问具体数据、分析、研究相关问题

请仔细分析用户的语言风格、问题深度和专业需求，然后只返回：amateur 或 professional"""
            
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=identity_prompt)]
            response = llm.invoke(messages)  # 按prompt要求，只返回amateur 或 professional
            user_type = response.content.strip().lower()
            
            # 验证响应
            if user_type not in ["amateur", "professional"]:
                # 如果LLM返回的不是预期格式，尝试从文本中提取
                if "professional" in user_type or "专业" in user_type:
                    user_type = "professional"
                elif "amateur" in user_type or "爱好者" in user_type or "业余" in user_type:
                    user_type = "amateur"
                else:
                    user_type = "amateur"  # 默认为爱好者
        else:
            # 如果LLM不可用，报错而不是使用关键词判断
            raise Exception("LLM服务不可用，无法进行身份识别")
        
        # 更新状态 - 只更新必要的字段，避免字段冲突
        updated_state = {
            "user_type": user_type,
            "current_step": "identity_checked",
            "identity_completed": True
        }
        
        # 使用Command语法直接路由到下一个节点
        if user_type == "amateur":
            # 业余用户需要先进行QA问答
            return Command(
                update=updated_state,
                goto="qa_agent"
            )
        elif user_type == "professional":
            # 专业用户直接进入任务选择
            return Command(
                update=updated_state,
                goto="task_selector"
            )
        else:
            # 异常情况，默认为业余用户，进入QA问答
            updated_state["user_type"] = "amateur"
            return Command(
                update=updated_state,
                goto="qa_agent"
            )
            
    except Exception as e:
        logger.error(f"身份检查失败: {str(e)}")
        # 错误时默认为业余用户
        return Command(
            update={
                "user_type": "amateur",
                "current_step": "identity_checked",
                "identity_completed": True,
                "error_info": {"error": str(e)}
            },
            goto="qa_agent"
        )
```

## 4. 后端输出处理

### 4.1 API响应构建
**文件**: `api_service/main.py`

**响应数据构建** (第90-110行):
```python
# 构建响应
response_data = {
    "query": request.query,                    # 原始查询
    "session_id": session_id,                  # 会话ID
    "user_type": result_state.get("user_type", "unknown"),  # 识别的用户类型
    "task_type": result_state.get("task_type", "unknown"),  # 任务类型
    "current_step": result_state.get("current_step", "unknown"),  # 当前步骤
    "is_complete": result_state.get("is_complete", False),  # 是否完成
    "answer": result_state.get("final_answer", "未找到答案"),  # 最终答案
    "generated_code": result_state.get("generated_code"),  # 生成的代码
    "execution_history": result_state.get("execution_history", []),  # 执行历史
    "error_info": result_state.get("error_info")  # 错误信息
}

execution_time = time.time() - start_time

return QueryResponse(
    success=True,
    message="查询处理成功",
    data=response_data,
    timestamp=datetime.now().isoformat(),
    execution_time=execution_time
)
```

### 4.2 Token使用统计收集
**文件**: `api_service/main.py`

**注意**: 已移除 token_usage 相关功能，简化了响应格式。

## 5. 前端输出显示

### 5.1 结果显示函数
**文件**: `api_service/frontend_examples.html`

**结果显示** (第450-500行):
```javascript
function displayResult(data) {
    const resultDiv = document.getElementById('queryResult');
    const loadingDiv = document.getElementById('loading');
    
    // 隐藏加载状态
    loadingDiv.style.display = 'none';
    resultDiv.style.display = 'block';
    
    if (data.success) {
        resultDiv.className = 'result success';
        resultDiv.innerHTML = `
            <strong>✅ 查询成功</strong><br>
            <strong>查询内容:</strong> ${data.data.query}<br>
            <strong>用户类型:</strong> ${data.data.user_type || '自动识别'}<br>
            <strong>任务类型:</strong> ${data.data.task_type || 'N/A'}<br>
            <strong>是否完成:</strong> ${data.data.is_complete ? '是' : '否'}<br>
            <strong>执行时间:</strong> ${data.execution_time.toFixed(2)}秒<br>
            <strong>回答:</strong><br>
            ${data.data.answer}
        `;
        
        // 显示完整的API响应格式
        showResponseFormat(data);
    } else {
        resultDiv.className = 'result error';
        resultDiv.innerHTML = `
            <strong>❌ 查询失败</strong><br>
            <strong>错误信息:</strong> ${data.message}<br>
            <strong>详细信息:</strong> ${JSON.stringify(data.data, null, 2)}
        `;
    }
}
```

### 5.2 完整API响应显示
**文件**: `api_service/frontend_examples.html`

**响应格式显示** (第500-550行):
```javascript
function showResponseFormat(data) {
    const responseDiv = document.getElementById('responseFormat');
    const jsonDiv = document.getElementById('responseJson');
    
    // 格式化JSON显示
    const formattedJson = JSON.stringify(data, null, 2);
    jsonDiv.innerHTML = `<pre><code>${formattedJson}</code></pre>`;
    
    responseDiv.style.display = 'block';
}
```

## 6. 完整数据流向总结

### 6.1 输入流向
```
用户在前端输入
    ↓
HTML表单 (queryInput, userType)
    ↓
JavaScript事件处理 (submitQuery函数)
    ↓
HTTP POST请求到 /query
    ↓
FastAPI端点 (query_endpoint函数)
    ↓
QueryRequest模型验证
    ↓
LangGraph工作流 (execute_workflow)
    ↓
各个节点处理 (identity_check, task_selector, qa_agent等)
```

### 6.2 输出流向
```
LangGraph工作流返回结果
    ↓
QueryResponse模型构建
    ↓
HTTP JSON响应
    ↓
JavaScript fetch接收
    ↓
displayResult函数处理
    ↓
HTML DOM更新显示
    ↓
showResponseFormat显示完整响应
```

## 7. 关键文件位置总结

| 功能 | 文件位置 | 关键函数/代码段 |
|------|----------|----------------|
| 前端输入 | `api_service/frontend_examples.html` | 第47-60行 (HTML表单) |
| 前端处理 | `api_service/frontend_examples.html` | 第400-450行 (JavaScript) |
| API端点 | `api_service/main.py` | 第80-120行 (query_endpoint) |
| 数据模型 | `api_service/main.py` | 第30-55行 (QueryRequest/QueryResponse) |
| 工作流入口 | `src/workflow.py` | 第101-153行 (execute_workflow) |
| 节点处理 | `src/graph/nodes.py` | 各节点函数 |
| 前端显示 | `api_service/frontend_examples.html` | 第450-550行 (displayResult) |

## 8. 测试方法

### 8.1 启动API服务
```bash
cd /Users/physicsboy/Desktop/Hackathon/Astro_Insight
python api_service/start_api.py --port 8000
```

### 8.2 测试API
```bash
# 使用curl测试
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是行星？", "user_type": "amateur"}'

# 使用前端页面测试
# 打开浏览器访问: http://localhost:8000/static/frontend_examples.html
```

### 8.3 查看API文档
```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc
```

这个文档完整地展示了从前端输入到后端处理，再到前端显示的整个数据流向，帮助初学者理解整个系统的运作机制。

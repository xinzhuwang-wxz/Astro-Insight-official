# Astro-Insight 项目架构流程图

## 🌌 核心系统架构

```mermaid
graph TB
    %% 用户交互层
    subgraph "用户交互层"
        UI[Web界面<br/>HTML/CSS/JS]
        API[REST API<br/>FastAPI]
    end
    
    %% 智能体层
    subgraph "核心智能体层"
        direction TB
        
        subgraph "主要智能体"
            IDENTITY[身份识别智能体<br/>Identity Check Agent]
            PLANNER[规划智能体<br/>Planner Agent]
            CODER[代码生成智能体<br/>Code Generator Agent]
            EXPLAINER[解释智能体<br/>Explainer Agent]
            QA[问答智能体<br/>QA Agent]
        end
        
        subgraph "支持智能体"
            TASK_SELECTOR[任务选择器<br/>Task Selector]
            ERROR_RECOVERY[错误恢复<br/>Error Recovery]
            REVIEW_LOOP[审查循环<br/>Review Loop]
        end
    end
    
    %% MCP服务层
    subgraph "MCP服务层"
        direction TB
        
        subgraph "数据服务"
            MCP_ML[机器学习MCP<br/>Model Training & Analysis]
            MCP_RETRIEVAL[数据检索MCP<br/>TAP Query Service]
        end
        
        subgraph "外部API"
            TAVILY[Tavily搜索API<br/>文献检索]
            SIMBAD[Simbad TAP<br/>天体数据查询]
        end
    end
    
    %% 数据处理层
    subgraph "数据处理层"
        direction TB
        
        subgraph "数据集管理"
            DATASET_MGR[数据集管理器<br/>Dataset Manager]
            DATASET_SELECTOR[数据集选择器<br/>Dataset Selector]
            DATA_PREPROC[数据预处理<br/>Data Preprocessing]
        end
        
        subgraph "存储系统"
            LOCAL_DB[本地数据库<br/>SQLite]
            QUERY_HISTORY[查询历史<br/>Query History]
            DIALOGUE_STORAGE[对话存储<br/>Dialogue Storage]
        end
    end
    
    %% LLM层
    subgraph "LLM服务层"
        direction TB
        
        subgraph "LLM类型"
            BASIC_LLM[基础LLM<br/>Basic LLM]
            CODE_LLM[代码LLM<br/>Code LLM]
            VISION_LLM[视觉LLM<br/>Vision LLM]
            REASONING_LLM[推理LLM<br/>Reasoning LLM]
        end
        
        subgraph "LLM提供商"
            OLLAMA[Ollama<br/>本地部署]
            QWEN[Qwen 2.5:7b<br/>中文优化]
        end
    end
    
    %% 工作流层
    subgraph "工作流层"
        direction TB
        
        subgraph "对话管理"
            DIALOGUE_MGR[对话管理器<br/>Dialogue Manager]
            STATE_MGR[状态管理器<br/>State Manager]
            TASK_DECOMPOSER[任务分解器<br/>Task Decomposer]
        end
        
        subgraph "代码执行"
            CODE_EXECUTOR[代码执行器<br/>Code Executor]
            SYNTAX_VALIDATOR[语法验证器<br/>Syntax Validator]
            ERROR_HANDLER[错误处理器<br/>Error Handler]
        end
    end
    
    %% 连接关系
    UI --> API
    API --> IDENTITY
    
    IDENTITY --> PLANNER
    PLANNER --> CODER
    CODER --> EXPLAINER
    EXPLAINER --> QA
    
    TASK_SELECTOR --> PLANNER
    ERROR_RECOVERY --> CODER
    REVIEW_LOOP --> EXPLAINER
    
    PLANNER --> MCP_ML
    PLANNER --> MCP_RETRIEVAL
    MCP_RETRIEVAL --> SIMBAD
    QA --> TAVILY
    
    CODER --> DATASET_MGR
    DATASET_MGR --> DATASET_SELECTOR
    DATASET_SELECTOR --> DATA_PREPROC
    
    DIALOGUE_MGR --> LOCAL_DB
    DIALOGUE_MGR --> QUERY_HISTORY
    DIALOGUE_MGR --> DIALOGUE_STORAGE
    
    IDENTITY --> BASIC_LLM
    PLANNER --> BASIC_LLM
    CODER --> CODE_LLM
    EXPLAINER --> VISION_LLM
    QA --> BASIC_LLM
    
    BASIC_LLM --> OLLAMA
    CODE_LLM --> OLLAMA
    VISION_LLM --> OLLAMA
    REASONING_LLM --> OLLAMA
    
    OLLAMA --> QWEN
    
    PLANNER --> DIALOGUE_MGR
    CODER --> STATE_MGR
    EXPLAINER --> TASK_DECOMPOSER
    
    CODER --> CODE_EXECUTOR
    CODE_EXECUTOR --> SYNTAX_VALIDATOR
    SYNTAX_VALIDATOR --> ERROR_HANDLER
    
    %% 样式定义
    classDef userLayer fill:#2d3748,stroke:#4a5568,stroke-width:2px,color:#ffffff
    classDef agentLayer fill:#1a365d,stroke:#2c5282,stroke-width:2px,color:#ffffff
    classDef mcpLayer fill:#553c9a,stroke:#7c3aed,stroke-width:2px,color:#ffffff
    classDef dataLayer fill:#065f46,stroke:#047857,stroke-width:2px,color:#ffffff
    classDef llmLayer fill:#7c2d12,stroke:#dc2626,stroke-width:2px,color:#ffffff
    classDef workflowLayer fill:#374151,stroke:#6b7280,stroke-width:2px,color:#ffffff
    
    class UI,API userLayer
    class IDENTITY,PLANNER,CODER,EXPLAINER,QA,TASK_SELECTOR,ERROR_RECOVERY,REVIEW_LOOP agentLayer
    class MCP_ML,MCP_RETRIEVAL,TAVILY,SIMBAD mcpLayer
    class DATASET_MGR,DATASET_SELECTOR,DATA_PREPROC,LOCAL_DB,QUERY_HISTORY,DIALOGUE_STORAGE dataLayer
    class BASIC_LLM,CODE_LLM,VISION_LLM,REASONING_LLM,OLLAMA,QWEN llmLayer
    class DIALOGUE_MGR,STATE_MGR,TASK_DECOMPOSER,CODE_EXECUTOR,SYNTAX_VALIDATOR,ERROR_HANDLER workflowLayer
```

## 🔄 用户对话流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant UI as Web界面
    participant API as API服务
    participant ID as 身份识别
    participant PL as 规划智能体
    participant CD as 代码智能体
    participant EX as 解释智能体
    participant MCP as MCP服务
    participant LLM as LLM服务
    
    U->>UI: 输入问题/请求
    UI->>API: 发送请求
    API->>ID: 识别用户类型
    
    alt 业余爱好者
        ID->>LLM: 使用简化prompt
    else 专业人员
        ID->>LLM: 使用专业prompt
    end
    
    ID->>PL: 开始任务规划
    PL->>MCP: 查询可用数据集
    MCP-->>PL: 返回数据集信息
    
    PL->>LLM: 生成对话策略
    PL->>U: 多轮对话澄清需求
    
    U->>PL: 确认需求
    PL->>CD: 传递最终需求
    
    CD->>MCP: 获取数据集
    CD->>LLM: 生成分析代码
    CD->>CD: 执行代码
    CD->>EX: 传递执行结果
    
    EX->>LLM: 分析可视化结果
    EX->>U: 返回解释报告
    
    U->>UI: 查看结果
```

## 📊 数据流向图

```mermaid
graph LR
    subgraph "输入源"
        USER_INPUT[用户输入]
        DATASETS[天文数据集]
        EXTERNAL_APIS[外部API]
    end
    
    subgraph "处理层"
        IDENTITY_CHECK[身份识别]
        TASK_CLASSIFICATION[任务分类]
        CODE_GENERATION[代码生成]
        CODE_EXECUTION[代码执行]
        RESULT_ANALYSIS[结果分析]
    end
    
    subgraph "输出层"
        VISUALIZATIONS[可视化图表]
        EXPLANATIONS[解释文本]
        CODE_OUTPUT[代码文件]
        REPORTS[分析报告]
    end
    
    USER_INPUT --> IDENTITY_CHECK
    IDENTITY_CHECK --> TASK_CLASSIFICATION
    TASK_CLASSIFICATION --> CODE_GENERATION
    
    DATASETS --> CODE_GENERATION
    EXTERNAL_APIS --> CODE_GENERATION
    
    CODE_GENERATION --> CODE_EXECUTION
    CODE_EXECUTION --> RESULT_ANALYSIS
    
    RESULT_ANALYSIS --> VISUALIZATIONS
    RESULT_ANALYSIS --> EXPLANATIONS
    RESULT_ANALYSIS --> CODE_OUTPUT
    RESULT_ANALYSIS --> REPORTS
    
    %% 样式
    classDef inputStyle fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#ffffff
    classDef processStyle fill:#7c2d12,stroke:#dc2626,stroke-width:2px,color:#ffffff
    classDef outputStyle fill:#065f46,stroke:#10b981,stroke-width:2px,color:#ffffff
    
    class USER_INPUT,DATASETS,EXTERNAL_APIS inputStyle
    class IDENTITY_CHECK,TASK_CLASSIFICATION,CODE_GENERATION,CODE_EXECUTION,RESULT_ANALYSIS processStyle
    class VISUALIZATIONS,EXPLANATIONS,CODE_OUTPUT,REPORTS outputStyle
```

## 🛠️ 技术栈架构

```mermaid
graph TB
    subgraph "前端技术栈"
        HTML[HTML5]
        CSS[CSS3 + 响应式设计]
        JS[JavaScript ES6+]
        BOOTSTRAP[Bootstrap框架]
    end
    
    subgraph "后端技术栈"
        FASTAPI[FastAPI框架]
        PYTHON[Python 3.9+]
        ASYNC[异步处理]
        PYDANTIC[数据验证]
    end
    
    subgraph "AI/ML技术栈"
        LANGGRAPH[LangGraph工作流]
        OLLAMA[Ollama本地LLM]
        QWEN[Qwen 2.5:7b模型]
        MCP[MCP协议]
        TAVILY[Tavily搜索API]
    end
    
    subgraph "数据处理技术栈"
        PANDAS[Pandas数据处理]
        NUMPY[NumPy数值计算]
        MATPLOTLIB[Matplotlib绘图]
        SEABORN[Seaborn统计可视化]
        SKLEARN[Scikit-learn机器学习]
    end
    
    subgraph "存储技术栈"
        SQLITE[SQLite数据库]
        JSON[JSON文件存储]
        CSV[CSV数据格式]
        PICKLE[Python对象序列化]
    end
    
    subgraph "部署技术栈"
        DOCKER[Docker容器化]
        NGINX[Nginx反向代理]
        SYSTEMD[Systemd服务管理]
        LOGGING[结构化日志]
    end
    
    %% 连接关系
    HTML --> FASTAPI
    CSS --> FASTAPI
    JS --> FASTAPI
    BOOTSTRAP --> FASTAPI
    
    FASTAPI --> PYTHON
    PYTHON --> ASYNC
    PYTHON --> PYDANTIC
    
    FASTAPI --> LANGGRAPH
    LANGGRAPH --> OLLAMA
    OLLAMA --> QWEN
    LANGGRAPH --> MCP
    MCP --> TAVILY
    
    PYTHON --> PANDAS
    PANDAS --> NUMPY
    PANDAS --> MATPLOTLIB
    MATPLOTLIB --> SEABORN
    PANDAS --> SKLEARN
    
    PYTHON --> SQLITE
    PYTHON --> JSON
    PANDAS --> CSV
    PYTHON --> PICKLE
    
    FASTAPI --> DOCKER
    DOCKER --> NGINX
    NGINX --> SYSTEMD
    SYSTEMD --> LOGGING
    
    %% 样式
    classDef frontendStyle fill:#1e40af,stroke:#3b82f6,stroke-width:2px,color:#ffffff
    classDef backendStyle fill:#dc2626,stroke:#ef4444,stroke-width:2px,color:#ffffff
    classDef aiStyle fill:#7c2d12,stroke:#dc2626,stroke-width:2px,color:#ffffff
    classDef dataStyle fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff
    classDef storageStyle fill:#7c3aed,stroke:#8b5cf6,stroke-width:2px,color:#ffffff
    classDef deployStyle fill:#374151,stroke:#6b7280,stroke-width:2px,color:#ffffff
    
    class HTML,CSS,JS,BOOTSTRAP frontendStyle
    class FASTAPI,PYTHON,ASYNC,PYDANTIC backendStyle
    class LANGGRAPH,OLLAMA,QWEN,MCP,TAVILY aiStyle
    class PANDAS,NUMPY,MATPLOTLIB,SEABORN,SKLEARN dataStyle
    class SQLITE,JSON,CSV,PICKLE storageStyle
    class DOCKER,NGINX,SYSTEMD,LOGGING deployStyle
```

## 🔧 核心组件说明

### 智能体层
- **身份识别智能体**: 判断用户是业余爱好者还是专业人员
- **规划智能体**: 管理多轮对话，分解复杂任务
- **代码生成智能体**: 生成天文数据分析代码
- **解释智能体**: 解释可视化结果和代码逻辑
- **问答智能体**: 处理一般性天文问题

### MCP服务层
- **机器学习MCP**: 提供模型训练和数据分析服务
- **数据检索MCP**: 连接Simbad TAP服务进行天体数据查询
- **外部API集成**: Tavily搜索、Simbad数据库等

### 数据处理层
- **数据集管理**: 管理SDSS星系数据、恒星分类数据等
- **存储系统**: SQLite数据库、查询历史、对话记录

### LLM服务层
- **多种LLM类型**: 基础、代码、视觉、推理专用模型
- **本地部署**: 使用Ollama部署Qwen 2.5:7b模型

### 工作流层
- **对话管理**: 多轮对话状态跟踪
- **代码执行**: 安全的代码执行环境
- **错误处理**: 智能错误恢复机制

---

*该架构图展示了Astro-Insight项目的完整技术栈和组件关系，采用模块化设计，支持扩展和维护。*


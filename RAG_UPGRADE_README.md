# 🚀 RAG增强代码审查系统升级指南

## 📋 升级概述

现有的AI代码审查系统添加了RAG（Retrieval-Augmented Generation）功能。升级后的系统具备以下新特性：

### 🆕 新增功能

1. **智能知识库管理**

   - 支持上传自定义技术文档（PDF、Word、Markdown、代码文件等）
   - 内置7种编程语言的最佳实践文档（HTML、CSS、JavaScript、Java、Python、C++、Go）
   - 文档自动分割和向量化存储
   - 基于ChromaDB的持久化向量存储
2. **智能语言检测与检索**

   - 自动检测代码语言特征（Python、JavaScript、Java、Go、C++、HTML、CSS）
   - 基于代码内容进行语义相似性搜索
   - 智能匹配相关技术文档和最佳实践
   - 支持相似度阈值过滤和结果数量限制
3. **RAG增强审查**

   - 结合检索到的知识文档进行代码审查
   - 提供基于最佳实践的具体建议
   - 动态生成上下文感知的审查提示词
   - 支持多种审查风格（专业、讽刺、温和、幽默）
4. **可视化管理界面**

   - 知识库状态监控和文档统计
   - 文档上传、管理和搜索
   - RAG功能测试和批量审查
   - 结果对比和报告导出
5. **高级功能**

   - 支持温度参数调节（0-2）
   - 相似度阈值配置（0-1）
   - 批量代码审查
   - 审查结果评分系统

## 🔧 部署步骤

### 1. 安装依赖

```bash
# 安装新增的RAG相关依赖
pip install -r requirements.txt
```

**核心RAG依赖包**：

- `chromadb==0.4.15` - 向量数据库
- `sentence-transformers==2.2.2` - 文本向量化
- `langchain==0.1.0` - 语言链框架
- `PyPDF2==3.0.1` - PDF文档处理
- `python-docx==0.8.11` - Word文档处理
- `markdown==3.5.1` - Markdown处理
- `beautifulsoup4==4.12.2` - HTML解析
- `faiss-cpu==1.7.4` - 向量检索

### 2. 配置环境变量

在 `conf/.env` 文件中添加以下RAG相关配置：

```bash
# RAG功能配置
ENABLE_RAG=1
# 1表示启用RAG，0表示使用原有审查方式

# 知识库配置  
KNOWLEDGE_BASE_PATH=data/knowledge_base
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
SEARCH_RESULTS_LIMIT=5

# 相似度配置
RAG_SIMILARITY_THRESHOLD=0.2

# 模型配置
AUTO_INIT_BUILTIN_KNOWLEDGE=1

# 其他配置保持不变...
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_api_key_here
GITLAB_ACCESS_TOKEN=your_token_here
```

### 3. 启动升级后的服务

#### 方式一：Docker部署（推荐）

```bash
# 使用现有的docker-compose，会自动支持RAG功能
docker-compose up -d
```

#### 方式二：本地部署

```bash
# 启动API服务（包含RAG功能）
python api.py

# 启动原有Dashboard
streamlit run ui.py --server.port=5002 --server.address=0.0.0.0

# 启动RAG管理界面
streamlit run rag_dashboard.py --server.port=5003 --server.address=0.0.0.0
```

### 4. 验证部署

- API服务：http://localhost:5001
- 原Dashboard：http://localhost:5002
- RAG管理界面：http://localhost:5003

## 🎯 使用指南

### RAG管理界面功能

#### 1. 状态总览 📊

- 查看RAG功能启用状态
- 监控知识库文档统计（自定义文档、内置文档）
- 检查系统配置和知识库路径

#### 2. 文档管理 📝

- 查看所有已上传的文档（自定义和内置）
- 管理自定义文档（删除、搜索）
- 恢复和重新加载内置文档

#### 3. 文档搜索 🔍

- 测试语义搜索功能
- 支持按来源过滤（自定义、内置、全部）
- 查看检索结果和相似度分数
- 验证知识库内容质量

#### 4. 上传文档 📁

- 支持多种文件格式：PDF、Word(docx)、Markdown、代码文件
- 添加标题和标签便于分类
- 自动处理和向量化存储

#### 5. RAG测试 🧪

- 输入代码片段测试审查功能
- 支持预设示例代码（HTML、CSS、JavaScript、Java、Python、C++、Go）
- 可调节温度参数（0-2）和相似度阈值（0-1）
- 查看检索到的相关文档
- 对比RAG前后的审查效果

#### 6. 批量审查 📦

- 支持多个代码文件批量审查
- 可选择RAG测试或RAG/普通对比模式
- 生成批量审查报告

### API接口

新增的知识库管理API：

```bash
# 获取知识库状态
GET /api/knowledge/status
Response: {
    "rag_enabled": true,
    "total_documents": 15,
    "custom_documents": 3,
    "builtin_documents": 12,
    "knowledge_base_path": "data/knowledge_base"
}

# 上传文档
POST /api/knowledge/upload
Content-Type: multipart/form-data
Body: {
    "file": <file>,
    "title": "文档标题",
    "tags": "tag1,tag2,tag3"
}

# 列出文档
GET /api/knowledge/documents
Response: {
    "documents": [
        {
            "id": "doc_id",
            "title": "文档标题",
            "tags": ["tag1", "tag2"],
            "source": "custom",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 15
}

# 删除文档
DELETE /api/knowledge/documents/{doc_id}?source=custom

# 搜索文档
POST /api/knowledge/search
Body: {
    "query": "搜索关键词",
    "n_results": 5,
    "source": "all",
    "similarity_threshold": 0.2
}

# 测试RAG
POST /api/knowledge/test_rag
Body: {
    "code": "代码内容",
    "commit_message": "提交信息",
    "temperature": 0.3,
    "similarity_threshold": 0.2
}
Response: {
    "code": "代码内容",
    "commit_message": "提交信息",
    "similarity_threshold": 0.2,
    "temperature": 0.3,
    "relevant_docs": "相关文档内容",
    "review_result": "审查结果",
    "score": 85
}

# 对比RAG和普通审查
POST /api/knowledge/compare_rag
Body: {
    "code": "代码内容",
    "commit_message": "提交信息",
    "temperature": 0.3,
    "similarity_threshold": 0.2
}
Response: {
    "rag_result": {
        "relevant_docs": "相关文档",
        "review_result": "RAG审查结果",
        "score": 85
    },
    "normal_result": {
        "review_result": "普通审查结果",
        "score": 75
    }
}
```

## 🔄 工作流程对比

### 原有流程

```
Webhook触发 → 获取代码变更 → 调用LLM → 返回审查结果
```

### 升级后RAG流程

```
Webhook触发 → 获取代码变更 → 语言特征检测 → 知识库检索 → RAG增强审查 → 返回基于最佳实践的审查结果
```

### 详细RAG流程

1. **代码接收**: 接收代码变更和提交信息
2. **语言检测**: 自动检测代码语言（Python、JavaScript、Java、Go、C++、HTML、CSS）
3. **特征提取**: 提取代码中的关键字、库引用等特征
4. **知识检索**: 在知识库中检索相关技术文档
5. **相似度过滤**: 根据阈值过滤相关文档
6. **RAG审查**: 结合检索到的文档进行代码审查
7. **结果生成**: 生成基于最佳实践的审查报告

## 📚 内置知识库

系统预置了以下编程语言规范文档：

1. **HTML编码规范** (`html_standards.md`)

   - 语义化标签使用指南
   - 可访问性最佳实践
   - SEO优化建议
2. **CSS编码规范** (`css_standards.md`)

   - BEM命名规范
   - 响应式设计原则
   - 性能优化指南
3. **JavaScript编码规范** (`javascript_standards.md`)

   - ES6+特性使用建议
   - 函数式编程最佳实践
   - 异步编程规范
4. **Java编码规范** (`java_standards.md`)

   - SOLID原则应用
   - 并发编程最佳实践
   - 性能优化指南
5. **Python编码规范** (`python_standards.md`)

   - PEP 8代码风格
   - 类型注解使用
   - 最佳实践建议
6. **C++编码规范** (`cpp_standards.md`)

   - 内存管理准则
   - RAII原则应用
   - 性能优化指南
7. **Go编码规范** (`go_standards.md`)

   - 并发安全最佳实践
   - 错误处理规范
   - 接口设计原则

## 🎨 自定义知识库

### 添加企业规范文档

1. 准备文档（支持TXT、PDF、Word(docx)、Markdown格式）
2. 通过RAG管理界面上传
3. 添加相关标签便于检索
4. 系统自动处理和向量化

### 文档组织建议

- **按技术栈分类**：React、Vue、Java、Python等
- **按类型分类**：编码规范、最佳实践、架构设计等
- **按团队分类**：前端团队、后端团队、移动端团队等

### 支持的文档格式

- **PDF文档**: 自动提取文本内容
- **Word文档**: 支持.docx格式
- **Markdown**: 保持格式结构
- **代码文件**: 支持.py、.js、.java、.cpp、.go等
- **文本文件**: 纯文本格式

## ⚙️ 高级配置

### 知识库配置

```bash
# 知识库路径
KNOWLEDGE_BASE_PATH=data/knowledge_base

# 文本分割参数
CHUNK_SIZE=1000        # 分块大小
CHUNK_OVERLAP=200      # 重叠大小

# 检索参数
SEARCH_RESULTS_LIMIT=5  # 检索结果数量

# RAG功能开关
ENABLE_RAG=1           # 1启用，0禁用

# 相似度阈值
RAG_SIMILARITY_THRESHOLD=0.2

# 向量模型配置
MODEL_PATH=model/all-MiniLM-L6-v2  # 本地模型路径
```

### 审查风格配置

```bash
REVIEW_STYLE=professional  # professional, sarcastic, gentle, humorous
```

### 温度参数说明

- **0.0-0.3**: 保守、一致的输出
- **0.3-0.7**: 平衡的创造性和一致性
- **0.7-1.0**: 更创造性的输出
- **1.0-2.0**: 高度创造性的输出

## 🐛 故障排除

### 常见问题

1. **RAG功能不生效**

   - 检查 `ENABLE_RAG=1` 配置
   - 确认依赖包安装完整
   - 查看日志确认知识库初始化状态
2. **知识库为空**

   - 系统首次启动会自动初始化内置文档
   - 检查 `data/knowledge_base` 目录权限
   - 查看启动日志确认初始化过程
3. **文档上传失败**

   - 检查文件格式是否支持
   - 确认 `data/uploads` 目录可写
   - 查看具体错误信息
4. **搜索结果为空**

   - 确认知识库中有相关文档
   - 尝试不同的搜索关键词
   - 检查向量化是否正常
5. **模型加载失败**

   - 检查 `model/all-MiniLM-L6-v2/` 目录
   - 确认模型文件完整性
   - 尝试重新下载模型

### 日志调试

```bash
# 查看详细日志
tail -f log/app.log
```

## 📈 性能优化

1. **向量模型选择**

   - 默认使用 `all-MiniLM-L6-v2`（轻量级，768维向量）
   - 支持本地模型和在线模型自动切换
   - 可升级到更大的模型获得更好效果
2. **文本分块优化**

   - 智能分块策略，支持在句子边界分割
   - 默认块大小1000字符，重叠200字符
   - 自动处理中英文混合文本
3. **检索优化**

   - 使用ChromaDB持久化存储
   - 支持标签过滤和元数据检索
   - 结果按相似度排序
   - 支持自定义检索数量限制
4. **语言检测优化**

   - 基于关键字和库引用的智能语言检测
   - 支持7种主流编程语言
   - 提高检索精度和效率

## 🔄 版本兼容性

- **向后兼容**：原有功能完全保留
- **可选启用**：通过 `ENABLE_RAG` 控制
- **平滑升级**：无需修改现有配置
- **渐进式部署**：可以逐步启用RAG功能

## 📊 功能对比

| 功能特性 | 原有系统        | RAG增强系统           |
| -------- | --------------- | --------------------- |
| 代码审查 | ✅ 基础审查     | ✅ 基于最佳实践的审查 |
| 知识库   | ❌ 无           | ✅ 智能知识库         |
| 语言检测 | ❌ 无           | ✅ 自动语言检测       |
| 文档检索 | ❌ 无           | ✅ 语义相似性检索     |
| 审查风格 | ✅ 多种风格可选 | ✅ 多种风格可选       |
| 温度调节 | ❌ 无           | ✅ 可调节创造性       |
| 批量审查 | ❌ 无           | ✅ 支持批量处理       |
| 结果对比 | ❌ 无           | ✅ RAG vs 普通对比    |

## 🔮 未来扩展

1. **更多语言支持**

   - 扩展语言检测能力
   - 添加更多编程语言规范
2. **高级检索功能**

   - 混合检索策略
   - 语义过滤功能
   - 多模态检索
3. **个性化定制**

   - 团队专属知识库
   - 个性化审查风格
   - 自定义评分标准
4. **集成增强**

   - IDE插件支持
   - CI/CD集成
   - 团队协作功能

---

*本文档描述了RAG代码审查系统的完整功能和使用方法，帮助用户快速上手和深度使用该系统。*

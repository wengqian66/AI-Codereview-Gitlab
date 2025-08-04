 # -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
import os
from datetime import datetime

# 导入示例代码
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from docs.examples.code_examples import (
    html_example as HTML_EXAMPLE,
    css_example as CSS_EXAMPLE,
    js_example as JS_EXAMPLE,
    java_example as JAVA_EXAMPLE,
    python_example as PYTHON_EXAMPLE,
    cpp_example as CPP_EXAMPLE,
    go_example as GO_EXAMPLE
)

# 设置页面配置
st.set_page_config(
    page_title="RAG代码审查 - 知识库管理",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API基础URL
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5001')

def get_knowledge_status():
    """获取知识库状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge/status")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"获取状态失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"连接API失败: {e}")
        return None

def list_documents():
    """获取文档列表"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge/documents")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"获取文档列表失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"连接API失败: {e}")
        return None

def search_documents(query, n_results=5, source='all', similarity_threshold=0.0):
    """搜索文档"""
    try:
        data = {
            'query': query,
            'n_results': n_results,
            'source': source,
            'similarity_threshold': similarity_threshold
        }
        response = requests.post(f"{API_BASE_URL}/api/knowledge/search", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"搜索失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"连接API失败: {e}")
        return None

def test_rag(code, commit_message='', temperature=0.3, similarity_threshold=0.2):
    """测试RAG功能"""
    try:
        data = {
            'code': code,
            'commit_message': commit_message,
            'temperature': temperature,
            'similarity_threshold': similarity_threshold
        }
        response = requests.post(f"{API_BASE_URL}/api/knowledge/test_rag", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"RAG测试失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"连接API失败: {e}")
        return None

def compare_rag(code, commit_message='', temperature=0.3, similarity_threshold=0.2):
    """对比测试RAG和非RAG功能"""
    try:
        data = {
            'code': code,
            'commit_message': commit_message,
            'temperature': temperature,
            'similarity_threshold': similarity_threshold
        }
        response = requests.post(f"{API_BASE_URL}/api/knowledge/compare_rag", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"RAG对比测试失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"连接API失败: {e}")
        return None

def upload_document(file_name, content, tags):
    """上传文档"""
    try:
        # 创建临时文件对象
        import io
        file_obj = io.BytesIO(content.encode('utf-8'))
        file_obj.name = file_name
        
        files = {'file': (file_name, file_obj, 'text/plain')}
        data = {
            'title': file_name,
            'tags': ','.join(tags) if tags else ''
        }
        response = requests.post(f"{API_BASE_URL}/api/knowledge/upload", files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"上传失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"连接API失败: {e}")
        return None

def delete_document(doc_id, source='custom'):
    """删除文档"""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/knowledge/documents/{doc_id}?source={source}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"删除失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"连接API失败: {e}")
        return None

def restore_builtin_documents():
    """恢复内置文档"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/knowledge/documents/restore")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"恢复失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"连接API失败: {e}")
        return None

def reload_builtin_documents():
    """重新加载内置文档"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/knowledge/documents/reload")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"重新加载失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"连接API失败: {e}")
        return None

def generate_markdown_report(result, code, commit_message, report_type="RAG"):
    """生成Markdown格式的审查报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 获取模型参数
    temperature = result.get('temperature', 'N/A')
    similarity_threshold = result.get('similarity_threshold', 'N/A')
    
    markdown_content = f"""# 代码审查报告

## 基本信息
- **报告类型**: {report_type}代码审查
- **生成时间**: {timestamp}

## 模型参数
- **模型温度**: {temperature}
- **相似度阈值**: {similarity_threshold}

## 代码信息
- **提交信息**: {commit_message if commit_message else '无'}
- **代码长度**: {len(code)} 字符

## 代码内容
```code
{code}
```

"""
    
    # 根据报告类型添加审查结果
    if report_type == "RAG":
        markdown_content += f"""
## 审查结果
{result.get('review_result', '无审查结果')}

"""
    
    # 如果是RAG审查，添加相关文档信息
    if report_type == "RAG" and result.get('relevant_docs'):
        markdown_content += f"""
## 检索到的相关文档
{result.get('relevant_docs', '无相关文档')}

"""
    
    # 如果是对比报告，添加对比信息
    if report_type == "对比" and 'comparison' in result:
        comparison = result['comparison']
        markdown_content += f"""
## 对比分析
- **评分差异**: {comparison.get('score_difference', 0):+d}
- **检索文档数**: {comparison.get('unique_docs_count', 0)}
- **是否找到相关文档**: {'是' if comparison.get('has_relevant_docs', False) else '否'}

### RAG增强审查结果
**评分**: {result.get('rag_result', {}).get('score', 'N/A')}/100

{result.get('rag_result', {}).get('review_result', '无审查结果')}

### 普通模型审查结果
**评分**: {result.get('normal_result', {}).get('score', 'N/A')}/100

{result.get('normal_result', {}).get('review_result', '无审查结果')}

"""
    
    markdown_content += f"""
---
*报告由AI代码审查系统自动生成*
"""
    
    return markdown_content

# 主界面
st.title("🤖 RAG代码审查 - 知识库管理")

# 侧边栏
with st.sidebar:
    st.header("导航")
    page = st.selectbox("选择功能", [
        "📊 状态总览",
        "📚 文档管理", 
        "🔍 文档搜索",
        "📤 文档上传",
        "🧪 RAG测试",
        "📁 批量文件审查"
    ])

# 状态总览页面
if page == "📊 状态总览":
    st.header("知识库状态")
    
    status = get_knowledge_status()
    if status:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("RAG状态", "启用" if status['rag_enabled'] else "禁用")
        
        with col2:
            st.metric("总文档数", status['total_documents'])
        
        with col3:
            st.metric("自定义文档", status['custom_documents'])
        
        with col4:
            st.metric("内置文档", status['builtin_documents'])
        

# 文档管理页面
elif page == "📚 文档管理":
    st.header("文档管理")
    
    # 添加恢复内置文档按钮和批量操作按钮
    col1, col2, col3, col4 = st.columns([3, 3, 2, 4])
    with col1:
        if st.button("🔄 恢复内置文档", use_container_width=True, help="恢复所有内置文档"):
            with st.spinner("正在恢复内置文档..."):
                result = restore_builtin_documents()
                if result:
                    st.success("✅ 内置文档已恢复!")
                    # 清除缓存的文档列表并标记需要刷新
                    if 'documents_cache' in st.session_state:
                        del st.session_state.documents_cache
                    st.session_state.refresh_documents = True
                    st.rerun()
    
    with col2:
        if st.button("🔄 重新加载内置文档", use_container_width=True, help="清除并重新加载最新的内置文档"):
            with st.spinner("正在重新加载内置文档..."):
                result = reload_builtin_documents()
                if result:
                    st.success("✅ 内置文档已重新加载!")
                    # 清除缓存的文档列表并标记需要刷新
                    if 'documents_cache' in st.session_state:
                        del st.session_state.documents_cache
                    st.session_state.refresh_documents = True
                    st.rerun()
    
    # 获取文档列表（使用缓存）
    if 'documents_cache' not in st.session_state or st.session_state.get('refresh_documents', False):
        with st.spinner("正在加载文档列表..."):
            documents_data = list_documents()
            st.session_state.documents_cache = documents_data.get('documents', []) if documents_data else []
            st.session_state.refresh_documents = False
    
    documents = st.session_state.documents_cache
    
    if documents:
        # 添加批量删除按钮
        with col3:
            if st.button("🗑️ 批量删除", type="primary", use_container_width=True):
                selected_docs = [
                    (doc['doc_id'], doc['source']) 
                    for doc in documents 
                    if st.session_state.get(f"select_{doc['doc_id']}", False)
                ]
                if selected_docs:
                    success_count = 0
                    progress_bar = st.progress(0)
                    for i, (doc_id, source) in enumerate(selected_docs):
                        with st.spinner(f"正在删除文档 {i+1}/{len(selected_docs)}..."):
                            result = delete_document(doc_id, source)
                            if result:
                                success_count += 1
                        progress_bar.progress((i + 1) / len(selected_docs))
                    st.success(f"✅ 成功删除 {success_count}/{len(selected_docs)} 个文档!")
                    # 清除缓存的文档列表并标记需要刷新
                    if 'documents_cache' in st.session_state:
                        del st.session_state.documents_cache
                    st.session_state.refresh_documents = True
                    # 清除所有选择状态
                    for doc in documents:
                        if hasattr(st.session_state, f"select_{doc['doc_id']}"):
                            delattr(st.session_state, f"select_{doc['doc_id']}")
                    st.rerun()
                else:
                    st.warning("请先选择要删除的文档")
        
        # 定义来源显示映射
        source_display = {
            "custom": "自定义文档",
            "builtin": "内置文档"
        }
        
        for doc in documents:
            source_text = source_display.get(doc['source'], doc['source'])
            col_checkbox, col_expander = st.columns([0.5, 11.5])
            
            with col_checkbox:
                st.checkbox("", key=f"select_{doc['doc_id']}", value=False)
            
            with col_expander:
                with st.expander(f"📄 {doc['title']} ({source_text})"):
                    col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**文档ID:** {doc['doc_id']}")
                    st.write(f"**来源:** {source_text}")
                    st.write(f"**标签:** {', '.join(doc['tags']) if doc['tags'] else '无'}")
                    st.write(f"**块数量:** {doc['chunk_count']}")
                
                with col2:
                    if st.button("删除", key=f"delete_{doc['doc_id']}"):
                        with st.spinner("正在删除文档..."):
                            result = delete_document(doc['doc_id'], doc['source'])
                            if result:
                                st.success("✅ 文档删除成功!")
                                # 清除缓存的文档列表并标记需要刷新
                                if 'documents_cache' in st.session_state:
                                    del st.session_state.documents_cache
                                st.session_state.refresh_documents = True
                                st.rerun()
    else:
        st.info("暂无文档")

# 文档搜索页面
elif page == "🔍 文档搜索":
    st.header("文档搜索")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("搜索查询", placeholder="输入搜索关键词...")
    
    with col2:
        n_results = st.number_input("结果数量", min_value=1, max_value=20, value=5)
        source = st.selectbox("搜索范围", ["全部", "自定义文档", "内置文档"])
        similarity_threshold = st.slider(
            "相似度阈值",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
            help="只显示相似度大于等于该值的结果"
        )
        
        # 映射source值
        source_mapping = {
            "全部": "all",
            "自定义文档": "custom",
            "内置文档": "builtin"
        }
        source = source_mapping[source]
    
    if st.button("搜索") and query:
        # 使用缓存的搜索结果
        cache_key = f"search_results_{query}_{n_results}_{source}_{similarity_threshold}"
        if cache_key not in st.session_state:
            with st.spinner("正在搜索相关文档..."):
                results = search_documents(query, n_results, source, similarity_threshold)
                st.session_state[cache_key] = results
        else:
            results = st.session_state[cache_key]
        
        if results and results['results']:
            # 过滤掉相似度低于阈值的结果
            filtered_results = [r for r in results['results'] if r['score'] >= similarity_threshold]
            
            if filtered_results:
                st.write(f"找到 {len(filtered_results)} 个相关结果 (相似度阈值: {similarity_threshold:.2f}):")
                
                # 定义来源映射
                source_display = {
                    "custom": "自定义文档",
                    "builtin": "内置文档"
                }
                
                for i, result in enumerate(filtered_results):
                    with st.expander(f"结果 {i+1}: {result['metadata']['title']} (相似度: {result['score']:.3f})"):
                        st.write(f"**来源:** {source_display.get(result['source'], result['source'])}")
                        st.write(f"**标签:** {result['metadata'].get('tags', '').replace(',', ', ')}")
                        st.write("**内容:**")
                        st.text(result['content'])
            else:
                st.info(f"未找到相似度大于等于 {similarity_threshold:.2f} 的结果")
        else:
            st.info("未找到相关结果")

# 文档上传页面
elif page == "📤 文档上传":
    st.header("📤 文档上传")
    
    st.write("上传文档到知识库，用于RAG增强的代码审查。支持的文件类型：")
    st.write("• **Markdown文档**: .md (推荐)")
    st.write("• **文本文档**: .txt")
    st.write("")
    st.info("💡 **建议上传内容**: 代码规范、最佳实践、设计文档、架构说明、API文档等")
    
    st.divider()
    
    uploaded_file = st.file_uploader("选择要上传的文档", type=['txt', 'md'])
    
    if uploaded_file is not None:
        st.success("✅ 文件已选择")
        
        # 显示文件信息
        st.write("**文件信息:**")
        st.write(f"- 文件名: {uploaded_file.name}")
        st.write(f"- 文件大小: {uploaded_file.size / 1024:.2f} KB")
        st.write(f"- 文件类型: {uploaded_file.type}")
        
        st.divider()
        
        # 添加标签输入
        st.write("**文档标签** (可选)")
        st.write("添加标签有助于文档分类和检索，多个标签用逗号分隔")
        tags = st.text_input("标签 (用逗号分隔)", placeholder="例如: python, 代码规范, 最佳实践")
        tags = [tag.strip() for tag in tags.split(",")] if tags else []
        
        if tags:
            st.write("**已添加标签:**")
            for tag in tags:
                st.write(f"• {tag}")
        
        st.divider()
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📤 上传文档", type="primary", use_container_width=True):
                with st.spinner("正在上传文档..."):
                    # 读取文件内容
                    content = uploaded_file.read().decode('utf-8')
                    
                    # 上传文档
                    result = upload_document(uploaded_file.name, content, tags)
                    
                    if result:
                        st.success("✅ 文档上传成功!")
                        st.balloons()
                        # 清除文档列表缓存，确保文档管理页面显示最新数据
                        if 'documents_cache' in st.session_state:
                            del st.session_state.documents_cache
                        st.session_state.refresh_documents = True
                        st.rerun()
                    else:
                        st.error("❌ 文档上传失败，请重试!")

# RAG测试页面
elif page == "🧪 RAG测试":
    st.header("RAG功能测试")
    
    st.write("输入代码片段，测试RAG增强的代码审查功能:")
    
    # 预设示例代码
    examples = {
        "HTML示例": {
            "code": HTML_EXAMPLE,
            "commit": "实现响应式导航菜单组件，支持移动端适配"
        },
        "CSS示例": {
            "code": CSS_EXAMPLE,
            "commit": "添加暗色主题样式，实现主题切换功能"
        },
        "JavaScript示例": {
            "code": JS_EXAMPLE,
            "commit": "实现用户数据异步获取函数，包含错误处理和状态检查"
        },
        "Java示例": {
            "code": JAVA_EXAMPLE,
            "commit": "实现用户创建服务，包含用户名查重和数据持久化功能"
        },
        "Python示例": {
            "code": PYTHON_EXAMPLE,
            "commit": "实现购物车商品总价计算函数，支持批量计算"
        },
        "C++示例": {
            "code": CPP_EXAMPLE,
            "commit": "实现线程安全的队列模板类，支持并发操作"
        },
        "Go示例": {
            "code": GO_EXAMPLE,
            "commit": "实现消息处理函数，支持上下文控制和错误处理"
        }
    }
    
    # 示例选择器
    st.subheader("💡 快速开始 - 选择示例代码")
    
    # 示例说明
    example_descriptions = {
        "HTML示例": "🌐 测试HTML结构和语义化标签使用 - 包含响应式布局、可访问性等",
        "CSS示例": "🎨 测试CSS样式规范 - 包含响应式设计、布局结构、命名规范等",
        "JavaScript示例": "📱 测试JavaScript交互逻辑 - 包含事件处理、DOM操作、性能优化等",
        "Java示例": "☕ 测试Java代码规范 - 包含面向对象设计、异常处理、CRUD操作等",
        "Python示例": "🐍 测试Python代码规范 - 包含数据库操作、类型注解、异常处理等",
        "C++示例": "⚡ 测试C++代码规范 - 包含内存管理、智能指针、并发安全等",
        "Go示例": "🔄 测试Go代码规范 - 包含并发处理、错误处理、接口设计等"
    }
    
    # 调整整体布局比例，给按钮区域更多空间
    col1, col2 = st.columns([2.2, 1])
    
    with col1:
        selected_example = st.selectbox(
            "选择示例",
            options=list(examples.keys()),
            help="选择一个预设的示例代码来测试RAG增强的代码审查功能"
        )
        
        # 显示选中示例的描述
        if selected_example in example_descriptions:
            st.info(example_descriptions[selected_example])
    
    with col2:
        # 两个按钮等宽排列
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            if st.button("使用此示例", type="primary", use_container_width=True):
                st.session_state.example_code = examples[selected_example]["code"]
                st.session_state.example_commit = examples[selected_example]["commit"]
                st.rerun()
        
        with col2_2:
            if st.button("清空代码", use_container_width=True):
                if hasattr(st.session_state, 'example_code'):
                    del st.session_state.example_code
                if hasattr(st.session_state, 'example_commit'):
                    del st.session_state.example_commit
                st.rerun()
    
    # 获取代码内容
    default_code = ""
    default_commit = ""
    
    if hasattr(st.session_state, 'example_code'):
        default_code = st.session_state.example_code
        default_commit = st.session_state.example_commit
    
    st.subheader("🔧 代码审查")
    
    code = st.text_area(
        "代码内容",
        value=default_code,
        height=300,
        placeholder="输入要审查的代码，或使用上面的示例...",
        help="输入需要进行代码审查的代码内容"
    )
    
    commit_message = st.text_area(
        "代码功能说明 (可选)",
        value=default_commit,  # 使用default_commit作为默认值
        placeholder="请简要说明这段代码的主要功能和目的...",
        height=100
    )
    
    # 添加模型参数控制区域
    st.subheader("⚙️ 模型参数设置")
    
    param_col1, param_col2, param_col3 = st.columns(3)
    
    # 初始化重置计数器
    if 'reset_counter' not in st.session_state:
        st.session_state.reset_counter = 0
    
    # 重置参数按钮
    with param_col3:
        # 重置参数按钮
        if st.button("🔄 重置参数", key="reset_params_btn", use_container_width=True):
            # 增加重置计数器，强制滑块重新初始化
            st.session_state.reset_counter += 1
            st.rerun()
    
    with param_col1:
        # 温度控制滑块 - 使用动态key
        temperature = st.slider(
            "🌡️ 模型温度",
            min_value=0.0,
            max_value=2.0,
            value=0.3,  # 直接使用默认值
            step=0.1,
            key=f"temperature_slider_{st.session_state.reset_counter}",
            help="控制AI输出的随机性：\n• 0.0-0.3: 确定性高，适合代码审查\n• 0.4-0.7: 平衡创造性和一致性\n• 0.8-2.0: 创造性高，输出更随机"
        )
        
        # 显示温度说明
        if temperature <= 0.3:
            st.info("🎯 确定性模式：输出稳定一致")
        elif temperature <= 0.7:
            st.info("⚖️ 平衡模式：平衡创造性和一致性")
        else:
            st.info("🎨 创造性模式：输出更具创造性")
    
    with param_col2:
        # 相似度阈值控制 - 使用动态key
        similarity_threshold = st.slider(
            "📊 相似度阈值",
            min_value=0.0,
            max_value=1.0,
            value=0.2,  # 直接使用默认值
            step=0.05,
            key=f"similarity_slider_{st.session_state.reset_counter}",
            help="控制检索文档的相关性：\n• 0.0: 显示所有检索结果\n• 0.2-0.5: 显示相关度较高的文档\n• 0.6-1.0: 只显示高度相关的文档"
        )
    
    # 显示当前参数状态
    with param_col3:
        # 显示当前参数状态
        st.markdown("**当前参数设置：**")
        st.markdown(f"• 温度: **{temperature}**")
        st.markdown(f"• 相似度阈值: **{similarity_threshold}**")
    
    # 测试按钮区域
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 RAG测试", type="primary", use_container_width=True):
            if code.strip():
                with st.spinner("正在进行RAG增强的代码审查..."):
                    result = test_rag(code, commit_message, temperature, similarity_threshold)
                
                if result:
                    st.success("RAG测试完成!")
                    
                    # 存储结果到session state
                    st.session_state.rag_result = result
                    st.session_state.current_code = code
                    st.session_state.current_commit = commit_message
                    
                    # 清除对比结果的显示标记，确保只显示RAG测试结果
                    if hasattr(st.session_state, 'show_compare_result'):
                        del st.session_state.show_compare_result
                    
                    # 显示相关文档
                    st.subheader("📚 检索到的相关文档")
                    if result['relevant_docs']:
                        # 按文档分段显示
                        docs = result['relevant_docs'].split('###')
                        for i, doc in enumerate(docs):
                            if doc.strip():  # 跳过空文档
                                # 提取标题和相似度
                                lines = doc.strip().split('\n')
                                if lines:
                                    title_line = lines[0]
                                    content = '\n'.join(lines[1:])
                                    with st.expander(f"📄 {title_line}"):
                                        st.text(content)
                    else:
                        st.info("未找到相关文档")
                    
                    # 显示审查结果
                    st.subheader("🔍 RAG审查结果")
                    st.markdown(result['review_result'])
                    
                    # 显示评分
                    st.metric("RAG审查评分", f"{result['score']}/100")
            else:
                st.error("请输入代码内容")
    
    with col2:
        if st.button("📊 普通/RAG模式对比", help="对比使用和不使用RAG（检索增强生成）的两种审查模式的效果差异", use_container_width=True):
            if code.strip():
                with st.spinner("正在对比两种审查模式的效果..."):
                    result = compare_rag(code, commit_message, temperature, similarity_threshold)
                    
                    if result:
                        st.success("审查模式对比完成!")
                        
                        # 将结果存储到session state中，以便在整个页面宽度显示
                        st.session_state.compare_result = result
                        st.session_state.current_code = code
                        st.session_state.current_commit = commit_message
                        st.session_state.show_compare_result = True # 标记显示对比结果
                        st.rerun()
            else:
                st.error("请输入代码内容")

    # 导出功能区域
    if hasattr(st.session_state, 'rag_result') or hasattr(st.session_state, 'compare_result'):
        st.subheader("📤 导出审查报告")
        
        export_col1, export_col2, export_col3 = st.columns([2, 2, 2])
        
        with export_col1:
            if hasattr(st.session_state, 'rag_result'):
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rag_code_review_{timestamp}.md"
                
                # 直接提供下载按钮
                markdown_content = generate_markdown_report(
                    st.session_state.rag_result,
                    st.session_state.current_code,
                    st.session_state.current_commit,
                    "RAG"
                )
                
                st.download_button(
                    label="📄 导出RAG报告",
                    data=markdown_content,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True
                )
        
        with export_col2:
            if hasattr(st.session_state, 'compare_result'):
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"compare_code_review_{timestamp}.md"
                
                # 直接提供下载按钮
                markdown_content = generate_markdown_report(
                    st.session_state.compare_result,
                    st.session_state.current_code,
                    st.session_state.current_commit,
                    "对比"
                )
                
                st.download_button(
                    label="📊 导出对比报告",
                    data=markdown_content,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True
                )
        
        with export_col3:
            if st.button("🗑️ 清除结果", use_container_width=True):
                # 清除所有结果
                for key in ['rag_result', 'compare_result', 'current_code', 'current_commit', 'show_compare_result']:
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                st.rerun()

    # 如果有对比结果，在整个页面宽度显示
    # 只有当用户明确点击了对比按钮时才显示对比内容
    if hasattr(st.session_state, 'compare_result') and st.session_state.get('show_compare_result', False):
        result = st.session_state.compare_result
        
        # 显示对比统计 - 占满整个宽度
        st.subheader("📈 对比统计")
        comp_col1, comp_col2, comp_col3 = st.columns(3)
        
        with comp_col1:
            st.metric(
                "评分差异", 
                f"{result['comparison']['score_difference']:+d}",
                help="RAG增强审查评分与普通审查评分的差值"
            )
        
        with comp_col2:
            st.metric(
                "检索文档数", 
                result['comparison']['unique_docs_count']
            )
        
        with comp_col3:
            has_docs = "✅" if result['comparison']['has_relevant_docs'] else "❌"
            st.metric("找到相关文档", has_docs)
        
        # 显示检索到的相关文档
        if result['rag_result']['relevant_docs']:
            st.subheader("📚 检索到的相关文档")
            # 按文档分段显示
            docs = result['rag_result']['relevant_docs'].split('###')
            for i, doc in enumerate(docs):
                if doc.strip():  # 跳过空文档
                    # 提取标题和相似度
                    lines = doc.strip().split('\n')
                    if lines:
                        title_line = lines[0]
                        content = '\n'.join(lines[1:])
                        with st.expander(f"📄 {title_line}"):
                            st.text(content)
        
        # 并排显示两个审查结果
        st.subheader("🔍 审查结果对比")
        
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            st.markdown("### 🤖 RAG增强审查")
            st.metric("评分", f"{result['rag_result']['score']}/100")
            st.markdown(result['rag_result']['review_result'])
        
        with result_col2:
            st.markdown("### 🔧 普通模型审查")
            st.metric("评分", f"{result['normal_result']['score']}/100")
            st.markdown(result['normal_result']['review_result'])
        
        if result['comparison']['has_relevant_docs']:
            st.info("📖 系统找到了相关的技术文档，这些文档被用于增强审查结果")
        else:
            st.warning("📭 系统未找到相关的技术文档，建议添加更多相关的编码规范文档")

# 批量文件审查页面
elif page == "📁 批量文件审查":
    st.header("📁 批量文件审查")
    
    st.write("上传多个代码文件，批量进行RAG增强的代码审查。支持多种编程语言：")
    st.write("• **Python**: .py")
    st.write("• **Java**: .java")
    st.write("• **C++**: .cpp, .cc, .cxx, .h, .hpp")
    st.write("• **JavaScript**: .js, .ts, .jsx, .tsx")
    st.write("• **Go**: .go")
    st.write("• **其他**: .txt, .md")
    
    st.divider()
    
    # 文件上传区域
    uploaded_files = st.file_uploader(
        "选择要审查的代码文件", 
        type=['py', 'java', 'cpp', 'cc', 'cxx', 'h', 'hpp', 'js', 'ts', 'jsx', 'tsx', 'go', 'txt', 'md'],
        accept_multiple_files=True,
        help="可以同时选择多个文件进行批量审查"
    )
    
    if uploaded_files:
        st.success(f"✅ 已选择 {len(uploaded_files)} 个文件")
        
        # 显示文件信息
        st.subheader("📋 文件信息")
        file_info = []
        for i, file in enumerate(uploaded_files):
            file_info.append({
                'index': i + 1,
                'name': file.name,
                'size': file.size,
                'type': file.type or '未知',
                'extension': file.name.split('.')[-1].lower() if '.' in file.name else '无扩展名'
            })
        
        # 创建文件信息表格
        import pandas as pd
        df = pd.DataFrame(file_info)
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # 批量审查设置
        st.subheader("⚙️ 批量审查设置")
        
        # 模型参数设置
        param_col1, param_col2, param_col3 = st.columns(3)
        
        with param_col1:
            temperature = st.slider(
                "🌡️ 模型温度",
                min_value=0.0,
                max_value=2.0,
                value=0.3,
                step=0.1,
                help="控制AI输出的随机性"
            )
        
        with param_col2:
            similarity_threshold = st.slider(
                "📊 相似度阈值",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.05,
                help="控制检索文档的相关性"
            )
        
        with param_col3:
            review_mode = st.selectbox(
                "🔍 审查模式",
                ["RAG测试", "RAG/普通对比"],
                help="选择审查模式：仅RAG测试或对比两种模式"
            )
        
        # 提交信息设置
        st.write("**提交信息设置**")
        commit_mode = st.radio(
            "提交信息模式",
            ["使用文件名作为提交信息", "自定义统一提交信息", "为每个文件单独设置"],
            help="选择如何为文件设置提交信息"
        )
        
        custom_commit = ""
        if commit_mode == "自定义统一提交信息":
            custom_commit = st.text_area(
                "统一提交信息",
                placeholder="请输入统一的提交信息...",
                height=80
            )
        
        # 文件提交信息映射
        file_commits = {}
        if commit_mode == "为每个文件单独设置":
            st.write("**为每个文件设置提交信息：**")
            for file in uploaded_files:
                commit = st.text_input(
                    f"文件 {file.name} 的提交信息",
                    placeholder="请输入提交信息...",
                    key=f"commit_{file.name}"
                )
                file_commits[file.name] = commit
        
        st.divider()
        
        # 开始批量审查
        if st.button("🚀 开始批量审查", type="primary", use_container_width=True):
            if not uploaded_files:
                st.error("请先选择要审查的文件")
            else:
                # 初始化进度
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 存储所有审查结果
                all_results = []
                
                for i, file in enumerate(uploaded_files):
                    try:
                        # 更新进度
                        progress = (i + 1) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"正在审查文件 {i+1}/{len(uploaded_files)}: {file.name}")
                        
                        # 读取文件内容
                        content = file.read().decode('utf-8')
                        
                        # 确定提交信息
                        if commit_mode == "使用文件名作为提交信息":
                            commit_message = f"文件: {file.name}"
                        elif commit_mode == "自定义统一提交信息":
                            commit_message = custom_commit
                        else:  # 为每个文件单独设置
                            commit_message = file_commits.get(file.name, f"文件: {file.name}")
                        
                        # 根据模式进行审查
                        if review_mode == "RAG测试":
                            result = test_rag(content, commit_message, temperature, similarity_threshold)
                            if result:
                                all_results.append({
                                    'file_name': file.name,
                                    'file_size': file.size,
                                    'commit_message': commit_message,
                                    'mode': 'RAG测试',
                                    'result': result,
                                    'success': True
                                })
                            else:
                                all_results.append({
                                    'file_name': file.name,
                                    'file_size': file.size,
                                    'commit_message': commit_message,
                                    'mode': 'RAG测试',
                                    'result': None,
                                    'success': False,
                                    'error': '审查失败'
                                })
                        else:  # RAG/普通对比
                            result = compare_rag(content, commit_message, temperature, similarity_threshold)
                            if result:
                                all_results.append({
                                    'file_name': file.name,
                                    'file_size': file.size,
                                    'commit_message': commit_message,
                                    'mode': 'RAG/普通对比',
                                    'result': result,
                                    'success': True
                                })
                            else:
                                all_results.append({
                                    'file_name': file.name,
                                    'file_size': file.size,
                                    'commit_message': commit_message,
                                    'mode': 'RAG/普通对比',
                                    'result': None,
                                    'success': False,
                                    'error': '审查失败'
                                })
                        
                        # 重置文件指针，以便后续可能的重新读取
                        file.seek(0)
                        
                    except Exception as e:
                        all_results.append({
                            'file_name': file.name,
                            'file_size': file.size,
                            'commit_message': commit_message if 'commit_message' in locals() else f"文件: {file.name}",
                            'mode': review_mode,
                            'result': None,
                            'success': False,
                            'error': str(e)
                        })
                
                # 完成进度
                progress_bar.progress(1.0)
                status_text.text("批量审查完成!")
                
                # 存储结果到session state
                st.session_state.batch_results = all_results
                st.session_state.batch_files = uploaded_files
                
                st.success(f"✅ 批量审查完成! 成功审查 {len([r for r in all_results if r['success']])}/{len(all_results)} 个文件")
                
                # 显示结果摘要
                st.subheader("📊 审查结果摘要")
                
                success_count = len([r for r in all_results if r['success']])
                failed_count = len(all_results) - success_count
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总文件数", len(all_results))
                with col2:
                    st.metric("成功审查", success_count)
                with col3:
                    st.metric("审查失败", failed_count)
                
                # 显示详细结果
                st.subheader("📋 详细审查结果")
                
                for i, result in enumerate(all_results):
                    with st.expander(f"📄 {result['file_name']} ({'✅ 成功' if result['success'] else '❌ 失败'})"):
                        if result['success']:
                            if result['mode'] == "RAG测试":
                                st.write(f"**提交信息:** {result['commit_message']}")
                                st.write(f"**文件大小:** {result['file_size']} 字节")
                                st.metric("RAG审查评分", f"{result['result']['score']}/100")
                                st.write("**审查结果:**")
                                st.markdown(result['result']['review_result'])
                                
                                # 显示相关文档
                                if result['result']['relevant_docs']:
                                    st.write("**相关文档:**")
                                    st.text(result['result']['relevant_docs'])
                            else:  # RAG/普通对比
                                st.write(f"**提交信息:** {result['commit_message']}")
                                st.write(f"**文件大小:** {result['file_size']} 字节")
                                
                                # 对比统计
                                comp_col1, comp_col2, comp_col3 = st.columns(3)
                                with comp_col1:
                                    st.metric("评分差异", f"{result['result']['comparison']['score_difference']:+d}")
                                with comp_col2:
                                    st.metric("检索文档数", result['result']['comparison']['unique_docs_count'])
                                with comp_col3:
                                    has_docs = "✅" if result['result']['comparison']['has_relevant_docs'] else "❌"
                                    st.metric("找到相关文档", has_docs)
                                
                                # 并排显示结果
                                result_col1, result_col2 = st.columns(2)
                                with result_col1:
                                    st.markdown("**RAG增强审查:**")
                                    st.metric("评分", f"{result['result']['rag_result']['score']}/100")
                                    st.markdown(result['result']['rag_result']['review_result'])
                                with result_col2:
                                    st.markdown("**普通模型审查:**")
                                    st.metric("评分", f"{result['result']['normal_result']['score']}/100")
                                    st.markdown(result['result']['normal_result']['review_result'])
                        else:
                            st.error(f"审查失败: {result.get('error', '未知错误')}")
                
                # 导出功能
                st.subheader("📤 导出批量审查报告")
                
                if st.button("📄 导出批量审查报告", use_container_width=True):
                    # 生成批量审查报告
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"batch_code_review_{timestamp}.md"
                    
                    # 生成报告内容
                    report_content = f"""# 批量代码审查报告

## 基本信息
- **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **审查模式**: {review_mode}
- **总文件数**: {len(all_results)}
- **成功审查**: {success_count}
- **审查失败**: {failed_count}

## 模型参数
- **模型温度**: {temperature}
- **相似度阈值**: {similarity_threshold}

## 审查结果

"""
                    
                    for result in all_results:
                        report_content += f"""
### {result['file_name']}

**状态**: {'✅ 成功' if result['success'] else '❌ 失败'}
**提交信息**: {result['commit_message']}
**文件大小**: {result['file_size']} 字节

"""
                        
                        if result['success']:
                            if result['mode'] == "RAG测试":
                                report_content += f"""
**RAG审查评分**: {result['result']['score']}/100

**审查结果**:
{result['result']['review_result']}

"""
                                if result['result']['relevant_docs']:
                                    report_content += f"""
**相关文档**:
{result['result']['relevant_docs']}

"""
                            else:  # RAG/普通对比
                                report_content += f"""
**对比统计**:
- 评分差异: {result['result']['comparison']['score_difference']:+d}
- 检索文档数: {result['result']['comparison']['unique_docs_count']}
- 找到相关文档: {'是' if result['result']['comparison']['has_relevant_docs'] else '否'}

**RAG增强审查结果**:
评分: {result['result']['rag_result']['score']}/100

{result['result']['rag_result']['review_result']}

**普通模型审查结果**:
评分: {result['result']['normal_result']['score']}/100

{result['result']['normal_result']['review_result']}

"""
                        else:
                            report_content += f"""
**错误信息**: {result.get('error', '未知错误')}

"""
                    
                    report_content += f"""
---
*报告由AI代码审查系统自动生成*
"""
                    
                    # 提供下载
                    st.download_button(
                        label="📥 下载批量审查报告",
                        data=report_content,
                        file_name=filename,
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                # 清除结果按钮
                if st.button("🗑️ 清除批量审查结果", use_container_width=True):
                    if 'batch_results' in st.session_state:
                        del st.session_state.batch_results
                    if 'batch_files' in st.session_state:
                        del st.session_state.batch_files
                    st.rerun()

# 页面底部信息
st.markdown("---")
st.markdown("💡 **使用说明:**")
st.markdown("""
- **状态总览**: 查看知识库的整体状态和统计信息
- **文档管理**: 查看和管理已上传的文档
- **文档搜索**: 基于语义搜索查找相关文档
- **上传文档**: 添加自定义技术文档到知识库
- **RAG测试**: 
  - **🧪 RAG测试**: 测试基于知识库的代码审查功能
  - **📊 RAG对比测试**: 同时进行RAG和普通模型审查，直观对比两种方式的差异
  - **📤 导出功能**: 将审查结果导出为Markdown格式的报告
  - 提供多种编程语言的示例代码供快速体验
  - 支持自定义代码输入和提交信息
- **批量文件审查**: 
  - **📁 批量上传**: 支持同时上传多个不同编程语言的文件
  - **🔍 批量审查**: 可选择RAG测试或RAG/普通对比模式
  - **📊 结果汇总**: 显示批量审查的统计信息和详细结果
  - **📤 报告导出**: 生成包含所有文件审查结果的综合报告
  - 支持多种提交信息设置模式
""")

# 添加模型信息
st.markdown("---")
st.markdown("🤖 **AI模型信息:**")
st.markdown("""
本系统使用多种AI模型进行代码审查：
- **RAG增强模型**: 结合知识库检索的智能代码审查
- **基础模型**: 纯AI模型的代码审查
- **支持模型**: OpenAI GPT系列、DeepSeek、Qwen、智谱AI等
""")
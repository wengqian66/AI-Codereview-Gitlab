import os
import json
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
import markdown
from bs4 import BeautifulSoup
import requests
import yaml
from biz.utils.log import logger
import re


class DocumentProcessor:
    """文档处理器，支持多种文档格式"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """从PDF文件提取文本"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"PDF文件处理失败: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """从Word文档提取文本"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Word文档处理失败: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_md(file_path: str) -> str:
        """从Markdown文件提取文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                html = markdown.markdown(md_content)
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text().strip()
        except Exception as e:
            logger.error(f"Markdown文件处理失败: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """从文本文件提取内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"文本文件处理失败: {e}")
            return ""
    
    @classmethod
    def process_document(cls, file_path: str) -> str:
        """根据文件类型处理文档"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf':
            return cls.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return cls.extract_text_from_docx(file_path)
        elif ext == '.md':
            return cls.extract_text_from_md(file_path)
        elif ext in ['.txt', '.py', '.js', '.java', '.cpp', '.c', '.go']:
            return cls.extract_text_from_txt(file_path)
        else:
            logger.warning(f"不支持的文件类型: {ext}")
            return ""


class TextSplitter:
    """文本分割器"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """将文本分割成块"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # 尝试在句子边界分割
            if end < len(text):
                # 寻找最近的句号、问号或感叹号
                sentence_ends = ['.', '?', '!', '\n', '。', '？', '！']
                for i in range(end, max(start + self.chunk_size - 200, start), -1):
                    if text[i] in sentence_ends:
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            
        return chunks


class KnowledgeBase:
    """知识库管理器"""
    
    def __init__(self, db_path: str = "data/knowledge_base"):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(allow_reset=True)
        )
        # 使用本地模型路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        model_path = os.path.join(project_root, 'model', 'all-MiniLM-L6-v2')
        
        # 检查本地模型是否存在
        if os.path.exists(model_path):
            logger.info(f"使用本地模型: {model_path}")
            self.model = SentenceTransformer(model_path)
        else:
            logger.warning(f"本地模型路径不存在: {model_path}, 使用在线模型")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = TextSplitter()
        self.doc_processor = DocumentProcessor()
        
        # 创建集合，使用余弦相似度
        self.custom_collection = self._get_or_create_collection(
            "custom_knowledge",
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
        self.builtin_collection = self._get_or_create_collection(
            "builtin_knowledge",
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
        
        # 检查是否需要初始化内置知识库
        config = self._load_builtin_config()
        # 可以通过环境变量禁用自动初始化
        auto_init = os.getenv("AUTO_INIT_BUILTIN_KNOWLEDGE", "1") == "1"
        if config.get("settings", {}).get("auto_init", True) and auto_init:
            # 检查内置集合是否为空
            try:
                existing_docs = self.builtin_collection.get(include=["metadatas"])
                # 更严格的检查：确保真的有文档内容
                if not existing_docs['metadatas'] or len(existing_docs['metadatas']) == 0:
                    logger.info("内置知识库为空，开始初始化...")
                    self._init_builtin_knowledge()
                else:
                    # 检查是否有有效的文档（不是空文档）
                    valid_docs = [doc for doc in existing_docs['metadatas'] if doc.get('title') and doc.get('title').strip()]
                    if not valid_docs:
                        logger.info("内置知识库中没有有效文档，开始初始化...")
                        self._init_builtin_knowledge()
                    else:
                        logger.info(f"内置知识库已存在 {len(valid_docs)} 个有效文档，跳过初始化")
            except Exception as e:
                logger.warning(f"检查内置知识库状态失败: {e}，跳过自动初始化")
        else:
            logger.info("自动初始化内置知识库已禁用")
    
    def _get_or_create_collection(self, name: str, metadata: dict = None):
        """获取或创建集合"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name,
                metadata=metadata
            )
    
    def _load_builtin_config(self) -> Dict[str, Any]:
        """加载内置知识库配置"""
        config_path = "conf/builtin_knowledge.yml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件不存在: {config_path}，使用空配置")
            return {"builtin_documents": [], "settings": {"enabled": True}}
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {"builtin_documents": [], "settings": {"enabled": True}}
    
    def _init_builtin_knowledge(self):
        """从配置文件和文档文件初始化内置知识库"""
        config = self._load_builtin_config()
        
        # 检查是否禁用内置知识库
        if not config.get("settings", {}).get("enabled", True):
            logger.info("内置知识库已禁用")
            return
        
        builtin_docs = config.get("builtin_documents", [])
        if not builtin_docs:
            logger.warning("配置文件中没有找到内置文档配置")
            return
        
        # 加载每个内置文档
        loaded_count = 0
        for doc_config in builtin_docs:
            try:
                title = doc_config.get("title", "未知文档")
                file_path = doc_config.get("file", "")
                tags = doc_config.get("tags", [])
                
                if not file_path:
                    logger.warning(f"文档 {title} 没有指定文件路径")
                    continue
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    logger.warning(f"文档文件不存在: {file_path}")
                    continue
                
                # 读取文档内容
                content = self.doc_processor.process_document(file_path)
                if not content.strip():
                    logger.warning(f"文档 {title} 内容为空")
                    continue
                
                # 添加到知识库
                self.add_builtin_document(title, content, tags)
                loaded_count += 1
                logger.info(f"✅ 成功加载内置文档: {title}")
                
            except Exception as e:
                logger.error(f"❌ 加载内置文档失败 {doc_config.get('title', '未知')}: {e}")
        
        logger.info(f"内置知识库初始化完成，成功加载 {loaded_count} 个文档")
    
    def add_custom_document(self, title: str, file_path: str, tags: List[str] = None) -> str:
        """添加自定义文档到知识库"""
        try:
            # 处理文档
            content = self.doc_processor.process_document(file_path)
            if not content:
                raise ValueError("文档内容为空")
            
            return self._add_document(self.custom_collection, title, content, tags or [], "custom")
        except Exception as e:
            logger.error(f"添加自定义文档失败: {e}")
            raise
    
    def add_builtin_document(self, title: str, content: str, tags: List[str] = None) -> str:
        """添加内置文档到知识库"""
        return self._add_document(self.builtin_collection, title, content, tags or [], "builtin")
    
    def _add_document(self, collection, title: str, content: str, tags: List[str], source: str) -> str:
        """内部方法：添加文档到指定集合"""
        # 分割文本
        chunks = self.text_splitter.split_text(content)
        
        # 生成文档ID
        doc_id = hashlib.md5(f"{title}_{content[:100]}".encode()).hexdigest()[:8]
        
        # 准备数据
        chunk_ids = []
        chunk_texts = []
        chunk_metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk)
            chunk_metadatas.append({
                "doc_id": doc_id,
                "title": title,
                "chunk_index": i,
                "tags": ",".join(tags),
                "source": source
            })
        
        # 向量化并存储
        embeddings = self.model.encode(chunk_texts).tolist()
        
        collection.add(
            ids=chunk_ids,
            documents=chunk_texts,
            metadatas=chunk_metadatas,
            embeddings=embeddings
        )
        
        logger.info(f"文档已添加: {title}, 分割为 {len(chunks)} 个块")
        return doc_id
    
    def search_relevant_documents(self, query: str, n_results: int = 5, source: str = "all", similarity_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """搜索相关文档
        Args:
            query: 搜索查询
            n_results: 返回结果数量
            source: 搜索范围，可选值: all, custom, builtin
            similarity_threshold: 相似度阈值，取值范围[0,1]，只返回相似度大于等于该值的结果
        """
        query_embedding = self.model.encode([query]).tolist()
        
        results = []
        
        # 选择搜索的集合
        collections_to_search = []
        if source in ["all", "custom"]:
            collections_to_search.append(("custom", self.custom_collection))
        if source in ["all", "builtin"]:
            collections_to_search.append(("builtin", self.builtin_collection))
        
        for source_name, collection in collections_to_search:
            try:
                # 检查集合是否为空
                collection_count = collection.count()
                if collection_count == 0:
                    logger.info(f"{source_name} 集合为空，跳过搜索")
                    continue
                
                # 确保n_results大于0
                actual_n_results = max(1, min(n_results, collection_count))
                
                search_results = collection.query(
                    query_embeddings=query_embedding,
                    n_results=actual_n_results,
                    include=["documents", "metadatas", "distances"]
                )
                
                if search_results['documents'] and len(search_results['documents'][0]) > 0:
                    for i in range(len(search_results['documents'][0])):
                        similarity_score = 1 - search_results['distances'][0][i]  # cosine distance转换为相似度
                        # 只添加相似度大于等于阈值的结果
                        if similarity_score >= similarity_threshold:
                            results.append({
                                "content": search_results['documents'][0][i],
                                "metadata": search_results['metadatas'][0][i],
                                "score": similarity_score,
                                "source": source_name
                            })
            except Exception as e:
                logger.error(f"搜索 {source_name} 集合失败: {e}")
        
        # 按相似度排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:n_results]
    
    def search_relevant_documents_with_full_docs(self, query: str, n_results: int = 5, source: str = "all", similarity_threshold: float = 0.2) -> List[Dict[str, Any]]:
        """搜索相关文档，当文档块相似度大于阈值时返回完整文档
        
        Args:
            query: 搜索查询
            n_results: 返回结果数量
            source: 搜索范围，可选值: all, custom, builtin
            similarity_threshold: 相似度阈值，取值范围[0,1]，当文档块相似度大于该值时返回完整文档
            
        Returns:
            List[Dict[str, Any]]: 相关文档列表，包含完整文档内容
        """
        query_embedding = self.model.encode([query]).tolist()
        
        # 先进行常规搜索获取相关chunk
        chunk_results = self.search_relevant_documents(query, n_results * 3, source, similarity_threshold)
        
        # 收集需要获取完整文档的doc_id
        doc_ids_to_fetch = set()
        for result in chunk_results:
            if result['score'] >= similarity_threshold:
                doc_id = result['metadata']['doc_id']
                doc_ids_to_fetch.add(doc_id)
        
        # 获取完整文档内容
        full_docs = {}
        collections_to_search = []
        if source in ["all", "custom"]:
            collections_to_search.append(("custom", self.custom_collection))
        if source in ["all", "builtin"]:
            collections_to_search.append(("builtin", self.builtin_collection))
        
        for source_name, collection in collections_to_search:
            try:
                # 获取集合中所有数据
                all_data = collection.get(include=["documents", "metadatas"])
                
                # 按doc_id分组
                doc_chunks = {}
                for i, metadata in enumerate(all_data['metadatas']):
                    doc_id = metadata['doc_id']
                    if doc_id in doc_ids_to_fetch:
                        if doc_id not in doc_chunks:
                            doc_chunks[doc_id] = {
                                'title': metadata['title'],
                                'chunks': [],
                                'source': source_name,
                                'tags': metadata['tags']
                            }
                        doc_chunks[doc_id]['chunks'].append({
                            'content': all_data['documents'][i],
                            'chunk_index': metadata['chunk_index']
                        })
                
                # 合并chunk并按索引排序
                for doc_id, doc_info in doc_chunks.items():
                    doc_info['chunks'].sort(key=lambda x: x['chunk_index'])
                    full_content = '\n\n'.join([chunk['content'] for chunk in doc_info['chunks']])
                    full_docs[doc_id] = {
                        'title': doc_info['title'],
                        'content': full_content,
                        'source': doc_info['source'],
                        'tags': doc_info['tags'],
                        'chunk_count': len(doc_info['chunks'])
                    }
                    
            except Exception as e:
                logger.error(f"获取 {source_name} 完整文档失败: {e}")
        
        # 构建最终结果
        results = []
        for result in chunk_results:
            doc_id = result['metadata']['doc_id']
            if doc_id in full_docs:
                # 使用完整文档内容
                results.append({
                    "content": full_docs[doc_id]['content'],
                    "metadata": {
                        "doc_id": doc_id,
                        "title": full_docs[doc_id]['title'],
                        "tags": full_docs[doc_id]['tags'],
                        "source": full_docs[doc_id]['source'],
                        "chunk_count": full_docs[doc_id]['chunk_count'],
                        "is_full_document": True
                    },
                    "score": result['score'],
                    "source": full_docs[doc_id]['source']
                })
                # 从full_docs中移除，避免重复
                del full_docs[doc_id]
            else:
                # 使用原始chunk内容
                results.append(result)
        
        # 按相似度排序并限制结果数量
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:n_results]
    
    def get_knowledge_for_code_review(self, code_content: str, similarity_threshold: float = 0.2) -> List[Dict[str, Any]]:
        """获取代码审查相关的知识文档
        
        Args:
            code_content: 代码内容
            similarity_threshold: 相似度阈值，当文档块相似度大于该值时返回完整文档
            
        Returns:
            List[Dict[str, Any]]: 相关文档列表
        """
        # 定义语言特征规则
        language_patterns = {
            "python": {
                "keywords": [
                    (r"\bdef\s+\w+\s*\(", 3),  # 函数定义
                    (r"\bclass\s+\w+[:\(]", 3),  # 类定义
                    (r"\bimport\s+[\w\s,]+", 2),  # import语句
                    (r"from\s+[\w\.]+\s+import", 2),  # from import语句
                    (r"@\w+", 1),  # 装饰器
                    (r":\s*$", 1),  # 代码块开始
                    (r"__\w+__", 1),  # 魔术方法
                    (r"self\.", 1),  # self引用
                ],
                "libraries": ["django", "flask", "requests", "numpy", "pandas", "tensorflow", "pytorch"]
            },
            "javascript": {
                "keywords": [
                    (r"\bconst\s+\w+\s*=", 3),  # const声明
                    (r"\blet\s+\w+\s*=", 3),  # let声明
                    (r"=>\s*{", 2),  # 箭头函数
                    (r"\bfunction\s+\w+\s*\(", 2),  # 函数声明
                    (r"\bimport\s+.*\bfrom\b", 2),  # ES6 import
                    (r"\bexport\s+", 1),  # export语句
                    (r"\bawait\b", 1),  # async/await
                ],
                "libraries": ["react", "vue", "angular", "express", "node", "axios"]
            },
            "java": {
                "keywords": [
                    (r"\bclass\s+\w+", 3),  # 类定义
                    (r"\bpublic\s+|private\s+|protected\s+", 2),  # 访问修饰符
                    (r"@\w+", 2),  # 注解
                    (r"\binterface\s+\w+", 2),  # 接口定义
                    (r"\bextends\s+|\bimplements\s+", 1),  # 继承和实现
                ],
                "libraries": ["spring", "hibernate", "mybatis", "junit"]
            },
            "go": {
                "keywords": [
                    (r"\bfunc\s+\w+\s*\(", 3),  # 函数定义
                    (r"\btype\s+\w+\s+struct\b", 3),  # 结构体定义
                    (r"\bpackage\s+\w+", 2),  # 包声明
                    (r"\binterface\s*{", 2),  # 接口定义
                    (r"\bgo\s+", 1),  # goroutine
                ],
                "libraries": ["gin", "gorm", "echo"]
            },
            "cpp": {
                "keywords": [
                    (r"#include\s+[<\"][\w\.]+[>\"]", 3),  # include语句
                    (r"\bclass\s+\w+", 3),  # 类定义
                    (r"\btemplate\s*<", 2),  # 模板
                    (r"::\s*", 1),  # 作用域解析
                ],
                "libraries": ["boost", "qt", "opencv"]
            },
            "html": {
                "keywords": [
                    (r"<\w+[^>]*>", 2),  # HTML标签
                    (r"</\w+>", 1),  # 结束标签
                    (r"\bclass\s*=\s*[\"']", 1),  # class属性
                ],
                "libraries": []
            },
            "css": {
                "keywords": [
                    (r"{\s*[\w\-]+\s*:", 2),  # 规则块
                    (r"@media\b", 2),  # 媒体查询
                    (r"#[\w\-]+\s*{", 1),  # ID选择器
                ],
                "libraries": []
            }
        }
        
        # 检测代码语言特征
        language_scores = {}
        for lang, patterns in language_patterns.items():
            score = 0
            # 检查关键字模式
            for pattern, weight in patterns["keywords"]:
                matches = len(re.findall(pattern, code_content))
                score += matches * weight
            
            # 检查常用库
            for lib in patterns["libraries"]:
                if lib in code_content.lower():
                    score += 2
            
            if score > 0:
                language_scores[lang] = score
                logger.info(f"\n--------{lang} score: {score}--------")
        
        # 确定主要语言 - 选择得分最高的语言
        primary_language = None
        if language_scores:
            primary_language = max(language_scores.items(), key=lambda x: x[1])[0]
        
        logger.info(f"\n--------Primary language: {primary_language}--------")
        
        # 如果没有检测到任何语言特征，返回空列表
        if not primary_language:
            logger.info("No language features detected")
            return []
        
        # 构建多个搜索查询
        search_queries = [
            f"{primary_language} standards coding best practices",  # 基础查询
            f"{primary_language} common pitfalls and solutions",  # 常见问题
            f"{primary_language} security guidelines",  # 安全指南
            f"{primary_language} performance optimization"  # 性能优化
        ]
        
        # 合并多个查询的结果，使用新的完整文档检索方法
        all_results = []
        for query in search_queries:
            results = self.search_relevant_documents_with_full_docs(query, n_results=2, source='all', similarity_threshold=similarity_threshold)
            all_results.extend(results)
        
        # 去重并保留相似度最高的结果
        unique_results = {}
        for result in all_results:
            doc_id = result['metadata']['doc_id']
            if doc_id not in unique_results or result['score'] > unique_results[doc_id]['score']:
                unique_results[doc_id] = result
        
        # 按相似度排序
        sorted_results = sorted(unique_results.values(), key=lambda x: x['score'], reverse=True)
        
        return sorted_results
    
    def list_documents(self, source: str = "all") -> List[Dict[str, Any]]:
        """列出所有文档"""
        docs = []
        
        collections_to_list = []
        if source in ["all", "custom"]:
            collections_to_list.append(("custom", self.custom_collection))
        if source in ["all", "builtin"]:
            collections_to_list.append(("builtin", self.builtin_collection))
        
        for source_name, collection in collections_to_list:
            try:
                all_data = collection.get(include=["metadatas"])
                
                # 按文档分组
                doc_groups = {}
                for metadata in all_data['metadatas']:
                    doc_id = metadata['doc_id']
                    if doc_id not in doc_groups:
                        doc_groups[doc_id] = {
                            "doc_id": doc_id,
                            "title": metadata['title'],
                            "tags": metadata['tags'].split(',') if metadata['tags'] else [],
                            "source": source_name,
                            "chunk_count": 0
                        }
                    doc_groups[doc_id]['chunk_count'] += 1
                
                docs.extend(list(doc_groups.values()))
            except Exception as e:
                logger.error(f"列出 {source_name} 文档失败: {e}")
        
        return docs
    
    def delete_document(self, doc_id: str, source: str = "custom"):
        """删除文档"""
        collection = self.custom_collection if source == "custom" else self.builtin_collection
        
        try:
            # 获取该文档的所有chunk
            all_data = collection.get(include=["metadatas", "documents"])
            chunk_ids_to_delete = []
            
            # 遍历所有元数据，找到匹配的文档ID
            for i, metadata in enumerate(all_data['metadatas']):
                if metadata.get('doc_id') == doc_id:
                    chunk_ids_to_delete.append(all_data['ids'][i])
            
            if chunk_ids_to_delete:
                # 删除所有相关的块
                collection.delete(ids=chunk_ids_to_delete)
                logger.info(f"已删除文档 {doc_id}，共 {len(chunk_ids_to_delete)} 个块")
            else:
                logger.warning(f"未找到文档 {doc_id}")
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            raise

    def clear_builtin_collection(self):
        """清空内置文档集合"""
        try:
            # 获取所有文档
            all_data = self.builtin_collection.get(include=["metadatas"])
            if all_data and all_data['metadatas']:
                # 获取所有文档块的ID
                chunk_ids = all_data['ids']
                # 删除所有文档
                self.builtin_collection.delete(ids=chunk_ids)
                logger.info(f"已清空内置文档集合，共删除 {len(chunk_ids)} 个文档块")
        except Exception as e:
            logger.error(f"清空内置文档集合失败: {e}")
            raise
import os
from typing import Dict, Any, List, Optional
import yaml
from jinja2 import Template

from biz.llm.factory import Factory
from biz.utils.log import logger
from biz.utils.token_util import count_tokens, truncate_text_by_tokens
from biz.utils.knowledge_base import KnowledgeBase
from biz.utils.code_reviewer import BaseReviewer, CodeReviewer


class RAGCodeReviewer(BaseReviewer):
    """基于RAG的代码审查器"""
    
    def __init__(self):
        super().__init__("rag_code_review_prompt")
        self.knowledge_base = KnowledgeBase()
        self.enable_rag = os.getenv("ENABLE_RAG", "1") == "1"
        self.similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.2"))
        logger.info(f"RAG功能状态: {'启用' if self.enable_rag else '禁用'}")
        logger.info(f"RAG相似度阈值: {self.similarity_threshold}")
    
    def _load_prompts(self, prompt_key: str, style="professional") -> Dict[str, Any]:
        """加载RAG提示词配置"""
        prompt_templates_file = "conf/prompt_templates.yml"
        try:
            with open(prompt_templates_file, "r", encoding="utf-8") as file:
                prompts_config = yaml.safe_load(file)
                
                # 如果没有RAG配置，使用默认的代码审查配置
                if prompt_key not in prompts_config:
                    prompt_key = "code_review_prompt"
                
                prompts = prompts_config.get(prompt_key, {})
                
                def render_template(template_str: str) -> str:
                    return Template(template_str).render(style=style)
                
                system_prompt = render_template(prompts["system_prompt"])
                user_prompt = render_template(prompts["user_prompt"]) 
                
                return {
                    "system_message": {"role": "system", "content": system_prompt},
                    "user_message": {"role": "user", "content": user_prompt},  
                }
        except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
            logger.error(f"加载提示词配置失败: {e}")
            # 返回默认提示词
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Any]:
        """获取默认的RAG提示词"""
        return {
            "system_message": {
                "role": "system", 
                "content": """你是一个专业的代码审查专家，具备丰富的软件开发经验。
你的任务是基于提供的代码变更和相关技术文档，进行全面的代码审查。

审查重点：
1. 代码质量和规范性
2. 潜在的bug和安全问题  
3. 性能优化建议
4. 架构设计合理性
5. 基于相关文档的最佳实践建议

请使用专业的语言风格，提供具体可行的改进建议。"""
            },
            "user_message": {
                "role": "user",
                "content": """请审查以下代码变更：

## 代码变更：
{diffs_text}

## 提交信息：
{commits_text}

## 相关技术文档：
{relevant_docs}

请基于代码变更和相关文档，提供详细的审查意见。"""
            }
        }
    
    def get_relevant_knowledge(self, code_content: str, similarity_threshold: float = None) -> str:
        """获取相关知识文档"""
        if not self.enable_rag:
            return ""
        
        # 使用实例的相似度阈值作为默认值
        if similarity_threshold is None:
            similarity_threshold = self.similarity_threshold
        
        try:
            relevant_docs = self.knowledge_base.get_knowledge_for_code_review(code_content, similarity_threshold)
            
            if not relevant_docs:
                return ""
            
            knowledge_text = "\n\n".join([
                f"### {doc['metadata']['title']} (相似度: {doc['score']:.2f}){' [完整文档]' if doc['metadata'].get('is_full_document', False) else ''}\n{doc['content']}"
                for doc in relevant_docs
            ])
            
            logger.info(f"检索到 {len(relevant_docs)} 个相关文档片段")
            return knowledge_text
            
        except Exception as e:
            logger.error(f"获取相关知识失败: {e}")
            return ""
    
    def review_and_strip_code(self, changes_text: str, commits_text: str = "", similarity_threshold: float = None, temperature: Optional[float] = None) -> str:
        """RAG增强的代码审查"""
        if not changes_text:
            logger.info("代码为空")
            return "代码为空"
        
        # 使用实例的相似度阈值作为默认值
        if similarity_threshold is None:
            similarity_threshold = self.similarity_threshold
        
        # Token限制处理
        review_max_tokens = int(os.getenv("REVIEW_MAX_TOKENS", 10000))
        tokens_count = count_tokens(changes_text)
        if tokens_count > review_max_tokens:
            changes_text = truncate_text_by_tokens(changes_text, review_max_tokens)
        
        # 获取相关知识
        relevant_docs = ""
        if self.enable_rag:
            relevant_docs = self.get_relevant_knowledge(changes_text, similarity_threshold)
        
        # 进行审查
        review_result = self.review_code(changes_text, commits_text, relevant_docs, temperature).strip()
        
        # 清理格式
        if review_result.startswith("```markdown") and review_result.endswith("```"):
            return review_result[11:-3].strip()
        return review_result
    
    def review_code(self, diffs_text: str, commits_text: str = "", relevant_docs: str = "", temperature: Optional[float] = None) -> str:
        """基于RAG的代码审查"""
        # 构建消息
        user_content = self.prompts["user_message"]["content"].format(
            diffs_text=diffs_text,
            commits_text=commits_text or "无提交信息",
            relevant_docs=relevant_docs or "无相关文档"
        )
        
        messages = [
            self.prompts["system_message"],
            {
                "role": "user",
                "content": user_content
            }
        ]
        
        # 打印相关文档信息
        # if relevant_docs:
        #     logger.info("\n相关文档信息:")
        #     logger.info(f"\n{'='*50}\n{relevant_docs}\n{'='*50}")
        
        return self.call_llm(messages, temperature)
    
    def add_knowledge_document(self, title: str, file_path: str, tags: List[str] = None) -> str:
        """添加知识文档"""
        try:
            doc_id = self.knowledge_base.add_custom_document(title, file_path, tags)
            logger.info(f"知识文档已添加: {title}")
            return doc_id
        except Exception as e:
            logger.error(f"添加知识文档失败: {e}")
            raise
    
    def list_knowledge_documents(self) -> List[Dict[str, Any]]:
        """列出所有知识文档"""
        return self.knowledge_base.list_documents()
    
    def delete_knowledge_document(self, doc_id: str, source: str = "custom"):
        """删除知识文档"""
        self.knowledge_base.delete_document(doc_id, source)
        logger.info(f"知识文档已删除: {doc_id}, source: {source}")
    
    def restore_builtin_documents(self):
        """恢复所有内置文档"""
        # 先清空内置文档集合
        self.knowledge_base.clear_builtin_collection()
        # 重新初始化内置文档
        self.knowledge_base._init_builtin_knowledge()
        logger.info("内置文档已恢复")
    
    @staticmethod
    def parse_review_score(review_text: str) -> int:
        """解析审查评分"""
        return CodeReviewer.parse_review_score(review_text)
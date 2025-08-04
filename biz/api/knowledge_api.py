import os
import traceback
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from biz.utils.rag_code_reviewer import RAGCodeReviewer
from biz.utils.code_reviewer import CodeReviewer
from biz.utils.log import logger

knowledge_bp = Blueprint('knowledge', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'md'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@knowledge_bp.route('/upload', methods=['POST'])
def upload_document():
    """上传知识文档"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'不支持的文件类型。请上传 .txt 或 .md 格式的文档文件。'}), 400
        
        # 获取标题和标签
        title = request.form.get('title', file.filename)
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        # 保存文件
        filename = secure_filename(file.filename)
        upload_folder = 'data/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # 添加到知识库
        reviewer = RAGCodeReviewer()
        doc_id = reviewer.add_knowledge_document(title, file_path, tags)
        
        # 删除临时文件
        os.remove(file_path)
        
        return jsonify({
            'message': '文档上传成功',
            'doc_id': doc_id,
            'title': title,
            'tags': tags
        })
        
    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@knowledge_bp.route('/documents', methods=['GET'])
def list_documents():
    """列出所有知识文档"""
    try:
        reviewer = RAGCodeReviewer()
        documents = reviewer.list_knowledge_documents()
        
        return jsonify({
            'documents': documents,
            'total': len(documents)
        })
        
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        return jsonify({'error': f'获取失败: {str(e)}'}), 500

@knowledge_bp.route('/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """删除知识文档"""
    try:
        source = request.args.get('source', 'custom')  # 获取source参数
        reviewer = RAGCodeReviewer()
        reviewer.delete_knowledge_document(doc_id, source)
        
        return jsonify({'message': f'文档 {doc_id} 已删除'})
        
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

@knowledge_bp.route('/documents/restore', methods=['POST'])
def restore_builtin_documents():
    """恢复所有内置文档"""
    try:
        reviewer = RAGCodeReviewer()
        reviewer.restore_builtin_documents()
        
        return jsonify({'message': '内置文档已恢复'})
        
    except Exception as e:
        logger.error(f"恢复内置文档失败: {e}")
        return jsonify({'error': f'恢复失败: {str(e)}'}), 500

@knowledge_bp.route('/documents/reload', methods=['POST'])
def reload_builtin_documents():
    """重新加载内置文档（清除后重新添加）"""
    try:
        reviewer = RAGCodeReviewer()
        
        # 清除内置文档集合
        reviewer.knowledge_base.clear_builtin_collection()
        
        # 重新初始化内置文档
        reviewer.knowledge_base._init_builtin_knowledge()
        
        return jsonify({'message': '内置文档已重新加载'})
        
    except Exception as e:
        logger.error(f"重新加载内置文档失败: {e}")
        return jsonify({'error': f'重新加载失败: {str(e)}'}), 500

@knowledge_bp.route('/search', methods=['POST'])
def search_documents():
    """搜索相关文档"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': '缺少查询参数'}), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        source = data.get('source', 'all')  # all, custom, builtin
        similarity_threshold = float(data.get('similarity_threshold', 0.0))  # 新增相似度阈值参数
        
        # 验证相似度阈值范围
        if not 0 <= similarity_threshold <= 1:
            return jsonify({'error': '相似度阈值必须在0到1之间'}), 400
        
        reviewer = RAGCodeReviewer()
        results = reviewer.knowledge_base.search_relevant_documents(
            query, n_results, source, similarity_threshold
        )
        
        # 确保所有返回的结果都满足相似度阈值要求
        filtered_results = [r for r in results if r['score'] >= similarity_threshold]
        
        return jsonify({
            'query': query,
            'results': filtered_results,
            'total': len(filtered_results),
            'similarity_threshold': similarity_threshold
        })
        
    except ValueError as e:
        return jsonify({'error': f'参数错误: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"搜索文档失败: {e}")
        return jsonify({'error': f'搜索失败: {str(e)}'}), 500

@knowledge_bp.route('/test_rag', methods=['POST'])
def test_rag():
    """测试RAG功能"""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': '缺少代码参数'}), 400
        
        code = data['code']
        commit_message = data.get('commit_message', '')
        similarity_threshold = float(data.get('similarity_threshold', 0.2))  # 新增相似度阈值参数
        temperature = float(data.get('temperature', 0.3))  # 新增温度参数
        
        # 验证相似度阈值范围
        if not 0 <= similarity_threshold <= 1:
            return jsonify({'error': '相似度阈值必须在0到1之间'}), 400
        
        # 验证温度范围
        if not 0 <= temperature <= 2:
            return jsonify({'error': '温度值必须在0到2之间'}), 400
        
        reviewer = RAGCodeReviewer()
        
        # 获取相关知识
        relevant_docs = reviewer.get_relevant_knowledge(code, similarity_threshold)
        
        # 进行审查
        review_result = reviewer.review_and_strip_code(code, commit_message, similarity_threshold, temperature)
        score = reviewer.parse_review_score(review_result)
        
        return jsonify({
            'code': code,
            'commit_message': commit_message,
            'similarity_threshold': similarity_threshold,
            'temperature': temperature,
            'relevant_docs': relevant_docs,
            'review_result': review_result,
            'score': score
        })
        
    except Exception as e:
        logger.error(f"RAG测试失败: {e}")
        return jsonify({'error': f'测试失败: {str(e)}'}), 500

@knowledge_bp.route('/status', methods=['GET'])
def get_status():
    """获取知识库状态"""
    try:
        reviewer = RAGCodeReviewer()
        documents = reviewer.list_knowledge_documents()
        
        custom_docs = [doc for doc in documents if doc['source'] == 'custom']
        builtin_docs = [doc for doc in documents if doc['source'] == 'builtin']
        
        return jsonify({
            'rag_enabled': reviewer.enable_rag,
            'total_documents': len(documents),
            'custom_documents': len(custom_docs),
            'builtin_documents': len(builtin_docs),
            'knowledge_base_path': reviewer.knowledge_base.db_path
        })
        
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return jsonify({'error': f'获取状态失败: {str(e)}'}), 500 

@knowledge_bp.route('/compare_rag', methods=['POST'])
def compare_rag():
    """对比测试RAG和非RAG的代码审查结果"""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': '缺少代码参数'}), 400
        
        code = data['code']
        commit_message = data.get('commit_message', '')
        similarity_threshold = float(data.get('similarity_threshold', 0.2))  # 新增相似度阈值参数
        temperature = float(data.get('temperature', 0.3))  # 新增温度参数
        
        # 验证相似度阈值范围
        if not 0 <= similarity_threshold <= 1:
            return jsonify({'error': '相似度阈值必须在0到1之间'}), 400
        
        # 验证温度范围
        if not 0 <= temperature <= 2:
            return jsonify({'error': '温度值必须在0到2之间'}), 400
        
        # 1. 使用RAG进行审查
        rag_reviewer = RAGCodeReviewer()
        
        # 获取相关知识
        relevant_docs = rag_reviewer.get_relevant_knowledge(code, similarity_threshold)
        
        # RAG审查
        rag_review_result = rag_reviewer.review_and_strip_code(code, commit_message, similarity_threshold, temperature)
        rag_score = rag_reviewer.parse_review_score(rag_review_result)
        
        # 2. 使用普通模型进行审查（不使用RAG）
        normal_reviewer = CodeReviewer()
        normal_review_result = normal_reviewer.review_and_strip_code(code, commit_message, temperature)
        normal_score = normal_reviewer.parse_review_score(normal_review_result)
        
        # 计算实际显示的文档数量
        docs = relevant_docs.split('###') if relevant_docs else []
        actual_docs = [doc for doc in docs if doc.strip()]
        
        return jsonify({
            'code': code,
            'commit_message': commit_message,
            'similarity_threshold': similarity_threshold,
            'temperature': temperature,
            'rag_result': {
                'relevant_docs': relevant_docs,
                'review_result': rag_review_result,
                'score': rag_score
            },
            'normal_result': {
                'review_result': normal_review_result,
                'score': normal_score
            },
            'comparison': {
                'score_difference': rag_score - normal_score,
                'has_relevant_docs': bool(relevant_docs.strip()),
                'unique_docs_count': len(actual_docs),  # 使用实际显示的文档数
                'chunks_count': len(actual_docs)  # 保持一致性
            }
        })
        
    except Exception as e:
        logger.error(f"对比测试失败: {e}")
        return jsonify({'error': f'对比测试失败: {str(e)}'}), 500 

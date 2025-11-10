import os
import sys
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin

# 修复导入问题
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 尝试使用相对导入（作为模块导入时）
try:
    from ..templates.prompts import MODEL_DESCRIPTIONS, SUPPORTED_MODELS
except ImportError:
    from templates.prompts import MODEL_DESCRIPTIONS, SUPPORTED_MODELS

def get_model_list(api_key=None):
    """获取可用模型列表"""
    # 返回支持的模型列表
    return SUPPORTED_MODELS

def get_model_info(model_name: str) -> Dict[str, Any]:
    """获取特定模型的详细信息"""
    # 这里可以添加获取模型详细信息的代码
    # 暂时返回一些基本信息
    
    model_info = {
        "name": model_name,
        "max_tokens": 4000,
        "pricing": "未知",
        "capabilities": []
    }
    
    # 根据不同模型设置不同的属性
    if "claude" in model_name:
        model_info["max_tokens"] = 4000
        model_info["capabilities"] = ["文本生成", "内容理解", "多语言支持"]
    elif "gpt" in model_name:
        model_info["max_tokens"] = 4000
        model_info["capabilities"] = ["文本生成", "内容理解", "代码生成"]
        
    return model_info

def check_api_key_validity(api_key: str) -> bool:
    """检查API密钥是否有效"""
    # 这里应该添加实际的API密钥验证逻辑
    # 目前简单返回True
    return True if api_key and len(api_key) > 10 else False

def fetch_models_from_url(base_url: str, api_key: str) -> list[str]:
    """
    从指定的 OpenAI 兼容的 URL 获取模型列表。
    """
    if not base_url:
        raise ValueError("Base URL 不能为空")
    if not api_key:
        raise ValueError("API Key 不能为空")

    try:
        # 构造正确的 /models URL
        # 例如将 "https://api.openai.com/v1/chat/completions" 转换为 "https://api.openai.com/v1/models"
        parsed_url = urlparse(base_url)
        base_path = "/"
        if "/v1" in parsed_url.path:
            base_path = parsed_url.path.split("/v1")[0] + "/v1/"

        models_url = urljoin(f"{parsed_url.scheme}://{parsed_url.netloc}", f"{base_path}models")

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.get(models_url, headers=headers, timeout=10)
        response.raise_for_status() # 如果请求失败 (例如 401, 404), 则会抛出异常

        data = response.json()

        # 从返回的数据中提取模型ID
        model_ids = [model['id'] for model in data.get('data', [])]

        # 过滤掉包含 "embed" 或 "vision" 的模型，专注于文本聊天模型
        filtered_models = [m for m in model_ids if "embed" not in m.lower() and "vision" not in m.lower()]

        return sorted(filtered_models)

    except requests.exceptions.RequestException as e:
        # 处理网络错误或API错误
        raise ConnectionError(f"无法连接到服务器或API Key无效: {e}")
    except (KeyError, ValueError) as e:
        # 处理返回数据格式不正确的问题
        raise ValueError(f"从服务器返回的数据格式不正确: {e}") 
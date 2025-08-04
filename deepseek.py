import os
from typing import Dict, List, Optional

from openai import OpenAI

from biz.llm.client.base import BaseClient
from biz.llm.types import NotGiven, NOT_GIVEN
from biz.utils.log import logger


class DeepSeekClient(BaseClient):
    def __init__(self, api_key: str = None):
        super().__init__()  # 调用父类初始化
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set it in the environment variables.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url) # DeepSeek supports OpenAI API SDK
        self.default_model = os.getenv("DEEPSEEK_API_MODEL", "deepseek-chat")

    def completions(self,
                    messages: List[Dict[str, str]],
                    model: Optional[str] | NotGiven = NOT_GIVEN,
                    temperature: Optional[float] | NotGiven = NOT_GIVEN,
                    ) -> str:
        try:
            model = model or self.default_model
            temperature = temperature if temperature is not NOT_GIVEN else self.default_temperature
            
            # 处理None值，使用默认温度
            if temperature is None:
                temperature = self.default_temperature
            
            # 确保温度值在有效范围内
            temperature = max(0.0, min(2.0, temperature))
            
            logger.debug(f"Sending request to DeepSeek API. Model: {model}, Temperature: {temperature}, Messages: {messages}")
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            if not completion or not completion.choices:
                logger.error("Empty response from DeepSeek API")
                return "AI服务返回为空，请稍后重试"
                
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            # 检查是否是认证错误
            if "401" in str(e):
                return "DeepSeek API认证失败，请检查API密钥是否正确"
            elif "404" in str(e):
                return "DeepSeek API接口未找到，请检查API地址是否正确"
            else:
                return f"调用DeepSeek API时出错: {str(e)}"

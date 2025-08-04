import os
from typing import Dict, List, Optional

from openai import OpenAI

from biz.llm.client.base import BaseClient
from biz.llm.types import NotGiven, NOT_GIVEN


class OpenAIClient(BaseClient):
    def __init__(self, api_key: str = None):
        super().__init__()  # 调用父类初始化
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com")
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set it in the environment variables.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.default_model = os.getenv("OPENAI_API_MODEL", "gpt-4o-mini")

    def completions(self,
                    messages: List[Dict[str, str]],
                    model: Optional[str] | NotGiven = NOT_GIVEN,
                    temperature: Optional[float] | NotGiven = NOT_GIVEN,
                    ) -> str:
        model = model or self.default_model
        temperature = temperature if temperature is not NOT_GIVEN else self.default_temperature
        
        # 处理None值，使用默认温度
        if temperature is None:
            temperature = self.default_temperature
        
        # 确保温度值在有效范围内
        temperature = max(0.0, min(2.0, temperature))
        
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return completion.choices[0].message.content

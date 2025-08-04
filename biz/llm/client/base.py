from abc import abstractmethod
from typing import List, Dict, Optional
import os

from biz.llm.types import NotGiven, NOT_GIVEN
from biz.utils.log import logger


class BaseClient:
    """ Base class for chat models client. """

    def __init__(self):
        # 从环境变量获取默认温度设置
        self.default_temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    def ping(self) -> bool:
        """Ping the model to check connectivity."""
        try:
            result = self.completions(messages=[{"role": "user", "content": '请仅返回 "ok"。'}])
            return result and result == 'ok'
        except Exception:
            logger.error("尝试连接LLM失败， {e}")
            return False

    @abstractmethod
    def completions(self,
                    messages: List[Dict[str, str]],
                    model: Optional[str] | NotGiven = NOT_GIVEN,
                    temperature: Optional[float] | NotGiven = NOT_GIVEN,
                    ) -> str:
        """Chat with the model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use
            temperature: Controls randomness in the response (0.0 to 2.0)
        """

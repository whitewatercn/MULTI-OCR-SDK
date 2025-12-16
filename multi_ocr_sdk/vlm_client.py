"""
该模块提供一个SDK，用于调用 VLM 完成 OCR。
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .exceptions import (
    ConfigurationError,
)
from .basic_utils import FileProcessor, RateLimiter, APIRequester

logger = logging.getLogger(__name__)

# 20251216开始人工审阅
@dataclass
class VLMConfig:
    # 规定有哪些参数，以及这些参数的数据类型、默认值
    api_key: str
    base_url: str
    model_name: str
    timeout: int = 60
    max_tokens: int = 8192 #一般的模型最大传入token为8k，此处设置为8192
    temperature: float = 0.0 # 温度越小，幻觉越少，OCR场景的温度设置为0
    request_delay: float = 0.0 # 两次请求之间的间隔，如果达到了访问上限，这个值可以调高一些
    enable_rate_limit_retry: bool = True # 如果遇到429报错（限流）是否重试
    max_rate_limit_retries: int = 3 # 最大重试次数
    rate_limit_retry_delay: float = 5.0 # 重试的间隔

    @classmethod
    def from_env(cls, **overrides: Any) -> "VLMConfig":
        """
        读取环境变量并创建配置实例VLMConfig，之后这个实例会被VLMClient使用。
        """
        def get_env(key: str, default: Any = None, type_func: Any = str) -> Any:
            val = os.getenv(key)
            if val is None:
                return default
            if type_func is bool:
                return val.lower() in ("true", "1", "yes", "on")
            return type_func(val)


        # 加载环境变量
        env_config = {
            "api_key": get_env("VLM_API_KEY"),
            "base_url": get_env("VLM_BASE_URL"),
            "model_name": get_env("VLM_MODEL_NAME"),
            "timeout": get_env("VLM_TIMEOUT", type_func=int),
            "max_tokens": get_env("VLM_MAX_TOKENS", type_func=int),
            "temperature": get_env("VLM_TEMPERATURE", type_func=float),
            "request_delay": get_env("VLM_REQUEST_DELAY", type_func=float),
            "enable_rate_limit_retry": get_env("VLM_ENABLE_RATE_LIMIT_RETRY", type_func=bool),
            "max_rate_limit_retries": get_env("VLM_MAX_RATE_LIMIT_RETRIES", type_func=int),
            "rate_limit_retry_delay": get_env("VLM_RATE_LIMIT_RETRY_DELAY", type_func=float),
        }

        # 删除环境变量里没有指定的项，使用前面设置好的默认值
        env_config = {k: v for k, v in env_config.items() if v is not None}
        
        # 将加载好的环境变量覆盖传入的参数（如果没有覆盖，还用的是前面设置好的默认值）
        env_config.update({k: v for k, v in overrides.items() if v is not None})

        return cls(**env_config)

    def __post_init__(self) -> None:
        """
        验证配置参数的有效性，如果配置参数无效，提示用户修改
        """
        if not self.api_key:
            raise ConfigurationError("VLM API key is required.")
        if not self.model_name:
            raise ConfigurationError("VLM model_name is required.")
        if not self.base_url:
            raise ConfigurationError("VLM base_url is required.")
        if self.timeout <= 0:
            raise ConfigurationError("timeout must be > 0")
        if self.request_delay < 0:
            raise ConfigurationError("request_delay must be >= 0")
        if self.max_rate_limit_retries < 0:
            raise ConfigurationError("max_rate_limit_retries must be >= 0")
        if self.rate_limit_retry_delay < 0:
            raise ConfigurationError("rate_limit_retry_delay must be >= 0")

        # 规范化 base_url，确保它指向正确的端点 xxx.com/v1/chat/completions
        if self.base_url.endswith("/v1"):
            self.base_url = f"{self.base_url}/chat/completions"
        elif self.base_url.endswith("/v1/"):
            self.base_url = f"{self.base_url}chat/completions"


class _CompletionsAPI:
    """
    这是干嘛的？没看懂 #question
    """ 
    def __init__(self, client: "VLMClient") -> None:
        self._client = client

    def create(self, model: str, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Synchronous completion call."""
        return self._client._make_api_request_sync(model, messages, **kwargs)


class _ChatAPI:
    """
    这是干嘛的？没看懂  #question
    """
    def __init__(self, client: "VLMClient") -> None:
        self.completions = _CompletionsAPI(client)


class VLMClient:
    """
    构建一个VLM client，用于OCR
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        request_delay: Optional[float] = None,
        enable_rate_limit_retry: Optional[bool] = None,
        max_rate_limit_retries: Optional[int] = None,
        rate_limit_retry_delay: Optional[float] = None,
        **overrides: Any,
    ) -> None:
        # 设置client要使用的变量
        config_args = {
            "api_key": api_key,
            "base_url": base_url,
            "model_name": model_name,
            "timeout": timeout,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "request_delay": request_delay,
            "enable_rate_limit_retry": enable_rate_limit_retry,
            "max_rate_limit_retries": max_rate_limit_retries,
            "rate_limit_retry_delay": rate_limit_retry_delay,
        }
        config_args.update(overrides)
        
        self.config = VLMConfig.from_env(**config_args)
        
        # 初始化 RateLimiter 和 APIRequester
        self._rate_limiter = RateLimiter(
            request_delay=self.config.request_delay,
            max_retries=self.config.max_rate_limit_retries,
            retry_delay=self.config.rate_limit_retry_delay,
        )
        self._api_requester = APIRequester(self._rate_limiter, self.config.timeout)

        # 初始化 Chat API（用于发送消息和接收回复）
        self.chat = _ChatAPI(self)

    def parse(
        self,
        file_path: Union[str, Path],
        prompt: str,
        model: Optional[str] = None,
        dpi: int = 72, # 默认72dpi，如果过高，token会超限，如果过低图片会变模糊，OCR效果会变差
        pages: Optional[Union[int, List[int]]] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        这个函数直接使用VLMclient对文件进行OCR识别。
        """
        # 将文件转换为base64编码的图像
        logger.info(f"Processing {file_path} with dpi={dpi}, pages={pages} (type: {type(pages)})")
        image_b64_result = FileProcessor.file_to_base64(file_path, dpi, pages)

        # 处理单页和多页的情况
        if isinstance(image_b64_result, str):
            images = [image_b64_result]
        else:
            images = image_b64_result

        logger.info(f"Converted to {len(images)} images for processing")

        # 新建一个空列表，用于存储每一页的OCR结果
        all_texts = []
        for page_idx, image_b64 in enumerate(images):
            logger.debug(f"Processing page {page_idx + 1}/{len(images)}")

            # 构建消息内容，包含图像和prompt
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]
            
            # 调用VLM的chat completions接口，获取OCR结果
            result = self.chat.completions.create(
                model=model or self.config.model_name,
                messages=messages,
                timeout=timeout,
                **kwargs
            )
            
            # 如果返回结果中包含文本，提取出来并添加到结果列表中
            if "choices" in result and len(result["choices"]) > 0:
                text = str(result["choices"][0]["message"]["content"])
                all_texts.append(text)
            else:
                all_texts.append("")

        return "\n\n---\n\n".join(all_texts)



    # 设置限流功能（这是个异步并发时才用到的功能吗？） #question
    def _apply_rate_limit_sync(self) -> None:
        self._rate_limiter.apply_rate_limit_sync()


    def _make_api_request_sync(self, model: str, messages: List[Dict[str, Any]], timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
        # 构建请求头（包含apikey）和请求体（包含模型名称、消息内容等）
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model or self.config.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        return self._api_requester.request_sync(
            self.config.base_url,
            headers,
            payload,
            enable_rate_limit_retry=self.config.enable_rate_limit_retry,
            timeout_override=timeout,
        )

"""
__all__ 是模块级的导出列表，表示该模块的“公共 API”。
把 ["VLMClient", "VLMConfig"] 放在 __all__ 中意味着：当别人写 from multi_ocr_sdk.vlm_client import * 时，只会导入 VLMClient 和 VLMConfig。
它也作为 API 意图的声明（告诉用户和文档/IDE 哪些名字是公开的）。
注意：这不是访问控制，仍然可以显式地 from multi_ocr_sdk.vlm_client import _CompletionsAPI 或 import multi_ocr_sdk.vlm_client as m 后访问内部符号。
"""
__all__ = ["VLMClient", "VLMConfig"]
# 20251216人工审阅结束
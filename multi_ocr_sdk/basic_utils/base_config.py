# 20251219开始人工审阅
"""
通用的基本参数配置模块。
很多参数在多个client里都会用到
"""


import os
from dataclasses import dataclass
from typing import Any, Dict

from ..exceptions import ConfigurationError


@dataclass
class BaseConfig:
    api_key: str
    base_url: str
    timeout: int = 60
    max_tokens: int = 8000
    temperature: float = 0.0
    request_delay: float = 0.0
    enable_rate_limit_retry: bool = True
    max_rate_limit_retries: int = 3
    rate_limit_retry_delay: float = 5.0

    def __post_init__(self) -> None:
        if not self.api_key:
            raise ConfigurationError("API key is required.")

        if not self.base_url:
            raise ConfigurationError("Base URL is required.")
        if self.timeout <= 0:
            raise ConfigurationError(f"Timeout must be positive. Got: {self.timeout}")
        if self.max_tokens <= 0:
            raise ConfigurationError(f"max_tokens must be positive. Got: {self.max_tokens}")
        if self.request_delay < 0:
            raise ConfigurationError(f"request_delay must be positive. Got: {self.request_delay}")
        if self.max_rate_limit_retries < 0:
            raise ConfigurationError(f"max_rate_limit_retries must be positive. Got: {self.max_rate_limit_retries}")
        if self.rate_limit_retry_delay < 0:
            raise ConfigurationError(f"rate_limit_retry_delay must be positive. Got: {self.rate_limit_retry_delay}")

    @staticmethod
    def _get_env(key: str, default: Any = None, type_func: Any = str) -> Any:
        """
        从环境中读取指定键（key）；
        如果不存在，返回传入的 default；
        否则把字符串值用 type_func 转换成相应类型（对布尔值有专门判断）。
        """
        val = os.getenv(key)
        if val is None:
            return default
        if type_func is bool:
            return val.lower() in ("true", "1", "yes", "on")
        return type_func(val)

    @staticmethod
    def _filter_none_values(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        过滤掉字典中值为 None 的键值对。
        """
        return {k: v for k, v in config.items() if v is not None}

# 20251219结束人工审阅
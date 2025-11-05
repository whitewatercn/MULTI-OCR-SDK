"""
DeepSeek OCR SDK

A simple and efficient Python SDK for DeepSeek OCR API.

Example:
    >>> from deepseek_ocr import DeepSeekOCR
    >>> client = DeepSeekOCR(api_key="your_api_key")
    >>> text = client.parse("document.pdf")
    >>> print(text)

Features:
    - Simple and clean API
    - Three OCR modes: FREE_OCR, GROUNDING, OCR_IMAGE
    - Intelligent fallback mechanism
    - Batch processing with progress tracking
    - Both sync and async support
"""

from .batch import BatchProcessor, BatchResult, BatchSummary
from .client import DeepSeekOCR
from .config import OCRConfig
from .enums import OCRMode
from .exceptions import (
    APIError,
    ConfigurationError,
    DeepSeekOCRError,
    FileProcessingError,
    InvalidModeError,
    TimeoutError,
)

__version__ = "0.1.0"
__author__ = "Chengjie"
__license__ = "MIT"

__all__ = [
    # Main client
    "DeepSeekOCR",
    # Configuration
    "OCRConfig",
    # Enums
    "OCRMode",
    # Batch processing
    "BatchProcessor",
    "BatchResult",
    "BatchSummary",
    # Exceptions
    "DeepSeekOCRError",
    "ConfigurationError",
    "APIError",
    "FileProcessingError",
    "InvalidModeError",
    "TimeoutError",
    # Metadata
    "__version__",
]

"""Utilities for SDK file logging.

Provides a small helper to create a timestamped log file under
"multi-ocr-sdk-logs" in the current working directory and attach
a FileHandler to the specified logger.
"""

import os
import logging
from datetime import datetime


def setup_file_logger(
    log_dir_name: str = "multi-ocr-sdk-logs",
    logger_name: str = "multi_ocr_sdk",
    level: int = logging.INFO,
) -> str:
    """Create log directory and attach file handler to the named logger.

    Args:
        log_dir_name: Directory to create inside current working dir.
        logger_name: Logger to which the FileHandler will be attached.
        level: Logging level for both logger and handler.

    Returns:
        Path to the created log file.
    """
    log_dir = os.path.join(os.getcwd(), log_dir_name)
    os.makedirs(log_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{logger_name}_{ts}.log")

    sdk_logger = logging.getLogger(logger_name)
    sdk_logger.setLevel(level)

    # Install one file handler per process to avoid duplicates
    if not getattr(sdk_logger, "_multi_ocr_file_handler_installed", False):
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        fh.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )
        fh.name = "multi_ocr_file_handler"
        sdk_logger.addHandler(fh)
        sdk_logger._multi_ocr_file_handler_installed = True

    return log_file

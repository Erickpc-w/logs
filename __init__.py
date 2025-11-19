"""
統一日誌管理模組

提供統一、可配置的日誌記錄解決方案，支持多種輸出格式和目標。
"""

from .config import setup_logger

__version__ = "0.1.0"
__all__ = ["setup_logger"]


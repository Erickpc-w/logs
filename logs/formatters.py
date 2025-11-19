import logging
import json
from datetime import datetime
import socket
import sys

class JsonFormatter(logging.Formatter):
    """ELK 專用日誌格式器，生成結構化 JSON 日誌"""
    
    def format(self, record):
        """覆寫格式方法，生成符合 ELK 標準的日誌結構"""
        
        # 基礎字段 (所有日誌必備)
        log_data = {
            '@timestamp': datetime.now().isoformat(),  # ISO 8601 時間格式，ELK 時間戳標準
            'level': record.levelname,                 # 日誌級別 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
            'logger': record.name,                     # 日誌記錄器名稱，用於識別來源模組
            'message': record.getMessage(),            # 原始日誌訊息內容
            'module': record.module,                   # 產生日誌的 Python 模組名稱
            'function': record.funcName,               # 產生日誌的函數名稱
            'line': record.lineno,                     # 產生日誌的程式碼行號
            'path': record.pathname,                    # 原始碼文件完整路徑
            'host': socket.gethostname()
        }

        # 異常資訊處理 (當有異常發生時自動添加)
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,          # 異常類型
                'message': str(record.exc_info[1]),           # 異常訊息
                'stack_trace': self.formatException(record.exc_info)  # 完整堆疊追蹤
            }

        # 添加額外上下文
        if hasattr(record, 'extra'):
            log_data['extra'] = record.extra

        return json.dumps(log_data, ensure_ascii=False)  # 禁用 ASCII 轉碼以支持中文

class StandardFormatter(logging.Formatter):
    """本地存儲用日誌格式器，生成易讀的文字格式"""
    
    def format(self, record):
        """覆寫格式方法，生成標準文字日誌"""
        # 基礎格式：時間 - 級別 - 訊息
        base_format = super().format(record)
        
        # 追加模組與行號資訊
        if record.exc_info:
            return f"{base_format}\n[模組 {record.module}:{record.lineno}]"
        return f"{base_format} [模組 {record.module}:{record.lineno}]"

class ColoredFormatter(logging.Formatter):
    """為控制台輸出添加顏色的格式化器"""
    
    COLORS = {
        'DEBUG': '\033[94m',     # 藍色
        'INFO': '\033[92m',      # 綠色
        'WARNING': '\033[93m',   # 黃色
        'ERROR': '\033[91m',     # 紅色
        'CRITICAL': '\033[41m',  # 紅底白字
        'RESET': '\033[0m'       # 重置
    }
    
    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        super().__init__(fmt, datefmt)
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)

class FileFormatter(logging.Formatter):
    """為文件輸出優化的格式化器，添加模塊名和行號"""
    
    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s'
        super().__init__(fmt, datefmt) 
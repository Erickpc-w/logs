import logging
import os
from logging.handlers import SMTPHandler
from typing import List, Optional


class EmailNotificationHandler(SMTPHandler):
    """
    Email 通知處理器
    當日誌級別達到 ERROR 或以上時，透過 Email 發送通知
    繼承自 Python 標準庫的 SMTPHandler，提供增強功能
    """
    
    def __init__(
        self,
        mailhost: tuple,
        fromaddr: str,
        toaddrs: List[str],
        subject: str,
        credentials: Optional[tuple] = None,
        secure: Optional[tuple] = None,
        timeout: float = 5.0,
        project_name: str = "專案"
    ):
        """
        初始化 Email 通知 Handler
        
        參數:
            mailhost (tuple): (SMTP 伺服器地址, 埠號)
            fromaddr (str): 發送者 Email 地址
            toaddrs (List[str]): 接收者 Email 地址列表
            subject (str): 郵件主題模板（可使用 %(levelname)s 等格式化）
            credentials (tuple, optional): (使用者名稱, 密碼) 元組
            secure (tuple, optional): TLS 設定，通常為空元組 () 表示啟用 TLS
            timeout (float): SMTP 連線逾時時間（秒），預設 5.0
            project_name (str): 專案名稱，會顯示在郵件中
        """
        super().__init__(
            mailhost=mailhost,
            fromaddr=fromaddr,
            toaddrs=toaddrs if isinstance(toaddrs, list) else [toaddrs],
            subject=subject,
            credentials=credentials,
            secure=secure,
            timeout=timeout
        )
        
        self.project_name = project_name
        self.setLevel(logging.ERROR)  # 只處理 ERROR 及以上的日誌
        
        # 設定格式器，包含完整的日誌資訊
        self.setFormatter(logging.Formatter(
            '%(asctime)s\n'
            '專案: %(project_name)s\n'
            '級別: %(levelname)s\n'
            '模組: %(module)s\n'
            '位置: %(filename)s:%(lineno)d\n'
            '函數: %(funcName)s\n'
            '\n訊息:\n%(message)s\n'
        ))
    
    def emit(self, record: logging.LogRecord):
        """
        發送日誌記錄到 Email
        增強版本，添加專案名稱到記錄中
        """
        # 添加專案名稱到記錄中，供格式器使用
        record.project_name = self.project_name
        
        try:
            super().emit(record)
        except Exception:
            # Email 發送錯誤不應中斷程式，僅記錄錯誤
            self.handleError(record)
    
    def getSubject(self, record: logging.LogRecord):
        """
        覆寫主題生成方法，提供更詳細的主題
        """
        level_emoji = {
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        emoji = level_emoji.get(record.levelname, '⚠️')
        
        # 格式化主題，包含專案名稱、級別和時間
        subject = self.subject % {
            'levelname': record.levelname,
            'project_name': self.project_name,
            'asctime': record.asctime
        }
        
        return f"{emoji} {subject}"


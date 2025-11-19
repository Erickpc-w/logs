import logging
import os
from logging.handlers import RotatingFileHandler, SocketHandler
from pathlib import Path
import inspect
from .formatters import JsonFormatter, StandardFormatter, ColoredFormatter, FileFormatter

def setup_logger(name=__name__, log_level=logging.DEBUG, module_log=True):
    """
    統一配置日誌系統，返回配置完成的日誌記錄器
    
    參數：
    name (str): 日誌記錄器名稱，通常使用 __name__ 來自動獲取模組名稱
    log_level (int): 日誌級別，預設為 DEBUG (10)
    module_log (bool): 是否在模組目錄生成單獨日誌文件，預設為 True
    
    返回：
    logging.Logger: 配置完成的日誌記錄器實例
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 防止重複添加 handler (避免多線程環境下的重複配置)
    if logger.handlers:
        return logger

    # 確保日誌目錄存在
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 定義不同級別的日誌文件
    log_files = {
        logging.DEBUG: log_dir / "debug.log",
        logging.INFO: log_dir / "info.log",
        logging.WARNING: log_dir / "warning.log",
        logging.ERROR: log_dir / "error.log",
        logging.CRITICAL: log_dir / "critical.log"
    }
    
    # 創建每一個日誌級別的文件處理器
    for log_level, log_file in log_files.items():
        # 創建級別過濾器
        level_filter = LevelFilter(log_level)
        
        # 創建旋轉文件處理器（限制文件大小為 10MB，最多保留 5 個備份）
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # 設置級別和格式
        file_handler.setLevel(log_level)
        file_handler.setFormatter(FileFormatter())
        file_handler.addFilter(level_filter)
        
        # 添加到 logger
        logger.addHandler(file_handler)
    
    # 保留一個統一的日誌文件，包含所有級別的日誌
    all_logs_handler = RotatingFileHandler(
        filename=log_dir / "application.log",
        maxBytes=20*1024*1024,  # 20MB
        backupCount=10,
        encoding='utf-8'
    )
    all_logs_handler.setFormatter(FileFormatter())
    logger.addHandler(all_logs_handler)
    
    # 添加控制台處理器
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(message)s [模組 %(module)s:%(lineno)d]",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 本地文件記錄配置 (可通過環境變數禁用)
    if os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true':
        # 確保日誌目錄存在
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 滾動日誌文件配置 - 集中式日誌
        file_handler = RotatingFileHandler(
            filename=log_dir / 'application.log',
            maxBytes=10*1024*1024,  # 10MB 後滾動
            backupCount=5,          # 保留 5 個備份
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 模塊專屬日誌文件 - 在調用模塊所在目錄
        if module_log:
            try:
                # 獲取調用者的文件路徑
                caller_frame = inspect.stack()[1]
                caller_file = Path(caller_frame.filename)
                caller_dir = caller_file.parent
                
                # 使用實際文件名而非模塊名
                file_name = caller_file.stem  # 獲取文件名（不含擴展名）
                module_log_file = caller_dir / f"{file_name}.log"
                
                # 創建模塊專屬日誌處理器
                module_handler = RotatingFileHandler(
                    filename=module_log_file,
                    maxBytes=5*1024*1024,  # 5MB 後滾動
                    backupCount=3,         # 保留 3 個備份
                    encoding='utf-8'
                )
                module_handler.setFormatter(StandardFormatter(
                    '%(asctime)s - %(levelname)s - %(message)s'
                ))
                logger.addHandler(module_handler)
            except (IndexError, AttributeError):
                # 無法確定調用者位置，跳過模塊專屬日誌
                pass

    # Logstash 集成配置 (需顯式啟用)
    if os.getenv('ENABLE_LOGSTASH', 'false').lower() == 'true':
        logstash_host = os.getenv('LOGSTASH_HOST', 'localhost')
        logstash_port = int(os.getenv('LOGSTASH_PORT', 5000))
        
        # 使用 JSON 格式發送到 Logstash
        logstash_handler = SocketHandler(logstash_host, logstash_port)
        logstash_handler.setFormatter(JsonFormatter())
        logger.addHandler(logstash_handler)

    # Email 通知配置 (需顯式啟用)
    email_enabled = os.getenv('ENABLE_EMAIL_NOTIFICATION', 'false').lower() == 'true'
    
    if email_enabled:
        try:
            from .email_handler import EmailNotificationHandler
            
            # 獲取 SMTP 設定
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
            
            # 獲取認證資訊
            email_from = os.getenv('EMAIL_FROM')
            email_to = os.getenv('EMAIL_TO')  # 可以是逗號分隔的多個地址
            email_username = os.getenv('EMAIL_USERNAME', email_from)
            email_password = os.getenv('EMAIL_PASSWORD')
            
            # 獲取專案名稱（從環境變數或使用預設值）
            project_name = os.getenv('PROJECT_NAME', 'coolpc-webcrawler')
            
            if email_from and email_to and email_password:
                # 將多個接收地址轉換為列表
                to_addresses = [addr.strip() for addr in email_to.split(',')]
                
                # 建立 Email Handler
                email_handler = EmailNotificationHandler(
                    mailhost=(smtp_host, smtp_port),
                    fromaddr=email_from,
                    toaddrs=to_addresses,
                    subject=f'[{project_name}] %(levelname)s - %(asctime)s',
                    credentials=(email_username, email_password) if email_username and email_password else None,
                    secure=() if smtp_use_tls else None,  # 空元組表示啟用 TLS
                    timeout=10.0,  # 10 秒超時
                    project_name=project_name
                )
                
                # 設定日誌級別
                email_handler.setLevel(logging.ERROR)
                
                logger.addHandler(email_handler)
            else:
                print("警告: Email 通知已啟用，但缺少必要的環境變數 (EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD)")
                
        except ImportError as e:
            print(f"無法初始化 Email 通知 (模組匯入錯誤): {e}")
        except Exception as e:
            # 記錄配置錯誤，但不中斷日誌系統初始化
            print(f"無法初始化 Email 通知: {e}")

    return logger

class LevelFilter(logging.Filter):
    """
    日誌級別過濾器，只允許特定級別的日誌通過
    """
    def __init__(self, level):
        super().__init__()
        self.level = level
        
    def filter(self, record):
        # 只讓指定級別的日誌通過
        return record.levelno == self.level 
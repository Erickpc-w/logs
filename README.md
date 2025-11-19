# 統一日誌管理模組

## 概述

本模組提供統一、可配置的日誌記錄解決方案，實現了集中式日誌管理架構，支持多種輸出格式和目標。設計宗旨是在不同環境下提供一致的日誌記錄體驗，同時確保足夠的靈活性和可擴展性。

## 主要功能

- **統一配置界面**：單一函數入口點設定所有日誌記錄器
- **多重輸出支持**：同時支持控制台、文件和 ELK 系統輸出
- **預防重複配置**：智能檢測並防止處理器重複添加
- **環境變數控制**：通過環境變數動態調整日誌行為
- **結構化日誌**：支持 JSON 格式輸出，便於機器處理
- **用戶友好格式**：易讀的文本格式，適合開發調試

## 核心組件

### 1. `config.py` - 配置管理器

提供 `setup_logger` 函數，是所有日誌記錄器的統一配置入口：

```python
def setup_logger(name=__name__, log_level=logging.DEBUG):
    """
    統一配置日誌系統，返回配置完成的日誌記錄器
    
    參數：
    name (str): 日誌記錄器名稱，通常使用 __name__ 來自動獲取模組名稱
    log_level (int): 日誌級別，預設為 DEBUG (10)
    
    返回：
    logging.Logger: 配置完成的日誌記錄器實例
    """
    # 實現細節...
```

### 2. `formatters.py` - 格式化器

定義了兩種專用的日誌格式化器：

- **JsonFormatter**：生成 JSON 格式日誌，適用於 ELK 系統
- **StandardFormatter**：生成文本格式日誌，適用於本地排錯

## 使用方法

在任何需要日誌記錄的模組中，使用以下方式配置日誌：

```python
from logs.config import setup_logger

# 獲取模組專用日誌記錄器
logger = setup_logger(__name__)

# 使用日誌記錄訊息
logger.debug("調試訊息")
logger.info("一般訊息")
logger.warning("警告訊息")
logger.error("錯誤訊息")
logger.critical("嚴重錯誤訊息")

# 記錄異常
try:
    # 某些可能引發異常的操作
    result = 1 / 0
except Exception as e:
    logger.exception("發生異常：除以零")  # 自動包含完整堆疊追蹤
```

## 配置選項

通過環境變數調整日誌行為：

| 環境變數 | 描述 | 預設值 |
|---------|------|-------|
| `ENABLE_FILE_LOGGING` | 是否啟用文件日誌輸出 | `true` |
| `ENABLE_LOGSTASH` | 是否啟用 Logstash 輸出 | `false` |
| `LOGSTASH_HOST` | Logstash 服務器地址 | `localhost` |
| `LOGSTASH_PORT` | Logstash 服務器埠 | `5000` |

## 最佳實踐

1. **統一命名**: 使用模組名（`__name__`）作為日誌記錄器名稱
2. **適當級別**: 根據訊息重要性選擇合適的日誌級別
3. **避免多餘配置**: 不要手動創建日誌記錄器，始終使用 `setup_logger`
4. **包含上下文**: 在日誌訊息中提供足夠的上下文資訊
5. **使用結構化資訊**: 對複雜資料使用 JSON 或字典格式

## 錯誤排除

- **日誌未顯示**: 檢查當前日誌級別是否高於所記錄訊息的級別
- **重複日誌**: 確保未在多處配置同一日誌記錄器
- **文件權限問題**: 確認應用有權寫入日誌目錄

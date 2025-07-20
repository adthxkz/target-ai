import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """Настройка логгера с форматированием и опциональным файловым выводом"""
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(console_handler)
    
    # Если указан файл для логов, добавляем файловый обработчик
    if log_file:
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_path / f"{log_file}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Создаем основной логгер приложения
app_logger = setup_logger("target_ai", "app")
# Создаем логгер для Facebook API
fb_logger = setup_logger("facebook_api", "facebook")

def log_error(logger: logging.Logger, error: Exception, context: str = None):
    """Логирование ошибок с контекстом"""
    if context:
        logger.error(f"{context}: {str(error)}")
    else:
        logger.error(str(error))

def log_api_call(logger: logging.Logger, method: str, params: dict = None):
    """Логирование API вызовов"""
    if params:
        logger.info(f"API call: {method} with params: {params}")
    else:
        logger.info(f"API call: {method}")

import os
from fastapi import Header, HTTPException

def get_api_key(x_api_key: str = Header(None)) -> str:
    """
    Получение API ключа из заголовка запроса
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API ключ отсутствует")
    return x_api_key

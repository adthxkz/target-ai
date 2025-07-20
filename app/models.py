from pydantic import BaseModel

class AdRequest(BaseModel):
    """
    Модель запроса для генерации рекламы
    """
    niche: str
    goal: str

class AdResponse(BaseModel):
    """
    Модель ответа с рекламным текстом
    """
    response: str

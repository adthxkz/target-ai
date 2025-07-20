from pydantic import BaseModel, ConfigDict

class AdRequest(BaseModel):
    """
    Модель запроса для генерации рекламы
    """
    model_config = ConfigDict(from_attributes=True)
    
    niche: str
    goal: str

class AdResponse(BaseModel):
    """
    Модель ответа с рекламным текстом
    """
    model_config = ConfigDict(from_attributes=True)
    
    response: str

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    fb_access_token = Column(String)
    fb_account_id = Column(String)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    campaigns = relationship("Campaign", back_populates="user")
    budgets = relationship("Budget", back_populates="user")

class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True)
    fb_campaign_id = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    status = Column(String)
    objective = Column(String)
    daily_budget = Column(Float)
    total_spent = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    last_updated = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    metrics = Column(JSON)
    
    user = relationship("User", back_populates="campaigns")
    creatives = relationship("Creative", back_populates="campaign")

class Creative(Base):
    __tablename__ = 'creatives'

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    fb_creative_id = Column(String)
    type = Column(String)  # image/video
    file_path = Column(String)
    analysis = Column(JSON)  # результаты анализа от GPT-4
    performance = Column(JSON)  # метрики производительности
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    campaign = relationship("Campaign", back_populates="creatives")

class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total_budget = Column(Float)
    daily_budget = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    spend_strategy = Column(JSON)  # настройки распределения бюджета
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="budgets")

def init_db(db_url: str):
    """Инициализирует базу данных."""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone
from typing import Optional

class Base(DeclarativeBase):
    pass

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True)
    fb_access_token: Mapped[Optional[str]] = mapped_column(String)
    fb_account_id: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="user")
    budgets: Mapped[list["Budget"]] = relationship("Budget", back_populates="user")

class Campaign(Base):
    __tablename__ = 'campaigns'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fb_campaign_id: Mapped[Optional[str]] = mapped_column(String, unique=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'))
    name: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[Optional[str]] = mapped_column(String)
    objective: Mapped[Optional[str]] = mapped_column(String)
    daily_budget: Mapped[Optional[float]] = mapped_column(Float)
    lifetime_budget: Mapped[Optional[float]] = mapped_column(Float)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0)
    stats: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    user: Mapped[Optional["User"]] = relationship("User", back_populates="campaigns")
    creatives: Mapped[list["Creative"]] = relationship("Creative", back_populates="campaign")

class Creative(Base):
    __tablename__ = 'creatives'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('campaigns.id'))
    fb_creative_id: Mapped[Optional[str]] = mapped_column(String)
    type: Mapped[Optional[str]] = mapped_column(String)  # image/video
    file_path: Mapped[Optional[str]] = mapped_column(String)
    analysis: Mapped[Optional[dict]] = mapped_column(JSON)  # результаты анализа от GPT-4
    performance: Mapped[Optional[dict]] = mapped_column(JSON)  # метрики производительности
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="creatives")

class Budget(Base):
    __tablename__ = 'budgets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'))
    campaign_id: Mapped[Optional[str]] = mapped_column(String)  # fb_campaign_id
    budget_type: Mapped[Optional[str]] = mapped_column(String)  # daily/lifetime
    total_budget: Mapped[Optional[float]] = mapped_column(Float)
    daily_budget: Mapped[Optional[float]] = mapped_column(Float)
    amount: Mapped[Optional[float]] = mapped_column(Float)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    spend_strategy: Mapped[Optional[dict]] = mapped_column(JSON)  # настройки распределения бюджета
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    
    user: Mapped[Optional["User"]] = relationship("User", back_populates="budgets")

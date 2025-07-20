from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class CampaignCreate(BaseModel):
    name: str
    objective: str
    daily_budget: float
    status: str = 'PAUSED'

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    daily_budget: Optional[float] = None

class AdCreate(BaseModel):
    campaign_id: str
    creative_id: str
    creative_type: str
    ad_text: str
    headline: str
    link: str
    targeting: Optional[Dict] = None
    optimization_goal: str = 'REACH'
    billing_event: str = 'IMPRESSIONS'
    daily_budget: Optional[float] = None
    bid_amount: Optional[int] = None

class TargetingCreate(BaseModel):
    countries: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    age_min: int = 18
    age_max: int = 65
    genders: Optional[List[int]] = None
    interests: Optional[List[str]] = None
    behaviors: Optional[List[str]] = None
    languages: Optional[List[str]] = None

class CreativeUpload(BaseModel):
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    name: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    objective: str
    daily_budget: float
    status: str = "PAUSED"

class CreativeUpload(BaseModel):
    campaign_id: str
    file_type: str  # "image" или "video"
    title: str
    description: str
    cta: Optional[str] = None
    url: Optional[str] = None

class BudgetSettings(BaseModel):
    total_budget: float
    daily_budget: float
    start_date: datetime
    end_date: Optional[datetime] = None
    campaign_distribution: Optional[Dict[str, float]] = None

class CampaignStats(BaseModel):
    campaign_id: str
    name: str
    status: str
    spend: float
    impressions: int
    clicks: int
    conversions: int
    roas: float
    start_date: datetime
    end_date: datetime

class CampaignOptimization(BaseModel):
    campaign_id: str
    recommendations: List[str]
    budget_adjustment: float
    status_change: Optional[str] = None
    performance_metrics: Dict[str, float]

class DashboardMetrics(BaseModel):
    total_spend: float
    total_revenue: float
    overall_roas: float
    active_campaigns: int
    top_performing_campaigns: List[CampaignStats]
    recent_optimizations: List[CampaignOptimization]
    budget_allocation: Dict[str, float]
    performance_trend: Dict[str, List[float]]

from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
import asyncio
import httpx
import logging
from datetime import datetime

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User as AdUser
from facebook_business.adobjects.campaign import Campaign
from facebook_business.exceptions import FacebookRequestError

from ..config import settings

router = APIRouter(
    prefix="/api/facebook",
    tags=["facebook"],
)

logger = logging.getLogger(__name__)

# Тестовые данные для разработки
MOCK_CAMPAIGNS = [
    {
        "id": "123456789",
        "name": "Test Campaign 1",
        "status": "ACTIVE",
        "objective": "CONVERSIONS",
    },
]

MOCK_AD_ACCOUNT = {
    "id": "act_123456789",
    "name": "Test Ad Account",
    "currency": "USD",
}

# Вспомогательные синхронные функции для работы с SDK
def _get_ad_accounts_sync(api: FacebookAdsApi):
    """Синхронная функция для получения рекламных аккаунтов."""
    try:
        me = AdUser(fbid='me', api=api)
        ad_accounts = me.get_ad_accounts(fields=[
            AdAccount.Field.id,
            AdAccount.Field.name,
            AdAccount.Field.currency,
            AdAccount.Field.timezone_name
        ])
        return [acc.export_all_data() for acc in ad_accounts]
    except FacebookRequestError as e:
        logger.error(f"Facebook API error getting ad accounts: {e}")
        raise HTTPException(status_code=e.http_status(), detail=e.api_error_message())
    except Exception as e:
        logger.error(f"Unexpected error getting ad accounts: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching ad accounts.")

def _get_campaigns_sync(api: FacebookAdsApi, ad_account_id: str):
    """Синхронная функция для получения кампаний."""
    try:
        ad_account = AdAccount(ad_account_id, api=api)
        campaigns = ad_account.get_campaigns(fields=[
            Campaign.Field.id,
            Campaign.Field.name,
            Campaign.Field.status,
            Campaign.Field.objective,
            Campaign.Field.daily_budget,
            Campaign.Field.lifetime_budget,
            Campaign.Field.start_time,
            Campaign.Field.end_time
        ])
        return [campaign.export_all_data() for campaign in campaigns]
    except FacebookRequestError as e:
        logger.error(f"Facebook API error getting campaigns: {e}")
        raise HTTPException(status_code=e.http_status(), detail=e.api_error_message())
    except Exception as e:
        logger.error(f"Unexpected error getting campaigns: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching campaigns.")

def _create_campaign_sync(api: FacebookAdsApi, ad_account_id: str, params: dict):
    """Синхронная функция для создания кампании."""
    try:
        ad_account = AdAccount(ad_account_id, api=api)
        campaign = ad_account.create_campaign(params=params)
        return campaign.export_all_data()
    except FacebookRequestError as e:
        logger.error(f"Facebook API error creating campaign: {e}")
        raise HTTPException(status_code=e.http_status(), detail=e.api_error_message())
    except Exception as e:
        logger.error(f"Unexpected error creating campaign: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the campaign.")

# Эндпоинты
@router.get("/auth")
async def facebook_auth():
    """Начало процесса авторизации Facebook"""
    logger.info(f"Starting Facebook auth process. REDIRECT_URI: {settings.FB_REDIRECT_URI}")
    
    if settings.MOCK_MODE:
        logger.info("Using mock mode - redirecting to mock callback")
        return RedirectResponse(url=f"{settings.BASE_URL}/api/facebook/callback?code=mock_code")
        
    if not settings.FACEBOOK_APP_ID or not settings.FACEBOOK_APP_SECRET:
        logger.error("Missing Facebook credentials")
        raise HTTPException(status_code=500, detail="Facebook credentials not configured")
    
    auth_url = f"https://www.facebook.com/v17.0/dialog/oauth?client_id={settings.FACEBOOK_APP_ID}&redirect_uri={settings.FB_REDIRECT_URI}&scope={settings.FB_SCOPE}"
    logger.info(f"Redirecting to Facebook auth URL: {auth_url}")
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def facebook_callback(code: str = None, error: str = None):
    """Обработка callback от Facebook"""
    logger.info("Received Facebook callback")
    
    if error:
        logger.error(f"Facebook OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        logger.error("No code provided in callback")
        raise HTTPException(status_code=400, detail="No code provided")
        
    if settings.MOCK_MODE and code == "mock_code":
        logger.info("Mock mode - returning test data")
        return JSONResponse({
            "status": "success",
            "access_token": "mock_access_token_123",
            "accounts": [MOCK_AD_ACCOUNT],
            "campaigns": MOCK_CAMPAIGNS
        })
    
    token_url = f"https://graph.facebook.com/v17.0/oauth/access_token"
    params = {
        "client_id": settings.FACEBOOK_APP_ID,
        "client_secret": settings.FACEBOOK_APP_SECRET,
        "redirect_uri": settings.FB_REDIRECT_URI,
        "code": code
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(token_url, params=params)
            response.raise_for_status()
            token_data = response.json()
        except httpx.RequestError as exc:
            logger.error(f"Error requesting access token: {exc}")
            raise HTTPException(status_code=500, detail="Could not retrieve access token")
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error requesting access token: {exc.response.status_code} - {exc.response.text}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error from Facebook: {exc.response.text}")

    access_token = token_data.get("access_token")
    if not access_token:
        logger.error(f"Access token not in response: {token_data}")
        raise HTTPException(status_code=500, detail="Access token not found in response")

    try:
        api = FacebookAdsApi.init(
            app_id=settings.FACEBOOK_APP_ID,
            app_secret=settings.FACEBOOK_APP_SECRET,
            access_token=access_token,
            crash_log=False
        )
        accounts = await asyncio.to_thread(_get_ad_accounts_sync, api)
        campaigns = []
        if accounts:
            campaigns = await asyncio.to_thread(_get_campaigns_sync, api, accounts[0]['id'])
        
        return JSONResponse({
            "status": "success",
            "access_token": access_token,
            "accounts": accounts,
            "campaigns": campaigns
        })
    except Exception as e:
        logger.error(f"Error fetching accounts or campaigns: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ad-accounts")
async def get_ad_accounts_endpoint(token: str):
    if settings.MOCK_MODE:
        return JSONResponse([MOCK_AD_ACCOUNT])
    try:
        api = FacebookAdsApi.init(access_token=token, crash_log=False)
        accounts = await asyncio.to_thread(_get_ad_accounts_sync, api)
        return JSONResponse(accounts)
    except Exception as e:
        logger.error(f"Error in get_ad_accounts_endpoint: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns")
async def get_campaigns_endpoint(ad_account_id: str, token: str):
    if settings.MOCK_MODE:
        return JSONResponse(MOCK_CAMPAIGNS)
    try:
        api = FacebookAdsApi.init(access_token=token, crash_log=False)
        campaigns = await asyncio.to_thread(_get_campaigns_sync, api, ad_account_id)
        return JSONResponse(campaigns)
    except Exception as e:
        logger.error(f"Error in get_campaigns_endpoint: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns")
async def create_campaign_endpoint(
    ad_account_id: str = Form(...),
    name: str = Form(...),
    objective: str = Form(...),
    status: str = Form("PAUSED"),
    daily_budget: int = Form(None),
    token: str = Form(...)
):
    if settings.MOCK_MODE:
        new_campaign = {
            "id": f"mock_id_{int(datetime.now().timestamp())}",
            "name": name,
            "objective": objective,
            "status": status,
            "daily_budget": daily_budget
        }
        MOCK_CAMPAIGNS.append(new_campaign)
        return JSONResponse(content=new_campaign, status_code=201)

    try:
        api = FacebookAdsApi.init(access_token=token, crash_log=False)
        params = {
            'name': name,
            'objective': objective,
            'status': status,
            'special_ad_categories': [],
        }
        if daily_budget:
            params['daily_budget'] = daily_budget
            
        campaign_data = await asyncio.to_thread(
            _create_campaign_sync, api, ad_account_id, params
        )
        logger.info(f"Successfully created campaign {campaign_data.get('id')}")
        return JSONResponse(content=campaign_data, status_code=201)
    except Exception as e:
        logger.error(f"Error in create_campaign_endpoint: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

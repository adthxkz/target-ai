from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class FacebookAdsService:
    def __init__(self, access_token=None):
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.api = None
        
    def initialize(self):
        """Инициализация API"""
        if not self.api:
            self.api = FacebookAdsApi.init(
                self.app_id,
                self.app_secret,
                self.access_token
            )
    
    async def get_ad_accounts(self):
        """Получение списка рекламных аккаунтов"""
        try:
            self.initialize()
            import requests
            response = requests.get(
                "https://graph.facebook.com/v17.0/me/adaccounts",
                params={"access_token": self.access_token}
            )
            return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Error getting ad accounts: {e}")
            return []

    async def get_campaigns(self, account_id):
        """Получение списка кампаний для аккаунта"""
        try:
            self.initialize()
            account = AdAccount(account_id)
            campaigns = account.get_campaigns(
                fields=["name", "status", "objective", "daily_budget", "lifetime_budget"]
            )
            return [campaign.export_all_data() for campaign in campaigns]
        except Exception as e:
            logger.error(f"Error getting campaigns: {e}")
            return []

    async def update_campaign_status(self, campaign_id, new_status):
        """Обновление статуса кампании"""
        try:
            self.initialize()
            campaign = Campaign(campaign_id)
            campaign.api_update(params={"status": new_status})
            return True
        except Exception as e:
            logger.error(f"Error updating campaign status: {e}")
            return False

    async def update_campaign_budget(self, campaign_id, budget_type, amount):
        """Обновление бюджета кампании"""
        try:
            self.initialize()
            campaign = Campaign(campaign_id)
            params = {}
            if budget_type == "daily":
                params["daily_budget"] = amount
            else:
                params["lifetime_budget"] = amount
            campaign.api_update(params=params)
            return True
        except Exception as e:
            logger.error(f"Error updating campaign budget: {e}")
            return False

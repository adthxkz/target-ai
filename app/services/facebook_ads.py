from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class FacebookAdsService:
    def __init__(self):
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self._access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self._ad_account_id = os.getenv("FACEBOOK_AD_ACCOUNT_ID")
        
        if not all([self.app_id, self.app_secret]):
            raise ValueError("Не установлены FACEBOOK_APP_ID или FACEBOOK_APP_SECRET")
        
        self._init_api()
    
    def _init_api(self):
        """Инициализация Facebook Ads API"""
        if not self.access_token or not self.ad_account_id:
            return
        FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
        self.account = AdAccount(self.ad_account_id)
    
    @property
    def access_token(self) -> str:
        return self._access_token
    
    @access_token.setter
    def access_token(self, value: str):
        self._access_token = value
        if hasattr(self, 'app_id') and hasattr(self, 'app_secret'):
            self._init_api()
    
    @property
    def ad_account_id(self) -> str:
        return self._ad_account_id
    
    @ad_account_id.setter
    def ad_account_id(self, value: str):
        self._ad_account_id = value
        if hasattr(self, '_access_token'):
            self._init_api()
    
    async def get_account_info(self) -> Dict:
        """Получает информацию о рекламном аккаунте"""
        try:
            account = self.account
            fields = [
                'name',
                'account_status',
                'balance',
                'currency',
                'business_name',
                'timezone_name'
            ]
            account_data = account.api_get(fields=fields)
            return {
                'name': account_data.get('name'),
                'status': account_data.get('account_status'),
                'balance': account_data.get('balance'),
                'currency': account_data.get('currency'),
                'business_name': account_data.get('business_name'),
                'timezone': account_data.get('timezone_name')
            }
        except Exception as e:
            raise Exception(f"Ошибка при получении информации об аккаунте: {str(e)}")
            
    async def get_campaign_stats(self, campaign_id: str) -> Dict:
        """Получает статистику рекламной кампании"""
        try:
            campaign = Campaign(campaign_id)
            fields = [
                'name',
                'status',
                'objective',
                'daily_budget',
                'lifetime_budget',
                'start_time',
                'stop_time'
            ]
            params = {
                'date_preset': 'last_30d',
                'fields': [
                    'spend',
                    'impressions',
                    'clicks',
                    'actions',
                    'cost_per_action_type'
                ]
            }
            
            # Получаем основную информацию о кампании
            campaign_data = campaign.api_get(fields=fields)
            
            # Получаем статистику
            insights = campaign.get_insights(params=params)
            
            if not insights:
                return {
                    'name': campaign_data.get('name'),
                    'status': campaign_data.get('status'),
                    'daily_budget': float(campaign_data.get('daily_budget', 0)) / 100,
                    'stats': {
                        'spend': 0,
                        'impressions': 0,
                        'clicks': 0,
                        'ctr': 0,
                        'cpc': 0
                    }
                }
            
            stats = insights[0]
            
            return {
                'name': campaign_data.get('name'),
                'status': campaign_data.get('status'),
                'daily_budget': float(campaign_data.get('daily_budget', 0)) / 100,
                'stats': {
                    'spend': float(stats.get('spend', 0)),
                    'impressions': int(stats.get('impressions', 0)),
                    'clicks': int(stats.get('clicks', 0)),
                    'ctr': float(stats.get('ctr', 0)) * 100,
                    'cpc': float(stats.get('cpc', 0))
                }
            }
        except Exception as e:
            raise Exception(f"Ошибка при получении статистики кампании: {str(e)}")

    async def create_campaign(
        self, 
        name: str, 
        objective: str,
        daily_budget: float,
        status: str = 'PAUSED'
    ) -> Dict:
        """Создает новую рекламную кампанию."""
        try:
            campaign = self.account.create_campaign(
                params={
                    'name': name,
                    'objective': objective,
                    'status': status,
                    'daily_budget': int(daily_budget * 100),  # конвертируем в центы
                    'special_ad_categories': [],
                }
            )
            return {'campaign_id': campaign['id']}
        except Exception as e:
            raise Exception(f"Ошибка при создании кампании: {str(e)}")

    async def upload_creative(
        self, 
        image_path: Optional[str] = None, 
        video_path: Optional[str] = None,
        name: Optional[str] = None
    ) -> Dict:
        """Загружает креатив (изображение или видео) в Facebook Ads."""
        try:
            if video_path:
                # Загрузка видео
                video = self.account.create_ad_video(
                    params={
                        'file_url': video_path,
                        'name': name or f'Video {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                        'description': 'Uploaded via API'
                    }
                )
                return {
                    'video_id': video['id'],
                    'type': 'video',
                    'name': name,
                    'url': video.get('url')
                }
            elif image_path:
                # Загрузка изображения
                image = self.account.create_ad_image(
                    params={
                        'filename': image_path,
                        'name': name or f'Image {datetime.now().strftime("%Y-%m-%d %H:%M")}'
                    }
                )
                return {
                    'image_id': image['id'],
                    'type': 'image',
                    'name': name,
                    'hash': image.get('hash'),
                    'url': image.get('url')
                }
            else:
                raise ValueError("Необходимо указать путь к изображению или видео")
        except Exception as e:
            raise Exception(f"Ошибка при загрузке креатива: {str(e)}")

    async def list_creatives(self, creative_type: str = 'ALL', limit: int = 100) -> List[Dict]:
        """Получает список креативов определенного типа."""
        try:
            fields = ['id', 'name', 'url', 'created_time']
            
            if creative_type.upper() == 'VIDEO' or creative_type.upper() == 'ALL':
                videos = self.account.get_ad_videos(
                    fields=fields + ['thumbnails', 'duration'],
                    params={'limit': limit}
                )
                video_list = [{
                    'id': video['id'],
                    'type': 'video',
                    'name': video.get('name'),
                    'url': video.get('url'),
                    'duration': video.get('duration'),
                    'thumbnail_url': video.get('thumbnails', {}).get('uri'),
                    'created_time': video.get('created_time')
                } for video in videos]
            else:
                video_list = []

            if creative_type.upper() == 'IMAGE' or creative_type.upper() == 'ALL':
                images = self.account.get_ad_images(
                    fields=fields + ['hash', 'height', 'width'],
                    params={'limit': limit}
                )
                image_list = [{
                    'id': image['id'],
                    'type': 'image',
                    'name': image.get('name'),
                    'url': image.get('url'),
                    'hash': image.get('hash'),
                    'dimensions': f"{image.get('width')}x{image.get('height')}",
                    'created_time': image.get('created_time')
                } for image in images]
            else:
                image_list = []

            return video_list + image_list
        except Exception as e:
            raise Exception(f"Ошибка при получении списка креативов: {str(e)}")

    async def delete_creative(self, creative_id: str, creative_type: str) -> Dict:
        """Удаляет креатив указанного типа."""
        try:
            if creative_type.upper() == 'VIDEO':
                from facebook_business.adobjects.advideo import AdVideo
                creative = AdVideo(creative_id)
            else:
                from facebook_business.adobjects.adimage import AdImage
                creative = AdImage(creative_id)

            creative.api_delete()
            return {
                'success': True, 
                'creative_id': creative_id,
                'type': creative_type
            }
        except Exception as e:
            raise Exception(f"Ошибка при удалении креатива: {str(e)}")

    async def create_ad(
        self,
        campaign_id: str,
        creative_id: str,
        creative_type: str,
        ad_text: str,
        headline: str,
        link: str,
        targeting: Optional[Dict] = None,
        optimization_goal: str = 'REACH',
        billing_event: str = 'IMPRESSIONS',
        daily_budget: Optional[float] = None,
        bid_amount: Optional[int] = None
    ) -> Dict:
        """
        Создает объявление с указанным креативом и настройками таргетинга.
        
        Args:
            campaign_id: ID рекламной кампании
            creative_id: ID креатива (изображения или видео)
            creative_type: Тип креатива ('image' или 'video')
            ad_text: Текст объявления
            headline: Заголовок объявления
            link: Ссылка для объявления
            targeting: Словарь с настройками таргетинга
            optimization_goal: Цель оптимизации (REACH, LINK_CLICKS, POST_ENGAGEMENT и т.д.)
            billing_event: Тип оплаты (IMPRESSIONS, LINK_CLICKS и т.д.)
            daily_budget: Дневной бюджет в валюте аккаунта
            bid_amount: Ставка в центах
        """
        try:
            # Базовые настройки таргетинга
            default_targeting = {
                'age_min': 18,
                'age_max': 65,
                'genders': [1, 2],  # Все пользователи
                'geo_locations': {
                    'countries': ['US']  # Можно настроить под нужную географию
                }
            }
            
            # Объединяем с пользовательскими настройками
            final_targeting = {**default_targeting, **(targeting or {})}
            
            # Создаем набор объявлений (Ad Set)
            adset_params = {
                'campaign_id': campaign_id,
                'name': f'AdSet {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'optimization_goal': optimization_goal,
                'billing_event': billing_event,
                'targeting': final_targeting,
                'status': 'PAUSED',
            }
            
            # Добавляем бюджет если указан
            if daily_budget:
                adset_params['daily_budget'] = int(daily_budget * 100)
            
            # Добавляем ставку если указана
            if bid_amount:
                adset_params['bid_amount'] = bid_amount
                
            adset = self.account.create_ad_set(params=adset_params)

            # Создаем объявление
            creative_params = {
                'object_story_spec': {
                    'page_id': self.page_id,
                    'link_data': {
                        'message': ad_text,
                        'link': link,
                        'caption': headline,
                    }
                }
            }

            if creative_type == 'video':
                creative_params['object_story_spec']['link_data']['video_id'] = creative_id
            else:
                creative_params['object_story_spec']['link_data']['image_hash'] = creative_id

            ad = self.account.create_ad(
                params={
                    'name': f'Ad {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                    'adset_id': adset['id'],
                    'creative': creative_params,
                    'status': 'PAUSED',
                }
            )

            return {'ad_id': ad['id'], 'adset_id': adset['id']}
        except Exception as e:
            raise Exception(f"Ошибка при создании объявления: {str(e)}")

    async def get_campaign_stats(self, campaign_id: str, days: int = 7) -> Dict:
        """Получает статистику по кампании за указанное количество дней."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            campaign = Campaign(campaign_id)
            insights = campaign.get_insights(
                params={
                    'date_preset': 'lifetime',
                    'fields': [
                        'spend',
                        'impressions',
                        'clicks',
                        'ctr',
                        'cpc',
                        'reach',
                        'actions'
                    ],
                    'time_range': {
                        'since': start_date.strftime('%Y-%m-%d'),
                        'until': end_date.strftime('%Y-%m-%d'),
                    }
                }
            )

            return insights[0] if insights else {}
        except Exception as e:
            raise Exception(f"Ошибка при получении статистики: {str(e)}")

    async def update_campaign(self, campaign_id: str, **kwargs) -> Dict:
        """Обновляет существующую рекламную кампанию."""
        try:
            campaign = Campaign(campaign_id)
            campaign.api_update(params=kwargs)
            return {'success': True, 'campaign_id': campaign_id}
        except Exception as e:
            raise Exception(f"Ошибка при обновлении кампании: {str(e)}")

    async def delete_campaign(self, campaign_id: str) -> Dict:
        """Удаляет рекламную кампанию."""
        try:
            campaign = Campaign(campaign_id)
            campaign.api_delete()
            return {'success': True, 'campaign_id': campaign_id}
        except Exception as e:
            raise Exception(f"Ошибка при удалении кампании: {str(e)}")

    async def list_campaigns(self, limit: int = 100) -> List[Dict]:
        """Получает список всех рекламных кампаний."""
        try:
            campaigns = self.account.get_campaigns(
                fields=[
                    'id',
                    'name',
                    'status',
                    'objective',
                    'daily_budget',
                    'lifetime_budget',
                    'start_time',
                    'stop_time'
                ],
                params={'limit': limit}
            )
            
            return [{
                'id': campaign['id'],
                'name': campaign['name'],
                'status': campaign['status'],
                'objective': campaign.get('objective'),
                'daily_budget': float(campaign.get('daily_budget', 0)) / 100,
                'lifetime_budget': float(campaign.get('lifetime_budget', 0)) / 100,
                'start_time': campaign.get('start_time'),
                'stop_time': campaign.get('stop_time')
            } for campaign in campaigns]
        except Exception as e:
            raise Exception(f"Ошибка при получении списка кампаний: {str(e)}")

    async def create_targeting(
        self,
        countries: List[str] = None,
        regions: List[str] = None,
        cities: List[str] = None,
        age_min: int = 18,
        age_max: int = 65,
        genders: List[int] = None,
        interests: List[str] = None,
        behaviors: List[str] = None,
        languages: List[str] = None,
    ) -> Dict:
        """
        Создает настройки таргетинга для рекламного набора.
        
        Args:
            countries: Список кодов стран (например, ['US', 'GB'])
            regions: Список регионов
            cities: Список городов
            age_min: Минимальный возраст
            age_max: Максимальный возраст
            genders: Список полов (1 - мужской, 2 - женский)
            interests: Список интересов
            behaviors: Список поведенческих характеристик
            languages: Список языков
        """
        targeting = {
            'age_min': age_min,
            'age_max': age_max,
            'geo_locations': {}
        }

        if countries:
            targeting['geo_locations']['countries'] = countries
        if regions:
            targeting['geo_locations']['regions'] = regions
        if cities:
            targeting['geo_locations']['cities'] = cities
            
        if genders:
            targeting['genders'] = genders
            
        if languages:
            targeting['locales'] = languages
            
        if interests:
            targeting['interests'] = await self._get_targeting_specs('interests', interests)
            
        if behaviors:
            targeting['behaviors'] = await self._get_targeting_specs('behaviors', behaviors)
            
        return targeting
        
    async def _get_targeting_specs(self, spec_type: str, terms: List[str]) -> List[Dict]:
        """
        Получает спецификации таргетинга (интересы или поведение) по ключевым словам.
        """
        try:
            specs = []
            for term in terms:
                results = self.account.get_targeting_search(
                    params={
                        'q': term,
                        'type': spec_type.upper(),
                        'limit': 50
                    }
                )
                if results:
                    specs.extend([{
                        'id': item['id'],
                        'name': item['name']
                    } for item in results])
            return specs
        except Exception as e:
            raise Exception(f"Ошибка при получении спецификаций таргетинга: {str(e)}")

    async def get_targeting_suggestions(self, seed_terms: List[str]) -> List[Dict]:
        """
        Получает предложения по таргетингу на основе исходных терминов.
        """
        try:
            suggestions = []
            for term in seed_terms:
                results = self.account.get_targeting_suggestions(
                    params={
                        'targeting_list': [{'id': term}],
                        'limit': 50
                    }
                )
                if results:
                    suggestions.extend([{
                        'id': item['id'],
                        'name': item['name'],
                        'audience_size': item.get('audience_size'),
                        'path': item.get('path', []),
                        'type': item.get('type')
                    } for item in results])
            return suggestions
        except Exception as e:
            raise Exception(f"Ошибка при получении предложений по таргетингу: {str(e)}")

    async def optimize_campaigns(self, target_roas: float = 1.0) -> List[Dict]:
        """
        Оптимизирует рекламные кампании на основе их эффективности.
        Отключает кампании с ROAS ниже целевого значения.
        """
        try:
            campaigns = self.account.get_campaigns(
                fields=['id', 'name', 'status']
            )

            results = []
            for campaign in campaigns:
                stats = await self.get_campaign_stats(campaign['id'])
                
                if not stats:
                    continue

                spend = float(stats.get('spend', 0))
                revenue = sum([
                    float(action.get('value', 0))
                    for action in stats.get('actions', [])
                    if action.get('action_type') == 'purchase'
                ])

                current_roas = revenue / spend if spend > 0 else 0

                # Если ROAS ниже целевого, отключаем кампанию
                if current_roas < target_roas and spend > 0:
                    campaign.api_update(
                        params={'status': 'PAUSED'}
                    )
                    action = 'paused'
                else:
                    action = 'running'

                results.append({
                    'campaign_id': campaign['id'],
                    'name': campaign['name'],
                    'spend': spend,
                    'revenue': revenue,
                    'roas': current_roas,
                    'action': action
                })

            return results
        except Exception as e:
            raise Exception(f"Ошибка при оптимизации кампаний: {str(e)}")

import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from utils.models import TarkovAccount, UserSettings, CATEGORIES


class LolzAPI:
    BASE_URL = "https://prod-api.lzt.market"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {"accept": "application/json", "authorization": f"Bearer {token}"}
    
    async def get_accounts_by_cat(self, cat: str, settings: UserSettings) -> List[TarkovAccount]:
        if cat not in CATEGORIES:
            return []
        
        url = f"{self.BASE_URL}/{CATEGORIES[cat]['endpoint']}"
        params = self._build_params(cat, settings)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_accounts(data.get('items', []), cat)
                    print(f"API Error {cat}: {resp.status}")
                    return []
        except Exception as e:
            print(f"API Request Error {cat}: {e}")
            return []
    
    async def get_all_accounts(self, settings: UserSettings) -> List[TarkovAccount]:
        all_accounts = []
        for cat in settings.categories:
            accounts = await self.get_accounts_by_cat(cat, settings)
            all_accounts.extend(accounts)
            await asyncio.sleep(0.5)
        return all_accounts
    
    def _build_params(self, cat: str, settings: UserSettings) -> Dict[str, Any]:
        params = {}
        
        if settings.min_price:
            params['pmin'] = settings.min_price
        if settings.max_price:
            params['pmax'] = settings.max_price
        if settings.order_by:
            params['order_by'] = settings.order_by
        if settings.show:
            params['show'] = settings.show
        if settings.nsb is not None:
            params['nsb'] = str(settings.nsb).lower()
        if settings.sb is not None:
            params['sb'] = str(settings.sb).lower()
        if settings.email_login_data is not None:
            params['email_login_data'] = str(settings.email_login_data).lower()
        
        if cat == "escape_from_tarkov":
            if settings.min_level:
                params['lmin'] = settings.min_level
            if settings.max_level:
                params['lmax'] = settings.max_level
            if settings.pve_access:
                params['pve'] = settings.pve_access
            
            if settings.game_versions:
                for version in settings.game_versions:
                    params.setdefault('version[]', []).append(version)
            
            if settings.regions:
                for region in settings.regions:
                    params['region'] = region
        
        if settings.origins:
            for origin in settings.origins:
                params.setdefault('origin[]', []).append(origin)
        
        return params
    
    def _parse_accounts(self, items: List[Dict[str, Any]], cat: str) -> List[TarkovAccount]:
        accounts = []
        for item in items:
            try:
                if cat == "escape_from_tarkov":
                    acc = self._parse_tarkov(item)
                else:
                    acc = self._parse_generic(item)
                
                if acc:
                    accounts.append(acc)
            except Exception as e:
                print(f"Parse error {item.get('item_id', 'unknown')} for {cat}: {e}")
        return accounts
    
    def _parse_tarkov(self, item: Dict[str, Any]) -> Optional[TarkovAccount]:
        return TarkovAccount(
            item_id=item.get('item_id', 0),
            title=item.get('title', ''),
            price=item.get('price', 0),
            price_with_seller_fee=item.get('priceWithSellerFee', 0),
            game_version=item.get('tarkov_game_version', ''),
            level=item.get('tarkov_level', 0),
            region=item.get('tarkov_region', ''),
            origin=item.get('item_origin', ''),
            seller_username=item.get('seller', {}).get('username', ''),
            seller_sold_items=item.get('seller', {}).get('sold_items_count', 0),
            seller_restore_percent=item.get('seller', {}).get('restore_percents'),
            rubles=item.get('tarkov_rubles', 0),
            dollars=item.get('tarkov_dollars', 0),
            euros=item.get('tarkov_euros', 0),
            nsb=item.get('nsb', 0) == 1,
            allow_ask_discount=item.get('allow_ask_discount', 0) == 1,
            max_discount_percent=item.get('max_discount_percent', 0),
            published_date=item.get('published_date', 0),
            last_activity=item.get('tarkov_last_activity', 0),
            email_type=item.get('email_type', ''),
            email_provider=item.get('email_provider', ''),
            pve_access=item.get('tarkov_access_pve', 0) == 1,
            url=f"https://lzt.market/{item.get('item_id', 0)}/"
        )
    
    def _parse_generic(self, item: Dict[str, Any]) -> Optional[TarkovAccount]:
        return TarkovAccount(
            item_id=item.get('item_id', 0),
            title=item.get('title', ''),
            price=item.get('price', 0),
            price_with_seller_fee=item.get('priceWithSellerFee', 0),
            game_version='',
            level=0,
            region='',
            origin=item.get('item_origin', ''),
            seller_username=item.get('seller', {}).get('username', ''),
            seller_sold_items=item.get('seller', {}).get('sold_items_count', 0),
            seller_restore_percent=item.get('seller', {}).get('restore_percents'),
            rubles=0,
            dollars=0,
            euros=0,
            nsb=item.get('nsb', 0) == 1,
            allow_ask_discount=item.get('allow_ask_discount', 0) == 1,
            max_discount_percent=item.get('max_discount_percent', 0),
            published_date=item.get('published_date', 0),
            last_activity=0,
            email_type=item.get('email_type', ''),
            email_provider=item.get('email_provider', ''),
            pve_access=False,
            url=f"https://lzt.market/{item.get('item_id', 0)}/"
        )

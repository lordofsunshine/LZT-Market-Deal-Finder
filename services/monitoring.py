import asyncio
from typing import List, Tuple
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.database import Database
from services.lolz_api import LolzAPI
from services.deal_analyzer import DealAnalyzer
from utils.models import UserSettings, DealAlert, GAME_VERSION_NAMES, REGION_NAMES, ORIGIN_NAMES, CATEGORIES


class MonitoringService:
    def __init__(self, bot: Bot, db: Database, api: LolzAPI, interval: int = 5):
        self.bot = bot
        self.db = db
        self.api = api
        self.analyzer = DealAnalyzer()
        self.scheduler = AsyncIOScheduler()
        self.interval = interval
        self.running = False
    
    async def start(self):
        if self.running:
            return
        
        self.scheduler.add_job(self.check_deals, 'interval', minutes=self.interval, id='checker')
        self.scheduler.add_job(self.cleanup, 'interval', hours=24, id='cleanup')
        self.scheduler.start()
        self.running = True
        print(f"Мониторинг запущен ({self.interval} мин)")
    
    async def stop(self):
        if not self.running:
            return
        self.scheduler.shutdown()
        self.running = False
        print("Мониторинг остановлен")
    
    async def check_deals(self):
        print("Проверка предложений...")
        try:
            users = await self.db.get_all_users()
            for user_id in users:
                settings = await self.db.get_user_settings(user_id)
                if settings and settings.notifications_enabled:
                    await self.check_user_deals(user_id, settings)
                    await asyncio.sleep(1)
            print(f"Проверено {len(users)} пользователей")
        except Exception as e:
            print(f"Ошибка проверки: {e}")
    
    async def check_user_deals(self, user_id: int, settings: UserSettings):
        try:
            accounts = await self.api.get_all_accounts(settings)
            if not accounts:
                return
            
            deals = self.analyzer.analyze_deals(accounts, settings)
            for deal in deals[:5]:
                if not await self.db.is_item_seen(user_id, deal.account.item_id):
                    await self.send_notification(user_id, deal, settings)
                    await self.db.mark_item_seen(user_id, deal.account.item_id)
                    await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Ошибка для пользователя {user_id}: {e}")
    
    async def send_notification(self, user_id: int, deal: DealAlert, settings: UserSettings):
        try:
            msg, kb = self._format_msg(deal, settings)
            await self.bot.send_message(
                chat_id=user_id, text=msg, parse_mode="HTML",
                reply_markup=kb, disable_web_page_preview=True
            )
            await self.db.save_notification(user_id, deal.account.item_id, msg)
        except Exception as e:
            print(f"Ошибка отправки уведомления {user_id}: {e}")
    
    def _format_msg(self, deal: DealAlert, settings: UserSettings) -> Tuple[str, InlineKeyboardMarkup]:
        acc = deal.account
        
        version = GAME_VERSION_NAMES.get(acc.game_version, acc.game_version)
        region = REGION_NAMES.get(acc.region, acc.region)
        origin = ORIGIN_NAMES.get(acc.origin, acc.origin)
        cat_name = self._get_cat_name(acc, settings)
        
        msg = f"🎯 <b>Выгодное предложение!</b>\n\n<b>{cat_name}</b>\n<b>Цена:</b> {acc.price:,} ₽"
        
        details = []
        if acc.game_version:
            details.append(f"Издание: {version}")
        if acc.level > 0:
            details.append(f"Уровень: {acc.level}")
        if acc.region:
            details.append(f"Регион: {region}")
        
        details.append(f"Происхождение: {origin}")
        
        if acc.rubles > 0:
            details.append(f"В игре: {acc.rubles:,} ₽")
        if acc.dollars > 0 or acc.euros > 0:
            details.append(f"Валюта: ${acc.dollars}, €{acc.euros}")
        if acc.nsb:
            details.append("Не продавался ранее")
        if acc.pve_access:
            details.append("Доступ к PVE")
        if acc.allow_ask_discount and acc.max_discount_percent > 0:
            details.append(f"Скидка до {acc.max_discount_percent}%")
        
        if details:
            msg += f"\n\n{' • '.join(details[:4])}"
            if len(details) > 4:
                msg += f"\n{' • '.join(details[4:])}"
        
        msg += f"\n\n<b>Продавец:</b> {acc.seller_username} ({acc.seller_sold_items:,} продаж"
        if acc.seller_restore_percent is not None:
            msg += f", {acc.seller_restore_percent}% возвратов"
        msg += ")"
        
        msg += f"\n<b>Оценка:</b> {deal.score:.1f}/100"
        msg += f"\n<b>Причины:</b> {deal.reason}"
        
        if deal.discount_potential > 0:
            msg += f"\n<b>Потенциал скидки:</b> {deal.discount_potential}%"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Перейти к предложению", url=acc.url)]
        ])
        
        return msg, kb
    
    def _get_cat_name(self, acc, settings: UserSettings) -> str:
        if acc.game_version:
            return CATEGORIES["escape_from_tarkov"]["name"]
        for cat in settings.categories:
            if cat in CATEGORIES:
                return CATEGORIES[cat]["name"]
        return "Неизвестная категория"
    
    async def cleanup(self):
        try:
            await self.db.cleanup_old_seen_items(7)
            print("Очистка завершена")
        except Exception as e:
            print(f"Ошибка очистки: {e}")
    
    async def send_test_notification(self, user_id: int):
        settings = await self.db.get_user_settings(user_id)
        if not settings:
            return False
        
        try:
            accounts = await self.api.get_all_accounts(settings)
            if accounts:
                deals = self.analyzer.analyze_deals(accounts[:10], settings)
                if deals:
                    await self.send_notification(user_id, deals[0], settings)
                    return True
            
            await self.bot.send_message(user_id, "Тест отправлен!\nНет подходящих предложений.")
            return True
        except Exception as e:
            print(f"Ошибка теста: {e}")
            return False

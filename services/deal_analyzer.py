from typing import List, Dict, Any, Tuple
from utils.models import TarkovAccount, DealAlert, UserSettings, GAME_VERSION_NAMES, CATEGORIES
import time


class DealAnalyzer:
    def __init__(self):
        self.avg_prices = {
            "escape_from_tarkov": {
                "standard": 1800, "left_behind": 2500, "prepare_for_escape": 3200,
                "edge_of_darkness": 4500, "unheard_edition": 6000
            },
            "steam": {"default": 500}, "fortnite": {"default": 300},
            "riot": {"default": 400}, "telegram": {"default": 50},
            "supercell": {"default": 200}, "epic_games": {"default": 300},
            "social_club": {"default": 800}, "uplay": {"default": 400},
            "discord": {"default": 100}, "battlenet": {"default": 600},
            "roblox": {"default": 150}, "minecraft": {"default": 200},
            "chatgpt": {"default": 300}, "mihoyo": {"default": 500},
            "world_of_tanks": {"default": 300}, "wot_blitz": {"default": 200},
            "ea_origin": {"default": 400}
        }
        
        self.level_multipliers = {
            range(0, 10): 1.0, range(10, 20): 1.1, range(20, 30): 1.2,
            range(30, 40): 1.3, range(40, 50): 1.4, range(50, 100): 1.5
        }
    
    def analyze_deals(self, accounts: List[TarkovAccount], settings: UserSettings) -> List[DealAlert]:
        deals = []
        for account in accounts:
            score, reasons = self._calc_score(account, settings)
            score = min(score, 100) 
            if score >= 60:
                deals.append(DealAlert(
                    account=account,
                    reason="; ".join(reasons),
                    score=score,
                    discount_potential=self._calc_discount(account)
                ))
        return sorted(deals, key=lambda x: x.score, reverse=True)
    
    def _calc_score(self, acc: TarkovAccount, settings: UserSettings) -> Tuple[float, List[str]]:
        score, reasons = 0.0, []
        category = self._get_category(acc, settings)
        expected = self._get_expected_price(acc, category)

        if expected > 0:
            ratio = acc.price / expected
            if ratio < 0.7:
                score += 30
                reasons.append(f"Цена на {int((1-ratio)*100)}% ниже средней")
            elif ratio < 0.8:
                score += 20
                reasons.append(f"Цена на {int((1-ratio)*100)}% ниже средней")
            elif ratio < 0.9:
                score += 10
                reasons.append("Цена немного ниже средней")

        if category == "escape_from_tarkov":
            if acc.level > 0:
                level_bonus = min(acc.level * 0.5, 15)
                score += level_bonus
                if acc.level >= 30:
                    reasons.append(f"Высокий уровень ({acc.level})")
                elif acc.level >= 15:
                    reasons.append(f"Средний уровень ({acc.level})")
            if acc.rubles > 500000:
                score += min((acc.rubles / 100000) * 2, 15)
                reasons.append(f"Много рублей ({acc.rubles:,})")
            if acc.dollars > 1000 or acc.euros > 1000:
                score += 8
                reasons.append(f"Валюта: ${acc.dollars}, €{acc.euros}")
            if acc.pve_access:
                score += 5
                reasons.append("Доступ к PVE")
            if acc.game_version in ["edge_of_darkness", "unheard_edition"]:
                score += 8
                reasons.append(f"Премиум издание ({GAME_VERSION_NAMES.get(acc.game_version, acc.game_version)})")
        else:
            if acc.nsb:
                score += 12
                reasons.append("Не продавался ранее")
            if acc.allow_ask_discount and acc.max_discount_percent > settings.max_discount_threshold:
                score += min(acc.max_discount_percent * 0.3, 15)
                reasons.append(f"Возможна скидка до {acc.max_discount_percent}%")
            trust_score = self._calc_trust(acc)
            score += trust_score
            if trust_score > 5:
                reasons.append("Надежный продавец")
            fresh_score = self._calc_freshness(acc)
            score += fresh_score
            if fresh_score > 3:
                reasons.append("Свежее предложение")
        return score, reasons
    
    def _get_category(self, acc: TarkovAccount, settings: UserSettings) -> str:
        if acc.game_version:
            return "escape_from_tarkov"
        for cat in settings.categories:
            if cat in self.avg_prices:
                return cat
        return "default"
    
    def _get_expected_price(self, acc: TarkovAccount, category: str) -> float:
        if category == "escape_from_tarkov":
            base = self.avg_prices["escape_from_tarkov"].get(acc.game_version, 2000)
            
            for level_range, mult in self.level_multipliers.items():
                if acc.level in level_range:
                    base *= mult
                    break
            
            if acc.rubles > 1000000:
                base += (acc.rubles / 100000) * 50
            if acc.nsb:
                base *= 1.1
            return base
        return self.avg_prices.get(category, {}).get("default", 500)
    
    def _calc_trust(self, acc: TarkovAccount) -> float:
        score = 0.0
        if acc.seller_sold_items > 1000:
            score += 8
        elif acc.seller_sold_items > 500:
            score += 5
        elif acc.seller_sold_items > 100:
            score += 3
        
        if acc.seller_restore_percent is not None:
            if acc.seller_restore_percent <= 5:
                score += 5
            elif acc.seller_restore_percent <= 10:
                score += 2
        return min(score, 10)
    
    def _calc_freshness(self, acc: TarkovAccount) -> float:
        hours = (int(time.time()) - acc.published_date) / 3600
        if hours < 1:
            return 8
        elif hours < 6:
            return 5
        elif hours < 24:
            return 3
        return 0
    
    def _calc_discount(self, acc: TarkovAccount) -> int:
        if not acc.allow_ask_discount:
            return 0
        potential = acc.max_discount_percent
        if acc.seller_sold_items > 1000:
            potential = min(potential + 5, 50)
        return potential

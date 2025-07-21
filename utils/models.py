from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class GameVersion(Enum):
    STANDARD = "standard"
    LEFT_BEHIND = "left_behind"
    PREPARE_FOR_ESCAPE = "prepare_for_escape"
    EDGE_OF_DARKNESS = "edge_of_darkness"
    UNHEARD_EDITION = "unheard_edition"


class Region(Enum):
    AF = "af"
    AS = "as"
    CIS = "cis"
    EU = "eu"
    ME = "me"
    OC = "oc"
    US = "us"


class ItemOrigin(Enum):
    BRUTE = "brute"
    PHISHING = "phishing"
    STEALER = "stealer"
    PERSONAL = "personal"
    RESALE = "resale"
    AUTOREG = "autoreg"
    SELF_REG = "self_registration"
    RETRIEVE = "retrieve"
    RETRIEVE_SUPPORT = "retrieve_via_support"
    DUMMY = "dummy"


@dataclass
class UserSettings:
    user_id: int
    categories: List[str]
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    game_versions: List[str] = None
    regions: List[str] = None
    origins: List[str] = None
    min_level: Optional[int] = None
    max_level: Optional[int] = None
    order_by: str = "price_to_up"
    show: str = "active"
    nsb: Optional[bool] = None
    sb: Optional[bool] = None
    email_login_data: Optional[bool] = None
    pve_access: Optional[str] = None
    notifications_enabled: bool = True
    max_discount_threshold: int = 20


@dataclass
class TarkovAccount:
    item_id: int
    title: str
    price: int
    price_with_seller_fee: float
    game_version: str
    level: int
    region: str
    origin: str
    seller_username: str
    seller_sold_items: int
    seller_restore_percent: Optional[int]
    rubles: int
    dollars: int
    euros: int
    nsb: bool
    allow_ask_discount: bool
    max_discount_percent: int
    published_date: int
    last_activity: int
    email_type: str
    email_provider: str
    pve_access: bool
    url: str


@dataclass
class DealAlert:
    account: TarkovAccount
    reason: str
    score: float
    discount_potential: int


CATEGORIES = {
    "steam": {"name": "Steam", "id": 1, "endpoint": "steam"},
    "fortnite": {"name": "Fortnite", "id": 9, "endpoint": "fortnite"},
    "riot": {"name": "Riot", "id": 13, "endpoint": "riot"},
    "telegram": {"name": "Telegram", "id": 17, "endpoint": "telegram"},
    "supercell": {"name": "Supercell", "id": 12, "endpoint": "supercell"},
    "gifts": {"name": "Gifts", "id": 5, "endpoint": "gifts"},
    "epic_games": {"name": "Epic Games", "id": 14, "endpoint": "epic-games"},
    "escape_from_tarkov": {"name": "Escape from Tarkov", "id": 18, "endpoint": "escape-from-tarkov"},
    "social_club": {"name": "Social Club", "id": 3, "endpoint": "social-club"},
    "uplay": {"name": "Uplay", "id": 11, "endpoint": "uplay"},
    "war_thunder": {"name": "War Thunder", "id": 7, "endpoint": "war-thunder"},
    "discord": {"name": "Discord", "id": 31, "endpoint": "discord"},
    "tiktok": {"name": "TikTok", "id": 35, "endpoint": "tiktok"},
    "instagram": {"name": "Instagram", "id": 32, "endpoint": "instagram"},
    "battlenet": {"name": "BattleNet", "id": 15, "endpoint": "battlenet"},
    "vpn": {"name": "VPN", "id": 4, "endpoint": "vpn"},
    "roblox": {"name": "Roblox", "id": 33, "endpoint": "roblox"},
    "warface": {"name": "Warface", "id": 36, "endpoint": "warface"},
    "minecraft": {"name": "Minecraft", "id": 37, "endpoint": "minecraft"},
    "chatgpt": {"name": "ChatGPT", "id": 38, "endpoint": "chatgpt"},
    "mihoyo": {"name": "miHoYo", "id": 39, "endpoint": "mihoyo"},
    "world_of_tanks": {"name": "World of Tanks", "id": 40, "endpoint": "world-of-tanks"},
    "wot_blitz": {"name": "WoT Blitz", "id": 41, "endpoint": "wot-blitz"},
    "ea_origin": {"name": "EA (Origin)", "id": 42, "endpoint": "ea-origin"}
}

GAME_VERSION_NAMES = {
    "standard": "Standard Edition",
    "left_behind": "Left Behind Edition", 
    "prepare_for_escape": "Prepare for Escape Edition",
    "edge_of_darkness": "Edge of Darkness Edition",
    "unheard_edition": "The Unheard Edition"
}

REGION_NAMES = {
    "af": "Африка",
    "as": "Азия", 
    "cis": "Россия + СНГ",
    "eu": "Европа",
    "me": "Ближний Восток",
    "oc": "Океания",
    "us": "Северная Америка"
}

ORIGIN_NAMES = {
    "brute": "Брут",
    "phishing": "Фишинг", 
    "stealer": "Стилер",
    "personal": "Личный",
    "resale": "Перепродажа",
    "autoreg": "Авторег",
    "self_registration": "Самостоятельная регистрация",
    "retrieve": "Восстановление",
    "retrieve_via_support": "Восстановление через поддержку",
    "dummy": "Пустой"
}

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List
from utils.models import CATEGORIES, GAME_VERSION_NAMES, REGION_NAMES, ORIGIN_NAMES


def get_cats_kb(selected: List[str] = None) -> InlineKeyboardMarkup:
    selected = selected or []
    builder = InlineKeyboardBuilder()
    
    for key, cat in CATEGORIES.items():
        check = "✅ " if key in selected else ""
        builder.button(text=f"{check}{cat['name']}", callback_data=f"category_{key}")
    
    builder.button(text="Далее", callback_data="categories_next")
    builder.adjust(3)
    return builder.as_markup()


def get_edit_cats_kb(selected: List[str] = None) -> InlineKeyboardMarkup:
    selected = selected or []
    builder = InlineKeyboardBuilder()
    
    for key, cat in CATEGORIES.items():
        check = "✅ " if key in selected else ""
        builder.button(text=f"{check}{cat['name']}", callback_data=f"edit_category_{key}")
    
    builder.button(text="✅ Сохранить", callback_data="save_categories")
    builder.button(text="Назад", callback_data="back_to_main")
    builder.adjust(3)
    return builder.as_markup()


def get_settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        ("Цена", "settings_price"), ("Издания", "settings_versions"),
        ("Регионы", "settings_regions"), ("Происхождение", "settings_origins"),
        ("Уровень", "settings_level"), ("Почта", "settings_email"),
        ("Сортировка", "settings_sorting"), ("PVE", "settings_pve"),
        ("Статус продажи", "settings_sale"), ("Скидки", "settings_discounts"),
        ("✅ Завершить", "settings_complete")
    ]
    
    for text, data in buttons:
        builder.button(text=text, callback_data=data)
    builder.adjust(2)
    return builder.as_markup()


def get_versions_kb(selected: List[str] = None) -> InlineKeyboardMarkup:
    selected = selected or []
    builder = InlineKeyboardBuilder()
    
    for key, name in GAME_VERSION_NAMES.items():
        check = "✅ " if key in selected else ""
        builder.button(text=f"{check}{name}", callback_data=f"version_{key}")
    
    builder.button(text="Назад", callback_data="back_to_settings")
    builder.adjust(1)
    return builder.as_markup()


def get_regions_kb(selected: List[str] = None) -> InlineKeyboardMarkup:
    selected = selected or []
    builder = InlineKeyboardBuilder()
    
    for key, name in REGION_NAMES.items():
        check = "✅ " if key in selected else ""
        builder.button(text=f"{check}{name}", callback_data=f"region_{key}")
    
    builder.button(text="Назад", callback_data="back_to_settings")
    builder.adjust(2)
    return builder.as_markup()


def get_origins_kb(selected: List[str] = None) -> InlineKeyboardMarkup:
    selected = selected or []
    builder = InlineKeyboardBuilder()
    
    for key, name in ORIGIN_NAMES.items():
        check = "✅ " if key in selected else ""
        builder.button(text=f"{check}{name}", callback_data=f"origin_{key}")
    
    builder.button(text="Назад", callback_data="back_to_settings")
    builder.adjust(2)
    return builder.as_markup()


def get_sort_kb(current: str = "price_to_up") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    options = {
        "price_to_up": "Сначала дешевые", "price_to_down": "Сначала дорогие",
        "pdate_to_down": "Новые", "pdate_to_up": "Старые",
        "pdate_to_down_upload": "Недавно загруженные",
        "edate_to_up": "Недавно отредактированные"
    }
    
    for key, name in options.items():
        check = "✅ " if key == current else ""
        builder.button(text=f"{check}{name}", callback_data=f"sort_{key}")
    
    builder.button(text="Назад", callback_data="back_to_settings")
    builder.adjust(1)
    return builder.as_markup()


def get_pve_kb(current: str = "nomatter") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    options = {
        "yes": "✅ Только с PVE", "no": "❌ Только без PVE", "nomatter": "Не важно"
    }
    
    for key, name in options.items():
        check = "✅ " if key == current else ""
        builder.button(text=f"{check}{name}", callback_data=f"pve_{key}")
    
    builder.button(text="Назад", callback_data="back_to_settings")
    builder.adjust(1)
    return builder.as_markup()


def get_sale_kb(nsb: bool = None, sb: bool = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    nsb_text = "✅ Не продавался ранее" if nsb else "Не продавался ранее"
    sb_text = "✅ Продавался ранее" if sb else "Продавался ранее"
    
    builder.button(text=nsb_text, callback_data="toggle_nsb")
    builder.button(text=sb_text, callback_data="toggle_sb")
    builder.button(text="Назад", callback_data="back_to_settings")
    builder.adjust(1)
    return builder.as_markup()


def get_email_kb(email: bool = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    text = "✅ С доступом к почте" if email else "С доступом к почте"
    
    builder.button(text=text, callback_data="toggle_email")
    builder.button(text="Назад", callback_data="back_to_settings")
    builder.adjust(1)
    return builder.as_markup()


def get_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = [
        ("Редактировать категории", "edit_categories"),
        ("Настройки", "open_settings"),
        ("Мои настройки", "view_settings"),
        ("Уведомления", "toggle_notifications"),
        ("Статистика", "view_stats")
    ]
    
    for text, data in buttons:
        builder.button(text=text, callback_data=data)
    builder.adjust(2)
    return builder.as_markup()

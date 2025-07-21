from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import List

from utils.database import Database
from utils.models import UserSettings, CATEGORIES, GAME_VERSION_NAMES, REGION_NAMES, ORIGIN_NAMES
from utils.keyboards import *


class States(StatesGroup):
    selecting_cats = State()
    editing_cats = State()
    settings_menu = State()
    price_min = State()
    price_max = State()
    level_min = State()
    level_max = State()
    discount_threshold = State()


router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext, db: Database):
    user_id = message.from_user.id
    existing = await db.get_user_settings(user_id)
    
    text = """🤖 <b>Lolz Market Deal Finder</b>\n\nПривет! Я бот для поиска выгодных предложений на Lolz Market. Я отслеживаю новые объявления, анализирую их выгодность по цене, уровню, репутации продавца и возможности скидки, и уведомляю только о действительно интересных вариантах с учётом ваших фильтров.\n\nАнализ каждого предложения учитывает рыночную стоимость, характеристики аккаунта, надёжность продавца и потенциальную скидку, чтобы вы не пропустили лучшие сделки на маркете."""
    
    if existing:
        await message.answer(text + "\n\nУ вас есть настройки.", reply_markup=get_main_kb(), parse_mode="HTML")
    else:
        await message.answer(text + "\n\nВыберите категории:", reply_markup=get_cats_kb(), parse_mode="HTML")
        await state.set_state(States.selecting_cats)


@router.callback_query(F.data.startswith("category_"))
async def handle_cat(callback: CallbackQuery, state: FSMContext):
    cat = callback.data.split("_", 1)[1]
    data = await state.get_data()
    selected = data.get("selected_cats", [])
    
    if cat in selected:
        selected.remove(cat)
    else:
        selected.append(cat)
    
    await state.update_data(selected_cats=selected)
    await callback.message.edit_reply_markup(reply_markup=get_cats_kb(selected))
    await callback.answer()


@router.callback_query(F.data == "categories_next")
async def cats_next(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_cats", [])
    
    if not selected:
        await callback.answer("Выберите хотя бы одну категорию!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⚙️ <b>Настройка параметров</b>\n\nВыберите что настроить или завершите:",
        reply_markup=get_settings_kb(), parse_mode="HTML"
    )
    await state.set_state(States.settings_menu)
    await callback.answer()


@router.callback_query(F.data == "edit_categories")
async def edit_cats(callback: CallbackQuery, state: FSMContext, db: Database):
    settings = await db.get_user_settings(callback.from_user.id)
    if not settings:
        await callback.answer("Настройки не найдены. Используйте /start", show_alert=True)
        return
    
    await state.update_data(selected_cats=settings.categories.copy())
    await callback.message.edit_text(
        "📂 <b>Редактирование категорий</b>\n\nВыберите активные категории:",
        reply_markup=get_edit_cats_kb(settings.categories), parse_mode="HTML"
    )
    await state.set_state(States.editing_cats)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_category_"))
async def edit_cat(callback: CallbackQuery, state: FSMContext):
    cat = callback.data.split("_", 2)[2]
    data = await state.get_data()
    selected = data.get("selected_cats", [])
    
    if cat in selected:
        selected.remove(cat)
    else:
        selected.append(cat)
    
    await state.update_data(selected_cats=selected)
    await callback.message.edit_reply_markup(reply_markup=get_edit_cats_kb(selected))
    await callback.answer()


@router.callback_query(F.data == "save_categories")
async def save_cats(callback: CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()
    selected = data.get("selected_cats", [])
    
    if not selected:
        await callback.answer("Выберите хотя бы одну категорию!", show_alert=True)
        return
    
    settings = await db.get_user_settings(callback.from_user.id)
    if settings:
        settings.categories = selected
        await db.save_user_settings(callback.from_user.id, settings)
        
        names = [CATEGORIES[cat]["name"] for cat in selected if cat in CATEGORIES]
        await callback.message.edit_text(
            f"✅ <b>Категории обновлены!</b>\n\n<b>Активные:</b>\n{', '.join(names)}",
            reply_markup=get_main_kb(), parse_mode="HTML"
        )
        await state.clear()
        await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def back_main(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🤖 <b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=get_main_kb(), parse_mode="HTML"
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "settings_price")
async def set_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💰 <b>Ценовой диапазон</b>\n\nВведите минимальную цену (или '-' для пропуска):",
        parse_mode="HTML"
    )
    await state.set_state(States.price_min)
    await callback.answer()


@router.message(States.price_min)
async def price_min_input(message: Message, state: FSMContext):
    try:
        min_price = None if message.text == "-" else int(message.text)
        await state.update_data(min_price=min_price)
        await message.answer("Введите максимальную цену (или '-' для пропуска):")
        await state.set_state(States.price_max)
    except ValueError:
        await message.answer("Введите число или '-'")


@router.message(States.price_max)
async def price_max_input(message: Message, state: FSMContext):
    try:
        max_price = None if message.text == "-" else int(message.text)
        await state.update_data(max_price=max_price)
        
        data = await state.get_data()
        text = "Настройка цены завершена!\n\n"
        if data.get("min_price"):
            text += f"Мин: {data['min_price']:,} ₽\n"
        if max_price:
            text += f"Макс: {max_price:,} ₽\n"
        
        await message.answer(text + "\nВозврат к настройкам:", reply_markup=get_settings_kb())
        await state.set_state(States.settings_menu)
    except ValueError:
        await message.answer("Введите число или '-'")


@router.callback_query(F.data == "settings_versions")
async def set_versions(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("game_versions", [])
    await callback.message.edit_text(
        "🎮 <b>Издания игры</b>\n\nВыберите издания Escape from Tarkov:",
        reply_markup=get_versions_kb(selected), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("version_"))
async def handle_version(callback: CallbackQuery, state: FSMContext):
    version = callback.data.split("_", 1)[1]
    data = await state.get_data()
    selected = data.get("game_versions", [])
    
    if version in selected:
        selected.remove(version)
    else:
        selected.append(version)
    
    await state.update_data(game_versions=selected)
    await callback.message.edit_reply_markup(reply_markup=get_versions_kb(selected))
    await callback.answer()


@router.callback_query(F.data == "settings_regions")
async def set_regions(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("regions", [])
    await callback.message.edit_text(
        "🌍 <b>Регионы</b>\n\nВыберите регионы:",
        reply_markup=get_regions_kb(selected), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("region_"))
async def handle_region(callback: CallbackQuery, state: FSMContext):
    region = callback.data.split("_", 1)[1]
    data = await state.get_data()
    selected = data.get("regions", [])
    
    if region in selected:
        selected.remove(region)
    else:
        selected.append(region)
    
    await state.update_data(regions=selected)
    await callback.message.edit_reply_markup(reply_markup=get_regions_kb(selected))
    await callback.answer()


@router.callback_query(F.data == "settings_complete")
async def complete_settings(callback: CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()
    
    settings = UserSettings(
        user_id=callback.from_user.id,
        categories=data.get("selected_cats", ["escape_from_tarkov"]),
        min_price=data.get("min_price"),
        max_price=data.get("max_price"),
        game_versions=data.get("game_versions", []),
        regions=data.get("regions", []),
        origins=data.get("origins", []),
        min_level=data.get("min_level"),
        max_level=data.get("max_level"),
        order_by=data.get("order_by", "price_to_up"),
        show=data.get("show", "active"),
        nsb=data.get("nsb"),
        sb=data.get("sb"),
        email_login_data=data.get("email_login_data"),
        pve_access=data.get("pve_access"),
        max_discount_threshold=data.get("max_discount_threshold", 20)
    )
    
    await db.save_user_settings(callback.from_user.id, settings)
    await callback.message.edit_text(
        "✅ <b>Настройки сохранены!</b>\n\nБот начнет отслеживать предложения.",
        reply_markup=get_main_kb(), parse_mode="HTML"
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def back_settings(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n\nВыберите параметр:",
        reply_markup=get_settings_kb(), parse_mode="HTML"
    )
    await state.set_state(States.settings_menu)
    await callback.answer()


@router.callback_query(F.data == "open_settings")
async def open_settings(callback: CallbackQuery, state: FSMContext, db: Database):
    settings = await db.get_user_settings(callback.from_user.id)
    if settings:
        await state.update_data(
            selected_cats=settings.categories,
            min_price=settings.min_price,
            max_price=settings.max_price,
            game_versions=settings.game_versions or [],
            regions=settings.regions or [],
            origins=settings.origins or [],
            min_level=settings.min_level,
            max_level=settings.max_level,
            order_by=settings.order_by,
            show=settings.show,
            nsb=settings.nsb,
            sb=settings.sb,
            email_login_data=settings.email_login_data,
            pve_access=settings.pve_access,
            max_discount_threshold=settings.max_discount_threshold
        )
    
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n\nВыберите что изменить:",
        reply_markup=get_settings_kb(), parse_mode="HTML"
    )
    await state.set_state(States.settings_menu)
    await callback.answer()


@router.callback_query(F.data == "view_settings")
async def view_settings(callback: CallbackQuery, db: Database):
    settings = await db.get_user_settings(callback.from_user.id)
    if not settings:
        await callback.answer("Настройки не найдены. Используйте /start", show_alert=True)
        return
    
    text = "📊 <b>Текущие настройки:</b>\n\n"
    
    if settings.categories:
        names = [CATEGORIES[cat]["name"] for cat in settings.categories if cat in CATEGORIES]
        text += f"<b>Категории:</b> {', '.join(names)}\n\n"
    
    if settings.min_price or settings.max_price:
        price_range = []
        if settings.min_price:
            price_range.append(f"от {settings.min_price:,} ₽")
        if settings.max_price:
            price_range.append(f"до {settings.max_price:,} ₽")
        text += f"<b>Цена:</b> {' '.join(price_range)}\n\n"
    
    if settings.game_versions:
        versions = [GAME_VERSION_NAMES.get(v, v) for v in settings.game_versions]
        text += f"<b>Издания:</b> {', '.join(versions)}\n\n"
    
    text += f"<b>Уведомления:</b> {'включены' if settings.notifications_enabled else 'выключены'}\n"
    text += f"<b>Мин. скидка:</b> {settings.max_discount_threshold}%"
    
    await callback.message.edit_text(text, reply_markup=get_main_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "toggle_notifications")
async def toggle_notif(callback: CallbackQuery, db: Database):
    settings = await db.get_user_settings(callback.from_user.id)
    if not settings:
        await callback.answer("Настройки не найдены", show_alert=True)
        return
    
    settings.notifications_enabled = not settings.notifications_enabled
    await db.save_user_settings(callback.from_user.id, settings)
    
    status = "включены" if settings.notifications_enabled else "выключены"
    await callback.answer(f"Уведомления {status}")
    
    try:
        await callback.message.edit_reply_markup(reply_markup=get_main_kb())
    except:
        pass


@router.callback_query(F.data == "view_stats")
async def view_stats(callback: CallbackQuery, db: Database):
    try:
        total = len(await db.get_all_users())
        text = f"📈 <b>Статистика</b>\n\n<b>Пользователей:</b> {total}\n<b>Статус:</b> Активно"
        
        await callback.message.edit_text(text, reply_markup=get_main_kb(), parse_mode="HTML")
        await callback.answer()
    except Exception:
        await callback.answer("Ошибка получения статистики", show_alert=True)


@router.message(Command("test"))
async def test_cmd(message: Message, monitoring):
    await message.answer("Отправляю тест...")
    success = await monitoring.send_test_notification(message.from_user.id)
    
    if success:
        await message.answer("Тест отправлен!")
    else:
        await message.answer("Ошибка теста. Проверьте настройки.")

@router.callback_query(F.data == "settings_email")
async def set_email(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    email = data.get("email_login_data")
    await callback.message.edit_text(
        "📧 <b>Почта</b>\n\nТребовать доступ к почте?",
        reply_markup=get_email_kb(email), parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "toggle_email")
async def toggle_email(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    email = data.get("email_login_data")
    new_email = not email if email is not None else True
    await state.update_data(email_login_data=new_email)
    await callback.message.edit_reply_markup(reply_markup=get_email_kb(new_email))
    await callback.answer()

@router.callback_query(F.data == "settings_sorting")
async def set_sorting(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data.get("order_by", "price_to_up")
    await callback.message.edit_text(
        "🔄 <b>Сортировка</b>\n\nВыберите способ сортировки:",
        reply_markup=get_sort_kb(current), parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("sort_"))
async def handle_sorting(callback: CallbackQuery, state: FSMContext):
    sorting = callback.data.split("_", 1)[1]
    await state.update_data(order_by=sorting)
    await callback.message.edit_reply_markup(reply_markup=get_sort_kb(sorting))
    await callback.answer("Сортировка изменена!")

@router.callback_query(F.data == "settings_pve")
async def set_pve(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current = data.get("pve_access", "nomatter")
    await callback.message.edit_text(
        "🎯 <b>PVE</b>\n\nВыберите предпочтения по PVE:",
        reply_markup=get_pve_kb(current), parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pve_"))
async def handle_pve(callback: CallbackQuery, state: FSMContext):
    pve = callback.data.split("_", 1)[1]
    await state.update_data(pve_access=pve)
    await callback.message.edit_reply_markup(reply_markup=get_pve_kb(pve))
    await callback.answer("Настройка PVE изменена!")

@router.callback_query(F.data == "settings_sale")
async def set_sale(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nsb = data.get("nsb")
    sb = data.get("sb")
    await callback.message.edit_text(
        "📊 <b>Статус продажи</b>\n\nНастройте предпочтения:",
        reply_markup=get_sale_kb(nsb, sb), parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "toggle_nsb")
async def toggle_nsb(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nsb = data.get("nsb")
    new_nsb = not nsb if nsb is not None else True
    await state.update_data(nsb=new_nsb)
    sb = data.get("sb")
    await callback.message.edit_reply_markup(reply_markup=get_sale_kb(new_nsb, sb))
    await callback.answer()

@router.callback_query(F.data == "toggle_sb")
async def toggle_sb(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sb = data.get("sb")
    new_sb = not sb if sb is not None else True
    await state.update_data(sb=new_sb)
    nsb = data.get("nsb")
    await callback.message.edit_reply_markup(reply_markup=get_sale_kb(nsb, new_sb))
    await callback.answer()

@router.callback_query(F.data == "settings_discounts")
async def set_discounts(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💸 <b>Порог скидки</b>\n\nВведите минимальный процент скидки (по умолчанию 20):",
        parse_mode="HTML"
    )
    await state.set_state(States.discount_threshold)
    await callback.answer()

@router.message(States.discount_threshold)
async def discount_input(message: Message, state: FSMContext):
    try:
        val = int(message.text)
        if val < 0 or val > 100:
            await message.answer("Процент должен быть от 0 до 100.")
            return
        await state.update_data(max_discount_threshold=val)
        await message.answer(f"Порог скидки установлен: {val}%\n\nВозврат к настройкам:", reply_markup=get_settings_kb())
        await state.set_state(States.settings_menu)
    except ValueError:
        await message.answer("Введите число от 0 до 100.")

@router.callback_query(F.data == "settings_origins")
async def set_origins(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("origins", [])
    await callback.message.edit_text(
        "📦 <b>Происхождение</b>\n\nВыберите происхождение:",
        reply_markup=get_origins_kb(selected), parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("origin_"))
async def handle_origin(callback: CallbackQuery, state: FSMContext):
    origin = callback.data.split("_", 1)[1]
    data = await state.get_data()
    selected = data.get("origins", [])
    if origin in selected:
        selected.remove(origin)
    else:
        selected.append(origin)
    await state.update_data(origins=selected)
    await callback.message.edit_reply_markup(reply_markup=get_origins_kb(selected))
    await callback.answer()

@router.callback_query(F.data == "settings_level")
async def set_level(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⭐ <b>Уровень</b>\n\nВведите минимальный уровень (или '-' для пропуска):",
        parse_mode="HTML"
    )
    await state.set_state(States.level_min)
    await callback.answer()

@router.message(States.level_min)
async def level_min_input(message: Message, state: FSMContext):
    try:
        min_level = None if message.text == "-" else int(message.text)
        await state.update_data(min_level=min_level)
        await message.answer("Введите максимальный уровень (или '-' для пропуска):")
        await state.set_state(States.level_max)
    except ValueError:
        await message.answer("Введите число или '-'")

@router.message(States.level_max)
async def level_max_input(message: Message, state: FSMContext):
    try:
        max_level = None if message.text == "-" else int(message.text)
        await state.update_data(max_level=max_level)
        data = await state.get_data()
        text = "Настройка уровня завершена!\n\n"
        if data.get("min_level"):
            text += f"Мин: {data['min_level']}\n"
        if max_level:
            text += f"Макс: {max_level}\n"
        await message.answer(text + "\nВозврат к настройкам:", reply_markup=get_settings_kb())
        await state.set_state(States.settings_menu)
    except ValueError:
        await message.answer("Введите число или '-'")

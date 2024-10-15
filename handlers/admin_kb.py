import aiosqlite

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from FSM import AddServiceStates
from functions import get_service_status
from keyboards import start_kb

router = Router()

# Добавление новой службы - ввод имени
@router.callback_query(F.data == "add_service")
async def add_service_name(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()  # Это предотвратит мигание
    await callback_query.message.answer("Впишите название службы:")
    await state.set_state(AddServiceStates.waiting_for_service_name)

# Обработчик ввода имени службы
@router.message(AddServiceStates.waiting_for_service_name)
async def add_service(message: Message, state: FSMContext) -> None:
    service_name = message.text
    status = get_service_status(service_name)  # Проверяем статус службы через systemctl
    # Сохранение в базу данных
    async with aiosqlite.connect("database.db") as db:
        await db.execute("INSERT INTO services (name, status) VALUES (?, ?)", (service_name, status))
        await db.commit()
    await message.answer(f"Служба {service_name} добавлена")
    await state.clear()  # Сбрасываем состояние

# Функция для отображения всех служб
@router.callback_query(F.data == "view_services")
async def show_services(callback_query: CallbackQuery, bot: Bot) -> None:
    await callback_query.answer()
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT name, status FROM services") as cursor:
            services = await cursor.fetchall()
            if services:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[])
                for service in services:
                    status_icon = "✅" if service[1] == "active" else "❌"
                    keyboard.inline_keyboard.append([InlineKeyboardButton(text=f"{service[0]} {status_icon}", callback_data=f"service_{service[0]}")])
                keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main")])
                await callback_query.message.edit_text("Список служб:", reply_markup=keyboard)
            else:
                await bot.send_message(callback_query.from_user.id, "Нет доступных служб")

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback_query: CallbackQuery):
    # Редактируем текущее сообщение, обновляя клавиатуру
    await callback_query.message.edit_text("Вы администратор. Выберите действие:", reply_markup=start_kb)
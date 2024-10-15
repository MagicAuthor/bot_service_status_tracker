from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import ADMINS
from keyboards import start_kb

router = Router()

# Добавляем проверку на администратора через фильтр
async def is_admin(message: Message):
    return message.from_user.id in ADMINS

@router.message(CommandStart(), is_admin)
async def start_command(message: Message, state: FSMContext) -> None:
    # Сохраняем состояние админа
    await state.update_data(is_admin=True)
    await message.answer("Вы администратор. Выберите действие:", reply_markup=start_kb)

@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext) -> None:
    # Проверяем, является ли пользователь админом из состояния
    data = await state.get_data()
    if data.get("is_admin"):
        await message.answer("Вы администратор. Выберите действие:", reply_markup=start_kb)
    else:
        await message.answer("У вас нет доступа к функционалу бота")
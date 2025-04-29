from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import app.keyboards as keyboards

router = Router()

@router.message(CommandStart())
@router.message(F.text == 'Старт')
async def start(message: Message):
    await message.answer('Добро пожаловать в PORT. Чем я могу Вам помочь?', reply_markup=keyboards.main_menu)

@router.callback_query(F.data == 'start')
async def main_menu(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Добро пожаловать в PORT. Чем я могу Вам помочь?', reply_markup=keyboards.main_menu)

@router.callback_query(F.data == 'categories')
async def categories(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Выберите категорию меню', reply_markup=keyboards.categories)

@router.callback_query(F.data == 'exit')
async def categories(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('До свидания!', reply_markup=keyboards.exit)

@router.callback_query(F.data == 'questions')
async def categories(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Выберите интересующий вас вопрос:', reply_markup=keyboards.questions)

@router.callback_query(F.data == 'dog')
async def categories(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('НЕТ!', reply_markup=keyboards.return_or_admin)

@router.callback_query(F.data == 'parking')
async def categories(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('ПРИХОДИТЕ ПЕШКОМ!', reply_markup=keyboards.return_or_admin)

@router.callback_query(F.data == 'сhild_seat')
async def categories(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('ЗАВЕДЕНИЕ ТОЛЬКО ДЛЯ ВЗРОСЛЫХ С БЛЕК_ДЖЕКОМ И ШЛ....!', reply_markup=keyboards.return_or_admin)

@router.callback_query(F.data == 'bron_number')
async def categories(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Телефон для бронирования столиков +78452252268', reply_markup=keyboards.return_or_admin)
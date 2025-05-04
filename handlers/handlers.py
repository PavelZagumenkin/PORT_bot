from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
import keyboards.keyboards as keyboards
from config import ADMIN_ID
from database.database import SessionLocal, User, Broadcast

router = Router()

class BroadcastState(StatesGroup):
    waiting_for_broadcast_text = State()

@router.message(CommandStart())
async def start(message: Message):
    db = SessionLocal()
    existing = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not existing:
        new_user = User(telegram_id=message.from_user.id, name=message.from_user.full_name)
        db.add(new_user)
        db.commit()
        await message.answer('Добро пожаловать в PORT. Вы подписались на нашу рассылку. Чем я могу Вам помочь?', reply_markup=keyboards.main_menu)
    else:
        await message.answer('Добро пожаловать в PORT. Чем я могу Вам помочь?', reply_markup=keyboards.main_menu)
    db.close()


@router.callback_query(F.data == 'return_main_menu')
async def return_main_menu(callback: CallbackQuery):
    await callback.message.edit_text('Главное меню: Выберите действие:', reply_markup=keyboards.main_menu)
    await callback.answer()

@router.callback_query(F.data == 'categories')
async def categories(callback: CallbackQuery):
    await callback.message.answer('Выберите категорию меню', reply_markup=keyboards.categories)
    await callback.answer()

@router.callback_query(F.data == 'questions')
async def categories(callback: CallbackQuery):
    await callback.message.answer('Выберите интересующий вас вопрос:', reply_markup=keyboards.questions)
    await callback.answer()

@router.callback_query(F.data == 'dog')
async def categories(callback: CallbackQuery):
    await callback.message.answer('НЕТ!', reply_markup=keyboards.return_or_admin)
    await callback.answer()

@router.callback_query(F.data == 'parking')
async def categories(callback: CallbackQuery):
    await callback.message.answer('ПРИХОДИТЕ ПЕШКОМ!', reply_markup=keyboards.return_or_admin)
    await callback.answer()

@router.callback_query(F.data == 'сhild_seat')
async def categories(callback: CallbackQuery):
    await callback.message.answer('ЗАВЕДЕНИЕ ТОЛЬКО ДЛЯ ВЗРОСЛЫХ С БЛЕК_ДЖЕКОМ И ШЛ....!', reply_markup=keyboards.return_or_admin)
    await callback.answer()

@router.callback_query(F.data == 'bron_number')
async def categories(callback: CallbackQuery):
    await callback.message.answer('Телефон для бронирования столиков +78452252268', reply_markup=keyboards.return_or_admin)
    await callback.answer()

@router.message(Command('admin'))
async def admin_panel(message: Message):
    if not message.from_user.id in ADMIN_ID:
        await message.answer("У вас нет доступа к этой команде!")
        return
    await message.answer("Добро пожаловать в админ-панель", reply_markup=keyboards.admin_main_menu)

@router.callback_query(F.data == 'return_admin_main_menu')
async def return_admin_main_menu(callback: CallbackQuery):
    await callback.message.edit_text('Админ-панель: Выберите действие:', reply_markup=keyboards.admin_main_menu)
    await callback.answer()

@router.callback_query(F.data == 'stats')
async def process_stats(callback: CallbackQuery):
    db = SessionLocal()
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.active == True).count()
    db.close()

    text = f"Статистика:\nВсего пользователей: {total_users}\nАктивных пользователей: {active_users}"
    await callback.message.edit_text(text, reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()

@router.callback_query(F.data == 'personal_broadcast')
async def process_personal_broadcast(callback: CallbackQuery):
    await callback.message.edit_text('Настройки', reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()

@router.callback_query(F.data == 'settings')
async def process_settings(callback: CallbackQuery):
    await callback.message.edit_text('Настройки', reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()

@router.callback_query(F.data == 'broadcast')
async def process_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите сообщение для рассылки:", reply_markup=keyboards.return_admin_main_menu)
    await state.set_state(BroadcastState.waiting_for_broadcast_text)
    await callback.answer()

@router.message(BroadcastState.waiting_for_broadcast_text)
async def handle_broadcast_text(message: Message, state: FSMContext, bot: Bot):
    broadcast_text = message.text
    db = SessionLocal()
    users_list = db.query(User).filter(User.active == True).all()
    count = 0
    for user in users_list:
        try:
            await bot.send_message(user.telegram_id, broadcast_text)
            count += 1
        except Exception as e:
            print(f"Ошибка отправки рассылки пользователю с ID {user.telegram_id}: {e}")

    new_broadcast = Broadcast(message=broadcast_text)
    db.add(new_broadcast)
    db.commit()
    db.close()
    await message.answer(f"Рассылка завершена! Сообщение отправлено {count} пользователям.")
    await state.clear()
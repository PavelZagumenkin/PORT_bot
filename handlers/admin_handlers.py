from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import SessionLocal, AdminSchedule, User
from keyboards.keyboards import return_admin_main_menu, main_menu
from datetime import date

router = Router()

class AdminScheduleState(StatesGroup):
    choosing_date = State()
    choosing_admins = State()

@router.callback_query(F.data == 'schedule_admins')
async def show_schedule_menu(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🗓️ Выбрать дату', callback_data='admin_sched_date')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='return_admin_main_menu')]
    ])
    await callback.message.edit_text('Настройка расписания администраторов:', reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == 'admin_sched_date')
async def ask_schedule_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите дату для назначения админов (YYYY-MM-DD):')
    await state.set_state(AdminScheduleState.choosing_date)
    await callback.answer()

@router.message(AdminScheduleState.choosing_date)
async def process_schedule_date(message: Message, state: FSMContext):
    try:
        selected_date = date.fromisoformat(message.text)
    except ValueError:
        await message.answer('Неверный формат даты. Попробуйте снова.')
        return

    await state.update_data(selected_date=selected_date)

    from config import ADMIN_ID
    kb = InlineKeyboardMarkup(row_width=1)
    for admin_id in ADMIN_ID:
        kb.insert(InlineKeyboardButton(text=f'Admin {admin_id}', callback_data=f'admin_ch_{admin_id}'))
    kb.add(InlineKeyboardButton(text='Готово', callback_data='admin_sched_done'))

    await message.answer('Выберите администраторов на эту дату:', reply_markup=kb)
    await state.set_state(AdminScheduleState.choosing_admins)

@router.callback_query(F.data.startswith('admin_ch_'))
async def toggle_admin_choice(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chosen = data.get('admins', set())
    admin_id = int(callback.data.split('_')[-1])
    if admin_id in chosen:
        chosen.remove(admin_id)
    else:
        chosen.add(admin_id)
    await state.update_data(admins=chosen)
    await callback.answer(f"Текущий выбор: {chosen}")

@router.callback_query(F.data == 'admin_sched_done')
async def save_schedule(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sched_date = data['selected_date']
    admins = data.get('admins', set())
    db = SessionLocal()
    db.query(AdminSchedule).filter(AdminSchedule.date == sched_date).delete()
    for admin_id in admins:
        db.add(AdminSchedule(user_id=admin_id, date=sched_date))
    db.commit()
    db.close()
    await callback.message.answer('Расписание сохранено.', reply_markup=return_admin_main_menu)
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == 'call_admin')
async def call_admin(callback: CallbackQuery):
    today = date.today()
    db = SessionLocal()
    scheduled = db.query(AdminSchedule).filter(AdminSchedule.date == today).all()
    if not scheduled:
        await callback.message.answer('Администраторы сегодня не назначены. Попробуйте позже.', reply_markup=main_menu)
    else:
        for sched in scheduled:
            await callback.bot.send_message(
                chat_id=sched.user_id,
                text=f'Пользователь {callback.from_user.full_name} просит помощи.'
            )
        await callback.message.answer('Администратор получит ваш запрос.', reply_markup=main_menu)
    db.close()

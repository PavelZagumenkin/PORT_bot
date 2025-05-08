from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import SessionLocal
from database.database import PersonalTemplate
from keyboards.keyboards import return_admin_main_menu

router = Router()

class TemplateEditState(StatesGroup):
    choosing_template = State()
    editing_text = State()
    editing_days_before = State()

@router.callback_query(F.data == 'personal_templates')
async def list_templates(callback: CallbackQuery):
    db = SessionLocal()
    templates = db.query(PersonalTemplate).all()
    kb = InlineKeyboardMarkup(row_width=1)
    for t in templates:
        kb.insert(InlineKeyboardButton(
            text=f"{t.name} ({t.days_before} дней)",
            callback_data=f"tpl_{t.id}"
        ))
    kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data='return_admin_main_menu'))
    await callback.message.edit_text('Выберите шаблон для редактирования:', reply_markup=kb)
    await callback.answer()
    db.close()

@router.callback_query(F.data.startswith('tpl_'))
async def choose_template(callback: CallbackQuery, state: FSMContext):
    tpl_id = int(callback.data.split('_')[1])
    db = SessionLocal()
    tpl = db.query(PersonalTemplate).get(tpl_id)
    db.close()
    await state.update_data(tpl_id=tpl_id)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='✏️ Редактировать текст', callback_data='edit_text'))
    kb.add(InlineKeyboardButton(text='⏱ Изменить период', callback_data='edit_days'))
    kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data='personal_templates'))

    await callback.message.edit_text(
        f"Шаблон: {tpl.name}\nТекст: {tpl.message_text}\nЗа сколько дней: {tpl.days_before}",
        reply_markup=kb
    )
    await state.set_state(TemplateEditState.choosing_template)
    await callback.answer()

@router.callback_query(F.data == 'edit_text')
async def ask_new_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите новый текст рассылки:')
    await state.set_state(TemplateEditState.editing_text)
    await callback.answer()

@router.message(TemplateEditState.editing_text)
async def save_new_text(message: Message, state: FSMContext):
    data = await state.get_data()
    tpl_id = data['tpl_id']
    db = SessionLocal()
    tpl = db.query(PersonalTemplate).get(tpl_id)
    tpl.message_text = message.text
    db.commit()
    db.close()
    await message.answer('Текст обновлен.', reply_markup=return_admin_main_menu)
    await state.clear()

@router.callback_query(F.data == 'edit_days')
async def ask_new_days(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите новое число дней до события:')
    await state.set_state(TemplateEditState.editing_days_before)
    await callback.answer()

@router.message(TemplateEditState.editing_days_before)
async def save_new_days(message: Message, state: FSMContext):
    try:
        days = int(message.text)
    except ValueError:
        await message.answer('Введите целое число. Попробуйте снова.')
        return

    data = await state.get_data()
    tpl_id = data['tpl_id']
    db = SessionLocal()
    tpl = db.query(PersonalTemplate).get(tpl_id)
    tpl.days_before = days
    db.commit()
    db.close()
    await message.answer('Период обновлен.', reply_markup=return_admin_main_menu)
    await state.clear()

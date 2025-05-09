from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import keyboards.keyboards as keyboards
from config import ADMIN_ID
from database.database import SessionLocal, User, Broadcast, AdminSchedule, Review, ActiveSupportChat, PersonalTemplate
from datetime import datetime, date

router = Router()


class BroadcastState(StatesGroup):
    waiting_for_broadcast_content = State()


class PersonalDataState(StatesGroup):
    waiting_for_sex = State()
    waiting_for_birthdate = State()


class AdminScheduleState(StatesGroup):
    choosing_date = State()
    waiting_for_contact = State()
    waiting_for_confirmation = State()


class ReviewState(StatesGroup):
    waiting_for_rating = State()
    waiting_for_text = State()


class TemplateState(StatesGroup):
    waiting_for_name = State()
    waiting_for_personal_broadcast_content = State()
    waiting_for_conditions = State()
    waiting_for_date = State()
    waiting_for_count_days = State()
    waiting_for_sex_personal_broadcast = State()
    waiting_for_confirming = State()


@router.message(CommandStart())
async def start(message: Message):
    db = SessionLocal()
    existing = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not existing:
        new_user = User(telegram_id=message.from_user.id, name=message.from_user.full_name)
        db.add(new_user)
        db.commit()
        await message.answer(
            'Добро пожаловать в PORT. Вы подписались на нашу рассылку. Чем я могу Вам помочь?',
            reply_markup=keyboards.main_menu
        )
    else:
        await message.answer(
            'Добро пожаловать в PORT. Чем я могу Вам помочь?',
            reply_markup=keyboards.main_menu
        )
    search_active_chat = db.query(ActiveSupportChat).filter(ActiveSupportChat.user_id == message.from_user.id).first()
    if search_active_chat:
        await message.answer("У вас есть незавершенный диалог с поддержкой.",
                             reply_markup=keyboards.end_chat_keyboard())
        db.close()
        return
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
async def questions(callback: CallbackQuery):
    await callback.message.answer('Выберите интересующий вас вопрос:', reply_markup=keyboards.questions)
    await callback.answer()


@router.callback_query(F.data == 'dog')
async def dog(callback: CallbackQuery):
    await callback.message.answer('НЕТ!', reply_markup=keyboards.return_or_admin)
    await callback.answer()


@router.callback_query(F.data == 'parking')
async def parking(callback: CallbackQuery):
    await callback.message.answer('ПРИХОДИТЕ ПЕШКОМ!', reply_markup=keyboards.return_or_admin)
    await callback.answer()


@router.callback_query(F.data == 'сhild_seat')
async def child_seat(callback: CallbackQuery):
    await callback.message.answer(
        'ЗАВЕДЕНИЕ ТОЛЬКО ДЛЯ ВЗРОСЛЫХ С БЛЕК_ДЖЕКОМ И ШЛ....!',
        reply_markup=keyboards.return_or_admin
    )
    await callback.answer()


@router.callback_query(F.data == 'bron_number')
async def bron_number(callback: CallbackQuery):
    await callback.message.answer(
        'Телефон для бронирования столиков +78452252268',
        reply_markup=keyboards.return_or_admin
    )
    await callback.answer()


@router.message(Command('admin'))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_ID:
        await message.answer("У вас нет доступа к этой команде!")
        return
    await message.answer("Добро пожаловать в админ-панель", reply_markup=keyboards.admin_main_menu)


@router.callback_query(F.data == 'return_admin_main_menu')
async def return_admin_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Админ-панель: Выберите действие:', reply_markup=keyboards.admin_main_menu)
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == 'stats')
async def process_stats(callback: CallbackQuery):
    db = SessionLocal()
    # всего пользователей
    total_users = db.query(User).count()
    # активных пользователей
    active_users = db.query(User).filter(User.active == True).count()
    # всего отзывов
    total_reviews = db.query(Review).count()
    # средний рейтинг
    reviews = db.query(Review).all()
    if reviews:
        avg = sum(r.rating for r in reviews) / len(reviews)
    else:
        avg = 0
    db.close()
    text = f"Статистика:\nВсего пользователей: {total_users}\nАктивных пользователей: {active_users}\nВсего отзывов: {total_reviews}\nСредний рейтинг: {avg:.2f}"
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
    await callback.message.edit_text(
        "Введите сообщение для рассылки:",
        reply_markup=keyboards.return_admin_main_menu
    )
    await state.set_state(BroadcastState.waiting_for_broadcast_content)
    await callback.answer()


@router.message(BroadcastState.waiting_for_broadcast_content)
async def handle_broadcast_content(message: Message, state: FSMContext, bot: Bot):
    db = SessionLocal()
    content_type = 'text'
    file_id = None
    caption = None
    if message.photo:
        content_type = 'photo'
        photo = message.photo[-1]
        file_id = photo.file_id
        caption = message.caption or ""
        broadcast_text = caption
    elif message.text:
        broadcast_text = message.text
    else:
        await message.answer("Отправьте текст или фото с подписью.")
        db.close()
        return
    users_list = db.query(User).filter(User.active == True).all()
    count = 0
    for user in users_list:
        try:
            if content_type == 'photo':
                await bot.send_photo(chat_id=user.telegram_id, photo=file_id, caption=caption)
            else:
                await bot.send_message(chat_id=user.telegram_id, text=broadcast_text)
            count += 1
        except Exception as e:
            print(f"Ошибка отправки пользователю {user.telegram_id}: {e}")
    new_broadcast = Broadcast(
        content_type=content_type,
        message_text=broadcast_text,
        file_id=file_id
    )
    db.add(new_broadcast)
    db.commit()
    db.close()
    await message.answer(f"Рассылка завершена! Сообщение отправлено {count} пользователям.",
                         reply_markup=keyboards.return_admin_main_menu)
    await state.clear()


@router.callback_query(F.data == 'personal_broadcast_form')
async def show_personal_form(callback: CallbackQuery):
    from_user = callback.from_user
    db = SessionLocal()
    existing = db.query(User).filter(User.telegram_id == from_user.id).first()
    if existing.personal_broadcast:
        await callback.message.answer('Вы уже подписаны на персональную рассылку',
                                      reply_markup=keyboards.personal_broadcast_yes)
    else:
        await callback.message.answer('Заполните небольшую анкету', reply_markup=keyboards.personal_broadcast_form)
    await callback.answer()


@router.callback_query(F.data == 'unsubscribe_personal_broadcast')
async def show_personal_form(callback: CallbackQuery):
    from_user = callback.from_user
    db = SessionLocal()
    existing = db.query(User).filter(User.telegram_id == from_user.id).first()
    existing.personal_broadcast = False
    db.commit()
    db.close()
    await callback.message.answer('Вы успешно отписались от персональной рассылки!', reply_markup=keyboards.main_menu)
    await callback.answer()


@router.callback_query(F.data == 'personal_broadcast_faq')
async def show_personal_broadcast_faq(callback: CallbackQuery):
    await callback.message.answer(
        'Вы будете получать от нас персональные предложения, промокоды и бонусы, по различным событиям, праздникам или дню рождению!',
        reply_markup=keyboards.personal_broadcast_form_posle_faq)
    await callback.answer()


@router.callback_query(F.data == 'personal_broadcast_form_start')
async def ask_sex(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите ваш пол:', reply_markup=keyboards.sex_form)
    await state.set_state(PersonalDataState.waiting_for_sex)
    await callback.answer()


@router.callback_query(F.data.startswith('pd_sex_'))
async def process_sex(callback: CallbackQuery, state: FSMContext):
    sex = 'female' if 'female' in callback.data else 'male'
    await state.update_data(sex=sex)
    await callback.message.answer('Введите дату рождения в формате DD.MM.YYYY:')
    await state.set_state(PersonalDataState.waiting_for_birthdate)
    await callback.answer()


@router.message(PersonalDataState.waiting_for_birthdate)
async def process_birthdate(message: Message, state: FSMContext):
    try:
        selected_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer('Неверный формат даты. Попробуйте снова.')
        return
    await state.update_data(selected_date=selected_date)
    # Приводим выбор к date
    birth = selected_date
    today = date.today()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    # Валидация
    if birth > today:
        await message.answer('Дата не может быть в будущем. Попробуйте снова.')
    elif age < 14:
        await message.answer('Вы должны быть старше 14 лет. Попробуйте снова.')
    elif age > 100:
        await message.answer('Возраст не может превышать 100 лет. Попробуйте снова.')
    else:
        data = await state.get_data()
        db = SessionLocal()
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if user:
            user.sex = data.get('sex')
            user.birthday = datetime(birth.year, birth.month, birth.day)
            user.personal_broadcast = True
            db.commit()
        db.close()
        await message.answer('Спасибо! Ваши данные сохранены.', reply_markup=keyboards.main_menu)
        await state.clear()
        return


@router.callback_query(F.data == 'pd_finish')
async def cancel_personal_data(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Заполнение отменено.', reply_markup=keyboards.main_menu)
    await callback.answer()


# Пользовательский поток отзывов
@router.callback_query(F.data == 'leave_review')
async def ask_rating(callback: CallbackQuery, state: FSMContext):
    kb_review_keyboard = keyboards.review_keyboard()
    await callback.message.answer('Пожалуйста, поставьте оценку (1-5):', reply_markup=kb_review_keyboard)
    await state.set_state(ReviewState.waiting_for_rating)
    await callback.answer()


@router.callback_query(F.data.startswith('review_'))
async def process_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split('_')[1])
    await state.update_data(rating=rating)
    await callback.message.answer(
        'Спасибо! Теперь вы можете оставить текстовый отзыв или фото. Отправьте сообщение или фото.')
    await state.set_state(ReviewState.waiting_for_text)
    await callback.answer()


@router.message(ReviewState.waiting_for_text)
async def save_review(message: Message, state: FSMContext):
    data = await state.get_data()
    rating = data.get('rating')
    text = message.text or ''
    photo_file = None
    if message.photo:
        photo_file = message.photo[-1].file_id
        text = message.caption or text
    # Сохраняем отзыв
    db = SessionLocal()
    existing_review = db.query(Review).filter(Review.user_id == message.from_user.id).first()
    if existing_review:
        existing_review.rating = rating
        existing_review.message_text = text
        existing_review.file_id = photo_file
        existing_review.created_at = datetime.now()
        db.commit()
        await message.answer('Ваш предыдущий отзыв был обновлён. Спасибо!', reply_markup=keyboards.main_menu)
    else:
        new_review = Review(
            user_id=message.from_user.id,
            name=message.from_user.full_name,
            rating=rating,
            message_text=text,
            file_id=photo_file,
            created_at=datetime.now()
        )
        db.add(new_review)
        db.commit()
        await message.answer('Спасибо за отзыв!', reply_markup=keyboards.main_menu)
    db.close()
    await state.clear()


# Админ: управление отзывами
@router.callback_query(F.data == 'manage_reviews')
async def list_reviews(callback: CallbackQuery):
    db = SessionLocal()
    reviews = db.query(Review).all()
    total_reviews = db.query(Review).count()
    if not reviews:
        await callback.message.answer('Нет отзывов.', reply_markup=keyboards.return_admin_main_menu)
    else:
        for r in reviews:
            text = f"ID: {r.id} User: {r.user_id} Оценка: {r.rating} {r.text or ''}"
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='Удалить', callback_data=f'del_review_{r.id}')
            ]])
            await callback.message.answer(text, reply_markup=kb)
        await callback.message.answer(f"Всего отзывов: {total_reviews}", reply_markup=keyboards.return_admin_main_menu)
    db.close()
    await callback.answer()


@router.callback_query(F.data.startswith('del_review_'))
async def delete_review(callback: CallbackQuery):
    review_id = int(callback.data.split('_')[-1])
    db = SessionLocal()
    db.query(Review).filter(Review.id == review_id).delete()
    db.commit()
    db.close()
    await callback.message.answer(f'Отзыв {review_id} удалён.', reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()


@router.callback_query(F.data == 'schedule_admins')
async def show_schedule_menu(callback: CallbackQuery):
    await callback.message.edit_text('Настройка расписания администраторов:',
                                     reply_markup=keyboards.kb_enter_date_admin)
    await callback.answer()


@router.callback_query(F.data == 'admin_sched_date')
async def ask_schedule_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите дату для просмотра или назначения админов (DD.MM.YYYY):')
    await state.set_state(AdminScheduleState.choosing_date)
    await callback.answer()


@router.message(AdminScheduleState.choosing_date)
async def process_schedule_date(message: Message, state: FSMContext):
    try:
        selected_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        db = SessionLocal()
        scheduled = db.query(AdminSchedule).filter(AdminSchedule.date == selected_date).all()
        if not scheduled:
            await message.answer('Администраторы не назначены на эту дату', reply_markup=keyboards.kb_add_admin)
        else:
            for admin in scheduled:
                await message.answer('Администраторы назначеные на эту дату:')
                text = f"{admin.name}"
                kb = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text='Удалить', callback_data=f'del_admin_{admin.id}')
                ]])
                await message.answer(text, reply_markup=kb)
                await message.answer('Добавить администратора:', reply_markup=keyboards.kb_add_admin)
    except ValueError:
        await message.answer('Неверный формат даты. Попробуйте снова.')
        return
    await state.update_data(selected_date=selected_date)


# Запрос контакта пользователя
@router.callback_query(F.data == 'choose_admin')
async def ask_for_contact(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Пожалуйста, отправьте контакт администратора, которого вы хотите добавить\n(или выберите свой по кнопке ниже)",
        reply_markup=keyboards.enter_contact)
    await state.set_state(AdminScheduleState.waiting_for_contact)
    await callback.answer()


# Обработка отправки контакта
@router.message(F.contact)
async def received_contact(message: Message, state: FSMContext):
    contact = message.contact
    if not contact.user_id:
        await message.answer("Этот контакт не связан с Telegram-аккаунтом.")
        return
    full_name = f"{contact.first_name} {contact.last_name or ''}".strip()
    await state.update_data(
        candidate_id=contact.user_id,
        candidate_name=full_name
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Добавить", callback_data="confirm_add_admin"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_add_admin")
    ]])
    await message.answer(
        f"Добавить администратора:\n{full_name} ({contact.user_id})?",
        reply_markup=kb
    )
    await state.set_state(AdminScheduleState.waiting_for_confirmation)


# Обработка подтверждения добавления администратора
@router.callback_query(F.data == "confirm_add_admin")
async def confirm_add_admin(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("candidate_id")
    full_name = data.get("candidate_name")
    # Предполагается, что ранее была выбрана дата
    date_chosen = data.get("selected_date")  # Например, дата была сохранена в state

    db = SessionLocal()
    exists = db.query(AdminSchedule).filter_by(user_id=user_id, date=date_chosen).first()
    if exists:
        await callback.message.answer("Этот пользователь уже администратор на выбранную дату.")
    else:
        db.add(AdminSchedule(user_id=user_id, name=full_name, date=date_chosen))
        db.commit()
        await callback.message.answer(f"{full_name} добавлен как администратор на {date_chosen.strftime('%d.%m.%Y')}.",
                                      reply_markup=keyboards.admin_main_menu)
    db.close()
    await state.clear()
    await callback.answer()


# Обработка отмены добавления администратора
@router.callback_query(F.data == "cancel_add_admin")
async def cancel_add_admin(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Добавление отменено.")
    await state.clear()
    await callback.answer()


# Пример функции для сохранения выбранной даты (можно адаптировать под вашу логику)
@router.callback_query(F.data.startswith('set_date_'))
async def set_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split('_')[2]
    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    await state.update_data(selected_date=selected_date)

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Выбрать администратора", callback_data="choose_admin")
    ]])
    await callback.message.answer(f"Вы выбрали дату: {selected_date.strftime('%d.%m.%Y')}", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith('del_admin_'))
async def delete_review(callback: CallbackQuery):
    admin_id = int(callback.data.split('_')[-1])
    db = SessionLocal()
    db.query(AdminSchedule).filter(AdminSchedule.id == admin_id).delete()
    db.commit()
    db.close()
    await callback.message.answer(f'Админ {admin_id} удалён c .', reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()


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
    await callback.message.answer('Расписание сохранено.', reply_markup=keyboards.return_admin_main_menu)
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == 'call_admin')
async def call_admin(callback: CallbackQuery):
    from_user = callback.from_user
    today = date.today()
    db = SessionLocal()
    search_active_chat = db.query(ActiveSupportChat).filter(ActiveSupportChat.user_id == from_user.id).first()
    if search_active_chat:
        await callback.message.answer("Вы уже начали диалог.", reply_markup=keyboards.end_chat_keyboard())
        db.close()
        await callback.answer()
        return
    scheduled = db.query(AdminSchedule).filter(AdminSchedule.date == today).all()
    if not scheduled:
        await callback.message.answer('Администраторы еще не назначены. Попробуйте позже.',
                                      reply_markup=keyboards.main_menu)
        db.close()
        await callback.answer()
        return
    else:
        db.add(ActiveSupportChat(user_id=from_user.id))
        db.commit()
        for sched in scheduled:
            db.add(ActiveSupportChat(user_id=from_user.id))
            await callback.bot.send_message(
                chat_id=sched.user_id,
                text=f'Пользователь {callback.from_user.full_name} просит помощи.',
                reply_markup=keyboards.reply_keyboard(from_user.id))
        await callback.message.answer('Администратор скоро вам ответит на ваш запрос.',
                                      reply_markup=keyboards.end_chat_keyboard())
    db.close()
    await callback.answer()


# Админ нажимает "Ответить"
@router.callback_query(F.data.startswith('reply_to_'))
async def reply_to_user(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split('_')[-1])
    db = SessionLocal()
    chat = db.query(ActiveSupportChat).filter(ActiveSupportChat.user_id == user_id).first()
    if chat and chat.admin_id:
        await callback.message.answer("С этим пользователем уже ведётся диалог.")
    elif chat:
        chat.admin_id = callback.from_user.id
        db.commit()
        await callback.message.answer("Вы подключились к пользователю.", reply_markup=keyboards.end_chat_keyboard())
        await callback.bot.send_message(chat.user_id, "Администратор подключился к чату.",
                                        reply_markup=keyboards.end_chat_keyboard())
    else:
        await callback.message.answer("Диалог не найден.")
    db.close()
    await callback.answer()


@router.callback_query(F.data == 'personal_templates')
async def show_personal_templates(callback: CallbackQuery):
    db = SessionLocal()
    templates = db.query(PersonalTemplate).all()
    db.close()

    # Собираем список строк клавиатуры
    keyboard_rows = []  # каждая строка — список InlineKeyboardButton
    if not templates:
        keyboard_rows.append([
            InlineKeyboardButton(text='➕ Добавить шаблон', callback_data='create_template'),
            InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_admin_main_menu')
        ])
        reply_text = 'Шаблоны персональных рассылок отсутствуют.'
    else:
        for tpl in templates:
            keyboard_rows.append([
                InlineKeyboardButton(text=f'✏️ {tpl.name}', callback_data=f'edit_template_{tpl.id}'),
                InlineKeyboardButton(text=f'🗑️ Удалить', callback_data=f'del_template_{tpl.id}')
            ])
        # Кнопка внизу
        keyboard_rows.append([
            InlineKeyboardButton(text='➕ Добавить шаблон', callback_data='create_template'),
            InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_admin_main_menu')
        ])
        reply_text = 'Существующие шаблоны:'

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    await callback.message.answer(reply_text, reply_markup=markup)
    await callback.answer()


# Поток создания шаблона
@router.callback_query(F.data == 'create_template')
async def create_template_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите название шаблона:', reply_markup=keyboards.return_admin_main_menu)
    await state.set_state(TemplateState.waiting_for_name)
    await callback.answer()


@router.message(TemplateState.waiting_for_name)
async def process_template_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите текст сообщения или фото(с подписью или без) для шаблона:',
                         reply_markup=keyboards.return_admin_main_menu)
    await state.set_state(TemplateState.waiting_for_personal_broadcast_content)


@router.message(TemplateState.waiting_for_personal_broadcast_content)
async def process_template_content(message: Message, state: FSMContext):
    file_id = None
    if message.photo:
        content_type = 'photo'
        file_id = message.photo[-1].file_id
        message_text = message.caption or ''
    elif message.text:
        content_type = 'text'
        message_text = message.text
    else:
        await message.answer("Пожалуйста, отправьте текст или фото.")
        return

    await state.update_data(
        content_type=content_type,
        message_text=message_text,
        file_id=file_id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='По дате', callback_data='personal_broadcast_when_date')],
        [InlineKeyboardButton(text='По дню рождения', callback_data='personal_broadcast_when_birthday')],
        [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_admin_main_menu')]
    ])
    await message.answer(
        f"Когда выполнять рассылку:", reply_markup=kb
    )
    await state.set_state(TemplateState.waiting_for_conditions)


@router.callback_query(F.data.startswith('personal_broadcast_when_'))
async def process_personal_broadcast_when(callback: CallbackQuery, state: FSMContext):
    if 'date' in callback.data:
        when = 'date'
        await callback.message.answer('Введите дату события к которому планируется рассылка в формате DD.MM.YYYY:')
        await state.set_state(TemplateState.waiting_for_date)
    else:
        when = 'birthday'
        await state.update_data(date_event=None)
        await callback.message.answer('Введите, за сколько дней до события делать рассылку:')
        await state.set_state(TemplateState.waiting_for_count_days)
    await state.update_data(when_broadcast=when)
    await callback.answer()


@router.message(TemplateState.waiting_for_date)
async def process_birthdate(message: Message, state: FSMContext):
    try:
        selected_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer('Неверный формат даты. Попробуйте снова.')
        return
    await state.update_data(date_event=selected_date)
    await message.answer('Введите, за сколько дней до события делать рассылку:')
    await state.set_state(TemplateState.waiting_for_count_days)


@router.message(TemplateState.waiting_for_count_days)
async def process_count_days(message: Message, state: FSMContext):
    try:
        count_days = int(message.text)
    except ValueError:
        await message.answer('Введите целое число и попробуйте снова.')
        return
    await state.update_data(days_before=count_days)
    await message.answer('Для кого выполнять рассылку?', reply_markup=keyboards.sex_personal_broadcast)
    await state.set_state(TemplateState.waiting_for_sex_personal_broadcast)


@router.callback_query(F.data.startswith('pb_sex_'))
async def process_sex(callback: CallbackQuery, state: FSMContext):
    if 'female' in callback.data:
        for_sex = 'female'
    elif 'all' in callback.data:
        for_sex = 'all'
    else:
        for_sex = 'male'
    await state.update_data(for_sex=for_sex)
    data = await state.get_data()
    confirmation_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_template')],
        [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_template')],
        [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_admin_main_menu')]
    ])
    if data['content_type'] == 'photo':
        await callback.message.answer_photo(photo=data['file_id'], caption=data['message_text'])
        await callback.message.answer(
            f"Подтвердите создание шаблона:\nИмя шаблона: {data['name']}\nРассылать к {'дню рождению' if data['when_broadcast'] == 'birthday' else data['date_event']} за {data['days_before']} дней до события.\nВыполнять рассылку для: {'женщин' if data['for_sex'] == 'female' else 'мужчин' if data['for_sex'] == 'male' else 'всех'}\n",
            reply_markup=confirmation_kb)
    else:
        await callback.message.answer(
            f"Подтвердите создание шаблона:\nИмя шаблона: {data['name']}\nТекст рассылки: {data['message_text']}\nРассылать к {'дню рождения' if data['when_broadcast'] == 'birthday' else data['date_event']} за {data['days_before']} дней до события.\nВыполнять рассылку для: {'женщин' if data['for_sex'] == 'female' else 'мужчин' if data['for_sex'] == 'male' else 'всех'}\n",
            reply_markup=confirmation_kb)
    await state.set_state(TemplateState.waiting_for_confirming)
    await callback.answer()


@router.callback_query(F.data == 'confirm_template')
async def save_new_template(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    db = SessionLocal()
    tpl = PersonalTemplate(
        name=data['name'],
        content_type=data['content_type'],
        message_text=data['message_text'],
        file_id=data['file_id'],
        when_broadcast=data['when_broadcast'],
        date_event=data['date_event'],
        days_before=data['days_before'],
        for_sex=data['for_sex']
    )
    db.add(tpl)
    db.commit()
    db.close()
    await callback.message.answer(f"Шаблон '{data['name']}' создан.", reply_markup=keyboards.admin_main_menu)
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == 'cancel_template')
async def cancel_template(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Создание шаблона отменено.', reply_markup=keyboards.admin_main_menu)
    await callback.answer()


@router.callback_query(F.data.startswith('del_template_'))
async def delete_template(callback: CallbackQuery):
    tpl_id = int(callback.data.split('_')[-1])
    db = SessionLocal()
    db.query(PersonalTemplate).filter(PersonalTemplate.id == tpl_id).delete()
    db.commit()
    db.close()
    await callback.message.answer(f'Шаблон удалён (ID {tpl_id}).', reply_markup=keyboards.admin_main_menu)
    await callback.answer()


# Пересылка сообщений
@router.message()
async def relay_message(message: Message):
    full_name = message.from_user.full_name
    db = SessionLocal()
    chat = db.query(ActiveSupportChat).filter(
        (ActiveSupportChat.user_id == message.from_user.id) | (ActiveSupportChat.admin_id == message.from_user.id)
    ).first()
    if chat:
        target_id = chat.admin_id if message.from_user.id == chat.user_id else chat.user_id
        sender = f"{full_name}" if message.from_user.id == chat.user_id else "Админ"
        await message.bot.send_message(chat_id=target_id, text=f"{sender}: {message.text}",
                                       reply_markup=keyboards.end_chat_keyboard())
    db.close()


# Завершение чата
@router.callback_query(F.data == 'end_chat')
async def end_chat(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    db = SessionLocal()
    chat = db.query(ActiveSupportChat).filter(
        (ActiveSupportChat.user_id == user_id) | (ActiveSupportChat.admin_id == user_id)
    ).first()

    if chat:
        try:
            await callback.bot.send_message(chat.user_id, "Диалог завершён.")
        except:
            pass
        try:
            await callback.bot.send_message(chat.admin_id, "Диалог завершён.")
        except:
            pass
        db.delete(chat)
        db.commit()
        await callback.message.answer("Вы завершили диалог.", reply_markup=keyboards.main_menu)
        await state.clear()
    else:
        await callback.message.answer("Нет активного чата.")
        await state.clear()
    db.close()
    await callback.answer()
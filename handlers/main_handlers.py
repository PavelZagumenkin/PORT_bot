from aiogram import F, Router, Bot
from aiogram.exceptions import TelegramBadRequest
import logging
from aiogram.filters import CommandStart, Command
import pandas as pd
from io import BytesIO
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
import keyboards.keyboards as keyboards
from config import ADMIN_ID
from database.database import SessionLocal, User, Broadcast, Review, PersonalTemplate
from datetime import datetime, date, timedelta

router = Router()


class BroadcastState(StatesGroup):
    waiting_for_broadcast_content = State()


class PersonalDataState(StatesGroup):
    waiting_for_sex = State()
    waiting_for_birthdate = State()


class ReviewState(StatesGroup):
    waiting_for_rating = State()
    waiting_for_text = State()
    editing_rating = State()
    editing_review = State()
    waiting_for_ID = State()


class TemplateState(StatesGroup):
    waiting_for_name = State()
    waiting_for_personal_broadcast_content = State()
    waiting_for_conditions = State()
    waiting_for_date = State()
    waiting_for_count_days = State()
    waiting_for_sex_personal_broadcast = State()
    waiting_for_confirming = State()


@router.message(CommandStart())
async def start(message: Message, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    db = SessionLocal()
    existing = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not existing:
        new_user = User(telegram_id=message.from_user.id, name=message.from_user.full_name)
        db.add(new_user)
        db.commit()
        await message.answer(
            'Добро пожаловать в PORT. Чем я могу Вам помочь?',
            reply_markup=keyboards.main_menu
        )
    else:
        await message.answer(
            'Добро пожаловать в PORT. Чем я могу Вам помочь?',
            reply_markup=keyboards.main_menu
        )
        db.close()
        return
    db.close()


@router.callback_query(F.data == 'return_main_menu')
async def return_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Главное меню: Выберите действие:', reply_markup=keyboards.main_menu)
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == 'return_admin_main_menu')
async def handle_admin_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    # Отправляем новое сообщение поверх старого
    await callback.message.answer(
        'Админ-панель: Выберите действие:',
        reply_markup=keyboards.admin_main_menu
    )
    await state.clear()


@router.callback_query(F.data == 'categories')
async def categories(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Выберите категорию меню', reply_markup=keyboards.categories)
    await callback.answer()


@router.callback_query(F.data == 'questions')
async def questions(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Выберите интересующий вас вопрос:', reply_markup=keyboards.questions)
    await callback.answer()


@router.callback_query(F.data == 'dog')
async def dog(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('ДА', reply_markup=keyboards.return_or_admin)
    await callback.answer()


@router.callback_query(F.data == 'parking')
async def parking(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('ДА', reply_markup=keyboards.return_or_admin)
    await callback.answer()


@router.callback_query(F.data == 'child_seat')
async def child_seat(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        'ДА',
        reply_markup=keyboards.return_or_admin
    )
    await callback.answer()


@router.callback_query(F.data == 'bron_number')
async def bron_number(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        'Телефон для бронирования столиков +78452252268',
        reply_markup=keyboards.return_or_admin
    )
    await callback.answer()


@router.message(Command('admin'))
async def admin_panel(message: Message, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    if message.from_user.id not in ADMIN_ID:
        await message.answer("У вас нет доступа к этой команде!")
        return
    await message.answer("Добро пожаловать в админ-панель", reply_markup=keyboards.admin_main_menu)


@router.callback_query(F.data == 'stats')
async def process_stats(callback: CallbackQuery):
    await callback.message.delete()
    db = SessionLocal()
    # всего пользователей
    total_users = db.query(User).count()
    # активных пользователей
    personal_broadcast = db.query(User).filter(User.personal_broadcast == True).count()
    # мужчин
    male = db.query(User).filter(User.sex == 'male').count()
    # женщин
    female = db.query(User).filter(User.sex == 'female').count()
    # всего отзывов
    total_reviews = db.query(Review).count()
    # средний рейтинг
    reviews = db.query(Review).all()
    if reviews:
        avg = sum(r.rating for r in reviews) / len(reviews)
    else:
        avg = 0
    db.close()
    text = f"Статистика:\nВсего пользователей: {total_users}\nПодписались на персональную рассылку: {personal_broadcast}\nМужчин: {male}\nЖенщин: {female}\nВсего отзывов: {total_reviews}\nСредний рейтинг: {avg:.2f}"
    await callback.message.answer(text, reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()


@router.callback_query(F.data == 'personal_broadcast')
async def process_personal_broadcast(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Настройки', reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()


@router.callback_query(F.data == 'settings')
async def process_settings(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Настройки', reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()


@router.callback_query(F.data == 'broadcast')
async def process_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "Введите текст или фото с подписью для рассылки:",
        reply_markup=keyboards.return_admin_main_menu
    )
    await state.set_state(BroadcastState.waiting_for_broadcast_content)
    await callback.answer()


@router.message(BroadcastState.waiting_for_broadcast_content)
async def handle_broadcast_content(message: Message, state: FSMContext, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
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
        await message.answer("Отправьте текст или фото с подписью.",
                         reply_markup=keyboards.return_admin_main_menu)
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


# @router.callback_query(F.data == 'anons_broadcast')
# async def show_recent_broadcasts(callback: CallbackQuery):
#     db = SessionLocal()
#     try:
#         # Получаем 5 последних рассылок (от новых к старым)
#         broadcasts = db.query(Broadcast).order_by(Broadcast.id.desc()).limit(5).all()
#
#         if not broadcasts:
#             await callback.message.answer("Нет сохраненных рассылок.")
#             return
#
#         # Отправляем рассылки в хронологическом порядке (от старых к новым)
#         for broadcast in reversed(broadcasts):
#             try:
#                 if broadcast.content_type == 'photo' and broadcast.file_id:
#                     await callback.message.answer_photo(
#                         photo=broadcast.file_id,
#                         caption=broadcast.message_text
#                     )
#                 else:
#                     await callback.message.answer(
#                         text=broadcast.message_text
#                     )
#             except Exception as e:
#                 # print(f"Ошибка при отображении рассылки {broadcast.id}: {e}")
#                 continue
#
#     finally:
#         db.close()
#
#     await callback.answer()


@router.callback_query(F.data == 'personal_broadcast_form')
async def show_personal_form(callback: CallbackQuery):
    await callback.message.delete()
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
    await callback.message.delete()
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
    await callback.message.delete()
    await callback.message.answer(
        'Вы будете получать от нас персональные предложения, промокоды и бонусы, по различным событиям, праздникам или дню рождению!',
        reply_markup=keyboards.personal_broadcast_form_posle_faq)
    await callback.answer()


@router.callback_query(F.data == 'personal_broadcast_form_start')
async def ask_sex(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Выберите ваш пол:', reply_markup=keyboards.sex_form)
    await state.set_state(PersonalDataState.waiting_for_sex)
    await callback.answer()


@router.callback_query(F.data.startswith('pd_sex_'))
async def process_sex(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    sex = 'female' if 'female' in callback.data else 'male'
    await state.update_data(sex=sex)
    await callback.message.answer('Введите дату рождения в формате DD.MM.YYYY:',
            reply_markup=keyboards.return_main_menu)
    await state.set_state(PersonalDataState.waiting_for_birthdate)
    await callback.answer()


@router.message(PersonalDataState.waiting_for_birthdate)
async def process_birthdate(message: Message, state: FSMContext, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    try:
        selected_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer('Неверный формат даты. Попробуйте снова (DD.MM.YYYY)',
            reply_markup=keyboards.return_main_menu)
        return
    await state.update_data(selected_date=selected_date)
    # Приводим выбор к date
    birth = selected_date
    today = date.today()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    # Валидация
    if birth > today:
        await message.answer('Дата не может быть в будущем. Попробуйте снова.',
            reply_markup=keyboards.return_main_menu)
    elif age < 14:
        await message.answer('Вы должны быть старше 14 лет. Попробуйте снова.',
            reply_markup=keyboards.return_main_menu)
    elif age > 100:
        await message.answer('Возраст не может превышать 100 лет. Попробуйте снова.',
            reply_markup=keyboards.return_main_menu)
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
    await callback.message.delete()
    await state.clear()
    await callback.message.answer('Заполнение отменено.', reply_markup=keyboards.main_menu)
    await callback.answer()


# Модифицированный обработчик для кнопки "Оставить отзыв"
@router.callback_query(F.data == 'leave_review')
async def ask_rating(callback: CallbackQuery):
    await callback.message.delete()
    db = SessionLocal()
    user_id = callback.from_user.id

    # Проверяем последний отзыв
    last_review = db.query(Review).filter(
        Review.user_id == user_id
    ).order_by(Review.created_at.desc()).first()

    if last_review and (datetime.now() - last_review.created_at) < timedelta(days=7):
        delta = last_review.created_at + timedelta(days=7) - datetime.now()
        days_left = delta.days + 1
        await callback.message.answer(
            f"❌ Вы можете оставить следующий отзыв через {days_left} дней",
            reply_markup=keyboards.my_reviews
        )
        db.close()
        await callback.answer()
        return
    await callback.message.answer('Выберите действие:', reply_markup=keyboards.my_reviews_add)
    db.close()
    await callback.answer()


@router.callback_query(F.data == 'create_reviews')
async def show_user_reviews(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Пожалуйста, поставьте оценку (1-5):', reply_markup=keyboards.review_keyboard())
    await state.set_state(ReviewState.waiting_for_rating)
    await callback.answer()


# Новый обработчик для просмотра отзывов
@router.callback_query(F.data == 'my_reviews')
async def show_user_reviews(callback: CallbackQuery):
    await callback.message.delete()
    db = SessionLocal()
    reviews = db.query(Review).filter(
        Review.user_id == callback.from_user.id
    ).order_by(Review.created_at.desc()).all()

    if not reviews:
        await callback.message.answer("📭 У вас пока нет отзывов",
            reply_markup=keyboards.return_main_menu)
        await callback.answer()
        db.close()
        return

    for review in reviews:
        text = (
            f"📅 Дата: {review.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"⭐ Оценка: {review.rating}\n"
            f"📝 Текст: {review.message_text or 'Нет текста'}"
        )

        buttons = [
            [InlineKeyboardButton(
                text="✏️ Редактировать",
                callback_data=f"edit_review_{review.id}"
            )],
            [InlineKeyboardButton(
                text="🗑 Удалить",
                callback_data=f"delete_review_{review.id}"
            )],
            [InlineKeyboardButton(
                text='🔙 Главное меню',
                callback_data='return_main_menu'
            )]
        ]

        if review.file_id:
            await callback.message.answer_photo(
                photo=review.file_id,
                caption=text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )
        else:
            await callback.message.answer(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

    db.close()
    await callback.answer()


# Обработчик для начала редактирования
@router.callback_query(F.data.startswith('edit_review_'))
async def start_edit_review(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    review_id = int(callback.data.split('_')[2])
    await state.update_data(review_id=review_id)
    await callback.message.answer(
        "Выберите новую оценку:",
        reply_markup=keyboards.review_keyboard()
    )
    await state.set_state(ReviewState.editing_rating)
    await callback.answer()


# Модифицированный обработчик оценок
@router.callback_query(F.data.startswith('review_'))
async def process_rating(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    rating = int(callback.data.split('_')[1])
    state_data = await state.get_data()

    if 'review_id' in state_data:  # Режим редактирования
        await state.update_data(rating=rating)
        await callback.message.answer(
            "Введите новый текст отзыва или отправьте фото с подписью:",
            reply_markup=keyboards.return_main_menu
        )
        await state.set_state(ReviewState.editing_review)
    else:  # Новый отзыв
        await state.update_data(rating=rating)
        await callback.message.answer(
            'Напишите текст отзыва или отправьте фото:',
            reply_markup=keyboards.return_main_menu
        )
        await state.set_state(ReviewState.waiting_for_text)

    await callback.answer()


# Обновлённый обработчик сохранения
@router.message(ReviewState.waiting_for_text)
async def save_new_review(message: Message, state: FSMContext, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    db = SessionLocal()
    try:
        data = await state.get_data()
        rating = data['rating']

        # Обработка контента
        text = message.text or ""
        file_id = None
        if message.photo:
            file_id = message.photo[-1].file_id
            text = message.caption or text

        # Сохраняем в БД
        new_review = Review(
            user_id=message.from_user.id,
            name=message.from_user.full_name,
            rating=rating,
            message_text=text,
            file_id=file_id,
            created_at=datetime.now()
        )

        db.add(new_review)
        db.commit()

        await message.answer(
            "✅ Отзыв успешно сохранен!",
            reply_markup=keyboards.return_main_menu
        )

    except Exception as e:
        db.rollback()
        await message.answer("❌ Ошибка сохранения отзыва",
            reply_markup=keyboards.return_main_menu)
    finally:
        db.close()
        await state.clear()


# Сохранение изменений
@router.message(ReviewState.editing_review)
async def save_edited_review(message: Message, state: FSMContext, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    db = SessionLocal()
    try:
        data = await state.get_data()
        review_id = data['review_id']

        # Ищем отзыв
        review = db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == message.from_user.id
        ).first()

        if not review:
            await message.answer("❌ Отзыв не найден",
            reply_markup=keyboards.return_main_menu)
            return

        # Обновляем данные
        review.message_text = message.text or ""
        if message.photo:
            review.file_id = message.photo[-1].file_id
            review.message_text = message.caption or review.message_text
        else:
            review.file_id = None  # Если фото нет, устанавливаем file_id в None
        review.created_at = datetime.now()

        db.commit()
        await message.answer(
            "✅ Отзыв обновлен!",
            reply_markup=keyboards.return_main_menu
        )

    except Exception as e:
        db.rollback()
        await message.answer("❌ Ошибка обновления",
            reply_markup=keyboards.return_main_menu)
    finally:
        db.close()
        await state.clear()


# Обработчик удаления отзыва
@router.callback_query(F.data.startswith('delete_review_'))
async def delete_review(callback: CallbackQuery):
    await callback.message.delete()
    review_id = int(callback.data.split('_')[2])
    db = SessionLocal()
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == callback.from_user.id
    ).first()

    if review:
        db.delete(review)
        db.commit()
        await callback.message.answer("✅ Отзыв успешно удален",
            reply_markup=keyboards.return_main_menu)
    else:
        await callback.message.answer("❌ Отзыв не найден",
            reply_markup=keyboards.return_main_menu)

    db.close()
    await callback.answer()

# Админ: управление отзывами
@router.callback_query(F.data == 'manage_reviews')
async def list_reviews(callback: CallbackQuery, bot: Bot):
    await callback.message.delete()
    db = SessionLocal()
    try:
        reviews = db.query(Review).all()
        if not reviews:
            await callback.message.answer('Нет отзывов.', reply_markup=keyboards.return_admin_main_menu)
            return
        # Собираем данные с URL
        rows = []
        for review in reviews:
            photo_url = ""
            if review.file_id:
                try:
                    file = await bot.get_file(review.file_id)
                    photo_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
                except Exception:
                    photo_url = "Ошибка получения фото"
            rows.append((
                review.id,
                review.user_id,
                review.rating,
                review.message_text or '',
                photo_url
            ))

        # Создаем DataFrame
        df = pd.DataFrame(
            rows,
            columns=['ID', 'User ID', 'Рейтинг', 'Сообщение', 'Фото']
        )

        # Создаем Excel с гиперссылками
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Отзывы')

            # Получаем доступ к листу
            worksheet = writer.sheets['Отзывы']

            # Форматируем столбец с фото
            for row_idx, url in enumerate(df['Фото'], start=2):
                cell = worksheet.cell(row=row_idx, column=5)
                if url.startswith('http'):
                    cell.hyperlink = url
                    cell.value = "Ссылка на фото"
                    cell.style = 'Hyperlink'
                else:
                    cell.value = url

            # Авто-ширина столбцов
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 5)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

        excel_buffer.seek(0)
        excel_file = BufferedInputFile(excel_buffer.getvalue(), filename='Отзывы.xlsx')

        await callback.message.answer_document(
            document=excel_file,
            caption=f"Всего отзывов {len(reviews)}",
            reply_markup=keyboards.return_reviews_manage
        )

        await callback.answer()
    except Exception as e:
        await callback.message.answer(f"Ошибка генерации отчета: {str(e)}")
    finally:
        db.close()
        await callback.answer()


@router.callback_query(F.data == 'manages_reviews')
async def ask_schedule_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('Введите ID отзыва для управления:', reply_markup=keyboards.admin_main_menu)
    await state.set_state(ReviewState.waiting_for_ID)
    await callback.answer()


@router.message(ReviewState.waiting_for_ID)
async def manage_review(message: Message, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    try:
        review_id = int(message.text)
        db = SessionLocal()
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            await message.answer("❌ Отзыв с таким ID не найден", reply_markup=keyboards.admin_main_menu)
            return
        # Формируем текст с Markdown
        text = (
            f"*ID отзыва:* {review.id}\n"
            f"*User ID:* {review.user_id}\n"
            f"*Оценка:* {review.rating}\n"
            f"*Сообщение:* {review.message_text or 'Нет текста'}"
        )

        kb = keyboards.delete_reviews(review.id)

        # Если есть прикрепленный файл
        if review.file_id:
            try:
                # Отправляем медиа с подписью
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=review.file_id,
                    caption=text,
                    reply_markup=kb,
                    parse_mode="Markdown"
                )
            except Exception as e:
                await message.answer(f"⚠️ Ошибка загрузки медиа: {str(e)}")
                await message.answer(text, reply_markup=kb, parse_mode="Markdown")
        else:
            await message.answer(
                text,
                reply_markup=kb,
                parse_mode="Markdown"
            )
    except ValueError:
        await message.answer("🔢 Введите корректный числовой ID")
    except Exception as e:
        await message.answer(f"🚨 Ошибка: {str(e)}")
    finally:
        db.close()



@router.callback_query(F.data.startswith('del_review_'))
async def delete_review(callback: CallbackQuery):
    await callback.message.delete()
    review_id = int(callback.data.split('_')[-1])
    db = SessionLocal()
    db.query(Review).filter(Review.id == review_id).delete()
    db.commit()
    db.close()
    await callback.message.answer(f'Отзыв {review_id} удалён.', reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()


# @router.callback_query(F.data == 'call_admin')
# async def ask_schedule_date(callback: CallbackQuery, state: FSMContext):
#     await callback.message.delete()
#     await callback.message.answer('Задайте Ваш вопрос, что бы администратор смог сразу написать Вам ответ.')
#     await callback.answer()


@router.callback_query(F.data == 'personal_templates')
async def show_personal_templates(callback: CallbackQuery):
    await callback.message.delete()
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
    await callback.message.delete()
    await callback.message.answer('Введите название шаблона:', reply_markup=keyboards.return_admin_main_menu)
    await state.set_state(TemplateState.waiting_for_name)
    await callback.answer()


@router.message(TemplateState.waiting_for_name)
async def process_template_name(message: Message, state: FSMContext, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    await state.update_data(name=message.text)
    await message.answer('Введите текст сообщения или фото(с подписью или без) для шаблона:',
                         reply_markup=keyboards.return_admin_main_menu)
    await state.set_state(TemplateState.waiting_for_personal_broadcast_content)


@router.message(TemplateState.waiting_for_personal_broadcast_content)
async def process_template_content(message: Message, state: FSMContext, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
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
    await callback.message.delete()
    if 'date' in callback.data:
        when = 'date'
        await callback.message.answer('Введите дату события к которому планируется рассылка в формате DD.MM.YYYY:')
        await state.set_state(TemplateState.waiting_for_date)
    else:
        when = 'birthday'
        await state.update_data(date_event=None)
        await callback.message.answer('Введите, за сколько дней до события делать рассылку:', reply_markup=keyboards.admin_main_menu)
        await state.set_state(TemplateState.waiting_for_count_days)
    await state.update_data(when_broadcast=when)
    await callback.answer()


@router.message(TemplateState.waiting_for_date)
async def process_event_date(message: Message, state: FSMContext, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    try:
        # Парсим дату, но сохраняем только день и месяц
        selected_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        date_event = selected_date.strftime("%d.%m")  # Формат DD.MM
    except ValueError:
        await message.answer("Неверный формат даты. Используйте DD.MM.YYYY.", reply_markup=keyboards.admin_main_menu)
        return

    await state.update_data(date_event=date_event)
    await message.answer("Введите, за сколько дней до события делать рассылку:")
    await state.set_state(TemplateState.waiting_for_count_days)


@router.message(TemplateState.waiting_for_count_days)
async def process_count_days(message: Message, state: FSMContext, bot: Bot):
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")
    try:
        count_days = int(message.text)
    except ValueError:
        await message.answer('Введите целое число и попробуйте снова.', reply_markup=keyboards.admin_main_menu)
        return
    await state.update_data(days_before=count_days)
    await message.answer('Для кого выполнять рассылку?', reply_markup=keyboards.sex_personal_broadcast)
    await state.set_state(TemplateState.waiting_for_sex_personal_broadcast)


@router.callback_query(F.data.startswith('pb_sex_'))
async def process_sex(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
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
    # Сохраняем message_id отправленных сообщений
    msgs_to_delete = []
    if data['content_type'] == 'photo':
        photo_msg = await callback.message.answer_photo(photo=data['file_id'], caption=data['message_text'])
        text_msg = await callback.message.answer(
            f"Подтвердите создание шаблона:\nИмя шаблона: {data['name']}\nРассылать к {'дню рождению' if data['when_broadcast'] == 'birthday' else data['date_event']} за {data['days_before']} дней до события.\nВыполнять рассылку для: {'женщин' if data['for_sex'] == 'female' else 'мужчин' if data['for_sex'] == 'male' else 'всех'}\n",
            reply_markup=confirmation_kb)
        msgs_to_delete = [photo_msg.message_id, text_msg.message_id]
    else:
        text_msg = await callback.message.answer(
            f"Подтвердите создание шаблона:\nИмя шаблона: {data['name']}\nТекст рассылки: {data['message_text']}\nРассылать к {'дню рождения' if data['when_broadcast'] == 'birthday' else data['date_event']} за {data['days_before']} дней до события.\nВыполнять рассылку для: {'женщин' if data['for_sex'] == 'female' else 'мужчин' if data['for_sex'] == 'male' else 'всех'}\n",
            reply_markup=confirmation_kb)
        msgs_to_delete = [text_msg.message_id]

    # Сохраняем ID сообщений для последующего удаления
    await state.update_data(msgs_to_delete=msgs_to_delete)
    await state.set_state(TemplateState.waiting_for_confirming)
    await callback.answer()


@router.callback_query(F.data == 'confirm_template')
async def save_new_template(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Удаляем все сообщения подтверждения
    for msg_id in data.get('msgs_to_delete', []):
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=msg_id
            )
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения {msg_id}: {e}")
    db = SessionLocal()
    try:
        tpl = PersonalTemplate(
            name=data['name'],
            content_type=data['content_type'],
            message_text=data['message_text'],
            file_id=data.get('file_id'),
            when_broadcast=data['when_broadcast'],
            date_event=data.get('date_event'),  # Уже в формате DD.MM
            days_before=data['days_before'],
            for_sex=data['for_sex']
        )
        db.add(tpl)
        db.commit()
        await callback.message.answer(f"✅ Шаблон '{data['name']}' создан!", reply_markup=keyboards.return_admin_main_menu)
        await callback.answer()
    except Exception as e:
        await callback.message.answer("❌ Ошибка при создании шаблона!", reply_markup=keyboards.return_admin_main_menu)
        await callback.answer()
        logging.error(e)
    finally:
        db.close()
        await state.clear()


@router.callback_query(F.data == 'cancel_template')
async def cancel_template(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.message.answer('Создание шаблона отменено.', reply_markup=keyboards.return_admin_main_menu)
    await callback.answer()


@router.callback_query(F.data.startswith('del_template_'))
async def delete_template(callback: CallbackQuery):
    await callback.message.delete()
    tpl_id = int(callback.data.split('_')[-1])
    db = SessionLocal()
    db.query(PersonalTemplate).filter(PersonalTemplate.id == tpl_id).delete()
    db.commit()
    db.close()
    await callback.message.answer(f'Шаблон удалён (ID {tpl_id}).', reply_markup=keyboards.admin_main_menu)
    await callback.answer()


async def check_personal_broadcasts(bot: Bot):
    db = SessionLocal()
    today = datetime.now().date()

    # Обрабатываем шаблоны с типом 'date' (праздники)
    date_templates = db.query(PersonalTemplate).filter(
        PersonalTemplate.when_broadcast == 'date'
    ).all()

    for template in date_templates:
        target_date = today + timedelta(days=template.days_before)
        if target_date.strftime("%d.%m") == template.date_event:
            users = db.query(User).filter(
                User.personal_broadcast == True,
                (User.sex == template.for_sex) if template.for_sex != 'all' else True
            ).all()
            await send_template(template, users, bot)

    # Обрабатываем шаблоны с типом 'birthday' (дни рождения)
    birthday_templates = db.query(PersonalTemplate).filter(
        PersonalTemplate.when_broadcast == 'birthday'
    ).all()

    for template in birthday_templates:
        target_date = today + timedelta(days=template.days_before)
        for user in db.query(User).filter(
                User.personal_broadcast == True,
                (User.sex == template.for_sex) if template.for_sex != 'all' else True
        ).all():
            if user.birthday:
                bday = user.birthday.date()
                try:
                    # Пробуем установить день рождения в текущем году
                    bday_this_year = bday.replace(year=target_date.year)
                except ValueError:
                    # Обработка 29 февраля в невисокосном году
                    bday_this_year = target_date.replace(day=28, month=2)

                if bday_this_year == target_date:
                    await send_template(template, [user], bot)

    db.close()


async def send_template(template, users, bot):
    for user in users:
        try:
            if template.content_type == 'photo':
                await bot.send_photo(
                    chat_id=user.telegram_id,
                    photo=template.file_id,
                    caption=template.message_text
                )
            else:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=template.message_text
                )
        except Exception as e:
            logging.error(f"Ошибка отправки пользователю {user.telegram_id}: {e}")
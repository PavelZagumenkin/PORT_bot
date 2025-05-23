from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📆 Анонс мероприятий', web_app=WebAppInfo(url='https://portfood.ru'))],
    [InlineKeyboardButton(text='🧾 Бронирование столика', callback_data='bron_number')],
    [InlineKeyboardButton(text='📋 Посмотреть меню', callback_data='categories')],
    [InlineKeyboardButton(text='🎁 Программа лояльности', web_app=WebAppInfo(url='https://portfood.ru/loyalty'))],
    [InlineKeyboardButton(text='📍 Как нас найти!', url='https://yandex.ru/maps/?um=constructor%3Ad9aa4631eaa489c014f2320d7709dfa34cb05016f6510fe33bfc0be46e0142ee&source=constructorLink')],
    [InlineKeyboardButton(text='⭐ Оставить отзыв', callback_data='leave_review')],
    [InlineKeyboardButton(text='❓ Часто задаваемые вопросы', callback_data='questions')],
    [InlineKeyboardButton(text='🪪 Персональные\nпредложения', callback_data='personal_broadcast_form')],
    [InlineKeyboardButton(text='🧑‍💼 Связать с администратором', callback_data='call_admin')]
])

categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🍜 Еда', web_app=WebAppInfo(url='https://portfood.ru/food'))],
    [InlineKeyboardButton(text='☕ Напитки', web_app=WebAppInfo(url='https://portfood.ru/drinks'))],
    [InlineKeyboardButton(text='🥃 Алкоголь', web_app=WebAppInfo(url='https://portfood.ru/alcohol'))],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])

questions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Можно ли с собакой?', callback_data='dog')],
    [InlineKeyboardButton(text='Где парковка?', callback_data='parking')],
    [InlineKeyboardButton(text='Есть детское кресло?', callback_data='сhild_seat')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])

return_or_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧑‍💼 Связать с администратором', callback_data='call_admin')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])

admin_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📢 Рассылка', callback_data='broadcast')],
    [InlineKeyboardButton(text='🔔 Персональные рассылки', callback_data='personal_templates')],
    [InlineKeyboardButton(text='📈 Статистика', callback_data='stats')],
    [InlineKeyboardButton(text='🗓️ Расписание администраторов', callback_data='schedule_admins')],
    [InlineKeyboardButton(text='📝 Отзывы', callback_data='manage_reviews')],
    [InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings')]
])

return_admin_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_admin_main_menu')]
])

personal_broadcast_form = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать', callback_data='personal_broadcast_form_start')],
    [InlineKeyboardButton(text='Что это?', callback_data='personal_broadcast_faq')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])

personal_broadcast_form_posle_faq = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать', callback_data='personal_broadcast_form_start')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])

finish_form = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Завершить", callback_data="pd_finish")]
])

sex_form = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='♂️ Мужчина', callback_data='pd_sex_male')],
        [InlineKeyboardButton(text='♀️ Женщина', callback_data='pd_sex_female')],
        [InlineKeyboardButton(text='🔙 Завершить', callback_data='pd_finish')]
    ])

sex_personal_broadcast = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='♂️ Мужчинам', callback_data='pb_sex_male')],
        [InlineKeyboardButton(text='♀️ Женщинам', callback_data='pb_sex_female')],
        [InlineKeyboardButton(text='💯 Для всех', callback_data='pb_sex_all')],
        [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_admin_main_menu')]
    ])

kb_enter_date_admin = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🗓️ Выбрать дату', callback_data='admin_sched_date')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='return_admin_main_menu')]
    ])


kb_add_admin = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='➕ Добавить', callback_data='choose_admin')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='return_admin_main_menu')]
    ])

enter_contact = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🗃️ Отправить свой контакт", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# для отзывов (оценка)
def review_keyboard():
    buttons = [InlineKeyboardButton(text=str(i), callback_data=f'review_{i}') for i in range(1, 6)]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Клавиатура завершения чата
def end_chat_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Завершить диалог', callback_data='end_chat')
    ]])

# Клавиатура ответа админу
def reply_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить", callback_data=f"reply_to_{user_id}")
    ]])

personal_broadcast_yes = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить данные', callback_data='personal_broadcast_form_start')],
    [InlineKeyboardButton(text='Отписаться', callback_data='unsubscribe_personal_broadcast')],
    [InlineKeyboardButton(text='Что это?', callback_data='personal_broadcast_faq')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])




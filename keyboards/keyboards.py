from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    # [InlineKeyboardButton(text='📆 Анонс мероприятий', callback_data='anons_broadcast')],
    [InlineKeyboardButton(text='🧾 Бронирование столика', callback_data='bron_number')],
    [InlineKeyboardButton(text='📋 Посмотреть меню', callback_data='categories')],
    [InlineKeyboardButton(text='🎁 Программа лояльности', web_app=WebAppInfo(url='https://portfood.ru/loyalty'))],
    [InlineKeyboardButton(text='📍 Как нас найти!', url='https://yandex.ru/maps/?um=constructor%3Ad9aa4631eaa489c014f2320d7709dfa34cb05016f6510fe33bfc0be46e0142ee&source=constructorLink')],
    [InlineKeyboardButton(text='✨ Отзывы', callback_data='leave_review')],
    [InlineKeyboardButton(text='❓ Часто задаваемые вопросы', callback_data='questions')],
    [InlineKeyboardButton(text='🪪 Получать персональные\nпредложения', callback_data='personal_broadcast_form')],
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
    [InlineKeyboardButton(text='Есть детское кресло?', callback_data='child_seat')],
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


# для отзывов (оценка)
def review_keyboard():
    buttons_line1 = [InlineKeyboardButton(text=str(i*'⭐'), callback_data=f'review_{i}') for i in range(1, 4)]
    buttons_line2 = [InlineKeyboardButton(text=str(i * '⭐'), callback_data=f'review_{i}') for i in range(4, 6)]
    return InlineKeyboardMarkup(inline_keyboard=[buttons_line1, buttons_line2])


# Удаления отзыва из админ-панели
def delete_reviews(review_ID):
    return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🗑 Удалить', callback_data=f'del_review_{review_ID}')],
            [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_admin_main_menu')]
        ])


personal_broadcast_yes = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить данные', callback_data='personal_broadcast_form_start')],
    [InlineKeyboardButton(text='Отписаться', callback_data='unsubscribe_personal_broadcast')],
    [InlineKeyboardButton(text='Что это?', callback_data='personal_broadcast_faq')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])

return_reviews_manage = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📈 Удалить отзывы', callback_data='manages_reviews')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_admin_main_menu')]
])

my_reviews = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💫 Мои отзывы', callback_data='my_reviews')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])

my_reviews_add = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💫 Мои отзывы', callback_data='my_reviews')],
    [InlineKeyboardButton(text='⭐ Оставить отзыв', callback_data='create_reviews')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])

return_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])




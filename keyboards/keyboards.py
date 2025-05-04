from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📆 Анонс мероприятий', web_app=WebAppInfo(url='https://portfood.ru'))],
    [InlineKeyboardButton(text='🧾 Бронирование столика', callback_data='bron_number')],
    [InlineKeyboardButton(text='📋 Посмотреть меню', callback_data='categories')],
    [InlineKeyboardButton(text='🎁 Программа лояльности', web_app=WebAppInfo(url='https://portfood.ru/loyalty'))],
    [InlineKeyboardButton(text='📍 Как нас найти!', url='https://yandex.ru/maps/?um=constructor%3Ad9aa4631eaa489c014f2320d7709dfa34cb05016f6510fe33bfc0be46e0142ee&source=constructorLink')],
    [InlineKeyboardButton(text='⭐ Оставить отзыв', web_app=WebAppInfo(url='https://portfood.ru'))],
    [InlineKeyboardButton(text='❓ Часто задаваемые вопросы', callback_data='questions')],
    [InlineKeyboardButton(text='🧑‍💼 Связать с администратором', web_app=WebAppInfo(url='https://portfood.ru'))]
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
    [InlineKeyboardButton(text='🧑‍💼 Связать с администратором', web_app=WebAppInfo(url='https://portfood.ru'))],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_main_menu')]
])

admin_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📢 Рассылка', callback_data='broadcast')],
    [InlineKeyboardButton(text='🔔 Персональные рассылки', callback_data='personal_broadcast')],
    [InlineKeyboardButton(text='📈 Статистика', callback_data='stats')],
    [InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings')]
])

return_admin_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='return_admin_main_menu')]
])
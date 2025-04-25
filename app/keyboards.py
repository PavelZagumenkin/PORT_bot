from aiogram.filters import callback_data
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📆 Анонс мероприятий', web_app=WebAppInfo(url='https://portfood.ru'))],
    [InlineKeyboardButton(text='🧾 Бронирование столика', web_app=WebAppInfo(url='https://portfood.ru'))],
    [InlineKeyboardButton(text='📋 Посмотреть меню', callback_data='categories')],
    [InlineKeyboardButton(text='🎁 Программа лояльности', web_app=WebAppInfo(url='https://portfood.ru/loyalty'))],
    [InlineKeyboardButton(text='⭐ Оставить отзыв', web_app=WebAppInfo(url='https://portfood.ru'))],
    [InlineKeyboardButton(text='❓ Часто задаваемые вопросы', callback_data='questions')],
    [InlineKeyboardButton(text='🧑‍💼 Связать с администратором', web_app=WebAppInfo(url='https://portfood.ru'))],
    [InlineKeyboardButton(text='❌ Закрыть', callback_data='exit')]
])

categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🍜 Еда', web_app=WebAppInfo(url='https://portfood.ru/food'))],
    [InlineKeyboardButton(text='☕ Напитки', web_app=WebAppInfo(url='https://portfood.ru/drinks'))],
    [InlineKeyboardButton(text='🥃 Алкоголь', web_app=WebAppInfo(url='https://portfood.ru/alcohol'))],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='start')]
])

exit = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Старт')]
], resize_keyboard=True, input_field_placeholder='Нажмите СТАРТ для общения с PORT_bot', one_time_keyboard=True)

questions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Можно ли с собакой?', callback_data='dog')],
    [InlineKeyboardButton(text='Где парковка?', callback_data='parking')],
    [InlineKeyboardButton(text='Есть детское кресло?', callback_data='сhild_seat')],
    [InlineKeyboardButton(text='🔙 Главное меню', callback_data='start')]
])

return_or_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧑‍💼 Связать с администратором', web_app=WebAppInfo(url='https://portfood.ru'))],
    [InlineKeyboardButton(text='🔙 К вопросам', callback_data='questions')]
])
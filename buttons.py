from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Регистрация в бонусной программе")]],
    resize_keyboard=True
)

test_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Передать номер телефона", request_contact=True)]],
    resize_keyboard=True
)

status_and_send_qr_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Статус"), KeyboardButton(text="Отправить QR-код")], [KeyboardButton(text="Получить бонус")]],
    resize_keyboard=True
)

admin_kb1 = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Кофе в подарок")]],
    resize_keyboard=True
)

admin_kb2 = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отмена")]],
    resize_keyboard=True
)

del_kb = ReplyKeyboardRemove()

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, Contact
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime
import os

import asyncio
import sys
import logging
from configparser import RawConfigParser

import buttons
import database
from states import UserState, AdminState
import qr_scanner
import qr_creator
import filter
import proverka_checka

file = 'config.ini'
config = RawConfigParser()
config.read(file)
token = config['telegram']['token']
path_to_db = config['client']['path_to_db']
db_customers = config['client']['database']
fn_etalon = config['client']['fn']
admin_ids = config['admin']['admin_ids'].split(',')

bot = Bot(token=token, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """ This handler receives messages with `/start` command """
    if await filter.is_admin(admin_ids, message.from_user.id):
        await message.answer(f"Привет, админ!", reply_markup=buttons.admin_kb1)
        await state.set_state(AdminState.main)
    else:
        await message.answer(f"Здравствуйте! Сканируйте qr-коды с ваших чеков с помощью этого телеграм-бота. "
                             f"Каждая 5 чашка кофе в подарок!", reply_markup=buttons.start_kb)
        await database.create_main_tables(path_to_db, db_customers)
        await state.set_state(UserState.register)


@dp.message(AdminState.main)
async def bonus_handler(message: Message, state: FSMContext) -> None:
    """
    Функция ждет, что админ нажмет на кнопку 'Кофе в подарок', чтобы подтвердить бонус клиента если он имеется.
    """
    if message.text == "Кофе в подарок":
        await message.answer("Пришлите qr-код клиента", reply_markup=buttons.admin_kb2)
        await state.set_state(AdminState.make_bonus)
    else:
        await message.answer("Если вы хотите подтвердить бонус пользователя, нажмите на кнопку 'Кофе в подарок'")


@dp.message(AdminState.make_bonus)
async def phone_message_handler(message: Message, state: FSMContext):
    """
    Админ может сфотографировать сгенерированный ботом qr-код пользователя для получения бонуса и отправить 
    его на проверку в чат или сделать откат назад, нажав 'Отмена'
    """
    if message.text == "Отмена":
        await message.answer("У нас отмена!", reply_markup=buttons.admin_kb1)
        await state.set_state(AdminState.main)
    elif message.photo:
        qr_data = await qr_scanner.get_qr_from_photo(message, bot, token)
        user_id = message.from_user.id
        database.change_status_in_qr_table(user_id, path_to_db, db_customers) # дописать функцию

        await message.answer(qr_data)
        await state.set_state(AdminState.main)
    else:
        await message.answer("Нужно прислать фото qr-кода")


@dp.message(UserState.register)
async def text_message_handler(message: Message, state: FSMContext) -> None:
    """
    Запрос на отправку номера телефона пользователя для регистрации в бонусной программе
    """
    if message.text == "Регистрация в бонусной программе":
        await message.answer("Пришлите номер телефона", reply_markup=buttons.test_kb)
        await state.set_state(UserState.get_phone)
    else:
        await message.answer("Для регистрации нажмите кноку ниже")


@dp.message(UserState.get_phone)
async def contact_handler(message: Message, state: FSMContext) -> None:
    """
    Регистрация и авторизация пользователя в бонусной программе.
    """
    contact: Contact = message.contact
    if contact is not None:
        if database.fill_customers(path_to_db, db_customers, contact.phone_number, str(contact.user_id)):
            await message.answer(
                f"Регистрация прошла успешно. Ваш номер добавлен в бонусную программу. Можете прислать фото чека",
                reply_markup=buttons.status_and_send_qr_kb)
        else:
            await message.answer(
                f"Вы уже зарегистрированы в нашей бонусной программе. Можете прислать фото или скан чека",
                reply_markup=buttons.status_and_send_qr_kb)
        await state.set_state(UserState.get_menu)


@dp.message(UserState.get_menu)
async def check_bonus(message: Message, state: FSMContext) -> None:
    """
    При смене статуса на get_menu бот будет ожидать одно из двух действий - Статус или Отправить QR.
    """
    if message.text == "Статус":
        user_id = message.from_user.id
        res = database.check_bonus_coffee_by_user(user_id, path_to_db, db_customers)
        print("BONUS CUPS", res)
        if res // 4 == 0:
            await message.answer(f"До бонуса осталось {4 - res} {filter.cups_left(4 - res)}")
        elif res % 4 == 0:
            await message.answer(f"Вам доступно {res // 4} {filter.bonus_left(res // 4)}")
        else:
            await message.answer(
                f"Вам доступно {res // 4} {filter.bonus_left(res // 4)}. До следующего вам необходимо {4 - (res % 4)} {filter.cups_left(4 - (res % 4))}")
    elif message.text == "Отправить QR-код":
        await message.answer("Можете прислать фото или скан qr")
        await state.set_state(UserState.get_qr)
    elif message.text == "Получить бонус":
        user_id = message.from_user.id
        res = database.check_bonus_coffee_by_user(user_id, path_to_db, db_customers)
        if res < 4:
            await message.answer("Вам не доступен бонус")
        else:
            qr = qr_creator.create_qr(user_id)
            qr.save(f"{user_id}.png")
            img = FSInputFile(f"{user_id}.png")
            await message.reply_photo(img, caption="Покажите qr кассиру и заберите свой бонус")
            os.remove(f"{user_id}.png")
    else:
        await message.answer("Выберите что-то из опций ниже")


@dp.message(UserState.get_qr)
async def qr_handler(message: Message, state: FSMContext) -> None:
    """
    Функция принимает только фото для обработки QR-кодов.
    """
    if message.photo:
        qr_data = await qr_scanner.get_qr_from_photo(message, bot, token)

        if qr_data:
            user_id = message.from_user.id

            qr_elements = qr_data.split('&')
            data_checks = {}
            for el in qr_elements:
                key, value = el.split('=')
                data_checks[key] = value
            date_of_purchase = datetime.strptime(data_checks['t'], '%Y%m%dT%H%M')
            summa = data_checks['s']
            fn = data_checks['fn']
            index = data_checks['i']

            amount = database.add_to_qr(user_id, date_of_purchase, summa, fn, index,
                                        path_to_db, db_customers)

            if amount % 4 == 0:
                await message.answer(f"Вам бесплатный кофе. Нажмите на кнопку 'Получить бонус' и покажите "
                                     f"сгенерированный QR-код бариста, он сделает вам бесплатный напиток")
            else:
                await message.answer(f"QR-code распознан и добавлен в базу!\n\n{qr_data}")
        else:
            await message.answer("QR-code не распознан")
        await state.set_state(UserState.get_menu)
    else:
        await message.answer("Нужно прислать картинку")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    register = State()
    get_phone = State()
    get_qr = State()
    get_menu = State()


class AdminState(StatesGroup):
    main = State()
    make_bonus = State()

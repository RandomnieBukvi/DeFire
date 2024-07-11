from aiogram.fsm.state import StatesGroup, State

class Subscribe(StatesGroup):
    device_id = State()
    password = State()

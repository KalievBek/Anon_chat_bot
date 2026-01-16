from aiogram.fsm.state import State, StatesGroup

class BroadcastStates(StatesGroup):
    waiting_message = State()
    waiting_filters = State()
    waiting_confirmation = State()
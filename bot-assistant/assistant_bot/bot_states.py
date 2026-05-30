from aiogram.fsm.state import StatesGroup, State


class QuestionForm(StatesGroup):
    default_question = State()
    other_question = State()

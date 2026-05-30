import uuid
from datetime import datetime

import structlog
from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from peewee import DoesNotExist, OperationalError, ProgrammingError

from assistant_bot.bot_states import QuestionForm
from assistant_bot.bot_choices import DetailedQuestions, answers
from assistant_bot.keyboards.for_questions import (
    get_choose_parking_inline_keyboard,
    get_choose_charging_connector_inline_keyboard,
    get_needed_question_inline_keyboard,
    get_start_question_session_keyboard_button,
    get_report_problem_inline_keyboard,
)
from assistant_bot.text_constants import start_message, choose_connector_message, choose_question_message
from config import Config
from orm.postgreSQL.models.sessions_table import Session
from orm.postgreSQL.models.users_table import User

_config = Config()
_logger = structlog.get_logger(__name__)

router = Router()
# router.message.middleware(QuestionsMiddleware())


@router.message(
    Command('start'),
    StateFilter(None),
)
async def cmd_start(
    message: types.Message,
    state: FSMContext,
    question_session: Session,
) -> None:
    default_state = await state.get_state()
    _logger.info(
        'Set default state',
        state=default_state,
        from_user=message.from_user,
    )

    user_id = message.from_user.id
    first_name = message.from_user.first_name
    second_name = message.from_user.last_name
    user_name = message.from_user.username

    try:
        user: User = User.get(User.user_telegram_id == user_id)

        _logger.info(
            'User found',
            user=user,
        )
    except DoesNotExist as err:
        _logger.error(
            'Getting user failed cause does not exist',
            error=err,
        )
        user = User.create(
            user_telegram_id=user_id,
            first_name=first_name,
            second_name=second_name,
            user_name=user_name,
        )
    except OperationalError as op_err:
        _logger.error(
            'Getting user failed by operational error',
            error=op_err,
        )
        user = User.create(
            user_telegram_id=user_id,
            first_name=first_name,
            second_name=second_name,
            user_name=user_name,
        )
    except ProgrammingError as program_err:
        _logger.error(
            'Getting user failed by some programming error',
            error=program_err,
        )
        user = User.create(
            user_telegram_id=user_id,
            first_name=first_name,
            second_name=second_name,
            user_name=user_name,
        )

    _logger.info(
        'Bot handled /start command',
        user=user,
    )

    question_session.session_id = uuid.uuid4()
    question_session.user = user
    question_session.asked_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    _logger.info(
        'Bot create new question session',
        session=question_session,
    )

    await message.answer(
        start_message,
        reply_markup=get_choose_parking_inline_keyboard(),
    )

    await state.set_state(QuestionForm.default_question)

    current_state = await state.get_state()
    _logger.info(
        'Current set state',
        state=current_state,
    )


@router.callback_query(F.data.startswith('place_'))
async def callback_chosen_place(callback: types.CallbackQuery, charging_space: dict):
    # TODO: in future replace dict to Space from Django econrg_server
    _logger.info(
        'handled callback from choosing space dialog',
        callback_message_id=callback.message.message_id,
        callback_message_date=callback.message.date,
        callback_message_chat_id=callback.message.chat.id,
        callback_data=callback.data,
        from_user=callback.from_user,
    )

    place = callback.data.split('_')[1]
    charging_space['place'] = place
    keyboard: InlineKeyboardMarkup

    result = get_choose_charging_connector_inline_keyboard(place)
    if type(result) is not InlineKeyboardMarkup:
        await callback.message.edit_text(result)
    else:
        keyboard = result
        await callback.message.edit_text(
            choose_connector_message,
            reply_markup=keyboard,
        )

    _logger.info(
        (
            'finished handling place/ callback' if type(result) is InlineKeyboardMarkup
            else 'finished handling place/ callback with place exception'
        ),
        resulting_reply_message=choose_connector_message,
        space=charging_space,
    )

    await callback.answer()


@router.callback_query(F.data.startswith('connector_'))
async def callback_chosen_connector(callback: types.CallbackQuery, charging_space: dict):
    _logger.info(
        'handled callback from choosing connector dialog',
        callback_message_id=callback.message.message_id,
        callback_message_date=callback.message.date,
        callback_message_chat_id=callback.message.chat.id,
        callback_data=callback.data,
        from_user=callback.from_user,
    )

    connector = callback.data.split('_')[1]
    charging_space['connector'] = connector

    await callback.message.edit_text(
        choose_question_message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_needed_question_inline_keyboard(),
    )

    _logger.info(
        'finished handling connector/ callback',
        message=choose_question_message,
    )

    await callback.answer()


@router.callback_query(F.data.startswith('back_to_'))
async def callback_back_to_places(callback: types.CallbackQuery, charging_space: dict):
    _logger.info(
        'handled callback back_to/ from choosing dialog',
        back_to=callback.data,
        callback_message_id=callback.message.message_id,
        callback_message_date=callback.message.date,
        callback_message_chat_id=callback.message.chat.id,
        from_user=callback.from_user,
    )

    case = callback.data.split('_')[2]

    if case.lower().strip() == 'places':
        await callback.message.edit_text(
            start_message,
            reply_markup=get_choose_parking_inline_keyboard(),
        )

    elif case.lower().strip() == 'connectors':
        await callback.message.edit_text(
            choose_connector_message,
            reply_markup=get_choose_charging_connector_inline_keyboard(
                charging_space.get('place')
            ),
        )

    await callback.answer()


@router.callback_query(F.data.startswith('question/'))
async def callback_answer_the_question(
    callback: types.CallbackQuery,
    state: FSMContext,
    question_session: Session,
    charging_space: dict,
):
    _logger.info(
        'handled callback from answering the dialog`s question',
        back_to=callback.data,
        callback_message_id=callback.message.message_id,
        callback_message_date=callback.message.date,
        callback_message_chat_id=callback.message.chat.id,
        from_user=callback.from_user,
    )

    detailed_questions = DetailedQuestions.__dict__
    question_alias = callback.data.split('/')[1]
    question = detailed_questions.get(question_alias)
    answer = answers.get(question)

    await callback.message.edit_text(
        f'Выбранная вами проблема:\n«{question}»'
    )

    if question == DetailedQuestions.OTHER_QUESTION:
        await callback.message.answer(
            'Опишите, пожалуйста, проблему',
        )
        await state.set_state(QuestionForm.other_question)

    else:
        message = (
            f'''
            {answer}
            '''
        )

        await callback.message.answer(
            message,
            reply_markup=get_start_question_session_keyboard_button(),
        )

        await callback.message.answer(
            f'''
                Номер Вашего обращения: {question_session.session_id}
                Зарядная станция и разъем, на которых у Вас возникла проблема: 
                {charging_space.get('place')} и {charging_space.get('connector')}
                ''',
            reply_markup=get_report_problem_inline_keyboard(),
        )

        await state.set_state(None)

    question_session.question = question
    question_session.place = f'{charging_space.get("place")}'
    question_session.connector = f'{charging_space.get("connector")}'
    question_session.is_solved = True
    question_session.solved_at = datetime.now()

    Session.create(
        session_id=question_session.session_id,
        user=question_session.user,
        question=question_session.question,
        place=question_session.place,
        connector=question_session.connector,
        asked_in=question_session.asked_in,
        is_solved=question_session.is_solved,
        solved_at=question_session.solved_at,
    )

    current_state = await state.get_state()

    _logger.info(
        'saved question session',
        session=question_session,
        state=current_state,
    )

    await callback.answer()


@router.message(F.text, QuestionForm.other_question)
async def listen_other_question(
        message: types.Message,
        state: FSMContext,
        question_session: Session,
        charging_space: dict,
):
    _logger.info(
        'start listener for other question',
        message_id=message.message_id,
        callback_message_date=message.date,
        callback_message_chat_id=message.chat.id,
        from_user=message.from_user,
    )
    
    _logger.info(
        'inner context data',
        current_session=question_session,
        current_space=charging_space,
    )

    await message.answer(
        '''
        Спасибо за Ваш вопрос, он будет передан первому свободному оператору
        ''',
        reply_markup=get_start_question_session_keyboard_button(),
    )

    session: Session = Session()
    try:
        session = Session.get(Session.session_id == question_session.session_id)
    except DoesNotExist as err:
        _logger.error(
            f'Catch exception with getting session by id: {question_session.session_id}',
            error=err,
        )

    _logger.info(
        'Get created question session',
        session=session,
    )

    other_question = message.text
    question = session.question.split()[0]
    question = f'{question} ({other_question})'
    session.question = question
    session.save()

    _logger.info(
        'Updated question session',
        session=session,
    )

    await message.answer(
        f'''
            Номер Вашего обращения: {question_session.session_id}
            Зарядная станция и разъем, на которых у Вас возникла проблема: 
            {charging_space.get('place')} и {charging_space.get('connector')}
            ''',
        reply_markup=get_report_problem_inline_keyboard(),
    )

    await state.set_state(None)

    current_state = await state.get_state()
    _logger.info(
        'Current set state',
        state=current_state,
    )


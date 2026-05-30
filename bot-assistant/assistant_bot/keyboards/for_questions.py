import math

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import structlog

from backend.services.space_service import ParkingPlaces
from assistant_bot.bot_choices import DetailedQuestions
from config import Config

_config = Config()
_logger = structlog.get_logger(__name__)
parking_places = ParkingPlaces()


def get_start_question_session_keyboard_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(
            text='/start',
        )
    )

    return builder.as_markup(resize_keyboard=True)


def get_choose_parking_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    parking_places.update_parking_places()
    for place in parking_places.parking_places.keys():
        builder.add(
            InlineKeyboardButton(
                text=place,
                callback_data=f'place_{place.strip()}'
            )
        )
    builder.adjust(int(math.sqrt(len(parking_places.parking_places))))
    return builder.as_markup()


def get_choose_charging_connector_inline_keyboard(place):
    try:
        connectors = parking_places.parking_places.get(place)
    except KeyError as err:
        _logger.error(
            'Getting connectors failed with key error',
            error=err,
        )
        return _config.BOT_TEXTS_UNEXPECTED_ERROR

    builder = InlineKeyboardBuilder()
    for connector in connectors:
        builder.add(
            InlineKeyboardButton(
                text=connector,
                callback_data=f'connector_{connector.strip()}'
            )
        )
    builder.adjust(int(math.sqrt(len(connectors))))
    builder.row(
        InlineKeyboardButton(
            text='Вернуться к выбору мест',
            callback_data='back_to_places'
        )
    )

    return builder.as_markup()


def get_needed_question_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    detailed_questions = DetailedQuestions.__dict__
    module = detailed_questions.get('__module__')

    for question in detailed_questions.keys():
        if type(detailed_questions.get(question)) is str and detailed_questions.get(question) != module:
            builder.row(
                InlineKeyboardButton(
                    text=detailed_questions.get(question),
                    callback_data=f'question/{question}'
                )
            )
    builder.row(
        InlineKeyboardButton(
            text='Вернуться к выбору разъема',
            callback_data='back_to_connectors',
        )
    )

    return builder.as_markup()


def get_report_problem_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='Сообщить оператору',
            url=_config.REPORT_PROBLEM_URL,
        )
    )

    return builder.as_markup()

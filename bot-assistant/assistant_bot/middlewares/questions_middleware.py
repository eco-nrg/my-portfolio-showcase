from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from assistant_bot.bot_states import QuestionForm


class QuestionsMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        state = data.get('state')
        user_data = await state.get_data()

        if not user_data:
            await QuestionForm.default_question.set()

        return await handler(event, data)

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from src.database import get_user, create_user
from src.services.i18n import _

class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        event_user: TgUser = data.get("event_from_user")
        
        if event_user:
            user = await get_user(event_user.id)
            if not user:
                user = await create_user(event_user.id)
                user_lang = user.interface_lang
                learn_lang = user.learning_lang
            else:
                user_lang = user.interface_lang
                learn_lang = user.learning_lang
            
            data["user_lang"] = user_lang
            data["learn_lang"] = learn_lang
            
            # Inject a lazy translation function
            data["_"] = lambda key, **kwargs: _(key, user_lang, **kwargs)
            
        return await handler(event, data)

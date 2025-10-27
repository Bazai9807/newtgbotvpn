from aiogram.filters import Command, CommandStart, BaseFilter
from aiogram.types import Message, CallbackQuery
import config_bd.users as sel


def list_admin():
    s = sel.SQL()
    return s.SELECT_ID_ADMIN()


class NewUser(BaseFilter):

    def __init__(self, ):
        pass


class IsAdmin(BaseFilter):

    admin_ids = list_admin()

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids


class IsDigitCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return isinstance(callback.data, str) and callback.data.isdigit()


class IsDelBookmarkCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return isinstance(callback.data, str) and 'del'         \
            in callback.data and callback.data[:-3].isdigit()
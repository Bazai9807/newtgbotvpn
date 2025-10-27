from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, KeyboardButton, InlineQueryResultLocation, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from lexicon.lexicon import LEXICON_MENU_COMMANDS_RU

dp: Dispatcher = Dispatcher()


# Функция генерит инлайн-клавиатуру автоматом в зависимости от ЛЕКСИКОНА

def create_inline_kb(width: int | list[int], link: list[str] | None = None, link_names: list[str] | None = None,  **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализация билдера
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализация списка кнопок
    buttons: list[InlineKeyboardButton] = []

    if link and link_names:
        try:
            for i in link:
                buttons.append(InlineKeyboardButton(text=link_names[link.index(i)], url=i))
        except IndexError:
            buttons.append(InlineKeyboardButton(text=link_names[0], url=link[0]))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(text=text, callback_data=button))
    kb_builder.add(*buttons)
    if isinstance(width, int):
        kb_builder.adjust(width)
    else:
        kb_builder.adjust(*width)
    # Возврат объекта инлайн-клавиатуры
    return kb_builder.as_markup()





def create_key_kb_inside(width: int, linc: str = None, *args: str, **kwargs: str):
    # Инициализируем билдер для клавиатуры ADMIN"
    admin_menu_b: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    # # Инициализация списка кнопок
    buttons: list[KeyboardButton] = []

    if args:
        for button in args:
            buttons.append(KeyboardButton(text=button))
    if kwargs:
        for key, button in kwargs.items():
            buttons.append(KeyboardButton(text=button))

    admin_menu_b.row(*buttons, width=width)
    return admin_menu_b.as_markup(resize_keyboard=True)


def create_link(link, last_btn: str | None = None, last1_btn: str | None = None):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    if last_btn:
        kb_builder.row(InlineKeyboardButton(text=last_btn, web_app=WebAppInfo(url=link)))
    if last1_btn:
        kb_builder.row(InlineKeyboardButton(text=last1_btn, callback_data='btp'))
    return kb_builder.as_markup()


def create_link1(link, last_btn: str | None = None, last1_btn: str | None = None):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    if last_btn:
        kb_builder.row(InlineKeyboardButton(text=last_btn, url=link))
    if last1_btn:
        kb_builder.row(InlineKeyboardButton(text=last1_btn, callback_data='btp'))
    return kb_builder.as_markup()



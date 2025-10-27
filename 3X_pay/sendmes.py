from keyboards.inline.keyboard import create_inline_kb
from lexicon.lexicon import *
from aiogram import Bot
from X3 import X3
from config_data.config import load_config

ADMIN = load_config().tg_bot.admin_ids


async def text(bot: Bot, t, markups):
    if markups == "1":
        markup = create_inline_kb(1, **LEXICON_LISTED)
    else:
        markup = create_inline_kb(5, **LEXICON_GRADE)
    x3 = X3()
    x3.test_connect()
    activ_list = x3.activ_list()
    for key, _ in activ_list.items():
        try:
            await bot.send_message(key, t, reply_markup=markup, parse_mode="html")
        except:
            pass
    for i in ADMIN:
        await bot.send_message(i, "Сообщение было доставлено")


async def text_to(bot: Bot, ids, markups, t):#аргумент ids передавать в качестве массива, образец - ["какой-то id", ]
    if markups == "1":
        markup = create_inline_kb(1, **LEXICON_LISTED)
    else:
        markup = create_inline_kb(1, **LEXICON_GRADE)
    for i in ids:
        try:
            await bot.send_message(i, t, reply_markup=markup)
        except:
            pass
    for i in ADMIN:
        await bot.send_message(i, "Сообщение было доставлено")

if __name__ == '__main__':
    text(Bot, t='132')

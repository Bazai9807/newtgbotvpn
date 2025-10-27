from aiogram import Bot
from X3 import X3
from keyboards.inline.keyboard import create_inline_kb
from lexicon.lexicon import LEXICON_MENU2_RU, LEXICON_MENU1_PAY2_RU, LEXICON_GRADE
from config_bd.users import SQL

LEXICON_GRADE['pp'] = "💸 Продлить подписку"

keyboard_in_pay = create_inline_kb(1, **LEXICON_MENU1_PAY2_RU)
keyboard_for_grade = create_inline_kb([5,5,1], link=['https://t.me/Avohelp'], link_names=['Поддержка🫂'],  **LEXICON_GRADE)
keyboard_teh = create_inline_kb(1 ,link=['https://t.me/Avohelp'], link_names=['Поддержка🫂'], **{'pp': "💸 Продлить подписку"})


async def send_message_cron(bot: Bot):
    x3 = X3()
    x3.test_connect()
    activ_list = x3.activ_list()
    for key, val in activ_list.items():
        try:
            if 1 < int(val) <= 2 and key.isdigit():
                sql = SQL()
                sql.UPDATE_BLOK(int(key), True)
                await bot.send_message(key, LEXICON_MENU2_RU['23'], reply_markup=keyboard_teh)
            elif 0 <= int(val) <= 1 and key.isdigit():
                sql = SQL()
                sql.UPDATE_BLOK(int(key), True)
                await bot.send_message(key, LEXICON_MENU2_RU['24'], reply_markup=keyboard_teh)
            elif int(val) == -1 and key.isdigit():
                sql = SQL()
                sql.UPDATE_BLOK(int(key), True)
                await bot.send_message(key, LEXICON_MENU2_RU['25'], reply_markup=keyboard_for_grade)
                x3.test_connect()
                x3.updateClientOut(key)
            else:
                continue
        except:
            pass


def send_message_cron1():
    x3 = X3()
    x3.test_connect()
    activ_list = x3.activ_list()
    for key, val in activ_list.items():
        print(val)
        if 1 > val <= 2 and key.isdigit():
            print(key)
        elif 0 >= val <= 1 and key.isdigit():
            print(key)
        elif val < 0 and key.isdigit():
            print(key)
        else:
            continue


if __name__ == '__main__':
    send_message_cron1()




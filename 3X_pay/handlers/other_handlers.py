import os
import time
import sqlite3
import pay_yoo
from config_bd.users import SQL
import asyncio
from yookassa import Payment
from X3 import X3
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, LabeledPrice, InputMediaPhoto, InputMediaVideo
from aiogram.filters import CommandStart, Text, Command
from keyboards.inline.keyboard import create_inline_kb, create_key_kb_inside, create_link, create_link1
from lexicon.lexicon import *
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config_data.config import load_config
ADMIN = load_config().tg_bot.admin_ids
global active
global time
global count_key

x3 = X3()
sql = SQL()

# Инициализируем роутер уровня модуля
router: Router = Router()
keyboard_in1 = create_inline_kb(1, **LEXICON_MENU1_BUTTON_RU)
keyboard_in11 = create_inline_kb(1, **LEXICON_MENU1_BUTTON_NEW_RU)
keyboard_in2 = create_inline_kb(1, **LEXICON_MENU2_BUTTON_RU)
keyboard_in33 = create_inline_kb(1, **LEXICON_MENU33_BUTTON_RU)
keyboard_in_pay = create_inline_kb(1, **LEXICON_MENU1_PAY_RU)
keyboard_supper = create_key_kb_inside(2, **LEXICON_MENU_RU)
keyboard_in4 = create_inline_kb(2, **LEXICON_MENU_INSTR_RU)
keyboard_in5 = create_inline_kb(2, **LEXICON_MENU_INSTRIOS_RU)
keyboard_link22 = create_inline_kb(1, **LEXICON_BACKINSTR, link=['https://play.google.com/store/apps/details?id=com.v2raytun.android','https://telegra.ph/Nastrojka-BARS-VPN-na-andriod-06-26'], link_names=['СКАЧАТЬ V2rayNG☕','Инструкция📕'])#android
keyboard_link24 = create_inline_kb(1, **LEXICON_BACKINSTR, link=['https://drive.google.com/file/d/1Eu7Eo6W0CdTF5dUvO608QqQClYTVu2fj/view?usp=sharing', 'https://telegra.ph/Nastrojka- -VPN-na-windows-12-27'], link_names=['СКАЧАТЬ v2rayNG(windows)☕', 'Инструкция📕'])#windows - изменена ссылка на скачивыание
keyboard_link25 = create_inline_kb(1, **LEXICON_BACKINSTR, link=['https://apps.apple.com/ru/app/v2raytun/id6476628951','https://telegra.ph/Nastrojka-BARS-VPN-na-iPhone-12-12'], link_names=['СКАЧАТЬ v2RayTun☕','Инструкция📕'])#iphone
keyboard_link_teh = create_link1('https://t.me/Avohelp', 'Поддержка🫂')



async def pay(callback: CallbackQuery, price: int, count: int):
    x = pay_yoo.pay(str(LEXICON_PRICE_RU[str(price)]), LEXICON_MENU1_PRICE_RU[str(price)])
    if x['status'] == 'pending':
        keyboard_link26 = create_link1(x['url'], 'ОПЛАТИТЬ', last1_btn='🔙 Назад')

        await callback.message.edit_text(text=LEXICON_MENU1_TEXT_RU[str(price)], reply_markup=keyboard_link26)
        payment = Payment.find_one(x['id'])
        timeout = time.time() + 60 * 10
        f = 0
        while payment.status == 'pending':
            if time.time() > timeout:
                f = 1
                break
            payment = Payment.find_one(x['id'])
            await asyncio.sleep(3)
        if payment.status == 'succeeded':
            print('OK')
            x3.test_connect()
            if str(callback.message.chat.id) in x3.activ_list():
                x3.test_connect()
                x3.updateClient(int(price), str(callback.message.chat.id), count)
                x3.test_connect()
                result_active = x3.activ(str(callback.message.chat.id))
                time1 = result_active['time']
                await callback.message.edit_text(text=LEXICON_MENU2_RU['26'].format(time1),reply_markup=keyboard_link_teh)
            else:
                x3.test_connect()
                print(x3.addClient(int(price), int(callback.message.chat.id), int(callback.message.chat.id), count).text)
                x3.test_connect()
                result_active = x3.activ(str(callback.message.chat.id))
                time1 = result_active['time']
                await callback.message.edit_text(text=LEXICON_MENU2_RU['22'].format(time1))
        elif f == 1:
            await callback.message.edit_text('Процесс оплаты был прерван по времени')
        else:
            await callback.message.edit_text('Процесс оплаты был прерван')
            print('cancel')


async def delet(msg: Message):
    try:
        await msg.delete()
    except:
        pass


class Present(StatesGroup):#не обработано
    name = State()


class sendm(StatesGroup):
    sendm = State()

    # Этот хэндлер срабатывает на команду /start


@router.message(CommandStart())
async def process_start_command(message: Message, bot: Bot):
    await message.delete()
    print(message.json(indent=4, exclude_none=True))
    file = FSInputFile('handlers/avocado.jpg')
    await message.answer_photo(file, caption=LEXICON_HI_TEXT['hi'], reply_markup=keyboard_supper, parse_mode='html')
    if sql.SELECT_REF(message.chat.id) is not None:
        if len(message.text.split(' ')) == 1:
            if sql.SELECT_ID(message.chat.id) is not None:
                await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in1)
            else:
                sql.INSERT(message.chat.id, False, False)
                await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in1)
        else:
            if sql.SELECT_ID(message.chat.id) is not None:
                await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in1)
            else:
                ref_login = message.text.split(' ')[1]
                sql.INSERT(message.chat.id, False, False, ref_login)
                await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in1)
    else:
        if len(message.text.split(' ')) == 1:
            if sql.SELECT_ID(message.chat.id) is not None:
                await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in11)
            else:
                sql.INSERT(message.chat.id, False, False)
                await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in11)
        else:
            if sql.SELECT_ID(message.chat.id) is not None:
                await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in11)
            else:
                ref_login = message.text.split(' ')[1]
                sql.INSERT(message.chat.id, False, False, ref_login)
                await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in11)


@router.message(Command(commands='help'))
async def com_help(message: Message):
    await message.answer(text=LEXICON_MENU4_RU['41'], reply_markup=keyboard_supper)


@router.message(Command(commands='on_vpn'))
async def com_help(message: Message):
    if sql.SELECT_REF(message.chat.id) is not None:
        await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in1)
    else:
        await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in11)


@router.message(Command(commands='my_vpn'))
async def comm_help(message: Message):
    x3.test_connect()
    result_active = x3.activ(str(message.chat.id))
    active = result_active['activ']
    time = result_active['time']
    try:
        count_key = result_active['key']
    except:
        count_key = '0'
    if time == '-':
        link = '----'
    elif time == '01-01-1970 03:00 МСК':
        time = '01-01-3000 03:00 МСК'
        active = 'Активен'
        link = x3.link(str(message.chat.id))
    else:
        link = x3.link(str(message.chat.id))
    if active == 'Не Активен':
        await message.answer(
            text=LEXICON_MENU2_RU['27'].format(
                'Не активна',
                time,
                link
            ), reply_markup=keyboard_in33, parse_mode="html"
        )
    else:
        await message.answer(
            text=LEXICON_MENU2_RU['21'].format(
                active,
                time,
                link,
                count_key
            ), reply_markup=keyboard_in2, parse_mode="html"
        )


@router.message(Command(commands='ref'))
async def com_help(message: Message):
    count = sql.SELECT_COUNT_REF(int(message.chat.id))
    await message.answer(text=LEXICON_MENU3_RU['31'].format(str(count), str(message.chat.id)), parse_mode="html",
                         reply_markup=keyboard_link_teh)


@router.message(Command(commands='my_id'))
async def com_help(message: Message):
    await message.answer(f'<code>{message.chat.id}</code>', parse_mode='html', reply_markup=keyboard_supper)


@router.message(Text(text='Мой ID'))
async def com_help(message: Message):
    await message.answer(f'<code>{message.chat.id}</code>', parse_mode='html', reply_markup=keyboard_supper)


@router.message(Text(text='✅ Подключить VPN / Продлить подписку'))
async def connect_vpn(message: Message):
    if sql.SELECT_REF(message.chat.id) is not None:
        await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in1)
    else:
        await message.answer(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in11)


async def day(name):
    list_result = name.split(' ')
    result = name.split(' ')[3]
    name1 = list_result[0] + ' ' + list_result[1] + ' ' + list_result[2] + ' ' + list_result[3] + ' ' + list_result[4]
    print(list_result)
    print(name1)
    PRICE = LabeledPrice(label=name1, amount=LEXICON_PRICE_RU[result])
    print(PRICE)
    return PRICE


async def day1(name):
    list_result = name.split(' ')
    name1 = list_result[0] + ' ' + list_result[1] + ' ' + list_result[2] + ' ' + list_result[3] + ' ' + list_result[4]
    return name1


@router.callback_query(Text(text=['btp','b','pp','26']))
async def pay30(callback: CallbackQuery):
    if sql.SELECT_REF(callback.message.chat.id) is not None:
        await callback.message.edit_text(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in11)
    else:
        await callback.message.edit_text(text=LEXICON_MENU1_RU['11'], reply_markup=keyboard_in1)


@router.callback_query(Text(text=['30']))
async def pay30(callback: CallbackQuery):
    await pay(callback, 30, 1)


@router.callback_query(Text(text=['90']))
async def pay30(callback: CallbackQuery):
    await pay(callback, 90, 1)


@router.callback_query(Text(text=['183']))
async def pay30(callback: CallbackQuery):
    await pay(callback, 183, 1)


@router.callback_query(Text(text=['365']))
async def pay30(callback: CallbackQuery):
    await pay(callback, 365, 1)


@router.callback_query(Text(text=['366']))
async def pay30(callback: CallbackQuery):
    await pay(callback, 366, 10)


@router.callback_query(Text(text=['5']))#рефералка
async def pay30(callback: CallbackQuery, bot: Bot):
    day = str(5)
    if sql.SELECT_ID(callback.message.chat.id) is None:
        sql.INSERT(callback.message.chat.id, False, False)
    x = sql.SELECT_ID(callback.message.chat.id)
    if x is not None:
        x3.test_connect()
        ractive = x3.activ(str(x[2]))
        if len(x) > 0 and ractive['activ'] == 'Активен':
            x3.test_connect()
            x3.updateClient(30, x[2], 1)
            await bot.send_message(int(x[2]),
                                   f'Вам добавлено 5 дней к вашей подписке за пользователя - {str(callback.message.chat.id)}')
    # все что выше нужно для реф программы, ниже - действия клиента который по ней перешел
    x3.test_connect()
    add_user = x3.addClient(int(day), str(callback.message.chat.username), int(callback.message.chat.id), 1).text
    x3.test_connect()
    result_active = x3.activ(str(callback.message.chat.id))
    time = result_active['time']
    if sql.SELECT_ID(callback.message.chat.id) is not None:
        sql.UPDATE_PAYNULL(callback.message.chat.id)
    else:
        sql.INSERT(callback.message.chat.id, True)
    await callback.message.edit_text(text=LEXICON_MENU2_RU['22'].format(time))


@router.message(Text(text='🚀 Мой VPN'))
async def vpn_con1nect(message: Message, bot: Bot):
    try:
        tmess = await message.edit_text('<b><i>Просим немного подождать, ответ формируется...</i></b>', parse_mode='html')
    except:
        tmess = await bot.send_message(message.chat.id, '<b><i>Просим немного подождать, ответ формируется...</i></b>', parse_mode='html')

    x3.test_connect()
    result_active = x3.activ(str(message.chat.id))
    active = result_active['activ']
    time = result_active['time']
    try:
        count_key = result_active['key']
    except:
        count_key = '0'
    if time == '-':
        link = '----'
    elif time == '01-01-1970 03:00 МСК':
        time = '01-01-3000 03:00 МСК'
        active = 'Активен'
        link = x3.link(str(message.chat.id))
    else:
        link = x3.link(str(message.chat.id))
    if active == 'Не Активен':
        await message.answer(
            text=LEXICON_MENU2_RU['27'].format(
                'Не активна',
                time,
                link
            ), reply_markup=keyboard_in33, parse_mode="html"
        )
    else:
        await message.answer(
            text=LEXICON_MENU2_RU['21'].format(
                active,
                time,
                link,
                count_key
            ), reply_markup=keyboard_in2, parse_mode="html"
        )
    await bot.delete_message(message_id=tmess.message_id, chat_id=tmess.chat.id)


@router.callback_query(Text(text=['22']))
async def pay30(callback: CallbackQuery):
    x3.test_connect()
    link = x3.link(str(callback.message.chat.id))
    await callback.message.edit_text(text=FoXrayx['22'].format(link), disable_web_page_preview=True, reply_markup=keyboard_link22)


@router.callback_query(Text(text=['24']))
async def pay30(callback: CallbackQuery):
    x3.test_connect()
    link = x3.link(str(callback.message.chat.id))
    await callback.message.edit_text(text=FoXrayx['24'].format(link), disable_web_page_preview=True, reply_markup=keyboard_link24)


@router.callback_query(Text(text=['25']))
async def pay30(callback: CallbackQuery):
    x3.test_connect()
    link = x3.link(str(callback.message.chat.id))
    await callback.message.edit_text(text=FoXrayx['25'].format(link), disable_web_page_preview=True, reply_markup=keyboard_link25)


@router.message(Text(text='🔥 Реферальная программа'))
async def connect_vpn(message: Message):
    count = sql.SELECT_COUNT_REF(int(message.chat.id))
    await message.answer(text=LEXICON_MENU3_RU['31'].format(str(count), str(message.chat.id)), parse_mode="html",
                         reply_markup=keyboard_link_teh)


@router.callback_query(Text(text=['31']))
async def setting_program(callback: CallbackQuery):
    count = sql.SELECT_COUNT_REF(int(callback.message.chat.id))
    await callback.message.edit_text(text=LEXICON_MENU3_RU['31'].format(str(count), str(callback.message.chat.id)),
                                     parse_mode="html", reply_markup=keyboard_link_teh)


@router.message(Text(text='❓ Информация'))
async def connect_vpn(message: Message):
    await message.answer(text=LEXICON_MENU4_RU['41'], reply_markup=keyboard_supper)


@router.message(Text(text='⚙ Техническая поддержка'))
async def connect_vpn(message: Message):
    await message.answer(f'Ваш уникальный номер, который нужно показать техподдержке -  <code>{message.chat.id}</code>', parse_mode='html', reply_markup=keyboard_link_teh)


@router.callback_query(Text(text=['back']))
async def bck(callback: CallbackQuery, bot: Bot):
    await vpn_con1nect(callback.message, bot)
    await delet(msg=callback.message)


@router.message()
async def process_successful_payment(message: Message):
    await message.answer(text='Я Вас не понимаю! Пожалуйста выберите действие из меню!', reply_markup=keyboard_supper)
    await delet(msg=message)
    time.sleep(1)

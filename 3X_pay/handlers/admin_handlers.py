from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from sendmes import text
from config_data.config import load_config
from keyboards.inline.keyboard import create_inline_kb, create_key_kb_inside
from lexicon.lexicon import LEXICON_LISTED, LEXICON_MENU_RU
from nps.nps import read, write, clear
ADMINS = load_config().tg_bot.admin_ids
router: Router = Router()
keyboard_listed = create_inline_kb(1, **LEXICON_LISTED)
keyboard_supper = create_key_kb_inside(2, **LEXICON_MENU_RU)


async def delet(msg: Message):
    try:
        await msg.delete()
    except:
        pass


class Sendmess(StatesGroup):
    mess = State()
    mkup = State()


@router.message(F.from_user.id.in_(ADMINS), Command(commands='send'), ~StateFilter(default_state))
async def run(message: Message, state: FSMContext):
    await state.clear()
    print('state clear')
    await message.answer("Отменено")


@router.message(F.from_user.id.in_(ADMINS), Command(commands='send'), StateFilter(default_state))
async def run(message: Message, state: FSMContext):
    print(f'activate send command by {message.from_user.id}')
    await state.set_state(Sendmess.mkup)
    await message.answer('Маркап 1 - listed, иначе - grade')


@router.message(F.from_user.id.in_(ADMINS), Command(commands='nps'))
async def run(message: Message):
    await message.answer(await read())


@router.message(F.from_user.id.in_(ADMINS), Command(commands='clear'))
async def run(message: Message):
    await message.answer(await clear())


@router.message(Sendmess.mkup)
async def run(message: Message, state: FSMContext, bot: Bot):
    print(message.text)
    await state.update_data(mkup=message.text)
    await state.set_state(Sendmess.mess)
    await message.answer("Текст сообщения\n\n/send")


@router.message(Sendmess.mess)
async def run(message: Message, state: FSMContext, bot: Bot):
    print(message.text)
    await state.update_data(mess=message.text)
    data = await state.get_data()
    await state.clear()
    await text(bot, data["mess"], data["mkup"])


@router.callback_query(F.data == 'listed')
async def setting_program(callback: CallbackQuery, bot: Bot):
    await delet(msg=callback.message)
    for i in ADMINS:
        await bot.send_message(i, f"<b>Пользователь @{callback.from_user.username} прочитал сообщение</b>\n<i>{callback.message.text}</i>",parse_mode='html')


@router.callback_query(F.data.startswith('g'))
async def handle_callback_query(callback: CallbackQuery, bot: Bot):
    _, value = callback.data.split('g')
    await delet(msg=callback.message)
    await bot.send_message(callback.message.chat.id, "<i><b>Благодарим за оценку!</b></i>", parse_mode='html', reply_markup=keyboard_supper)
    await write(int(value))
    for i in ADMINS:
        await bot.send_message(i, "<b>НОВАЯ ОЦЕНКА</b>\n\n"
                                       f"<i>Пользователь @{callback.from_user.username} поставил оценку <b>{value}</b></i>",parse_mode='html')
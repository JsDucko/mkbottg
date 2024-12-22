from database import db
from aiogram import types
from aiogram.dispatcher import FSMContext
from data.config import ADMIN_ID, OP_TEXT
from utils import utils
import os
from keyboards.keyboards import create_subscription_keyboard, keyboard_admin_start, keyboard_user_start
from data.loader import dp, bot, Dispatcher
from aiogram.utils.exceptions import MessageCantBeDeleted

async def delete_and_send_new_message(chat_id, message_id, text=None, photo=None, caption=None, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass

    if photo is not None:
        await bot.send_photo(chat_id, photo, caption=caption, parse_mode='html', reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'check_subscription')
async def check_subscription_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if await utils.is_user_subscribed(user_id):
        await bot.answer_callback_query(callback_query.id, text="✅ Подписка на канал подтверждена. Вы можете использовать все функции бота.")
        await cmd_handler(callback_query.message)
    else:
        await bot.answer_callback_query(callback_query.id, text="❗️ Вы не подписаны на канал. Пожалуйста, подпишитесь и проверьте подписку снова.")


@dp.message_handler(commands=['start'])
async def cmd_handler(message: types.Message):
    user_id = message.from_user.id

    await db.db_start()

    args = message.get_args()
    print(f"Args: {args}")

    user = db.cur.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if not user:
        referrer_id = None
        if args:
            try:
                referrer_id = int(args)
                if referrer_id == user_id:
                    referrer_id = None
            except ValueError:
                pass

        if referrer_id is not None:
            db.cur.execute('INSERT INTO users (id, balance, subscription_status, total_invest, earnings, broker_balance, referrer_id, total_deposit, referral_deposit) VALUES (?, 50, "Не активна", 0, 0, 0, ?, 0, 0)', (user_id, referrer_id))
            db.db.commit()

            referrer_user = await bot.get_chat(referrer_id)
            referrer_username = referrer_user.username

            subscription_status = await db.get_user_subscription_status(referrer_id)

            if "Активна" in subscription_status:
                referrer_username = f"{referrer_username} ⭐️"

            if referrer_username is None:
                referrer_username = str(referrer_id)

            await message.reply(f"🎉 Вы получили 50 Рублей на баланс от пользователя @{referrer_username}")
            print(f"Реферальная ссылка обработана: пользователь {user_id} приглашен пользователем {referrer_id}")
        else:
            db.cur.execute('INSERT INTO users (id, balance, subscription_status, total_invest, earnings, broker_balance, referrer_id, total_deposit, referral_deposit) VALUES (?, 0, "Не активна", 0, 0, 0, NULL, 0, 0)', (user_id,))
            db.db.commit()
    else:
        if args:
            await message.reply("❗️ Реферальную ссылку могут активировать только новые пользователи бота, либо вы уже активировали ссылку.")

    if not await utils.is_user_subscribed(user_id):
        subscription_keyboard = create_subscription_keyboard()
        await message.reply(f"{OP_TEXT}", reply_markup=subscription_keyboard)
        return

    photo_path = os.path.join('img', 'start.png')

    with open(photo_path, 'rb') as photo_file:
        if user_id == ADMIN_ID:
            await delete_and_send_new_message(message.chat.id, message.message_id, photo=photo_file, caption='👋🏼 <b>Добро пожаловать.</b>\n\n🔹<i>Система имеет пять различных программ инвестиций.</i>\n\n🔹<i>Процентная программа реферальной системы.</i>\n\n🔹 <i>Премиум статус для более доходного инвестирования.</i>\n\n🔸 <b>Удачных сделок.</b>', reply_markup=keyboard_admin_start)
        else:
            await delete_and_send_new_message(message.chat.id, message.message_id, photo=photo_file, caption='👋🏼 <b>Добро пожаловать.</b>\n\n🔹<i>Система имеет пять различных программ инвестиций.</i>\n\n🔹<i>Процентная программа реферальной системы.</i>\n\n🔹 <i>Премиум статус для более доходного инвестирования.</i>\n\n🔸 <b>Удачных сделок.</b>', reply_markup=keyboard_user_start)
            
                     
@dp.callback_query_handler(lambda callback_query: callback_query.data in ['back_profile', 'back', 'back_zero', 'exit_adm', 'back_sposob_withdraw', 'back_sposob', 'exit_plus', 'back_to_menu', 'back_typeCrypto', 'back_payments', 'exit_info', 'exit_withdraw', 'back_rev', 'back_calculator_finish', 'back_calculator', 'cancel_go', 'cancel_sub', 'cancel_sub_srok', 'back_to_main_menu_inv', 'back_invest_deposit'], state="*")
async def back_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    await state.finish()

    photo_path = os.path.join('img', 'start.png')
    if callback_query.from_user.id == ADMIN_ID:
        with open(photo_path, 'rb') as photo_file:
            await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption='👋🏼 <b>Добро пожаловать.</b>\n\n🔹<i>Система имеет пять различных программ инвестиций.</i>\n\n🔹<i>Процентная программа реферальной системы.</i>\n\n🔹 <i>Премиум статус для более доходного инвестирования.</i>\n\n🔸 <b>Удачных сделок.</b>', reply_markup=keyboard_admin_start)
    else:
        with open(photo_path, 'rb') as photo_file:
            await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption='👋🏼 <b>Добро пожаловать.</b>\n\n🔹<i>Система имеет пять различных программ инвестиций.</i>\n\n🔹<i>Процентная программа реферальной системы.</i>\n\n🔹 <i>Премиум статус для более доходного инвестирования.</i>\n\n🔸 <b>Удачных сделок.</b>', reply_markup=keyboard_user_start)
         
         
         
def register_handlers_main_menu(dp: Dispatcher):
    dp.register_message_handler(cmd_handler, commands=['start'], state="*")
    dp.register_callback_query_handler(check_subscription_callback, lambda callback_query: callback_query.data == 'check_subscription', state="*")
    dp.register_callback_query_handler(check_subscription_callback, lambda callback_query: callback_query.data in ['back_profile', 'back', 'back_zero', 'exit_adm', 'back_sposob_withdraw', 'back_sposob', 'exit_plus', 'back_to_menu', 'back_typeCrypto', 'back_payments', 'exit_info', 'exit_withdraw', 'back_rev', 'back_calculator_finish', 'back_calculator', 'cancel_go', 'cancel_sub', 'cancel_sub_srok', 'back_to_main_menu_inv'], state="*")
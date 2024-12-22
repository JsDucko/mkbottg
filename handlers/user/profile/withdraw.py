from data.loader import dp, bot, Dispatcher
from database import db
from aiogram import types
from data.config import CHANNEL_ID
from states import states_group
from aiogram.dispatcher import FSMContext
from keyboards.keyboards import keyboard_one_can, keyboard_sposob_withdraw, keyboard_sucs_withdraw
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from aiogram.utils.exceptions import MessageCantBeDeleted


async def delete_and_send_new_message(chat_id, message_id, text=None, photo=None, caption=None, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass

    if photo is not None:
        await bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)
        

@dp.message_handler(lambda message: not message.text.isdigit(), state=states_group.Form.waiting_for_withdraw)
async def process_invalid_amount(message: types.Message):
    await delete_and_send_new_message(chat_id=message.chat.id, message_id=message.message_id, text="❗️ Введите сумму вывода, используя только цифры.\n\n👇🏼 Введите корректную сумму ещё раз.", reply_markup=keyboard_one_can)
    return


@dp.callback_query_handler(lambda callback_query: callback_query.data in ['withdraw_profile'])
async def withdraw_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    photo_path = os.path.join('img', 'withdraw.png')
    user_id = callback_query.from_user.id
    balance = await db.get_user_balance(user_id=user_id)
    if balance < 100:
        with open(photo_path, 'rb') as photo_file:
            await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption=f'❌ На вашем балансе недостаточно средств.\n\n❗️ Ваш баланс должен быть более 100 Рублей', reply_markup=keyboard_one_can) 
    else:
        with open(photo_path, 'rb') as photo_file:
            await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption=f'💸 Выберите способ вывода:', reply_markup=keyboard_sposob_withdraw) 
  
    
@dp.callback_query_handler(lambda callback_query: callback_query.data in ['qiwi_withdraw', 'card_withdraw', 'crypto_withdraw'])
async def withdraw_choose_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, text="💵 Введите сумму вывода:")
    await states_group.Form.waiting_for_withdraw.set()


@dp.message_handler(lambda message: message.text.isdigit(), state=states_group.Form.waiting_for_withdraw)
async def process_withdraw_balance(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    amount = int(message.text)
    balance = await db.get_user_balance(user_id=user_id)

    if amount < 100:
        await delete_and_send_new_message(chat_id=message.chat.id, message_id=message.message_id, text="❗️ Минимальная сумма вывода составляет 100 Рублей.\n\n👇🏼 Введите корректную сумму ещё раз.", reply_markup=keyboard_one_can)
        return
    elif balance < amount:
        await delete_and_send_new_message(chat_id=message.chat.id, message_id=message.message_id, text=f"❌ На вашем балансе недостаточно средств.\n\n💵 Ваш баланс: {balance}₽\n\n👇🏼 Введите корректную сумму ещё раз.", reply_markup=keyboard_one_can)
        return
    else:
        await states_group.Form.next()
        await state.update_data(amount=amount)
        await delete_and_send_new_message(chat_id=message.chat.id, message_id=message.message_id, text="👇🏼 Введите ваши реквизиты для вывода\n\n❗️ Если вы используете криптовалюту, пожалуйста указывайте сеть токена.", reply_markup=keyboard_one_can)
        await states_group.Form.waiting_for_requisites.set()


@dp.message_handler(lambda message: not message.text.isdigit(), state=states_group.Form.waiting_for_requisites)
async def process_requisites(message: types.Message, state: FSMContext):
    requisites = message.text
    await state.update_data(requisites=requisites)

    user_data = await state.get_data()
    amount = user_data["amount"]

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("✅ Проверил", callback_data="checked"))
    markup.row(InlineKeyboardButton("✏️ Редактировать", callback_data="edit"))
    markup.row(InlineKeyboardButton("◀️ Назад", callback_data="back"))

    await delete_and_send_new_message(chat_id=message.chat.id, message_id=message.message_id, text=f"❗️ Проверьте ваши реквизиты!\n\nЕсли вы уверены, что указали правильно - нажмите \"✅ Проверил\"\n\n📎 Ваши реквизиты: {requisites}", reply_markup=markup)
    await states_group.Form.waiting_for_confirmation.set()
    
@dp.callback_query_handler(lambda callback_query: callback_query.data in ["checked", "edit", "back"], state=states_group.Form.waiting_for_confirmation)
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    if callback_query.data == "edit":
        await delete_and_send_new_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="👇🏼 Введите ваши реквизиты для вывода ещё раз:")
        await states_group.Form.waiting_for_requisites.set()
    elif callback_query.data == "back":
        await delete_and_send_new_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="Возвращаемся назад...")
    elif callback_query.data == "checked":
        user_data = await state.get_data()
        amount = user_data["amount"]
        requisites = user_data["requisites"]
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username
        await db.update_user_balance1(user_id, amount, "subtract")
        await delete_and_send_new_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=f"✅ Подана заявка на вывод {amount}₽\n\nОна будет обработна в течении 24 часов, вы получите уведомление.", reply_markup=keyboard_one_can)

        chat_id = CHANNEL_ID
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("✅", callback_data=f"approve_{user_id}_{amount}"), InlineKeyboardButton("❌", callback_data=f"decline_{user_id}_{amount}"))

        await bot.send_message(chat_id=chat_id, text=f"🔔 Пользователь @{username} подал заявку на вывод {amount}₽\n\n💳 Реквизиты: {requisites}", reply_markup=markup)

        await state.finish()
        

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("approve_") or callback_query.data.startswith("decline_"))
async def process_admin_response(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    action, user_id, amount = callback_query.data.split("_")
    user_id = int(user_id)
    amount = int(amount)

    if action == "approve":
        await bot.send_message(chat_id=user_id, text=f"🔔 <b>Заявка успешно обработана!</b>\n\n<i>💸 Ожидайте прихода средств {amount}₽ в течении 24 часов.</i>\n\n ✅ <b>Благодарим за доверие</b>",  parse_mode='html', reply_markup=keyboard_sucs_withdraw)
    elif action == "decline":
        await db.update_user_balance1(user_id, amount, 'add')
        await bot.send_message(chat_id=user_id, text=f"🔔 <b>Заявка успешно обработана!</b>\n\n<i>❌ Мы отклонили вывод средств {amount}₽.</i>\n\n<b>Деньги были возвращены на баланс.</b>\n\n❗<b>️ Чтобы узнать причину отмены вывода, вы можете обратится в тех.поддержку.</b>",  parse_mode='html', reply_markup=keyboard_one_can)
        
        
def register_handlers_withdraw(dp: Dispatcher):
    dp.register_message_handler(process_invalid_amount, lambda message: not message.text.isdigit(), state=states_group.Form.waiting_for_withdraw)
    dp.register_message_handler(process_withdraw_balance, lambda message: message.text.isdigit(), state=states_group.Form.waiting_for_withdraw)
    dp.register_message_handler(process_requisites, lambda message: not message.text.isdigit(), state=states_group.Form.waiting_for_requisites)
    dp.register_callback_query_handler(withdraw_handler, lambda callback_query: callback_query.data in ['withdraw_profile'], state="*")
    dp.register_callback_query_handler(withdraw_choose_handler, lambda callback_query: callback_query.data in ['qiwi_withdraw', 'card_withdraw', 'crypto_withdraw'], state="*")
    dp.register_callback_query_handler(process_confirmation, lambda callback_query: callback_query.data in ["checked", "edit", "back"], state=states_group.Form.waiting_for_confirmation)
    dp.register_callback_query_handler(process_admin_response, lambda callback_query: callback_query.data.startswith("approve_") or callback_query.data.startswith("decline_"), state="*")


from data.loader import dp, bot, Dispatcher
from aiogram import types
from keyboards.keyboards import keyboard_calculator_deposit, keyboard_one_can, create_result_keyboard
import os
from states import states_group
from aiogram.dispatcher import FSMContext
from typing import Tuple
from handlers.user.main_menu import cmd_handler
from handlers.user.profile.invest_1day_sub import balance_handler
from aiogram.utils.exceptions import MessageCantBeDeleted

async def delete_and_send_new_message(chat_id, message_id, text=None, photo=None, caption=None, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass

    if photo is not None:
        return await bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup)
    else:
        return await bot.send_message(chat_id, text, reply_markup=reply_markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data in ['calculator_admin', 'calculator_user', 'calculator_profile'])
async def calculator_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    photo_path = os.path.join('img', 'profile.png')
    with open(photo_path, 'rb') as photo_file:
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption=f'⏳ Выберите срок депозита:', reply_markup=keyboard_calculator_deposit)
        
        
def calculate_profit(deposit_term: str, deposit_amount: float) -> Tuple[float, float]:
    interest_rates = {
        '24h': 1.2,
        '7d': 1.54,
        '14d': 1.91,
        '28d': 2.74
    }
    interest_rate = interest_rates[deposit_term]
    days_mapping = {
        '24h': 1,
        '7d': 7,
        '14d': 14,
        '28d': 28
    }
    days = days_mapping[deposit_term]
    profit = deposit_amount * interest_rate * days / 100
    total_amount = deposit_amount + profit
    return profit, total_amount

@dp.callback_query_handler(lambda callback_query: callback_query.data in ['24h', '7d', '14d', '28d'])
async def calculator_handler_days(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(deposit_term=callback_query.data)
    await bot.send_message(chat_id=callback_query.message.chat.id, text="💵 Введите сумму инвестиции:", reply_markup=keyboard_one_can)
    await states_group.Form.waiting_for_balance_calculator.set()
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    

@dp.message_handler(lambda message: message.text.replace('.', '', 1).isdigit(), state=states_group.Form.waiting_for_balance_calculator)
async def process_balance_calculator(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    deposit_term = user_data['deposit_term']
    deposit_amount = float(message.text)

    if deposit_amount < 100:
        await message.reply("❗️ Минимальная сумма инвестиции составляет 100 Рублей.\n\n👇🏼 Введите корректную сумму ещё раз.", reply_markup=keyboard_one_can)
        return

    profit, total_amount = calculate_profit(deposit_term, deposit_amount)
    result_keyboard = create_result_keyboard()

    message_id_to_delete = message.message_id - 1

    await bot.delete_message(chat_id=message.chat.id, message_id=message_id_to_delete)

    await message.delete()
    await bot.send_message(chat_id=message.chat.id, text=f"📍 Персональная информация по депозиту {deposit_amount}₽ на срок {deposit_term}:\n\n📈 Начисленная прибыль: {profit:.2f}₽\n💸 Сумма после окончания депозита: {total_amount:.2f}₽", reply_markup=result_keyboard)
    
@dp.message_handler(lambda message: not message.text.replace('.', '', 1).isdigit(), state=states_group.Form.waiting_for_balance_calculator)
async def process_invalid_input(message: types.Message):
    await message.reply("❗️ Введите корректную сумму инвестиции (только числа).", reply_markup=keyboard_one_can)
    
    
@dp.callback_query_handler(lambda callback_query: callback_query.data in ["retry_sum", "retry_term", "go_back", "go_inv"])
async def retry_or_exit(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.data == "retry_sum":
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.send_message(chat_id=callback_query.message.chat.id, text="💵 Введите сумму инвестиции:", reply_markup=keyboard_one_can)
        await states_group.Form.waiting_for_balance_calculator.set()
    elif callback_query.data == "retry_term":
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.send_message(chat_id=callback_query.message.chat.id, text="⏳ Выберите срок депозита:", reply_markup=keyboard_calculator_deposit)
    elif callback_query.data == "go_inv":
        await state.finish()
        await balance_handler(callback_query.message)
        await bot.answer_callback_query(callback_query.id)
        
    elif callback_query.data == "go_back":
        await state.finish()
        await cmd_handler(callback_query.message)
        await bot.answer_callback_query(callback_query.id)
        


def register_handlers_calculator(dp: Dispatcher):
    dp.callback_query_handler(calculator_handler, lambda callback_query: callback_query.data in ['calculator_admin', 'calculator_user', 'calculator_profile'], state="*")
    dp.register_callback_query_handler(calculator_handler_days, lambda callback_query: callback_query.data in ['24h', '7d', '14d', '28d'], state="*")
    dp.register_message_handler(process_balance_calculator, lambda message: message.text.replace('.', '', 1).isdigit(), state=states_group.Form.waiting_for_balance_calculator)
    dp.register_message_handler(process_invalid_input, lambda message: not message.text.replace('.', '', 1).isdigit(), state=states_group.Form.waiting_for_balance_calculator)
    dp.register_callback_query_handler(retry_or_exit, lambda callback_query: callback_query.data in ["retry_sum", "retry_term", "go_back"], state="*")
    
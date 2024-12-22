from data.loader import dp, bot, Dispatcher
from database import db
from states import states_group
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.keyboards import keyboard_zero_balance, keyboard_one_can, create_inline_keyboard, keyboard_invest_deposit, keyboard_invest_go
from handlers.user.main_menu import cmd_handler
from aiogram.utils.exceptions import MessageCantBeDeleted
from datetime import datetime, timedelta
import pytz


tz = pytz.timezone('Europe/Moscow')

def now():
    return datetime.now(tz)


async def delete_and_send_new_message(chat_id, message_id, text=None, photo=None, caption=None, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass

    if photo is not None:
        await bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)

async def is_n_hours_passed(investment_date, n_hours):
    now = datetime.now()
    investment_date = datetime.strptime(investment_date, "%Y-%m-%d %H:%M:%S")
    diff = now - investment_date
    return diff < timedelta(hours=n_hours)
    
def time_left(end_date: str):
    end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    delta = end_date - now

    days_left = delta.days
    hours_left = delta.seconds // 3600

    if days_left < 1:
        return f"{hours_left} часа" if hours_left > 1 else f"{hours_left} час"
    else:
        return f"{days_left} дней" if days_left > 1 else f"{days_left} день"
    
    
def days_to_readable(days: int) -> str:
    years = days // 365
    remaining_days = days % 365
    months = remaining_days // 30
    remaining_days %= 30

    parts = []
    if years > 0:
        if 10 <= years % 100 <= 20:
            years_ending = "лет"
        else:
            years_ending = {1: "год", 2: "года", 3: "года", 4: "года"}.get(years % 10, "лет")
        parts.append(f"{years} {years_ending}")

    if months > 0:
        if 10 <= months % 100 <= 20:
            months_ending = "месяцев"
        else:
            months_ending = {1: "месяц", 2: "месяца", 3: "месяца", 4: "месяца"}.get(months % 10, "месяцев")
        parts.append(f"{months} {months_ending}")

    if remaining_days > 0:
        if 10 <= remaining_days % 100 <= 20:
            days_ending = "дней"
        else:
            days_ending = {1: "день", 2: "дня", 3: "дня", 4: "дня"}.get(remaining_days % 10, "дней")
        parts.append(f"{remaining_days} {days_ending}")

    return ', '.join(parts)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'myinvest_profile')
async def my_investments_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    investments = await db.get_term_investments(user_id)

    if not investments:
        await delete_and_send_new_message(user_id, message_id, text="❗️ Активных инвестиций нет.", reply_markup=keyboard_one_can)
    else:
        text = "👇🏼 Ваши инвестиции:"
        buttons = []
        for investment in investments:
            investment_id = investment[0]
            investment_amount = investment[2]
            investment_term = int(investment[3])
            investment_term_readable = days_to_readable(investment_term)
            end_date = investment[7]
            time_remaining = time_left(end_date)

            button_text = f"💸 {investment_amount}₽ | ⏳ {investment_term_readable} | Осталось {time_remaining}"
            buttons.append(types.InlineKeyboardButton(button_text, callback_data=f"investment_details:{investment_id}"))

        buttons.append(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main_menu_inv"))

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        await delete_and_send_new_message(user_id, message_id, text=text, reply_markup=keyboard)

@dp.callback_query_handler(lambda callback_query: 'investment_details' in callback_query.data)
async def investment_details_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    investment_id = int(callback_query.data.split(':')[1])

    db.cur.execute("SELECT * FROM investments WHERE id=?", (investment_id,))
    investment = db.cur.fetchone()

    investment_amount = investment[2]
    investment_term = int(investment[3]) 
    investment_term_readable = days_to_readable(investment_term)
    interest_rate = float(investment[5])
    end_date = investment[7]
    time_remaining = time_left(end_date)
    calculate_pribile = round(investment_amount * interest_rate * investment_term, 2)
    calculate_zarabotok = round((investment_amount * interest_rate * investment_term) + investment_amount, 2)

    text = f"💎 Ваша инвестиция:\n\n💸 Сумма инвестирования: {investment_amount}₽\n⏳ Срок инвестирования: {investment_term_readable}\nДо окончания срока: {time_remaining}\n\n📈 Прибыль: {calculate_pribile}₽\n💸 Заработок к концу срока: {calculate_zarabotok}₽"
    keyboard = types.InlineKeyboardMarkup()
    #keyboard.add(types.InlineKeyboardButton("🟢 Дополнить", callback_data=f"add_funds1:{investment_id}"))
    keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="myinvest_profile"))

    await delete_and_send_new_message(user_id, message_id, text=text, reply_markup=keyboard)

@dp.callback_query_handler(lambda callback_query: 'add_funds1' in callback_query.data)
async def add_funds_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    investment_id = int(callback_query.data.split(':')[1])

    db.cur.execute("SELECT * FROM investments WHERE id=?", (investment_id,))
    investment = db.cur.fetchone()
    investment_date = investment[6]

    if await is_n_hours_passed(investment_date, 12):
        await bot.send_message(user_id, "✏️ Введите сумму дополнения:")
        await states_group.Form.waiting_for_add_funds.set()
    else:
        await bot.send_message(user_id, "❗️ Вы можете добавить средства только в течение первых 12 часов с момента инвестиции.")

@dp.message_handler(lambda message: message.text.isdigit() and int(message.text) > 0, state=states_group.Form.waiting_for_add_funds)
async def add_funds_amount_handler11(message: types.Message):
    user_id = message.from_user.id
    add_funds_amount = int(message.text)

    user_balance = await db.get_user_balance(user_id)
    enough_balance = user_balance >= add_funds_amount

    if not enough_balance:
        await bot.send_message(user_id, "❗️ Недостаточно средств на балансе.")
    else:
        text = f"🟢 Вы хотите добавить {add_funds_amount}₽ к вашей инвестиции? Это сумма будет списана с вашего баланса."
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("✅ Да", callback_data=f"confirm_add_funds:{add_funds_amount}"))
        keyboard.add(types.InlineKeyboardButton("❌ Нет", callback_data="cancel_add_funds"))

        await bot.send_message(user_id, text, reply_markup=keyboard)

@dp.callback_query_handler(lambda callback_query: 'confirm_add_funds' in callback_query.data)
async def confirm_add_funds_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    add_funds_amount = int(callback_query.data.split(':')[1])

    investment = await db.get_investment_by_user_id(user_id)
    new_investment_amount = investment[2] + add_funds_amount
    await db.update_investment_amount(investment[0], new_investment_amount)

    user_balance = await db.get_user_balance(user_id)
    new_balance = user_balance - add_funds_amount
    await db.update_user_balance(user_id, new_balance)

    await bot.send_message(user_id, "✅ Ваша инвестиция успешно дополнена!")









def register_handlers_my_invest(dp: Dispatcher):
    dp.register_callback_query_handler(my_investments_handler, lambda callback_query: callback_query.data == 'myinvest_profile', state="*")
    dp.register_callback_query_handler(investment_details_handler, lambda callback_query: 'investment_details' in callback_query.data, state="*")
    dp.register_callback_query_handler(add_funds_handler, lambda callback_query: 'add_funds' in callback_query.data, state="*")
    dp.register_message_handler(add_funds_amount_handler11, lambda message: message.text.isdigit() and int(message.text) > 0, state=states_group.Form.waiting_for_add_funds)
    dp.register_callback_query_handler(confirm_add_funds_handler, lambda callback_query: callback_query.data.isdigit() and int(callback_query.data) > 0, state="*")
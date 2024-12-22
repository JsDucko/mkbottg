from data.loader import dp, bot, Dispatcher
from database import db
from states import states_group
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.keyboards import keyboard_zero_balance, keyboard_one_can, create_inline_keyboard, keyboard_invest_deposit, keyboard_invest_go
import asyncio
from datetime import datetime as dt
from datetime import timedelta
from handlers.user.main_menu import cmd_handler
from aiogram.utils.exceptions import MessageCantBeDeleted


async def delete_and_send_new_message(chat_id, message_id, text, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass
    await bot.send_message(chat_id, text, reply_markup=reply_markup)

    
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'invest', state= '*')
async def balance_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user_balance = await db.get_user_balance(user_id)

    if user_balance == 0:
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, '❗️ Ваш баланс равен 0₽, вы не можете начать инвестировать. Пополните баланс.', reply_markup=keyboard_zero_balance)
    else:
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, f'👉🏼 Выберите срок инвестирования:', reply_markup=keyboard_invest_deposit)
        

investment_terms = {
    '24h_invest_deposit': {'duration': '24 часа', 'days': 1, 'rate': 0.012},
    '7d_invest_deposit': {'duration': '7 дней', 'days': 7, 'rate': 0.0154},
    '14d_invest_deposit': {'duration': '14 дней', 'days': 14, 'rate': 0.0191},
    '28d_invest_deposit': {'duration': '28 дней', 'days': 28, 'rate': 0.0274},
    'evryday_invest_deposit': {'duration': None, 'days': 10000, 'rate': 0.015}
}

@dp.callback_query_handler(lambda callback_query: callback_query.data in investment_terms)
async def investment_term_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    term_data = investment_terms[callback_query.data]

    subscription_status = await db.get_user_subscription_status(user_id)
    if callback_query.data == 'evryday_invest_deposit' and not subscription_status.startswith("Активна"):
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, "❌ Данный тип инвестиции доступен только с подпиской.", reply_markup=keyboard_one_can)
    else:
        state = dp.current_state(user=callback_query.from_user.id)
        term_investments = await db.get_user_term_investments(user_id)
        if term_investments and callback_query.data != 'evryday_invest_deposit':
            await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, "❌ У вас уже есть активные срочные инвестиции. Вам разрешено инвестировать только в инвестиции с ежедневным начислением.", reply_markup=keyboard_one_can)
            return
        await state.update_data(duration=term_data['duration'], investment_term=term_data['days'], interest_rate=term_data['rate'])

        if callback_query.data == 'evryday_invest_deposit':
            investment_type = 'daily'
        else:
            investment_type = 'term'

        await state.update_data(investment_type=investment_type)

        await state.set_state('enter_investment_amount')
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, '💰 Введите сумму, которую вы хотите инвестировать:', reply_markup=keyboard_one_can)
    
    
@dp.message_handler(lambda message: message.text.isdigit(), state='enter_investment_amount')
async def investment_amount_handler(message: types.Message):
    user_id = message.from_user.id
    investment_amount = int(message.text)

    if investment_amount < 100:
        await delete_and_send_new_message(user_id, message.message_id, '❗️ Минимальная сумма инвестиции составляет 100 Рублей. Пожалуйста, попробуйте ещё раз.', reply_markup=keyboard_one_can)
        return

    user_balance = await db.get_user_balance(user_id)
    if investment_amount > user_balance:
        await delete_and_send_new_message(user_id, message.message_id, f'❗️ Недостаточно средств на балансе. Ваш баланс: {user_balance}₽.', reply_markup=keyboard_one_can)
        return

    state = dp.current_state(user=user_id)
    data = await state.get_data()

    duration = data.get('duration')
    interest_rate = data.get('interest_rate')
    investment_term = data.get('investment_term')
    investment_type = data.get('investment_type') 
    investment_start_date = dt.now()
    investment_end_date = (investment_start_date + timedelta(days=investment_term)).strftime('%Y-%m-%d %H:%M:%S')
    
    total_investment = investment_amount * (1 + interest_rate * investment_term)

    await state.update_data(investment_amount=investment_amount, investment_type=investment_type, investment_start_date=investment_start_date, investment_end_date=investment_end_date)
    await state.set_state('confirm_investment')
    if investment_type == 'daily':
        daily_earning = round(investment_amount * interest_rate, 2)
        confirm_text = f"👉 Вы собираетесь инвестировать {investment_amount}₽ с ежедневным начислением прибыли. Ваш ежедневный заработок составит {daily_earning:.2f}₽. Подтвердите инвестицию."
    else:
        confirm_text = f"👉 Вы собираетесь инвестировать {investment_amount}₽ на срок {duration or investment_term}. Ваш заработок к концу срока составит {total_investment:.2f}₽. Подтвердите инвестицию."

    await state.set_state('confirm_investment')
    await delete_and_send_new_message(message.chat.id, message.message_id, confirm_text, reply_markup=create_inline_keyboard())
    
    
@dp.callback_query_handler(lambda c: c.data in ['confirm_invest', 'go_back'], state='confirm_investment')
async def confirm_investment_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = await state.get_data()

    investment_amount = data.get('investment_amount')
    interest_rate = data.get('interest_rate')
    investment_term = data.get('investment_term')
    duration = data.get('duration')
    investment_type = data.get('investment_type')
    
    if callback_query.data == 'confirm_invest':
        daily_income = investment_amount * interest_rate
        if investment_type == 'daily':
            await delete_and_send_new_message(user_id, callback_query.message.message_id, f'🎉 Поздравляем! Вы успешно инвестировали {investment_amount}₽ с ежедневными начислениями. Ваша ежедневная прибыль составит {daily_income:.2f}₽.', reply_markup=keyboard_one_can)
        else:
            total_investment = investment_amount * (1 + interest_rate * investment_term)
            await delete_and_send_new_message(user_id, callback_query.message.message_id, f'🎉 Поздравляем! Вы успешно инвестировали {investment_amount}₽ на срок {duration}. Ваш заработок к концу срока составит {total_investment:.2f}₽.', reply_markup=keyboard_one_can)

        user_balance = await db.get_user_balance(user_id)
        broker_balance = await db.get_broker_balance(user_id)
        total_invest = await db.get_user_total_invest(user_id)
        earnings = await db.get_user_earnings(user_id)

        new_user_balance = user_balance - investment_amount
        if investment_type == 'term':
            new_broker_balance = broker_balance + investment_amount
        else:
            new_broker_balance = broker_balance
        new_total_invest = total_invest + investment_amount

        if investment_type == 'daily':
            new_earnings = earnings + (investment_amount * interest_rate)
        else:
            new_earnings = earnings 

        await db.update_user_balance(user_id, new_user_balance)
        await db.update_broker_balance(user_id, new_broker_balance)
        await db.update_total_invest(user_id, new_total_invest)
        await db.update_earnings(user_id, new_earnings)

        investment_start_date = dt.now().replace(second=0, microsecond=0)
        investment_end_date = (investment_start_date + timedelta(days=investment_term)).strftime('%Y-%m-%d %H:%M:%S')
        daily_income = investment_amount * interest_rate
        await db.add_investment(user_id, investment_amount, investment_term, daily_income, interest_rate, investment_start_date, investment_end_date, investment_type)
        
        await state.finish()
        await bot.answer_callback_query(callback_query.id)

    elif callback_query.data == 'go_back':
        await state.finish()
        await cmd_handler(callback_query.message)
        await bot.answer_callback_query(callback_query.id)

    await state.finish()
    await bot.answer_callback_query(callback_query.id)
    
    
    

async def process_investments():
    all_investments = await db.get_active_investments(6122881267)
    print(f"All investments: {all_investments}")
    while True:
        print("Processing investments...")
        users = await db.get_all_users()
        for user in users:
            user_id = user[0]
            subscription_status = user[3]
            balance = user[2]

            active_investments = await db.get_active_investments(user_id)

            for investment in active_investments:
                investment_id = investment[0]
                investment_type = investment[8]
                interest_rate = investment[5]
                daily_income = investment[4]
                end_date = investment[7]
                print(f"End date: {end_date}")
                print(f"Current date: {dt.now().date()}")
                start_date = investment[6]
                remaining_days = (dt.strptime(end_date, '%Y-%m-%d %H:%M:%S').date() - dt.now().date()).days
                investment_amount = investment[2]
                investment_term = int(investment[3])

                if investment_type == 'daily':
                    if subscription_status.startswith('Активна'):
                        new_balance = round(balance + daily_income, 2)
                        await db.update_user_balance(user_id, new_balance)
                        await bot.send_message(user_id, f'💸 Девиденды в размере {daily_income:.2f}₽ зачислены на баланс.', reply_markup=keyboard_one_can)
                    else:
                        print('Подписка не найдена')
                        await bot.send_message(user_id, '❗️ Начисление девидендов для ежедневных инвестиций временно остановлено. Пожалуйста, продлите подписку, чтобы продолжить начисление.', reply_markup=keyboard_one_can)

                elif investment_type == 'term':
                    print(f"Processing term investment for user {user_id}")
                    start_date_date = dt.strptime(start_date, '%Y-%m-%d %H:%M:%S').date()
                    days_passed = (dt.now().date() - start_date_date).days

                    print(f"Current date: {dt.now().date()} for user {user_id}")
                    print(f"End date: {end_date} for user {user_id}")
                    print(f"Remaining days: {remaining_days} for user {user_id}")
                    print(f"Investment term: {investment_term} for user {user_id}")

                    if remaining_days <= 0:
                        print(f"Remaining days == 0 for user {user_id}")
                        total_investment = round(investment_amount * (1 + interest_rate * investment_term), 2)
                        new_balance = round(balance + total_investment, 2)
                        await db.update_user_balance(user_id, new_balance)
                        await db.delete_investment(investment_id)
                        await db.update_broker_balance(user_id, 0)
                        await bot.send_message(user_id, f'✅ Начислено {total_investment:.2f}₽ на баланс за инвестицию. Теперь вы можете снова инвестировать срочным типом.', reply_markup=keyboard_invest_go)
                    elif remaining_days > 0 and investment_term > 1:
                        if days_passed % 1 == 0:
                            daily_dividends = round(investment_amount *interest_rate, 2)
                            await bot.send_message(user_id, f'💸 Пришли девиденды в размере {daily_dividends:.2f}₽.', reply_markup=keyboard_one_can)

        await asyncio.sleep(86410)
    
    
    

def register_handlers_invest_1day_sub(dp: Dispatcher):
    dp.register_callback_query_handler(balance_handler, lambda callback_query: callback_query.data == 'invest', state="*")
    dp.register_callback_query_handler(investment_term_handler, lambda callback_query: callback_query.data in investment_terms, state="*")
    dp.register_callback_query_handler(investment_amount_handler, lambda message: message.text.isdigit(), state='enter_investment_amount')
    dp.register_callback_query_handler(confirm_investment_callback_handler, lambda c: c.data in ['confirm_invest', 'go_back'], state='confirm_investment')

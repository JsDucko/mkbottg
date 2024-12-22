from data.loader import dp, bot, Dispatcher
from database import db
from aiogram import types
from data.config import ADMIN_ID
from states import states_group
from aiogram.dispatcher import FSMContext
from keyboards.keyboards import types_crypto, keyboard_one_can, crypto_kb
from data import aiocryptopay
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


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'crypto')
async def balance_crypto_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_and_send_new_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=f'💵 Введите сумму пополнения:')
    await states_group.Form.waiting_for_balance.set()


@dp.message_handler(lambda message: message.text.isdigit(), state=states_group.Form.waiting_for_balance)
async def process_crypto_balance(message: types.Message, state: FSMContext):
    amount = int(message.text)

    if amount < 100:
        await delete_and_send_new_message(chat_id=message.chat.id, message_id=message.message_id, text="❗️ Минимальная сумма пополнения составляет 100 Рублей.\n\nВведите корректную сумму ещё раз.")
        return

    await state.update_data(amount=amount, message_id=message.message_id)

    await crypto_pay(message, state)
    
    
# Оплата крипто
async def crypto_pay(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get('amount')
    message_id = data.get('message_id')

    await state.update_data(amount=amount)

    await states_group.Form.amount.set()

    await delete_and_send_new_message(chat_id=message.chat.id, message_id=message_id, text='🪙 валюту для пополнения:', reply_markup=types_crypto())


# Выбор криптовалюты для крипто
@dp.callback_query_handler(lambda call: call.data.startswith("type_"), state="*")
async def type_crypto(call: types.CallbackQuery, state: FSMContext):
    #print("type_crypto вызвана")
    await bot.answer_callback_query(call.id)
    #print("type_crypto после answer_callback_query")
    crypto = call.data.split('_')[1]

    # Извлечение суммы пополнения из FSMContext
    data = await state.get_data()
    amount = data.get('amount')

    #print(f"Создание счета для криптовалюты: {crypto}, сумма: {amount}")

    bill = aiocryptopay.CryptoBot().create_bill(crypto, amount)

    #print(f"Создан счет: {bill}")

    invoice_id, pay_url = bill
    payment_markup = crypto_kb(pay_url, invoice_id)
    await delete_and_send_new_message(chat_id=call.from_user.id, message_id=call.message.message_id, text='🧾 Выставлен новый счет\n\n❗️  Оплатите его в течении 30 минут.', reply_markup=crypto_kb(pay_url, invoice_id))


# Проверка оплаты
@dp.callback_query_handler(text_startswith='check', state=states_group.Form.amount)
async def check_payment(call: types.CallbackQuery, state: FSMContext):
    payment_method = call.data.split('|')[1]
    id = call.data.split('|')[2]
    user_id = call.from_user.id
    data = await state.get_data()
    amount = data.get('amount')

    match payment_method:
        case 'crypto':
            payed = aiocryptopay.CryptoBot().get_bill_status(id)

            match payed:
                case 'paid':
                    current_balance = await db.get_user_balance(user_id)
                    new_balance = current_balance + amount
                    await db.update_user_balance(user_id, new_balance)
                    referrer_id = await db.get_referrer(user_id)
                    if amount >= 120:
                        if referrer_id is not None:
                            # Проверка статуса подписки реферера
                            subscription_status = await db.get_user_subscription_status(referrer_id)

                            if subscription_status.startswith("Активна"):
                                referrer_bonus = round(amount * 0.15)
                            else:
                                referrer_bonus = round(amount * 0.1)

                            current_referrer_balance = await db.get_user_balance(referrer_id)
                            new_referrer_balance = current_referrer_balance + referrer_bonus
                            await db.update_user_balance(referrer_id, new_referrer_balance)
                            await db.update_referral_deposit(referrer_id, amount)
                    else: 
                        print('Сумма пополнения менее 120 Рублей')
                    await db.update_user_total_deposit(user_id, amount)
                    await delete_and_send_new_message(chat_id=user_id, message_id=call.message.message_id, text=f"✅ Оплата прошла. Зачислено {amount}₽ на баланс.", reply_markup=keyboard_one_can)
                    await state.finish()

                    await bot.send_message(chat_id=ADMIN_ID, text=f"💸 Пользователь @{call.from_user.username} пополнил {amount}₽ через CRYPTO.")
                    
                case 'expired':
                    await bot.edit_message_text('❗️ Счёт просрочен.', call.from_user.id, call.message.message_id, reply_markup=keyboard_one_can)
                    await state.finish()
                case _:
                    await call.answer('⛔️ Счёт не оплачен')
                    
                    
def register_handlers_cryptobot(dp: Dispatcher):
    dp.register_callback_query_handler(balance_crypto_handler, lambda callback_query: callback_query.data == 'crypto', state="*")
    dp.register_message_handler(process_crypto_balance, lambda query: query.data.isdigit(), state=states_group.Form.waiting_for_balance)
    dp.register_callback_query_handler(type_crypto, lambda call: call.data.startswith("type_"), state="*")
    dp.register_callback_query_handler(check_payment, text_startswith='check', state=states_group.Form.amount)
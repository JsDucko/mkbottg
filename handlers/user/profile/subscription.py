from data.loader import dp, bot, Dispatcher
from aiogram import types
from keyboards.keyboards import keyboard_one_can, keyboard_buy_sub, keyboard_buy_sub_srok, create_keyboard_confirm_purchase
import os
from aiogram.utils.exceptions import MessageCantBeDeleted
from database import db
from datetime import datetime
from dateutil.relativedelta import relativedelta
import asyncio


async def delete_and_send_new_message(chat_id, message_id, text=None, photo=None, caption=None, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass

    if photo is not None:
        return await bot.send_photo(chat_id, photo, caption=caption, parse_mode='html', reply_markup=reply_markup)
    else:
        return await bot.send_message(chat_id, text, parse_mode='html', reply_markup=reply_markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data in ['sub_profile'])
async def sub_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    photo_path = os.path.join('img', 'start.png')
    with open(photo_path, 'rb') as photo_file:
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption=f'⭐️<b>Преимущества подписки:</b>\n\n<i>1. Возможность инвестировать типом "Ежедневное начисление".️\n\n2. Повышенный процент бонуса за депозит реферала - 15%.\n\n3. Уникальная "звёздочка" возле вашего ника.</i>\n\n<b>🔹1 Месяц - 1500 Рублей\n🔹3 Месяца - 3000 Рублей\n🔹12 Месяцев - 5500 Рублей</b>', reply_markup=keyboard_buy_sub)
        

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'buy_sub')
async def buysub_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, "⏰ Выберите срок действия подписки:", reply_markup=keyboard_buy_sub_srok)
    

def get_subscription_cost(duration):
    if duration == '1m':
        return 1500
    elif duration == '3m':
        return 3000
    else:  # '12m'
        return 5500

def get_subscription_duration_text(duration):
    if duration == '1m':
        return "1 месяц"
    elif duration == '3m':
        return "3 месяца"
    else:  # '12m'
        return "12 месяцев"

@dp.callback_query_handler(lambda callback_query: callback_query.data in ['1m', '3m', '12m'])
async def subscription_duration_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id
    duration = callback_query.data
    cost = get_subscription_cost(duration)

    user_balance = await db.get_user_balance(user_id)
    
    subscription_status = await db.get_user_subscription_status(user_id)
    if "Активна" in subscription_status:
        await delete_and_send_new_message(
            callback_query.message.chat.id,
            callback_query.message.message_id,
            "❌ У вас уже есть активная подписка. Пожалуйста, дождитесь её окончания.", reply_markup=keyboard_one_can
        )
        return

    if user_balance < cost:
        await delete_and_send_new_message(
            callback_query.message.chat.id,
            callback_query.message.message_id,
            f"❌ У вас недостаточно средств на балансе для покупки подписки на {get_subscription_duration_text(duration)}.", reply_markup=keyboard_one_can
        )
    else:
        confirmation_text = f"❗️ Вы уверены, что хотите купить подписку на {get_subscription_duration_text(duration)}? С вашего баланса будет списано {cost}₽"
        await delete_and_send_new_message(
            callback_query.message.chat.id,
            callback_query.message.message_id,
            confirmation_text,
            reply_markup=create_keyboard_confirm_purchase(duration)
        )


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('confirm_purchase'))
async def confirm_purchase_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id
    _, duration = callback_query.data.split(':')
    cost = get_subscription_cost(duration)

    current_balance = await db.get_user_balance(user_id)

    new_balance = current_balance - cost
    await db.update_user_balance(user_id, new_balance)

    end_date = datetime.now() + relativedelta(months=int(duration[:-1]))
    new_status = f"Активна до {end_date.strftime('%d.%m.%Y')}"
    await db.update_subscription_status(user_id, new_status)

    await delete_and_send_new_message(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        f"✅ Подписка успешно приобретена! Срок действия подписки: {get_subscription_duration_text(duration)}.", reply_markup=keyboard_one_can
    )
    
    
    
    
    
async def check_subscriptions_expiration():
    while True:
        all_users = await db.get_all_users()
        for user in all_users:
            user_id, subscription_status = user[0], user[3]
            if "Активна" in subscription_status:
                end_date_str = subscription_status.split()[-1]
                end_date = datetime.strptime(end_date_str, '%d.%m.%Y')
                if datetime.now() > end_date:
                    await db.update_subscription_status(user_id, "Не активна")
                    await bot.send_message(user_id, "❗️ Ваша подписка закончилась. Пожалуйста, продлите срок действия подписки.", reply_markup=keyboard_one_can)
        await asyncio.sleep(60 * 60)










def register_handlers_subscription(dp: Dispatcher):
    dp.register_callback_query_handler(sub_handler, lambda callback_query: callback_query.data in ['sub_profile'], state="*")
    dp.register_callback_query_handler(buysub_handler, lambda callback_query: callback_query.data == 'buy_sub', state="*")
    dp.register_callback_query_handler(subscription_duration_handler, lambda callback_query: callback_query.data in ['1m', '3m', '12m'], state="*")
    dp.register_callback_query_handler(confirm_purchase_handler, lambda callback_query: callback_query.data == 'confirm_purchase', state="*")

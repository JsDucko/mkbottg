from database import db
from data.loader import dp, bot, Dispatcher
from aiogram import types
import os
from keyboards.keyboards import keyboard_profile, keyboard_sposob, keyboard_info
from aiogram.types import ParseMode
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.user.main_menu import cmd_handler
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted
import asyncio

async def delete_and_send_new_message(chat_id, message_id, text=None, photo=None, caption=None, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass

    if photo is not None:
        return await bot.send_photo(chat_id, photo, caption=caption, parse_mode='html', reply_markup=reply_markup)
    else:
        return await bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode='html')


@dp.callback_query_handler(lambda callback_query: callback_query.data in ['profile', 'profile_admin'])
async def profile_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.full_name
    subscription_status = await db.get_user_subscription_status(user_id)
    user_balance = await db.get_user_balance(user_id)
    daily_earning = await db.get_user_earnings(user_id)
    total_invest = await db.get_user_total_invest(user_id)
    broker_balance = await db.get_broker_balance(user_id)

    if "Активна" in subscription_status:
        user_name = f"{user_name} ⭐️"

    photo_path = os.path.join('img', 'profile.png')
    with open(photo_path, 'rb') as photo_file:
        await delete_and_send_new_message(
            callback_query.message.chat.id, 
            callback_query.message.message_id,
            photo=photo_file,
            caption=f'💼 {user_name}, <b>Ваш портфель:</b>\n\n👤 <b>ID:</b> {user_id}\n💵 <b>Баланс:</b> {user_balance}₽\n⭐️ <b>Подписка:</b> {subscription_status}\n\n📊 <b>Брокерский счёт:</b> {broker_balance}₽\n📈 <b>Ежедневное начисление:</b> {daily_earning}₽\n💰 <b>Всего инвестировано:</b> {total_invest}₽',
            reply_markup=keyboard_profile
        )
        
              
@dp.callback_query_handler(lambda callback_query: callback_query.data in ['deposit_profile', 'deposit_zero'])
async def balance_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    photo_path = os.path.join('img', 'deposit.png')
    with open(photo_path, 'rb') as photo_file:
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption=f'💸 Выберите способ оплаты:', reply_markup=keyboard_sposob)
               
@dp.callback_query_handler(lambda callback_query: callback_query.data in ['info', 'info_admin'])
async def back_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    photo_path = os.path.join('img', 'info.png')
    with open(photo_path, 'rb') as photo_file:
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption=f'<b>📂 Информация о Нас: </b>\n\n<i>🔹 Свидетельство постановке на учет:  https://bit.ly/IC_uchet\n\n 🔹Свидетельство о регистрации: : https://bit.ly/IC_UR\n\n🔹Пользовательское соглашение:  https://bit.ly/IC_PS\n\n🔹Как мы зарабатываем? https://bit.ly/IC_HOW\n\n</i>', reply_markup=keyboard_info)

@dp.callback_query_handler(lambda callback_query: callback_query.data in ['tp', 'tp_admin'])
async def back_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    photo_path = os.path.join('img', 'info.png')
    with open(photo_path, 'rb') as photo_file:
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption=f'<b>🧑🏼‍💻 Техническая Поддержка 24/7.</b>\n\n <i>Заполните форму обратной связи:\n\n1. Ваш Логин:\n2. Ваша проблема\n\n</i><b>Адресуйте письмо нашей поддержки: @user</b>', reply_markup=keyboard_info)

review_callback = CallbackData("review", "action", "review_id")
REVIEW_ID = 0
REVIEW_USER_ID = 1
REVIEW_USERNAME = 2
REVIEW_TEXT = 3
REVIEW_PHOTO_ID = 4

@dp.callback_query_handler(review_callback.filter(action=["previous", "next", "back_o"]))
async def review_navigation(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    review_id, action = int(callback_data["review_id"]), callback_data["action"]
    if action == "previous":
        review_id -= 1
    elif action == "next":
        review_id += 1
    elif action == "back_o":
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await cmd_handler(call.message)
        await bot.answer_callback_query(call.id)
        return

    review = db.get_review_by_id(review_id)
    if review:
        markup = get_review_navigation_keyboard(review_id, db.get_review_count())
        username = review[REVIEW_USERNAME] if review[REVIEW_USERNAME] else "Анонимный отзыв"

        user_id = review[REVIEW_USER_ID]
        subscription_status = await db.get_user_subscription_status(user_id)

        if "Активна" in subscription_status:
            username = f"{username} ⭐️"

        caption = f"{review[REVIEW_TEXT]}\n\n👁 Отзыв оставил: @{username}"

        message_id = call.message.message_id
        chat_id = call.message.chat.id

        await delete_message_with_ignore(chat_id, message_id)

        if review[REVIEW_PHOTO_ID]:
            await bot.send_photo(chat_id, photo=review[REVIEW_PHOTO_ID], caption=caption, reply_markup=markup)
        else:
            await bot.send_message(chat_id, text=caption, reply_markup=markup)

        await call.answer()
    else:
        await call.answer("Нет больше отзывов")

@dp.callback_query_handler(lambda callback_query: callback_query.data in ['otziv'])
async def show_reviews(callback_query: types.CallbackQuery):
    review = db.get_review_by_id(1)
    chat_id = callback_query.message.chat.id
    if review:
        markup = get_review_navigation_keyboard(1, db.get_review_count())
        username = review[REVIEW_USERNAME] if review[REVIEW_USERNAME] else "Аноним"
        caption = f"{review[REVIEW_TEXT]}\n\n👁 Отзыв оставил: @{username}"
        if review[REVIEW_PHOTO_ID]:
            await bot.send_photo(chat_id, photo=review[REVIEW_PHOTO_ID], caption=caption, reply_markup=markup)
        else:
            await bot.send_message(chat_id, text=caption, reply_markup=markup)
    else:
        await callback_query.answer("Нет доступных отзывов")
        
def get_review_navigation_keyboard(review_id, review_count):
    markup = InlineKeyboardMarkup(row_width=2)
    if review_id > 1:
        markup.insert(InlineKeyboardButton(f"⬅️ {review_id - 1}/{review_count}", callback_data=review_callback.new(action="previous", review_id=review_id)))
    if review_id < review_count:
        markup.insert(InlineKeyboardButton(f"➡️ {review_id + 1}/{review_count}", callback_data=review_callback.new(action="next", review_id=review_id)))
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data=review_callback.new(action="back_o", review_id=review_id)))
    return markup


async def delete_message_with_ignore(chat_id: int, message_id: int):
    try:
        await asyncio.sleep(0.1)
        await bot.delete_message(chat_id, message_id)
    except MessageToDeleteNotFound:
        pass
    


def register_handlers_profile(dp: Dispatcher):
    dp.register_message_handler(profile_handler, lambda callback_query: callback_query.data in ['profile', 'profile_admin'], state="*")
    dp.register_callback_query_handler(balance_handler, lambda callback_query: callback_query.data in ['deposit_profile', 'deposit_zero'], state="*")
    dp.register_callback_query_handler(back_handler, lambda callback_query: callback_query.data in ['info', 'info_admin'], state="*")
    dp.register_callback_query_handler(review_navigation, review_callback.filter(action=["previous", "next", "back_o"]), state="*")
    dp.register_callback_query_handler(show_reviews, lambda callback_query: callback_query.data in ['otziv'], state="*")
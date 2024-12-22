from data.loader import dp, bot, Dispatcher
from database import db
from aiogram import types
from utils import utils
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageCantBeDeleted

async def delete_and_send_new_message(chat_id, message_id, text=None, photo=None, caption=None, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass

    if photo is not None:
        return await bot.send_photo(chat_id, photo, caption=caption, parse_mode='html', reply_markup=reply_markup)
    else:
        return await bot.send_message(chat_id, text, parse_mode='html', reply_markup=reply_markup)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'referal_profile')
async def referral_profile(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    referral_link = utils.create_referral_link(user_id)
    
    referral_count = db.get_referral_count(user_id)
    money_ref = await db.get_referral_deposit(user_id)
    
    subscription_status = await db.get_user_subscription_status(user_id)

    if subscription_status.startswith("Активна"):
        text = f"🔗 <b>Ваша реферальная ссылка:</b>\n {referral_link}\n\n🧑🏼‍💻 <b>Рефералы:</b> {referral_count}\n💸 <b>Заработок:</b> {money_ref * 0.15}₽\n⭐️ <b>Подписка:</b> ✅\n\n<b>Условия:</b>\n<i>За каждого приглашённого вами пользователя вы получаете 15% от пополнения на баланс. Каждый новый пользователь, который перейдёт по вашей ссылке получит 50 Рублей на баланс.</i>"
    else:
        text = f"🔗 <b>Ваша реферальная ссылка:</b>\n {referral_link}\n\n🧑🏼‍💻 <b>Рефералы:</b> {referral_count}\n💸 <b>Заработок:</b> {money_ref * 0.1}₽\n⭐️ <b>Подписка:</b> ❌\n\n<b>Условия:</b>\n<i>За каждого приглашённого вами пользователя вы получаете 10% от пополнения на баланс. Каждый новый пользователь, который перейдёт по вашей ссылке получит 50 Рублей на баланс.</i>\n\n<b>⭐️ Оформите подписку и будете получать 15% с депозита вашего реферала.</b>"
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    share_button = InlineKeyboardButton(text="📎 Поделиться", url=f"https://t.me/share/url?url={referral_link}")
    back_button = InlineKeyboardButton(text="◀️ Назад", callback_data='back_to_menu')
    keyboard.add(share_button, back_button)

    await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, text=text, reply_markup=keyboard)
    
    
def register_handlers_referal(dp: Dispatcher):
    dp.register_message_handler(referral_profile, lambda callback_query: callback_query.data == 'referal_profile', state="*")
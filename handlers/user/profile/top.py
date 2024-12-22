from data.loader import bot, dp, Dispatcher
from aiogram import types
import os
from keyboards.keyboards import keyboard_one_can
from aiogram.utils.exceptions import MessageCantBeDeleted
from data.config import BOT_LINK

async def delete_and_send_new_message(chat_id, message_id, text=None, photo=None, caption=None, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass

    if photo is not None:
        return await bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup)
    else:
        return await bot.send_message(chat_id, text, reply_markup=reply_markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data in ['top_admin', 'top'])
async def top_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    photo_path = os.path.join('img', 'start.png')
    with open(photo_path, 'rb') as photo_file:
        await delete_and_send_new_message(callback_query.message.chat.id, callback_query.message.message_id, photo=photo_file, caption=f'🏆 Новостной Канал - {BOT_LINK}', reply_markup=keyboard_one_can)
            
            
def register_handlers_top(dp: Dispatcher):
    dp.register_message_handler(top_handler, lambda callback_query: callback_query.data in ['top_admin', 'top'], state="*")
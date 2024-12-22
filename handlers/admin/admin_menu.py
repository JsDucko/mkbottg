from data.loader import dp, bot, Dispatcher
from database import db
from aiogram import types
from keyboards.keyboards import keyboard_adm_menu


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'admin')
async def admin_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    total_users = db.get_total_users_count()
    total_deposit = db.get_total_deposits()
    await bot.send_message(chat_id=user_id, text=f'📊 Статистика:\n🦣 Пользователей в боте: {total_users}\n💰 Всего пополнений: {total_deposit}₽', reply_markup=keyboard_adm_menu)
    
def register_handlers_admin_menu(dp: Dispatcher):
    dp.register_message_handler(admin_handler, commands=['admin'], state="*")
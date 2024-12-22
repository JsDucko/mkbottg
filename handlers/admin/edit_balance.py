from data.loader import dp, bot, Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'edit_balance', state='*')
async def edit_balance_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        user_id = data.get('user_id')
        if user_id:
            await bot.send_message(chat_id=callback_query.message.chat.id, text=f'Вы выбрали редактирование баланса пользователя {user_id}')
        else:
            await bot.send_message(chat_id=callback_query.message.chat.id, text='Не удалось получить ID пользователя')
            
def register_handlers_edit_balance(dp: Dispatcher):
    dp.register_message_handler(edit_balance_handler, commands=['edit_balance'], state="*")
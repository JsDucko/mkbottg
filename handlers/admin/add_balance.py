from data.loader import dp, bot, Dispatcher
from database import db
from aiogram import types
from states import states_group
from aiogram.dispatcher import FSMContext
from keyboards.keyboards import keyboard_one_can, keyboard_balance_plus


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'plus_balance')
async def balance_handler1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text='Введите ID пользователя')
    await states_group.Form.WAITING_FOR_ANSWER.set()

@dp.message_handler(state=states_group.Form.WAITING_FOR_ANSWER)
async def waiting_for_answer_handler(message: types.Message, state: FSMContext):
    user_id = message.text.strip()
    if user_id.isdigit():
        async def find_user_by_id(user_id):
            db.cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = db.cur.fetchone()
            return user

        user_id = int(user_id)
        user = await find_user_by_id(user_id)
        if user:
            await bot.send_message(chat_id=message.chat.id, text=f'Пользователь {user_id} найден!', reply_markup=keyboard_balance_plus)
            await state.update_data(user_id=user_id)
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Пользователь {user_id} не найден!')
            await bot.send_message(chat_id=message.chat.id, text='Попробуйте снова ввести ID пользователя')
    else:
        await bot.send_message(chat_id=message.chat.id, text='ID должен состоять только из цифр!')
        await bot.send_message(chat_id=message.chat.id, text='Попробуйте снова ввести ID пользователя')
        
        
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'plus', state='*')
async def plus_balance_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text='Введите, сколько хотите прибавить? (писть просто число)')
    await states_group.Form.WAITING_FOR_ANSWER_NUM.set()

@dp.message_handler(state=states_group.Form.WAITING_FOR_ANSWER_NUM)
async def waiting_for_answer_num_handler(message: types.Message, state: FSMContext):
    plus_balance = message.text.strip()
    print(f"Plus balance: {plus_balance}")
    async with state.proxy() as data:
        user_id = data.get('user_id')
        user_balance = await db.get_user_balance(user_id)
        print(f"Old balance: {user_balance}")
        if user_balance is not None:
            user_balance = int(user_balance)
            new_balance = user_balance + int(plus_balance)
            await db.update_user_balance(user_id, new_balance)

            await bot.send_message(chat_id=message.chat.id, text=f'Баланс пользователя {user_id} успешно обновлен. Новый баланс: {new_balance}', reply_markup=keyboard_one_can)
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Ошибка: не удалось получить текущий баланс пользователя {user_id}', reply_markup=keyboard_one_can)

    await state.finish()
    
    
def register_handlers_add_balance(dp: Dispatcher):
    dp.register_message_handler(balance_handler1, lambda callback_query: callback_query.data == 'plus_balance', state="*")
    dp.register_callback_query_handler(plus_balance_handler, lambda callback_query: callback_query.data == 'plus', state="*")
    dp.register_callback_query_handler(waiting_for_answer_num_handler, state=states_group.Form.WAITING_FOR_ANSWER_NUM)
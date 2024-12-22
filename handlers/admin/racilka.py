from data.loader import dp, bot, Dispatcher
from database import db
from aiogram import types
from states import states_group
from aiogram.dispatcher import FSMContext
from keyboards.keyboards import keyboard_one_can, keyboard_racilka
from utils import utils
from handlers.user import main_menu
from handlers.admin import admin_menu


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'racilka')
async def racilka_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Введите текст рассылки.', reply_markup=keyboard_one_can)
    await states_group.Form.waiting_for_txt.set()

@dp.message_handler(state=states_group.Form.waiting_for_txt)
async def send_broadcast_message(message: types.Message, state: FSMContext):
    text_racilka = message.text
    total_users = db.get_total_users_count()
    await bot.send_message(chat_id=message.chat.id,
                           text=f'Рассылку получат: {total_users} пользователей\nТекст рассылки: {text_racilka}\nВы уверены, что хотите отправить рассылку?',
                           reply_markup=keyboard_racilka)
    await state.update_data(text_racilka=text_racilka)

@dp.callback_query_handler(lambda callback_query: callback_query.data in ['no', 'exit_plus'], state='*')
async def racilka_handler_no(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        pass

    await state.finish()
    await main_menu.cmd_handler(callback_query.message)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'yes', state='*')
async def confirm_broadcast(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Рассылка началась...')
    data = await state.get_data()
    text_racilka = data.get('text_racilka')
    user_ids = utils.get_all_users()
    if text_racilka:
        for user_id in user_ids:
            try:
                await bot.send_message(chat_id=user_id, text=text_racilka)
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {str(e)}")
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Рассылка успешно завершена!', reply_markup=keyboard_one_can)
        async with state.proxy() as data:
            pass

        await state.finish()
        await admin_menu.admin_handler(callback_query.message)
    else:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Текст рассылки пустой. Рассылка не была отправлена.', reply_markup=keyboard_one_can)
        await state.finish
        
def register_handlers_racilka(dp: Dispatcher):
    dp.register_message_handler(racilka_handler, lambda callback_query: callback_query.data == 'racilka', state="*")
    dp.register_callback_query_handler(send_broadcast_message, state=states_group.Form.waiting_for_txt)
    dp.register_callback_query_handler(racilka_handler_no, lambda callback_query: callback_query.data in ['no', 'exit_plus'], state='*')
    dp.register_callback_query_handler(confirm_broadcast, lambda callback_query: callback_query.data == 'yes', state='*')
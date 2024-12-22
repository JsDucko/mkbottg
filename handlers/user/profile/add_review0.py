from aiogram import types
from data.loader import dp, bot, Dispatcher
from database import db
from aiogram.dispatcher import FSMContext
from states.states_group import ReviewStates
from keyboards.keyboards import otziv_wihdraw_keyboard, confirm_publish_keyboard, keyboard_one_can
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageCantBeDeleted

async def delete_and_send_new_message(chat_id, message_id, text=None, photo=None, caption=None, reply_markup=None):
    try:
        await bot.delete_message(chat_id, message_id)
    except MessageCantBeDeleted:
        pass

    if photo is not None:
        await bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)


def review_text(user_data):
    photo_line = f"{user_data['photo_id']}\n\n" if user_data['photo_id'] else "Без фото\n\n"
    anonymous_line = "🥷🏼 Оставлен анонимно\n\n" if user_data.get('anonymous', False) else ""
    return f"💬 Ваш отзыв:\n\n{photo_line}{anonymous_line}{user_data['text']}"


@dp.callback_query_handler(lambda call: call.data == 'otziv_wihdraw')
async def process_callback_otziv_wihdraw(call: types.CallbackQuery):
    await call.answer()
    await delete_and_send_new_message(call.message.chat.id, call.message.message_id, text="💬 Отправьте свой отзыв о нашем боте.")
    await ReviewStates.Text.set()

@dp.message_handler(state=ReviewStates.Text)
async def process_review_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text, anonymous=False)
    await delete_and_send_new_message(message.chat.id, message.message_id, text=f'❗️ Проверьте текст. Если вы уверены в правильности - нажмите "✅ Далее"\n📎 Ваши текст: {message.text}', reply_markup=otziv_wihdraw_keyboard())
    await ReviewStates.ConfirmText.set()

@dp.callback_query_handler(lambda call: call.data in ['confirm_text', 'edit_text', 'back_to_menu'], state=ReviewStates.ConfirmText)
async def process_callback_confirm_text(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    user_data = await state.get_data()

    if call.data == 'confirm_text':
        await delete_and_send_new_message(call.message.chat.id, call.message.message_id, text="📸 Отправьте один скриншот, где видно поступление средств.\n\n🤔 Если не хотите добовлять фото, нажмите \"↪️ Пропустить\".", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↪️ Пропустить", callback_data="skip_photo")))
        await ReviewStates.Photo.set()
    elif call.data == 'edit_text':
        await delete_and_send_new_message(call.message.chat.id, call.message.message_id, text="💬 Отправьте свой отзыв о нашем боте.")
        await ReviewStates.Text.set()
    else:
        pass

@dp.callback_query_handler(lambda call: call.data == 'skip_photo', state=ReviewStates.Photo)
async def process_callback_skip_photo(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(photo_id=None)
    user_data = await state.get_data()
    await delete_and_send_new_message(call.message.chat.id, call.message.message_id, text=f"💬 Ваш отзыв:\n\nБез фото\n\n{user_data['text']}\n\n❗️Проверьте содержимое отзыва и нажмите \"✅ Опубликовать\"", reply_markup=confirm_publish_keyboard(False))
    await ReviewStates.Publish.set()

@dp.message_handler(content_types=types.ContentType.PHOTO, state=ReviewStates.Photo)
async def process_review_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    user_data = await state.get_data()
    await delete_and_send_new_message(message.chat.id, message.message_id, text=f"💬 Ваш отзыв:\n\n{photo_id}\n\n{user_data['text']}\n\n❗️Проверьте содержимое отзыва и нажмите \"✅ Опубликовать\"", reply_markup=confirm_publish_keyboard(False))
    await ReviewStates.Publish.set()

@dp.callback_query_handler(lambda call: call.data in ['publish_review', 'toggle_anonymous', 'back_to_menu'], state=ReviewStates.Publish)
async def process_callback_publish_review(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    user_data = await state.get_data()

    if call.data == 'publish_review':
        db.add_review(call.from_user.id, call.from_user.username if not user_data.get('anonymous', False) else None, user_data['text'], user_data['photo_id'])
        await delete_and_send_new_message(call.message.chat.id, call.message.message_id, text="✅ Ваш отзыв был опубликован!", reply_markup=keyboard_one_can)
    elif call.data == 'toggle_anonymous':
        anonymous = not user_data.get('anonymous', False)
        await state.update_data(anonymous=anonymous)
        await call.message.edit_reply_markup(reply_markup=confirm_publish_keyboard(anonymous))
    else:
        pass

    await state.finish()
    
    
    
def register_handlers_add_review(dp: Dispatcher):
    dp.register_message_handler(process_callback_otziv_wihdraw, lambda call: call.data == 'otziv_wihdraw', state="*")
    dp.register_message_handler(process_review_text, state=ReviewStates.Text)
    dp.register_message_handler(process_callback_confirm_text, lambda call: call.data in ['confirm_text', 'edit_text', 'back_to_menu'], state=ReviewStates.ConfirmText)
    dp.register_message_handler(process_callback_skip_photo, lambda call: call.data == 'skip_photo', state=ReviewStates.Photo)
    dp.register_message_handler(process_review_photo, content_types=types.ContentType.PHOTO, state=ReviewStates.Photo)
    dp.register_message_handler(process_callback_publish_review, lambda call: call.data in ['publish_review', 'toggle_anonymous', 'back_to_menu'], state=ReviewStates.Publish)
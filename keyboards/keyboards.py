from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import CHANNEL_LINK


keyboard_user_start = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_user_profile = types.InlineKeyboardButton(text='💼 Личный Кабинет', callback_data='profile')
kb_user_top = types.InlineKeyboardButton(text='🔰 Новости', callback_data='top')
kb_user_info = types.InlineKeyboardButton(text='ℹ️ Информация', callback_data='info')
kb_referal_profile = types.InlineKeyboardButton(text='💸 Реферальная система', callback_data='referal_profile')
kb_calculator_user = types.InlineKeyboardButton(text='⚖️ Калькулятор прибыли', callback_data='calculator_user')
kb_sub_profile = types.InlineKeyboardButton(text='⭐️ Подписка', callback_data='sub_profile')
kb_otziv = types.InlineKeyboardButton(text='💭 Отзывы', callback_data='otziv')
kb_user_tp = types.InlineKeyboardButton(text='🧑🏼‍💻 Техническая Поддержка', callback_data='tp')
keyboard_user_start.add(kb_user_profile)
keyboard_user_start.row(kb_user_top, kb_user_info)
keyboard_user_start.row(kb_referal_profile)
keyboard_user_start.row(kb_calculator_user)
keyboard_user_start.row(kb_sub_profile, kb_otziv)
keyboard_user_start.row(kb_user_tp)

keyboard_admin_start = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_admin_profile = types.InlineKeyboardButton(text='💼 Личный Кабинет', callback_data='profile_admin')
kb_admin_top = types.InlineKeyboardButton(text='🔰 Новости', callback_data='top_admin')
kb_admin_info = types.InlineKeyboardButton(text='ℹ️ Информация', callback_data='info_admin')
kb_referal_profile = types.InlineKeyboardButton(text='💸 Реферальная система', callback_data='referal_profile')
kb_calculator_admin = types.InlineKeyboardButton(text='⚖️ Калькулятор прибыли', callback_data='calculator_admin')
kb_sub_profile = types.InlineKeyboardButton(text='⭐️ Подписка', callback_data='sub_profile')
kb_otziv = types.InlineKeyboardButton(text='💭 Отзывы', callback_data='otziv')
kb_user_tp = types.InlineKeyboardButton(text='🧑🏼‍💻 Техническая Поддержка', callback_data='tp')
kb_admin = types.InlineKeyboardButton(text='⚙️ Админ панель', callback_data='admin')
keyboard_admin_start.add(kb_admin_profile)
keyboard_admin_start.row(kb_admin_top, kb_admin_info)
keyboard_admin_start.row(kb_referal_profile)
keyboard_admin_start.add(kb_calculator_admin)
keyboard_admin_start.row(kb_sub_profile, kb_otziv)
keyboard_admin_start.row(kb_user_tp)
keyboard_admin_start.row(kb_admin)


keyboard_profile = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_invest_profile = types.InlineKeyboardButton(text='📊 Инвестировать', callback_data='invest')
kb_deposit_profile = types.InlineKeyboardButton(text='🟢 Пополнение', callback_data='deposit_profile')
kb_withdraw_profile = types.InlineKeyboardButton(text='🔴 Вывод', callback_data='withdraw_profile')
kb_myinvest_profile = types.InlineKeyboardButton(text='🔐 Мои инвестиции', callback_data='myinvest_profile')
kb_calculator_profile = types.InlineKeyboardButton(text='⚖️ Калькулятор прибыли', callback_data='calculator_profile')
kb_referal_profile = types.InlineKeyboardButton(text='💸 Реферальная система', callback_data='referal_profile')
kb_sub_profile = types.InlineKeyboardButton(text='⭐️ Подписка', callback_data='sub_profile')
kb_back_profile = types.InlineKeyboardButton(text='◀️ Назад', callback_data='back_profile')
keyboard_profile.add(kb_invest_profile)
keyboard_profile.row(kb_deposit_profile, kb_withdraw_profile)
keyboard_profile.row(kb_myinvest_profile)
keyboard_profile.row(kb_calculator_profile)
keyboard_profile.row(kb_referal_profile)
keyboard_profile.row(kb_sub_profile)
keyboard_profile.row(kb_back_profile)


keyboard_one_can = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_back = types.InlineKeyboardButton(text='◀️ Назад', callback_data='back')
keyboard_one_can.add(kb_back)


keyboard_zero_balance = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_zero_deposit = types.InlineKeyboardButton(text='🟢 Пополнить баланс', callback_data='deposit_zero')
kb_zero_back = types.InlineKeyboardButton(text='◀️ Назад', callback_data='back_zero')
keyboard_zero_balance.add(kb_zero_deposit)
keyboard_zero_balance.row(kb_zero_back)


keyboard_sposob = types.InlineKeyboardMarkup(resize_keyboard=True)
#kb_qiwi = types.InlineKeyboardButton(text='💳 QIWI / Карта', callback_data='qiwi')
kb_crypto = types.InlineKeyboardButton(text='🪙 Криптовалюта', callback_data='crypto')
kb_sposob_back = types.InlineKeyboardButton(text='◀️ Назад', callback_data='back_sposob')
#keyboard_sposob.add(kb_qiwi)
keyboard_sposob.row(kb_crypto)
keyboard_sposob.row(kb_sposob_back)


keyboard_sposob_withdraw = types.InlineKeyboardMarkup(resize_keyboard=True)
#kb_qiwi_withdraw = types.InlineKeyboardButton(text='🥝 QIWI', callback_data='qiwi_withdraw')
kb_card_withdraw = types.InlineKeyboardButton(text='💳 Карта', callback_data='card_withdraw')
kb_crypto_withdraw = types.InlineKeyboardButton(text='🪙 Криптовалюта', callback_data='crypto_withdraw')
kb_sposob_back_withdraw = types.InlineKeyboardButton(text='◀️ Назад', callback_data='back_sposob_withdraw')
#keyboard_sposob_withdraw.add(kb_qiwi_withdraw)
keyboard_sposob_withdraw.row(kb_card_withdraw)
keyboard_sposob_withdraw.row(kb_crypto_withdraw)
keyboard_sposob_withdraw.row(kb_sposob_back_withdraw)


keyboard_adm_menu = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_racilka = types.InlineKeyboardButton(text='💬 Рассылка', callback_data='racilka')
kb_plusbalance = types.InlineKeyboardButton(text='💸 Выдать баланс', callback_data='plus_balance')
#Реализуется позже kb_plussub = types.InlineKeyboardButton(text='🔄 Продлить подписку', callback_data='plus_sub')
kb_exit_adm_menu = types.InlineKeyboardButton(text='◀️ Назад', callback_data='exit_adm')
keyboard_adm_menu.add(kb_racilka)
keyboard_adm_menu.row(kb_plusbalance)
#keyboard_adm_menu.row(kb_plussub)
keyboard_adm_menu.row(kb_exit_adm_menu)

keyboard_racilka = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_yes = types.InlineKeyboardButton(text='✅ Да', callback_data='yes')
kb_no = types.InlineKeyboardButton(text='❌ Отмена', callback_data='no')
keyboard_racilka.add(kb_yes)
keyboard_racilka.row(kb_no)

keyboard_balance_plus = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_plus = types.InlineKeyboardButton(text='Добавить', callback_data='plus')
kb_edit = types.InlineKeyboardButton(text='Изменить', callback_data='edit_balance')
kb_exit_plus = types.InlineKeyboardButton(text='◀️ Назад', callback_data='exit_plus')
keyboard_balance_plus.add(kb_plus)
keyboard_balance_plus.row(kb_edit)
keyboard_balance_plus.row(kb_exit_plus)


keyboard_info = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_exit_info = types.InlineKeyboardButton(text='◀️ Назад', callback_data='exit_info')
keyboard_info.row(kb_exit_info)


keyboard_sucs_withdraw = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_otziv_withdraw = types.InlineKeyboardButton(text='📝 Оставить отзыв (Бонус на баланс)', callback_data='otziv_wihdraw')
kb_exit_withdraw = types.InlineKeyboardButton(text='◀️ Назад', callback_data='exit_withdraw')
keyboard_sucs_withdraw.add(kb_otziv_withdraw)
keyboard_sucs_withdraw.row(kb_exit_withdraw)


keyboard_calculator_deposit = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_24h = types.InlineKeyboardButton(text='🚀 Депозит на 24 часа', callback_data='24h')
kb_7d = types.InlineKeyboardButton(text='🏆 Депозит на 7 дней', callback_data='7d')
kb_14d = types.InlineKeyboardButton(text='👑 Депозит на 14 дней', callback_data='14d')
kb_28d = types.InlineKeyboardButton(text='💎 Депозит на 28 дней', callback_data='28d')
kb_back_calculator = types.InlineKeyboardButton(text='◀️ Назад', callback_data='back_calculator')
keyboard_calculator_deposit.add(kb_24h)
keyboard_calculator_deposit.row(kb_7d)
keyboard_calculator_deposit.row(kb_14d)
keyboard_calculator_deposit.row(kb_28d)
keyboard_calculator_deposit.row(kb_back_calculator)


keyboard_invest_deposit = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_24h_invest_deposit = types.InlineKeyboardButton(text='🚀 Депозит на 24 часа', callback_data='24h_invest_deposit')
kb_7d_invest_deposit = types.InlineKeyboardButton(text='🏆 Депозит на 7 дней', callback_data='7d_invest_deposit')
kb_14d_invest_deposit = types.InlineKeyboardButton(text='👑 Депозит на 14 дней', callback_data='14d_invest_deposit')
kb_28d_invest_deposit = types.InlineKeyboardButton(text='💎 Депозит на 28 дней', callback_data='28d_invest_deposit')
kb_evryday_invest_deposit = types.InlineKeyboardButton(text='⭐️ Ежедневное начисление', callback_data='evryday_invest_deposit')
kb_back_invest_deposit = types.InlineKeyboardButton(text='◀️ Назад', callback_data='back_invest_deposit')
keyboard_invest_deposit.add(kb_24h_invest_deposit)
keyboard_invest_deposit.row(kb_7d_invest_deposit)
keyboard_invest_deposit.row(kb_14d_invest_deposit)
keyboard_invest_deposit.row(kb_28d_invest_deposit)
keyboard_invest_deposit.row(kb_evryday_invest_deposit)
keyboard_invest_deposit.row(kb_back_invest_deposit)


keyboard_invest_go = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_go_inv = types.InlineKeyboardButton(text='🚀 Перейти к инвестированию прямо сейчас!', callback_data='go_inv')
kb_cancel_go = types.InlineKeyboardButton(text='◀️ Назад', callback_data='cancel_go')
keyboard_invest_go.add(kb_go_inv)
keyboard_invest_go.row(kb_cancel_go)


keyboard_buy_sub = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_buy_sub = types.InlineKeyboardButton(text='⭐️ Купить подписку', callback_data='buy_sub')
kb_cancel_sub = types.InlineKeyboardButton(text='◀️ Назад', callback_data='cancel_sub')
keyboard_buy_sub.add(kb_buy_sub)
keyboard_buy_sub.row(kb_cancel_sub)


keyboard_buy_sub_srok = types.InlineKeyboardMarkup(resize_keyboard=True)
kb_1m = types.InlineKeyboardButton(text='1 Месяц (1500₽)', callback_data='1m')
kb_3m = types.InlineKeyboardButton(text='3 Месяц (3000₽)', callback_data='3m')
kb_12m = types.InlineKeyboardButton(text='12 Месяц (5500₽)', callback_data='12m')
kb_cancel_sub_srok = types.InlineKeyboardButton(text='◀️ Назад', callback_data='cancel_sub_srok')
keyboard_buy_sub_srok.add(kb_1m)
keyboard_buy_sub_srok.row(kb_3m)
keyboard_buy_sub_srok.row(kb_12m)
keyboard_buy_sub_srok.row(kb_cancel_sub_srok)


def create_keyboard_confirm_purchase(duration):
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("✅ Да", callback_data=f"confirm_purchase:{duration}"),
        InlineKeyboardButton("◀️ Назад", callback_data="go_back")
    )


# Виды криптовалют Crypto
def types_crypto():
    markup = types.InlineKeyboardMarkup()
    btc = types.InlineKeyboardButton('BTC', callback_data='type_btc')
    ton = types.InlineKeyboardButton('TON', callback_data='type_ton')
    eth = types.InlineKeyboardButton('ETH', callback_data='type_eth')
    usdt = types.InlineKeyboardButton('USDT', callback_data='type_usdt')
    usdc = types.InlineKeyboardButton('USDC', callback_data='type_usdc')
    #busd = types.InlineKeyboardButton('BUSD', callback_data='type_busd')
    back = types.InlineKeyboardButton('◀️ Назад', callback_data='back_payments')
    markup.row(btc, ton, eth)
    markup.row(usdt, usdc)
    markup.add(back)
    return markup


# Ссылка и проверка оплаты Crypto
def crypto_kb(url: str, id: str | int):
    markup = types.InlineKeyboardMarkup(1)
    link = types.InlineKeyboardButton('📎Ссылка на оплату', url=url)
    check_pay = types.InlineKeyboardButton(
        '🔍Проверить оплату', callback_data=f'check|crypto|{id}')
    back = types.InlineKeyboardButton(
        '◀️ Назад', callback_data='back_typeCrypto')
    markup.add(link, check_pay, back)
    return markup


#Клавиатура ОП
def create_subscription_keyboard():
    keyboard = InlineKeyboardMarkup()
    subscribe_button = InlineKeyboardButton(text="📎 Подписаться", url=CHANNEL_LINK)
    check_subscription_button = InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscription")
    keyboard.add(subscribe_button, check_subscription_button)
    return keyboard


#Клавиатура, согласится ли с инвестированием
def create_inline_keyboard():
    inline_keyboard = InlineKeyboardMarkup()
    yes_button = InlineKeyboardButton("✅ Да", callback_data="confirm_invest")
    back_button = InlineKeyboardButton("◀️ Назад", callback_data="go_back")
    inline_keyboard.add(yes_button, back_button)
    return inline_keyboard


def otziv_wihdraw_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ Далее", callback_data="confirm_text"))
    keyboard.add(InlineKeyboardButton("✏️ Редактировать", callback_data="edit_text"))
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu"))
    return keyboard

def confirm_publish_keyboard(is_anonymous):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ Опубликовать", callback_data="publish_review"))
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu"))
    return keyboard

def create_result_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🚀 Перейти к инвестированию!", callback_data="go_invest"),
    )
    keyboard.add(
        InlineKeyboardButton("🔄 Другая Сумма", callback_data="retry_sum"),
        InlineKeyboardButton("⌛️ Другой Срок", callback_data="retry_term"),
        InlineKeyboardButton("◀️ Назад", callback_data="go_back")
    )
    return keyboard


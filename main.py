from aiogram import executor
import asyncio
from data.loader import *
from database.db import *
from utils.daily_earnings import *
import logging
from data.loader import dp, bot


async def on_startup(_):
    asyncio.create_task(daily_earnings_update())
    asyncio.create_task(db.db_start())
    asyncio.create_task(db.reviews_db_start())
    asyncio.create_task(db.investments_db_start())
    print('База данных успешно подключена')
    

async def on_shutdown(dp):
    logging.info("Shutting down bot...")
    
    for task in asyncio.all_tasks():
        task.cancel()

    await bot.close()
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.info("Bot has been shut down.")
    
    
from handlers.admin import add_balance, admin_menu, edit_balance, racilka
from handlers.user import main_menu
from handlers.user.profile import invest_1day_sub, profile, referal, subscription, top, withdraw, add_review0, calculator, my_invest
from handlers.user.profile.payments import cryptobot

main_menu.register_handlers_main_menu(dp)
add_balance.register_handlers_add_balance(dp)
admin_menu.register_handlers_admin_menu(dp)
edit_balance.register_handlers_edit_balance(dp)
racilka.register_handlers_racilka(dp)
invest_1day_sub.register_handlers_invest_1day_sub(dp)
profile.register_handlers_profile(dp)
referal.register_handlers_referal(dp)
subscription.register_handlers_subscription(dp)
top.register_handlers_top(dp)
withdraw.register_handlers_withdraw(dp)
cryptobot.register_handlers_cryptobot(dp)
add_review0.register_handlers_add_review(dp)
calculator.register_handlers_calculator(dp)
my_invest.register_handlers_my_invest(dp)

from handlers.user.profile.invest_1day_sub import process_investments
from handlers.user.profile.subscription import check_subscriptions_expiration
# Выдача девидендов
asyncio.ensure_future(process_investments())
print('Выдача ежедневного заработка запущена')
# Проверка срока подписок
asyncio.get_event_loop().create_task(check_subscriptions_expiration())
print('Проверка статуса подписок запущена')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)

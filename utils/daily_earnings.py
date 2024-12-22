from database import db
import asyncio

#⭐️Ежедневное начисление (которое с подпиской)
async def daily_earnings_update():
    while True:
        await asyncio.sleep(86400)  # 1 день в секундах (86400 сек)
        users = await db.get_all_users()

        for user in users:
            user_id = user[0]
            broker_balance = user[6]
            daily_earning = broker_balance * 0.009

            if daily_earning > 0:
                new_balance = user[2] + daily_earning
                rounded_balance = round(new_balance, 1)
                await db.update_user_balance(user_id, rounded_balance)
                
                
async def main():            
    await asyncio.gather(daily_earnings_update())
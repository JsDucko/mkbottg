from database import db
from data.config import OP_ID, TOKEN,BOT_LINK
from aiogram import Bot


def get_total_users_count():
    users = db.cur.execute('SELECT COUNT(*) FROM users').fetchone()
    total_count = users[0] if users else 0
    return total_count


async def get_ref_money(user_id):
    total_referral_deposit = await db.get_referral_deposit(user_id)
    return total_referral_deposit

def get_all_users():
    users = db.cur.execute('SELECT * FROM users').fetchall()
    return [user[0] for user in users] if users else []


async def is_user_subscribed(user_id):
    bot = Bot(token=TOKEN)
    try:
        member_status = await bot.get_chat_member(OP_ID, user_id)
        return member_status.status not in ["left", "kicked"]
    except Exception as e:
        print(f"Error while checking subscription: {e}")
        return False
    
def create_referral_link(user_id):
    return f"{BOT_LINK}?start={user_id}"
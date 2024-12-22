import sqlite3 as sq

db = sq.connect('database/users.db')
cur = db.cursor()

# Создание бд и таблицы с юзерами
async def db_start():
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            balance INTEGER,
            subscription_status TEXT,
            total_invest INTEGER,
            earnings INTEGER,
            broker_balance INTEGER,
            referrer_id INTEGER,
            total_deposit INTEGER,
            referral_deposit INTEGER
        )
    ''')
    db.commit()
    
# Создание бд и таблицы для отзывов
async def reviews_db_start():
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            text TEXT,
            photo_id TEXT
        )
    ''')
    db.commit()
    
# Создание бд и таблицы с инвестициями
async def investments_db_start():
    cur.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            investment_amount INTEGER,
            investment_term TEXT,
            daily_income INTEGER,
            interest_rate REAL,
            start_date TEXT,
            end_date TEXT,
            investment_type TEXT
        )
    ''')
    db.commit()
    
def add_referrer(user_id, referrer_id):
    cur.execute("UPDATE users SET referrer_id = ? WHERE id = ?", (referrer_id, user_id))
    db.commit()
    return cur.rowcount

async def get_referrer(user_id):
    cur.execute("SELECT referrer_id FROM users WHERE id = ?", (user_id,))
    return cur.fetchone()[0]

def get_referral_count(user_id):
    cur.execute("SELECT COUNT(*) FROM users WHERE referrer_id = ?", (user_id,))
    return cur.fetchone()[0]

async def get_user_name(user_id):
    return cur.execute('SELECT first_name FROM users WHERE id = ?', (user_id,)).fetchone()[0]

async def get_broker_balance(user_id):
    cur.execute("SELECT broker_balance FROM users WHERE id = ?", (user_id,))
    return cur.fetchone()[0]

async def get_user_balance(user_id):
    return cur.execute('SELECT balance FROM users WHERE id = ?', (user_id,)).fetchone()[0]

async def get_user_subscription_status(user_id):
    return cur.execute('SELECT subscription_status FROM users WHERE id = ?', (user_id,)).fetchone()[0]

async def get_user_earnings(user_id):
    return cur.execute('SELECT earnings FROM users WHERE id = ?', (user_id,)).fetchone()[0]

async def get_user_total_invest(user_id):
    return cur.execute('SELECT total_invest FROM users WHERE id = ?', (user_id,)).fetchone()[0]

async def get_referral_deposit(user_id):
    return cur.execute('SELECT referral_deposit FROM users WHERE id = ?', (user_id,)).fetchone()[0]

def get_total_deposits():
    cur.execute("SELECT SUM(total_deposit) FROM users")
    total_deposits = cur.fetchone()[0]
    return total_deposits or 0

async def get_user_total_deposit(user_id):
    return cur.execute('SELECT total_deposit FROM users WHERE id = ?', (user_id,)).fetchone()[0]

def get_total_users_count():
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    return total_users

async def get_all_users():
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    db.commit()
    return users
   
async def update_user_balance1(user_id, amount, operation):
    cur.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    current_balance = cur.fetchone()[0]

    if operation == "add":
        new_balance = current_balance + amount
    elif operation == "subtract":
        new_balance = current_balance - amount
    else:
        raise ValueError("Invalid operation. Use 'add' or 'subtract'.")

    cur.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
    db.commit()
    
async def update_user_total_deposit(user_id, amount):
    cur.execute("SELECT total_deposit FROM users WHERE id = ?", (user_id,))
    current_deposit = cur.fetchone()[0]

    new_deposit = current_deposit + amount
    cur.execute("UPDATE users SET total_deposit = ? WHERE id = ?", (new_deposit, user_id))
    db.commit()

    new_deposit = current_deposit + amount

    cur.execute("UPDATE users SET balance = ? WHERE id = ?", (new_deposit, user_id))
    db.commit()

async def update_user_balance(user_id, new_balance):
    cur.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
    db.commit()
    

async def get_investment_by_user_id(user_id):
    cur.execute("SELECT * FROM investments WHERE user_id = ?", (user_id,))
    investment = cur.fetchone()
    return investment


async def update_investment_amount(investment_id, new_amount):
    cur.execute("UPDATE investments SET investment_amount = ? WHERE id = ?", (new_amount, investment_id))
    db.commit()
    

    
async def update_referral_deposit(user_id, amount):
    cur.execute("UPDATE users SET referral_deposit = referral_deposit + ? WHERE id = ?", (amount, user_id))
    db.commit()  
    
async def update_broker_balance(user_id, new_broker_balance):
    cur.execute("UPDATE users SET broker_balance = ? WHERE id = ?", (new_broker_balance, user_id))
    db.commit()
    
async def update_subscription_status(user_id, new_status):
    cur.execute("UPDATE users SET subscription_status = ? WHERE id = ?", (new_status, user_id))
    db.commit()

async def update_total_invest(user_id, new_total_invest):
    cur.execute("UPDATE users SET total_invest = ? WHERE id = ?", (new_total_invest, user_id))
    db.commit()

async def update_earnings(user_id, new_earnings):
    cur.execute("UPDATE users SET earnings = ? WHERE id = ?", (new_earnings, user_id))
    db.commit()
    
    
async def get_user_by_id(user_id):
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    return user



#Отзывы
def add_review(user_id, username, text, photo_id):
    cur.execute("INSERT INTO reviews (user_id, username, text, photo_id) VALUES (?, ?, ?, ?)", (user_id, username, text, photo_id))
    db.commit()

def get_review_by_id(review_id):
    cur.execute("SELECT * FROM reviews WHERE id = ?", (review_id,))
    return cur.fetchone()

def get_review_count():
    cur.execute("SELECT COUNT(*) FROM reviews")
    return cur.fetchone()[0]

    
# Очистка бд
def clear_database():
    cur.execute("DELETE FROM numbers_table")
    db.commit()
    
    
# Добавление инвестиции
async def add_investment(user_id, investment_amount, investment_term, daily_income, interest_rate, start_date, end_date, investment_type):
    cur.execute("INSERT INTO investments (user_id, investment_amount, investment_term, daily_income, interest_rate, start_date, end_date, investment_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, investment_amount, investment_term, daily_income, interest_rate, start_date, end_date, investment_type))
    db.commit()

# Получение всех активных инвестиций пользователя
async def get_active_investments(user_id):
    cur.execute("SELECT * FROM investments WHERE user_id=? AND end_date > date('now')", (user_id,))
    return cur.fetchall()

# Обновление статуса инвестиции после истечения срока
async def update_investment_status(investment_id, end_date):
    cur.execute("UPDATE investments SET end_date=? WHERE id=?", (end_date, investment_id))
    db.commit()

# Получение срочных инвестиций пользователя
async def get_user_term_investments(user_id):
    cur.execute("SELECT * FROM investments WHERE user_id=? AND investment_type='term' AND end_date > date('now')", (user_id,))
    return cur.fetchall()

# Получение пользователей с активными инвестициями
async def get_users_with_active_investments():
    cur.execute("SELECT DISTINCT user_id, daily_income as daily_earning FROM investments WHERE end_date > date('now')")
    return cur.fetchall()

# Получение инвестиций с указанным датой окончания
async def get_investments_with_end_date():
    cur.execute("SELECT * FROM investments WHERE end_date > date('now')")
    return cur.fetchall()

async def delete_investment(investment_id: int):
    query = "DELETE FROM investments WHERE id = ?"
    cur.execute(query, (investment_id,))
    db.commit()
    
async def get_term_investments(user_id):
    cur.execute("SELECT * FROM investments WHERE user_id=? AND end_date > date('now') AND investment_type='term'", (user_id,))
    return cur.fetchall()

def get_interest_rate(user_id):
    cur.execute("SELECT interest_rate FROM investments WHERE user_id=? AND end_date > date('now') AND investment_type='term'", (user_id,))
    return cur.fetchall()


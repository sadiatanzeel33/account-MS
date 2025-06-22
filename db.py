import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "account_management.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT NOT NULL,
            email TEXT
        )
    """)

    # Accounts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            user_id INTEGER PRIMARY KEY,
            balance REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Transactions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def register_user(username, password, email):
    hashed_pw = generate_password_hash(password)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                  (username, hashed_pw, email))
        conn.commit()

        user_id = c.lastrowid
        c.execute("INSERT INTO accounts (user_id, balance) VALUES (?, ?)", (user_id, 0))
        conn.commit()

        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user_by_username(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user


def get_account_balance(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT balance FROM accounts WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def update_balance(user_id, amount, txn_type, item_name=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT balance FROM accounts WHERE user_id = ?", (user_id,))
    current_balance = c.fetchone()[0]

    if txn_type in ["withdraw", "purchase"] and amount > current_balance:
        conn.close()
        return False

    if txn_type in ["withdraw", "purchase"]:
        new_balance = current_balance - amount
    elif txn_type == "deposit":
        new_balance = current_balance + amount
    else:
        conn.close()
        return False

    # Update balance
    c.execute("UPDATE accounts SET balance = ? WHERE user_id = ?", (new_balance, user_id))

    # Add transaction with description (if purchase)
    description = item_name if txn_type == "purchase" else None
    c.execute("""
        INSERT INTO transactions (user_id, type, amount, timestamp, description)
        VALUES (?, ?, ?, datetime('now'), ?)
    """, (user_id, txn_type, amount, description))

    conn.commit()
    conn.close()
    return True


def get_transaction_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT type, amount, timestamp, description
        FROM transactions
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))
    transactions = c.fetchall()
    conn.close()
    return transactions

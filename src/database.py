import sqlite3
from pathlib import Path
import pandas as pd
from src.utils import DB_PATH

def connect(db_path=None):
    path = Path(db_path or DB_PATH); path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)

def init_db(db_path=None):
    with connect(db_path) as con:
        con.execute("CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, description TEXT NOT NULL, category TEXT NOT NULL, amount REAL NOT NULL CHECK(amount > 0), payment_method TEXT NOT NULL, notes TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        con.execute("CREATE TABLE IF NOT EXISTS budgets (budget_id INTEGER PRIMARY KEY AUTOINCREMENT, year INTEGER NOT NULL, month INTEGER NOT NULL, category TEXT NOT NULL, amount REAL NOT NULL CHECK(amount > 0), created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(year, month, category))")

def get_transactions(db_path=None):
    init_db(db_path)
    with connect(db_path) as con: return pd.read_sql_query("SELECT transaction_id,date,description,category,amount,payment_method,notes,created_at FROM transactions ORDER BY date DESC, transaction_id DESC", con)

def add_transactions(df, db_path=None):
    init_db(db_path)
    cols=["date","description","category","amount","payment_method","notes"]
    with connect(db_path) as con: df[cols].to_sql("transactions", con, if_exists="append", index=False)
    return len(df)

def update_transaction(transaction_id, values, db_path=None):
    init_db(db_path)
    with connect(db_path) as con: con.execute("UPDATE transactions SET date=?,description=?,category=?,amount=?,payment_method=?,notes=? WHERE transaction_id=?", (*values, int(transaction_id)))

def delete_transaction(transaction_id, db_path=None):
    init_db(db_path)
    with connect(db_path) as con: con.execute("DELETE FROM transactions WHERE transaction_id=?", (int(transaction_id),))

def get_budgets(year, month, db_path=None):
    init_db(db_path)
    with connect(db_path) as con: return pd.read_sql_query("SELECT category,amount FROM budgets WHERE year=? AND month=?", con, params=(int(year),int(month)))

def save_budget(year, month, category, amount, db_path=None):
    init_db(db_path)
    with connect(db_path) as con: con.execute("INSERT INTO budgets(year,month,category,amount) VALUES(?,?,?,?) ON CONFLICT(year,month,category) DO UPDATE SET amount=excluded.amount", (int(year),int(month),str(category),float(amount)))

def delete_budget(year, month, category, db_path=None):
    init_db(db_path)
    with connect(db_path) as con: con.execute("DELETE FROM budgets WHERE year=? AND month=? AND category=?",(int(year),int(month),str(category)))

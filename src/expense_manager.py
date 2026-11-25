import pandas as pd
from src.database import get_transactions, add_transactions, update_transaction, delete_transaction
from src.data_cleaner import clean_transactions

def create_expense(record, db_path=None):
    df=clean_transactions(pd.DataFrame([record])); add_transactions(df,db_path); return df.iloc[0].to_dict()

def edit_expense(transaction_id, record, db_path=None):
    df=clean_transactions(pd.DataFrame([record])); row=df.iloc[0]
    update_transaction(transaction_id,[row.date,row.description,row.category,float(row.amount),row.payment_method,row.notes],db_path)

def remove_expense(transaction_id, db_path=None): delete_transaction(transaction_id,db_path)

def filtered_transactions(df, start=None, end=None, category=None, payment_method=None, search=None):
    out=df.copy()
    if not out.empty:
        out["date"] = pd.to_datetime(out["date"])
        if start is not None: out=out[out.date.dt.date >= start]
        if end is not None: out=out[out.date.dt.date <= end]
        if category and category != "All": out=out[out.category==category]
        if payment_method and payment_method != "All": out=out[out.payment_method==payment_method]
        if search: out=out[out.description.str.contains(search,case=False,na=False) | out.notes.str.contains(search,case=False,na=False)]
    return out

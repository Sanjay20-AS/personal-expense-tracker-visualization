import pandas as pd
from src.database import init_db,get_transactions,add_transactions,update_transaction,delete_transaction,get_budgets,save_budget,delete_budget
from src.data_cleaner import clean_transactions

def test_transaction_crud(tmp_path):
 db=str(tmp_path/'db.sqlite');init_db(db);df=clean_transactions(pd.DataFrame([{'date':'2026-01-01','description':'x','amount':10,'payment_method':'UPI'}]));add_transactions(df,db);rows=get_transactions(db);assert len(rows)==1;tid=int(rows.iloc[0].transaction_id);update_transaction(tid,['2026-01-02','edited','Food',12,'Cash','note'],db);assert get_transactions(db).iloc[0].amount==12;delete_transaction(tid,db);assert get_transactions(db).empty

def test_budget_crud(tmp_path):
 db=str(tmp_path/'db.sqlite');init_db(db);save_budget(2026,1,'Food',1000,db);assert get_budgets(2026,1,db).iloc[0].amount==1000;save_budget(2026,1,'Food',2000,db);assert get_budgets(2026,1,db).iloc[0].amount==2000;delete_budget(2026,1,'Food',db);assert get_budgets(2026,1,db).empty

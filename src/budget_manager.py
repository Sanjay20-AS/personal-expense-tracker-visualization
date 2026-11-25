from src.database import get_budgets, save_budget, delete_budget

def set_budget(year, month, category, amount, db_path=None):
    if float(amount)<=0: raise ValueError("Budget must be greater than zero")
    save_budget(year,month,category,amount,db_path)

def budgets_for_month(year,month,db_path=None): return get_budgets(year,month,db_path)

def remove_budget(year,month,category,db_path=None): delete_budget(year,month,category,db_path)

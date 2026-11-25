import pandas as pd
import numpy as np

def summary_metrics(df):
    total=float(df.amount.sum()) if not df.empty else 0.0
    count=int(len(df)); avg=total/count if count else 0.0
    cats=df.groupby("category").amount.sum() if count else pd.Series(dtype=float)
    highest=str(cats.idxmax()) if len(cats) else "—"
    daily=total/max(df.date.nunique(),1) if count else 0.0
    return {"total":total,"count":count,"average_transaction":avg,"highest_category":highest,"average_per_active_day":daily}

def category_summary(df):
    if df.empty: return pd.DataFrame(columns=["category","amount","share_pct"])
    out=df.groupby("category",as_index=False).amount.sum().sort_values("amount",ascending=False)
    total=out.amount.sum(); out["share_pct"]=(out.amount/total*100) if total else 0
    return out

def monthly_summary(df):
    if df.empty: return pd.DataFrame(columns=["month","amount"])
    work=df.copy(); work["date"]=pd.to_datetime(work.date); work["month"]=work.date.dt.to_period("M").astype(str)
    return work.groupby("month",as_index=False).amount.sum().sort_values("month")

def payment_summary(df):
    if df.empty:return pd.DataFrame(columns=["payment_method","amount"])
    return df.groupby("payment_method",as_index=False).amount.sum().sort_values("amount",ascending=False)

def daily_summary(df):
    if df.empty:return pd.DataFrame(columns=["date","amount"])
    w=df.copy();w["date"]=pd.to_datetime(w.date).dt.date;return w.groupby("date",as_index=False).amount.sum()

def budget_analysis(spending, budgets):
    spend=spending.groupby("category",as_index=False).amount.sum() if not spending.empty else pd.DataFrame(columns=["category","amount"])
    result=budgets.merge(spend,on="category",how="outer").fillna(0).rename(columns={"amount_x":"budget","amount_y":"actual"})
    if "budget" not in result: result["budget"]=0
    if "actual" not in result: result["actual"]=0
    result["remaining"]=result.budget-result.actual
    result["utilization_pct"]=np.where(result.budget>0,result.actual/result.budget*100, np.nan)
    result["status"]=np.where(result.actual>result.budget,"Exceeded",np.where(result.budget>0,"Within budget","No budget"))
    return result

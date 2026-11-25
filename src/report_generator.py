import pandas as pd
from src.analytics import category_summary, monthly_summary, payment_summary, summary_metrics

def monthly_report(df, year, month):
    if df.empty: selected=df.copy()
    else:
        dates=pd.to_datetime(df.date); selected=df[(dates.dt.year==int(year))&(dates.dt.month==int(month))].copy()
    metrics=summary_metrics(selected)
    return {"transactions":selected,"metrics":metrics,"categories":category_summary(selected),"monthly":monthly_summary(selected),"payments":payment_summary(selected)}

def export_csv(df): return df.to_csv(index=False).encode("utf-8")

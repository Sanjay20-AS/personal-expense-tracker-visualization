import pandas as pd
from src.analytics import summary_metrics, category_summary, monthly_summary, payment_summary, daily_summary, budget_analysis

def sample(): return pd.DataFrame([{'date':'2026-01-01','description':'a','category':'Food','amount':100,'payment_method':'UPI'},{'date':'2026-01-02','description':'b','category':'Bills','amount':200,'payment_method':'Cash'},{'date':'2026-02-01','description':'c','category':'Food','amount':300,'payment_method':'UPI'}])
def test_total(): assert summary_metrics(sample())['total']==600

def test_count(): assert summary_metrics(sample())['count']==3

def test_average(): assert summary_metrics(sample())['average_transaction']==200

def test_highest_category(): assert summary_metrics(sample())['highest_category']=='Food'

def test_category_summary_sorted(): assert category_summary(sample()).iloc[0].category=='Food'

def test_category_share_sum(): assert round(category_summary(sample()).share_pct.sum())==100

def test_monthly_two_rows(): assert len(monthly_summary(sample()))==2

def test_payment_total(): assert payment_summary(sample()).amount.sum()==600

def test_daily_rows(): assert len(daily_summary(sample()))==3

def test_empty_metrics(): assert summary_metrics(pd.DataFrame())['total']==0

def test_budget_analysis():
 b=pd.DataFrame([{'category':'Food','amount':250}]);s=sample();r=budget_analysis(s,b);food=r[r.category=='Food'].iloc[0];assert food.actual==400 and food.remaining==-150

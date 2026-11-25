import pandas as pd
import pytest
from src.data_cleaner import clean_transactions, likely_duplicates

def test_clean_valid_row():
 d=clean_transactions(pd.DataFrame([{'date':'2026-01-01','description':'Swiggy','amount':'100','payment_method':'UPI'}]))
 assert d.iloc[0].category=='Food' and d.iloc[0].amount==100

def test_optional_notes():
 d=clean_transactions(pd.DataFrame([{'date':'2026-01-01','description':'x','amount':1,'payment_method':'Cash'}]))
 assert d.iloc[0].notes==''

def test_bad_column_raises():
 with pytest.raises(ValueError): clean_transactions(pd.DataFrame([{'date':'2026-01-01','amount':1}]))
@pytest.mark.parametrize('amount',[0,-1,'bad',None])
def test_bad_amount(amount):
 with pytest.raises(ValueError): clean_transactions(pd.DataFrame([{'date':'2026-01-01','description':'x','amount':amount,'payment_method':'UPI'}]))

def test_bad_date():
 with pytest.raises(ValueError): clean_transactions(pd.DataFrame([{'date':'not-date','description':'x','amount':1,'payment_method':'UPI'}]))

def test_empty_description_rejected():
 with pytest.raises(ValueError): clean_transactions(pd.DataFrame([{'date':'2026-01-01','description':'','amount':1,'payment_method':'UPI'}]))

def test_unknown_category_maps_other():
 d=clean_transactions(pd.DataFrame([{'date':'2026-01-01','description':'unknown','amount':1,'payment_method':'UPI','category':'MadeUp'}]))
 assert d.iloc[0].category=='Other'

def test_unknown_payment_maps_other():
 d=clean_transactions(pd.DataFrame([{'date':'2026-01-01','description':'x','amount':1,'payment_method':'Wire'}]))
 assert d.iloc[0].payment_method=='Other'

def test_duplicate_detect():
 ex=pd.DataFrame([{'date':'2026-01-01','description':'Coffee','amount':50,'payment_method':'UPI'}]); inc=ex.copy()
 assert bool(likely_duplicates(ex,inc).iloc[0])

def test_duplicate_case_insensitive():
 ex=pd.DataFrame([{'date':'2026-01-01','description':'Coffee','amount':50,'payment_method':'UPI'}]);inc=pd.DataFrame([{'date':'2026-01-01','description':'coffee','amount':50,'payment_method':'upi'}])
 assert bool(likely_duplicates(ex,inc).iloc[0])

def test_empty_existing():
 inc=pd.DataFrame([{'date':'2026-01-01','description':'Coffee','amount':50,'payment_method':'UPI'}])
 assert not bool(likely_duplicates(pd.DataFrame(),inc).iloc[0])

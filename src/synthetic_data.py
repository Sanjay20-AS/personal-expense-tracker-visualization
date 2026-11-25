import numpy as np
import pandas as pd
from datetime import date
from src.utils import DEFAULT_CATEGORIES, PAYMENT_METHODS

DESCRIPTIONS={"Food":["Swiggy dinner","Zomato lunch","Grocery store","Cafe coffee","Restaurant meal"],"Transportation":["Uber ride","Bus ticket","Metro fare","Fuel purchase","Auto ride"],"Shopping":["Amazon purchase","Clothes shopping","Flipkart order","Mall purchase"],"Bills":["Electricity bill","Internet bill","Mobile recharge","Water bill"],"Education":["Course fee","Book purchase","Stationery","Online course"],"Health":["Apollo pharmacy","Doctor visit","Medicine purchase"],"Entertainment":["Movie ticket","Netflix subscription","Concert ticket","Game purchase"],"Housing":["Monthly rent","Home maintenance"],"Personal Care":["Salon visit","Haircut","Personal care items"],"Other":["Miscellaneous expense","Small purchase"]}
RANGES={"Food":(80,1500),"Transportation":(30,1200),"Shopping":(150,5000),"Bills":(200,5000),"Education":(100,6000),"Health":(100,3000),"Entertainment":(100,2500),"Housing":(5000,18000),"Personal Care":(100,1500),"Other":(50,2000)}

def generate_synthetic_data(n=500, seed=42, end_date=None):
    rng=np.random.default_rng(seed); end=end_date or date.today(); start=pd.Timestamp(end)-pd.Timedelta(days=365)
    dates=start+pd.to_timedelta(rng.integers(0,366,size=n),unit="D")
    categories=rng.choice(DEFAULT_CATEGORIES,size=n,p=[.22,.14,.12,.10,.08,.07,.08,.05,.04,.10])
    records=[]
    for i,cat in enumerate(categories):
        lo,hi=RANGES[cat]; amount=round(float(rng.uniform(lo,hi)),2)
        records.append({"date":dates[i].strftime("%Y-%m-%d"),"description":rng.choice(DESCRIPTIONS[cat]),"category":cat,"amount":amount,"payment_method":rng.choice(PAYMENT_METHODS[:-1]),"notes":"Synthetic sample transaction"})
    return pd.DataFrame(records)

import pandas as pd
from src.utils import DEFAULT_CATEGORIES, PAYMENT_METHODS
from src.categorizer import categorize
REQUIRED_COLUMNS = ["date", "description", "amount", "payment_method"]

def clean_transactions(data: pd.DataFrame, categorize_missing=True):
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
    df = data.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing: raise ValueError("Missing required columns: " + ", ".join(missing))
    if "category" not in df.columns: df["category"] = ""
    if "notes" not in df.columns: df["notes"] = ""
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["description"] = df["description"].fillna("").astype(str).str.strip()
    df["payment_method"] = df["payment_method"].fillna("Other").astype(str).str.strip()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["category"] = df["category"].fillna("").astype(str).str.strip()
    df["notes"] = df["notes"].fillna("").astype(str)
    invalid = df["date"].isna() | df["amount"].isna() | (df["amount"] <= 0) | (df["description"] == "")
    if invalid.any(): raise ValueError(f"Invalid data in {int(invalid.sum())} row(s): date, description and positive amount are required.")
    if categorize_missing:
        df.loc[df["category"].isin(["", "nan", "None"]), "category"] = df.loc[df["category"].isin(["", "nan", "None"]), "description"].map(categorize)
    df["category"] = df["category"].apply(lambda c: c if c in DEFAULT_CATEGORIES else "Other")
    df["payment_method"] = df["payment_method"].apply(lambda p: p if p in PAYMENT_METHODS else "Other")
    return df[["date", "description", "category", "amount", "payment_method", "notes"]]

def likely_duplicates(existing: pd.DataFrame, incoming: pd.DataFrame):
    keys = ["date", "description", "amount", "payment_method"]
    if existing.empty: return pd.Series(False, index=incoming.index)
    ex = existing.copy(); inc = incoming.copy()
    for frame in [ex, inc]:
        frame["date"] = frame["date"].astype(str)
        frame["description"] = frame["description"].astype(str).str.strip().str.lower()
        frame["amount"] = pd.to_numeric(frame["amount"])
        frame["payment_method"] = frame["payment_method"].astype(str).str.strip().str.lower()
    existing_keys = set(map(tuple, ex[keys].values.tolist()))
    return inc[keys].apply(lambda row: tuple(row) in existing_keys, axis=1)

from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "outputs" / "expenses.db"
DEFAULT_CATEGORIES = ["Food", "Transportation", "Shopping", "Bills", "Education", "Health", "Entertainment", "Housing", "Personal Care", "Other"]
PAYMENT_METHODS = ["UPI", "Cash", "Debit Card", "Credit Card", "Net Banking", "Other"]

def parse_date(value):
    return datetime.strptime(str(value), "%Y-%m-%d").date()

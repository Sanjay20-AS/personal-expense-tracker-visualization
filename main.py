from src.database import init_db
from src.utils import DB_PATH
from src.synthetic_data import generate_synthetic_data
from src.database import get_transactions, add_transactions
from src.data_cleaner import clean_transactions

def main():
    init_db()
    if get_transactions().empty:
        sample=clean_transactions(generate_synthetic_data(500))
        add_transactions(sample)
        print(f"Seeded {len(sample)} synthetic transactions into {DB_PATH}")
    else: print(f"Database ready: {DB_PATH}")
if __name__ == "__main__": main()

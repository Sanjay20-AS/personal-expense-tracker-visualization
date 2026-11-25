# Personal Expense Tracker with Data Visualization

A local Python expense analytics application with CSV import, manual expense entry, rule-based categorization, SQLite persistence, monthly budgets, interactive Streamlit dashboards and reports. Uses synthetic data only; no banking integrations.

## Features
- Transaction add/edit/delete and filters
- CSV upload preview, validation and likely-duplicate detection
- Keyword auto-categorization
- SQLite storage for expenses and budgets
- Dashboard KPI cards and Plotly charts
- Category, daily, monthly and payment-method analytics
- Overall and category budgets
- Monthly CSV reports and data exports
- Synthetic dataset generator (500 records)
- Notebook learning examples and Pytest suite

## Stack
Python 3.11+, Pandas, NumPy, SQLite, Streamlit, Plotly, Matplotlib, Seaborn, Pytest.

## Quick start (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
streamlit run app.py
```
Open the local URL Streamlit displays (normally http://localhost:8501).

## CSV schema
Required: `date`, `description`, `amount`, `payment_method`. Optional: `category`, `notes`. Dates use YYYY-MM-DD and amounts must be positive.

## Screenshots
Run the app and capture Dashboard, Transactions, Analytics and Budgets views. Save captures in `images/` and replace this section with Markdown image links before publishing.

## Tests
```powershell
python -m pytest -q
```

## Repository structure
`app.py` is the Streamlit interface; `src/` contains database, cleaning, categorization, analytics, budget and report modules; `data/` contains synthetic sample data; `notebooks/` contains exploratory examples; `tests/` contains automated tests.

## GitHub
1. Create a repository named `Personal-Expense-Tracker-Visualization`.
2. Keep `.gitignore` in place and never commit private transactions or secrets.
3. Run `git init`, `git add .`, `git commit -m "Build personal expense tracker"`.
4. Add your GitHub remote and push the main branch.
5. Add screenshots to `images/` and update README.

## Limitations and future work
Local-only, single-user demo; synthetic data; keyword categorization; no bank integrations or financial advice. Possible future work: customizable rules, PDF generation, optional authentication, ML categorization or cloud deployment.

## Disclaimer
For learning and personal record-keeping only. Not financial advice.

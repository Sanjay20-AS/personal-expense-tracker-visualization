# Architecture

CSV/manual input → validation and cleaning → rule-based categorization → SQLite → analytics → Streamlit dashboard, charts, budgets and reports.

Core tables: `transactions` and `budgets`. See modules in `src/`.

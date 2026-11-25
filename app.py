import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime

from src.database import init_db, get_transactions, add_transactions, get_budgets
from src.data_cleaner import clean_transactions, likely_duplicates
from src.categorizer import categorize
from src.utils import DEFAULT_CATEGORIES, PAYMENT_METHODS
from src.expense_manager import filtered_transactions, edit_expense, remove_expense, create_expense
from src.analytics import (
    summary_metrics,
    category_summary,
    monthly_summary,
    payment_summary,
    daily_summary,
    budget_analysis,
)
from src.budget_manager import set_budget, remove_budget
from src.report_generator import monthly_report, export_csv
from src.synthetic_data import generate_synthetic_data


st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide",
)

# -------------------- CUSTOM STYLING --------------------

st.markdown(
    """
    <style>

    /* Main background */
    [data-testid="stAppViewContainer"] {
        background: #080B12;
    }

    [data-testid="stHeader"] {
        background: rgba(8,11,18,0.92);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #101622;
        border-right: 1px solid #263244;
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    /* Main spacing */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #151D2B, #101622);
        border: 1px solid #29364A;
        padding: 18px 20px;
        border-radius: 16px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.18);
    }

    [data-testid="stMetricLabel"] p {
        color: #A8B5C7 !important;
        font-size: 14px;
    }

    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.85rem;
    }

    /* Bordered containers */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        border-color: #29364A !important;
        border-radius: 16px !important;
        background: rgba(17,24,39,0.48);
    }

    /* Charts */
    [data-testid="stPlotlyChart"] {
        border-radius: 12px;
    }

    /* Headings */
    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    /* Horizontal separators */
    hr {
        border-color: #263244;
    }

    /* Buttons */
    .stButton button,
    .stDownloadButton button {
        border-radius: 10px;
        border: 1px solid #2DD4BF;
        transition: 0.2s ease;
    }

    .stButton button:hover,
    .stDownloadButton button:hover {
        border-color: #5EEAD4;
        color: #5EEAD4;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid #29364A;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Inputs */
    div[data-baseweb="input"] {
        border-radius: 10px;
    }

    div[data-baseweb="select"] {
        border-radius: 10px;
    }

    /* Progress bars */
    [data-testid="stProgress"] {
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- INITIALIZATION --------------------

init_db()

if "import_message" not in st.session_state:
    st.session_state.import_message = ""


def money(x):
    return f"₹{float(x):,.2f}"


def load():
    return get_transactions()


def form_record(d, cat, amount, pay, notes):
    return {
        "date": d,
        "description": str(d),
        "category": cat,
        "amount": amount,
        "payment_method": pay,
        "notes": notes,
    }


# -------------------- SIDEBAR --------------------

st.sidebar.title("💰 Expense Tracker")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Transactions",
        "Import CSV",
        "Budgets",
        "Analytics",
        "Reports",
        "Settings",
    ],
)

st.sidebar.caption("Local personal finance analytics · No bank connections")

all_df = load()


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("📊 Expense Dashboard")

    today = date.today()

    year = st.sidebar.selectbox(
        "Year",
        sorted(
            set(
                pd.to_datetime(all_df.date).dt.year.tolist()
                + [today.year]
            )
        ) if not all_df.empty else [today.year],
        index=0,
    )

    month = st.sidebar.selectbox(
        "Month",
        list(range(1, 13)),
        index=today.month - 1,
        format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
    )

    selected = (
        all_df[
            pd.to_datetime(all_df.date).dt.year.eq(year)
            & pd.to_datetime(all_df.date).dt.month.eq(month)
        ]
        if not all_df.empty
        else all_df
    )

    m = summary_metrics(selected)
    budgets = get_budgets(year, month)

    overall = (
        budgets[budgets.category == "Overall"]
        if not budgets.empty
        else pd.DataFrame()
    )

    overall_budget = float(overall.amount.iloc[0]) if not overall.empty else 0

    remaining = overall_budget - m["total"] if overall_budget else None

    # -------------------- KPI CARDS --------------------

    cols = st.columns(4)

    metric_items = [
        ("Total spending", money(m["total"])),
        ("Transactions", m["count"]),
        ("Top category", m["highest_category"]),
        (
            "Budget remaining",
            money(remaining) if remaining is not None else "Not set",
        ),
    ]

    for col, (label, value) in zip(cols, metric_items):

        with col:

            with st.container(border=True):
                st.metric(label, value)

    # -------------------- BUDGET PROGRESS --------------------

    if overall_budget:

        st.markdown("### 🎯 Monthly budget")

        st.progress(
            min(m["total"] / overall_budget, 1.0),
            text=f"Overall budget used: {m['total'] / overall_budget * 100:.1f}%",
        )

    # -------------------- CHARTS --------------------

    c1, c2 = st.columns(2)

    cats = category_summary(selected)
    months = monthly_summary(all_df)
    pay = payment_summary(selected)

    with c1:

        with st.container(border=True):

            st.subheader("🍕 Category spending")

            if not cats.empty:

                fig = px.pie(
                    cats,
                    names="category",
                    values="amount",
                    hole=0.45,
                )

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=20, l=20, r=20),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            else:
                st.info("No expenses for this month.")

    with c2:

        with st.container(border=True):

            st.subheader("💳 Payment method")

            if not pay.empty:

                fig = px.bar(
                    pay,
                    x="payment_method",
                    y="amount",
                    labels={"amount": "Amount (₹)"},
                )

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=20, l=20, r=20),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            else:
                st.info("No payment data yet.")

    # -------------------- MONTHLY TREND --------------------

    with st.container(border=True):

        st.subheader("📈 Monthly spending trend")

        if not months.empty:

            fig = px.line(
                months,
                x="month",
                y="amount",
                markers=True,
                labels={"amount": "Amount (₹)"},
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=20, r=20),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:
            st.info("No spending trend available yet.")

    # -------------------- RECENT TRANSACTIONS --------------------

    with st.container(border=True):

        st.subheader("🧾 Recent transactions")

        st.dataframe(
            selected.sort_values("date", ascending=False).head(10),
            use_container_width=True,
            hide_index=True,
        )

    st.download_button(
        "📥 Download selected month transactions",
        export_csv(selected),
        file_name=f"transactions_{year}_{month:02}.csv",
        mime="text/csv",
    )


# =========================================================
# TRANSACTIONS
# =========================================================

elif page == "Transactions":

    st.title("🧾 Transactions")

    with st.expander("➕ Add an expense", expanded=True):

        with st.form("add_expense"):

            d = st.date_input("Date", value=date.today())

            desc = st.text_input(
                "Description",
                placeholder="e.g. Swiggy dinner",
            )

            suggestion = categorize(desc)

            cat = st.selectbox(
                "Category",
                DEFAULT_CATEGORIES,
                index=DEFAULT_CATEGORIES.index(suggestion),
            )

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                value=100.0,
                step=10.0,
            )

            pay = st.selectbox("Payment method", PAYMENT_METHODS)

            notes = st.text_input("Notes (optional)")

            submit = st.form_submit_button("Save expense")

            if submit:

                if not desc.strip():

                    st.error("Please enter a description.")

                else:

                    create_expense(
                        {
                            "date": d,
                            "description": desc,
                            "category": cat,
                            "amount": amount,
                            "payment_method": pay,
                            "notes": notes,
                        }
                    )

                    st.success("Expense saved.")
                    st.rerun()

    st.subheader("🔎 Search and filter")

    q = st.text_input("Search description or notes")

    cats = ["All"] + DEFAULT_CATEGORIES
    cat_filter = st.selectbox("Category filter", cats)

    pays = ["All"] + PAYMENT_METHODS
    pay_filter = st.selectbox("Payment filter", pays)

    if not all_df.empty:

        dates = pd.to_datetime(all_df.date)

        start = st.date_input(
            "Start date",
            dates.min().date(),
            key="tx_start",
        )

        end = st.date_input(
            "End date",
            dates.max().date(),
            key="tx_end",
        )

        view = filtered_transactions(
            all_df,
            start,
            end,
            cat_filter,
            pay_filter,
            q,
        )

        with st.container(border=True):

            st.dataframe(
                view,
                use_container_width=True,
                hide_index=True,
            )

        st.download_button(
            "📥 Export filtered CSV",
            export_csv(view),
            "filtered_transactions.csv",
            "text/csv",
        )

        st.caption("Edit/delete a record by transaction ID below.")

        ids = view.transaction_id.tolist() if "transaction_id" in view else []

        if ids:

            tid = st.selectbox("Select transaction ID", ids)

            row = view[view.transaction_id == tid].iloc[0]

            with st.container(border=True):

                with st.form("edit_tx"):

                    edate = st.date_input(
                        "Edit date",
                        pd.to_datetime(row.date).date(),
                    )

                    edesc = st.text_input(
                        "Edit description",
                        row.description,
                    )

                    ecat = st.selectbox(
                        "Edit category",
                        DEFAULT_CATEGORIES,
                        index=DEFAULT_CATEGORIES.index(row.category),
                    )

                    eamount = st.number_input(
                        "Edit amount",
                        min_value=0.01,
                        value=float(row.amount),
                    )

                    epay = st.selectbox(
                        "Edit payment",
                        PAYMENT_METHODS,
                        index=(
                            PAYMENT_METHODS.index(row.payment_method)
                            if row.payment_method in PAYMENT_METHODS
                            else 0
                        ),
                    )

                    enotes = st.text_input("Edit notes", row.notes)

                    save = st.form_submit_button("Update transaction")

                    if save:

                        edit_expense(
                            tid,
                            {
                                "date": edate,
                                "description": edesc,
                                "category": ecat,
                                "amount": eamount,
                                "payment_method": epay,
                                "notes": enotes,
                            },
                        )

                        st.success("Updated")
                        st.rerun()

            if st.button("🗑️ Delete selected transaction", type="secondary"):

                remove_expense(tid)
                st.success("Deleted")
                st.rerun()

    else:

        st.info("No transactions yet. Add one above or import CSV.")


# =========================================================
# IMPORT CSV
# =========================================================

elif page == "Import CSV":

    st.title("📥 Import CSV")

    st.write(
        "Required columns: date, description, amount, payment_method. "
        "Category and notes are optional."
    )

    st.code(
        "date,description,amount,payment_method,category,notes\n"
        "2026-01-03,Swiggy lunch,250,UPI,Food,Lunch"
    )

    uploaded = st.file_uploader("Choose CSV", type=["csv"])

    if uploaded:

        try:

            raw = pd.read_csv(uploaded)

            st.subheader("Preview")

            st.dataframe(
                raw.head(20),
                use_container_width=True,
            )

            cleaned = clean_transactions(raw)

            dup = likely_duplicates(all_df, cleaned)

            st.info(
                f"Validated {len(cleaned)} row(s); "
                f"likely duplicates: {int(dup.sum())}."
            )

            exclude = st.checkbox("Skip detected duplicates", value=True)

            if st.button("Import validated rows"):

                to_add = cleaned.loc[~dup] if exclude else cleaned

                add_transactions(to_add)

                st.success(f"Imported {len(to_add)} transaction(s).")

                st.rerun()

        except Exception as e:

            st.error(f"CSV validation failed: {e}")

    if st.button("Generate and import 500 synthetic sample transactions"):

        sample = clean_transactions(generate_synthetic_data(500))

        dups = likely_duplicates(all_df, sample)

        to_add = sample.loc[~dups]

        add_transactions(to_add)

        st.success(
            f"Added {len(to_add)} synthetic records "
            f"(skipped {int(dups.sum())} likely duplicates)."
        )

        st.rerun()


# =========================================================
# BUDGETS
# =========================================================

elif page == "Budgets":

    st.title("🎯 Budget management")

    today = date.today()

    year = st.selectbox(
        "Budget year",
        range(today.year - 2, today.year + 3),
        index=2,
    )

    month = st.selectbox(
        "Budget month",
        range(1, 13),
        index=today.month - 1,
        format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
    )

    with st.container(border=True):

        with st.form("budget_form"):

            category = st.selectbox(
                "Budget type/category",
                ["Overall"] + DEFAULT_CATEGORIES,
            )

            amount = st.number_input(
                "Monthly budget (₹)",
                min_value=1.0,
                value=5000.0,
            )

            save = st.form_submit_button("Save budget")

            if save:

                set_budget(year, month, category, amount)

                st.success("Budget saved.")

                st.rerun()

    budget = get_budgets(year, month)

    month_df = (
        all_df[
            pd.to_datetime(all_df.date).dt.year.eq(year)
            & pd.to_datetime(all_df.date).dt.month.eq(month)
        ]
        if not all_df.empty
        else all_df
    )

    if not budget.empty:

        st.subheader("📊 Budget summary")

        if "Overall" in budget.category.values:

            ob = float(budget[budget.category == "Overall"].amount.iloc[0])

            actual = float(month_df.amount.sum())

            cols = st.columns(2)

            with cols[0]:

                with st.container(border=True):
                    st.metric("Overall budget", money(ob))

            with cols[1]:

                with st.container(border=True):
                    st.metric("Actual spending", money(actual))

            st.progress(
                min(actual / ob, 1),
                text=f"{actual / ob * 100:.1f}% used",
            )

        catbud = budget[budget.category != "Overall"]

        if not catbud.empty:

            analysis = budget_analysis(month_df, catbud)

            with st.container(border=True):

                st.dataframe(
                    analysis,
                    use_container_width=True,
                    hide_index=True,
                )

            for _, r in analysis.iterrows():

                if r.budget > 0:

                    st.progress(
                        min(float(r.actual / r.budget), 1),
                        text=(
                            f"{r.category}: {money(r.actual)} / "
                            f"{money(r.budget)} "
                            f"({r.utilization_pct:.1f}%)"
                        ),
                    )

        with st.container(border=True):

            st.subheader("Saved budgets")

            st.dataframe(
                budget,
                use_container_width=True,
                hide_index=True,
            )

        delcat = st.selectbox(
            "Remove budget entry",
            budget.category.tolist(),
        )

        if st.button("Delete budget entry"):

            remove_budget(year, month, delcat)

            st.rerun()

    else:

        st.info("No budget entries for this month.")


# =========================================================
# ANALYTICS
# =========================================================

elif page == "Analytics":

    st.title("📈 Analytics")

    if all_df.empty:

        st.info("Add or import expenses to view analytics.")

    else:

        start = st.date_input(
            "Analysis start",
            pd.to_datetime(all_df.date).min().date(),
            key="an_start",
        )

        end = st.date_input(
            "Analysis end",
            pd.to_datetime(all_df.date).max().date(),
            key="an_end",
        )

        df = filtered_transactions(all_df, start, end)

        c1, c2 = st.columns(2)

        cats = category_summary(df)
        daily = daily_summary(df)
        pay = payment_summary(df)
        months = monthly_summary(df)

        with c1:

            with st.container(border=True):

                st.subheader("📊 Category distribution")

                if not cats.empty:

                    fig = px.bar(
                        cats,
                        x="category",
                        y="amount",
                        labels={"amount": "₹"},
                    )

                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

        with c2:

            with st.container(border=True):

                st.subheader("📅 Daily spending")

                if not daily.empty:

                    fig = px.area(
                        daily,
                        x="date",
                        y="amount",
                        labels={"amount": "₹"},
                    )

                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

        with st.container(border=True):

            st.subheader("💳 Payment methods")

            if not pay.empty:

                fig = px.bar(
                    pay,
                    x="payment_method",
                    y="amount",
                )

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

        with st.container(border=True):

            st.subheader("📈 Monthly comparison")

            if not months.empty:

                fig = px.bar(
                    months,
                    x="month",
                    y="amount",
                )

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

        with st.container(border=True):

            st.subheader("📋 Category share")

            st.dataframe(
                cats,
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# REPORTS
# =========================================================

elif page == "Reports":

    st.title("📑 Monthly reports")

    today = date.today()

    year = st.selectbox(
        "Report year",
        range(today.year - 5, today.year + 2),
        index=5,
    )

    month = st.selectbox(
        "Report month",
        range(1, 13),
        index=today.month - 1,
        format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
    )

    report = monthly_report(all_df, year, month)

    m = report["metrics"]

    cols = st.columns(3)

    for col, (label, value) in zip(
        cols,
        [
            ("Total", money(m["total"])),
            ("Transactions", m["count"]),
            ("Top category", m["highest_category"]),
        ],
    ):

        with col:

            with st.container(border=True):
                st.metric(label, value)

    with st.container(border=True):

        st.subheader("📊 Category totals")

        st.dataframe(
            report["categories"],
            use_container_width=True,
            hide_index=True,
        )

    with st.container(border=True):

        st.subheader("💳 Payment methods")

        st.dataframe(
            report["payments"],
            use_container_width=True,
            hide_index=True,
        )

    with st.container(border=True):

        st.subheader("🧾 Transactions")

        st.dataframe(
            report["transactions"],
            use_container_width=True,
            hide_index=True,
        )

    st.download_button(
        "📥 Download monthly transactions",
        export_csv(report["transactions"]),
        file_name=f"report_{year}_{month:02}_transactions.csv",
        mime="text/csv",
    )

    st.download_button(
        "📥 Download category summary",
        export_csv(report["categories"]),
        file_name=f"report_{year}_{month:02}_categories.csv",
        mime="text/csv",
    )

    st.markdown("---")

    with st.container(border=True):

        st.subheader("🖨️ Print-friendly view")

        st.write(
            "Use your browser's **Print** command (Ctrl+P) "
            "to save this report view as PDF."
        )


# =========================================================
# SETTINGS
# =========================================================

elif page == "Settings":

    st.title("⚙️ Settings and data tools")

    with st.container(border=True):

        st.write(
            "This app uses local SQLite storage. "
            "Currency display is currently INR (₹)."
        )

    st.subheader("🛠️ Data tools")

    with st.container(border=True):

        if st.button("Generate sample dataset CSV"):

            sample = generate_synthetic_data(500)

            st.download_button(
                "Download synthetic CSV",
                export_csv(sample),
                "sample_expenses_500.csv",
                "text/csv",
            )

        st.download_button(
            "📥 Backup all transactions to CSV",
            export_csv(all_df),
            "expense_database_backup.csv",
            "text/csv",
        )

    st.warning(
        "This application is a learning and record-keeping tool, "
        "not financial advice. Store only data you are comfortable "
        "keeping on this device."
    )
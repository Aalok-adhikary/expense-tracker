import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import xlsxwriter

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Kuber - Indian Finance Hub", 
    page_icon="💎", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_custom_styles():
    st.markdown("""
        <style>
        /* Main background and font */
        .main { background-color: #f0f2f6; font-family: 'Inter', sans-serif; }
        
        /* Glassmorphism Cards */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px 0 rgba(0,0,0,0.05);
            border: 1px solid rgba(255, 255, 255, 0.3);
            text-align: center;
        }
        
        /* Custom sidebar */
        section[data-testid="stSidebar"] {
            background-color: #0e1117;
            color: white;
        }
        
        /* Headers */
        h1, h2, h3 { color: #1e293b; font-weight: 700; }
        
        /* Buttons */
        .stButton>button {
            border-radius: 10px;
            height: 3rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Dataframes */
        [data-testid="stTable"] { border-radius: 15px; overflow: hidden; }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            font-weight: 600;
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- INITIALIZATION ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"

# Simulated DB Initialization
if 'expenses' not in st.session_state:
    dates = [datetime.now() - timedelta(days=x) for x in range(45)]
    categories = ["Food & Swiggy", "Transport/Petrol", "Rent", "EMI", "Utilities", "Amazon/Shopping", "Investment/SIP"]
    st.session_state.expenses = pd.DataFrame({
        'ID': range(45),
        'Date': pd.to_datetime([d.date() for d in dates]),
        'Category': [np.random.choice(categories) for _ in range(45)],
        'Amount': [np.random.uniform(200, 8000) for _ in range(45)],
        'Description': ["Monthly expense" for _ in range(45)]
    })

if 'budgets' not in st.session_state:
    st.session_state.budgets = {
        "Food & Swiggy": 15000,
        "Transport/Petrol": 8000,
        "Rent": 25000,
        "EMI": 20000,
        "Utilities": 5000,
        "Amazon/Shopping": 10000,
        "Investment/SIP": 30000
    }

# --- HELPER FUNCTIONS ---
def save_expense(date, category, amount, desc):
    df = st.session_state.expenses
    new_id = df['ID'].max() + 1 if not df.empty else 0
    new_row = pd.DataFrame([{
        'ID': new_id,
        'Date': pd.to_datetime(date),
        'Category': category,
        'Amount': amount,
        'Description': desc
    }])
    st.session_state.expenses = pd.concat([df, new_row], ignore_index=True)

def delete_expense(expense_id):
    st.session_state.expenses = st.session_state.expenses[st.session_state.expenses['ID'] != expense_id]

# --- PAGES ---

def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='text-align: center; padding-top: 50px;'>", unsafe_allow_html=True)
        st.title("💎 Kuber")
        st.subheader("Your Personal Wealth Guardian")
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            email = st.text_input("Email Address", placeholder="name@example.in")
            password = st.text_input("Password", type="password")
            if st.button("Access Dashboard"):
                if email and password:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Please enter credentials.")
            st.markdown("</div>", unsafe_allow_html=True)

def dashboard_tab():
    df = st.session_state.expenses
    current_month = datetime.now().month
    month_df = df[df['Date'].dt.month == current_month]
    
    total_spent = month_df['Amount'].sum()
    prev_month_spent = df[df['Date'].dt.month == (current_month - 1)]['Amount'].sum()
    
    # Hero Section
    st.markdown(f"## Monthly Overview: {datetime.now().strftime('%B %Y')}")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Spends", f"₹{total_spent:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with m2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        change = ((total_spent - prev_month_spent) / prev_month_spent * 100) if prev_month_spent > 0 else 0
        st.metric("vs Prev Month", f"{change:+.1f}%", delta_color="inverse")
        st.markdown("</div>", unsafe_allow_html=True)
    with m3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        top_cat = month_df.groupby('Category')['Amount'].sum().idxmax() if not month_df.empty else "N/A"
        st.metric("Top Category", top_cat)
        st.markdown("</div>", unsafe_allow_html=True)
    with m4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Invested", f"₹{month_df[month_df['Category'] == 'Investment/SIP']['Amount'].sum():,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Spending Trend (Last 30 Days)")
        trend = df.sort_values('Date').groupby('Date')['Amount'].sum().reset_index()
        fig = px.line(trend, x='Date', y='Amount', markers=True, template="plotly_white")
        fig.update_traces(line_color='#008CFF', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("Composition")
        fig = px.pie(month_df, values='Amount', names='Category', hole=0.5)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def ledger_tab():
    st.subheader("Transaction History")
    
    col_a, col_b = st.columns([1, 3])
    
    with col_a:
        st.markdown("#### Log Expense")
        with st.form("add_exp", clear_on_submit=True):
            d = st.date_input("Date")
            c = st.selectbox("Category", list(st.session_state.budgets.keys()) + ["Other"])
            a = st.number_input("Amount (₹)", min_value=1)
            de = st.text_input("Note")
            if st.form_submit_button("Add to Ledger"):
                save_expense(d, c, a, de)
                st.success("Added!")
                st.rerun()

    with col_b:
        search = st.text_input("🔍 Search transactions...", placeholder="Search description or category")
        df_display = st.session_state.expenses.copy()
        if search:
            df_display = df_display[df_display['Description'].str.contains(search, case=False) | df_display['Category'].str.contains(search, case=False)]
        
        # Display as table with ID for reference
        st.dataframe(df_display.sort_values('Date', ascending=False)[['Date', 'Category', 'Amount', 'Description', 'ID']], 
                     use_container_width=True, hide_index=True)
        
        exp_to_del = st.number_input("Enter ID to delete", min_value=0, step=1)
        if st.button("Delete Entry"):
            delete_expense(exp_to_del)
            st.warning(f"Deleted ID {exp_to_del}")
            st.rerun()

def budget_tab():
    st.subheader("Monthly Budget Planner")
    df = st.session_state.expenses
    current_month = datetime.now().month
    
    st.info("Set your monthly limits below and track your adherence.")
    
    cols = st.columns(2)
    for i, (cat, limit) in enumerate(st.session_state.budgets.items()):
        with cols[i % 2]:
            spent = df[(df['Category'] == cat) & (df['Date'].dt.month == current_month)]['Amount'].sum()
            remaining = limit - spent
            percent = min(100, int((spent / limit) * 100)) if limit > 0 else 0
            
            color = "green" if percent < 80 else "orange" if percent < 100 else "red"
            
            st.markdown(f"**{cat}**")
            st.progress(percent / 100)
            st.markdown(f"₹{spent:,.0f} / ₹{limit:,.0f} ({percent}%)")
            
            # Ability to update budget
            new_limit = st.number_input(f"New limit for {cat}", value=limit, step=500, key=f"bud_{cat}")
            st.session_state.budgets[cat] = new_limit

def report_tab():
    st.subheader("Data Export Center")
    df = st.session_state.expenses
    
    st.markdown("Download your financial data for offline tax filing or analysis.")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### CSV Report")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name=f"Kuber_Report_{datetime.now().date()}.csv", mime="text/csv")
        st.write("Best for importing into other financial tools.")

    with c2:
        st.markdown("#### Excel Report")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='All Transactions')
            # Summary sheet
            summary = df.groupby('Category')['Amount'].sum().reset_index()
            summary.to_excel(writer, index=False, sheet_name='Summary')
        excel_data = output.getvalue()
        st.download_button("📥 Download Excel", data=excel_data, file_name=f"Kuber_Full_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.write("Includes transaction logs and category summaries.")

# --- MAIN APP FLOW ---
apply_custom_styles()

if not st.session_state.authenticated:
    login_page()
else:
    # Sidebar Navigation
    with st.sidebar:
        st.title("💎 Kuber")
        st.write(f"Logged in as: **{st.session_state.user_email}**")
        st.divider()
        
        page = st.radio("Navigation", ["Dashboard", "My Ledger", "Budget Planner", "Reports"], label_visibility="collapsed")
        
        st.spacer = st.container()
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # Page Routing
    if page == "Dashboard":
        dashboard_tab()
    elif page == "My Ledger":
        ledger_tab()
    elif page == "Budget Planner":
        budget_tab()
    elif page == "Reports":
        report_tab()

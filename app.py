import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import json
import base64
from sklearn.linear_model import LinearRegression

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Smart Finance Hub", page_icon="💰", layout="wide")

def local_css():
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #4F46E5; color: white; }
        .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .card { background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .sidebar-content { padding: 20px; }
        </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
if 'expenses' not in st.session_state:
    # Seed some dummy data
    dates = [datetime.now() - timedelta(days=x) for x in range(30)]
    categories = ["Food", "Transport", "Rent", "Entertainment", "Utilities", "Shopping"]
    st.session_state.expenses = pd.DataFrame({
        'Date': pd.to_datetime([d.date() for d in dates]),
        'Category': [np.random.choice(categories) for _ in range(30)],
        'Amount': [np.random.uniform(10, 200) for _ in range(30)],
        'Description': ["Sample expense" for _ in range(30)]
    })

# --- GEMINI AI INTEGRATION ---
async def get_ai_advice(query, context_data):
    api_key = "" # Environment provides key
    system_prompt = "You are a world-class financial advisor AI. Analyze the user's spending data and provide actionable, encouraging advice."
    user_query = f"Here is my spending summary: {context_data}. Question: {query}"
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
    try:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
        # Implementing basic retry logic
        for delay in [1, 2, 4]:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
        return "The AI assistant is currently busy. Please try again in a moment."
    except Exception as e:
        return f"Error connecting to AI assistant: {str(e)}"

# --- UTILITY FUNCTIONS ---
def export_pdf(df):
    # Simplified PDF generation using a markdown-to-pdf style or placeholder logic
    # Real PDF generation in Streamlit often uses FPDF or ReportLab
    return "PDF Binary Data Placeholder"

def predict_future_expenses(df):
    if len(df) < 5:
        return None
    daily_totals = df.groupby('Date')['Amount'].sum().reset_index()
    daily_totals['DayCount'] = (daily_totals['Date'] - daily_totals['Date'].min()).dt.days
    
    X = daily_totals[['DayCount']]
    y = daily_totals['Amount']
    
    model = LinearRegression()
    model.fit(X, y)
    
    next_day = np.array([[daily_totals['DayCount'].max() + 1]])
    prediction = model.predict(next_day)[0]
    return max(0, prediction)

# --- PAGE COMPONENTS ---

def login_page():
    st.markdown("<h1 style='text-align: center;'>Smart Finance Hub</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Secure Access")
        email = st.text_input("Email Address", placeholder="hello@example.com")
        password = st.text_input("Password", type="password")
        if st.button("Sign In"):
            if email and password: # Simple validation for demo
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Please enter valid credentials.")
        st.markdown("</div>", unsafe_allow_html=True)

def sidebar_nav():
    with st.sidebar:
        st.markdown(f"### Welcome, \n**{st.session_state.user_email}**")
        st.divider()
        if st.button("📊 Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
        if st.button("💸 Add Expense"): st.session_state.page = "Add Expense"; st.rerun()
        if st.button("🤖 AI Assistant"): st.session_state.page = "AI Assistant"; st.rerun()
        if st.button("📥 Export Data"): st.session_state.page = "Export"; st.rerun()
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

def dashboard_view():
    st.title("Financial Overview")
    df = st.session_state.expenses
    
    # Top Stats
    total_spent = df['Amount'].sum()
    avg_spent = df['Amount'].mean()
    predicted = predict_future_expenses(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Monthly Spend", f"${total_spent:,.2f}", "+5.2%")
    col2.metric("Average per Transaction", f"${avg_spent:,.2f}")
    col3.metric("Predicted Tomorrow", f"${predicted:,.2f}" if predicted else "N/A", delta_color="inverse")
    
    st.markdown("---")
    
    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Spending by Category")
        fig = px.pie(df, values='Amount', names='Category', hole=.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Spending Trend")
        trend_df = df.groupby('Date')['Amount'].sum().reset_index()
        fig = px.area(trend_df, x='Date', y='Amount', line_shape='spline')
        fig.update_traces(fillcolor="rgba(79, 70, 229, 0.2)", line_color="#4F46E5")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Transactions")
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

def add_expense_view():
    st.title("Add New Transaction")
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("Date", datetime.now())
        category = col1.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Utilities", "Shopping", "Other"])
        amount = col2.number_input("Amount ($)", min_value=0.01, step=0.01)
        desc = col2.text_input("Description", placeholder="Dinner at Joe's")
        
        submitted = st.form_submit_button("Save Expense")
        if submitted:
            new_row = {'Date': pd.to_datetime(date), 'Category': category, 'Amount': amount, 'Description': desc}
            st.session_state.expenses = pd.concat([st.session_state.expenses, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Expense logged successfully!")

def ai_assistant_view():
    st.title("AI Financial Assistant")
    st.info("Ask our AI anything about your spending habits, budget planning, or saving tips.")
    
    chat_container = st.container()
    
    query = st.text_input("How can I help you today?", placeholder="Analyze my food spending for this month...")
    
    if query:
        # Prepare context
        summary = st.session_state.expenses.groupby('Category')['Amount'].sum().to_dict()
        with st.spinner("Consulting the experts..."):
            import asyncio
            # In a real streamlit env, we use synchronous calls or st.cache_data
            # For this example, we'll simulate the call
            advice = asyncio.run(get_ai_advice(query, json.dumps(summary)))
            st.markdown(f"<div class='card'>{advice}</div>", unsafe_allow_html=True)

def export_view():
    st.title("Data Management & Exports")
    df = st.session_state.expenses
    
    st.markdown("### Download Data")
    col1, col2, col3 = st.columns(3)
    
    # CSV
    csv = df.to_csv(index=False).encode('utf-8')
    col1.download_button("Download CSV", data=csv, file_name="expenses.csv", mime="text/csv")
    
    # Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_data = output.getvalue()
    col2.download_button("Download Excel", data=excel_data, file_name="expenses.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # PDF Placeholder
    col3.button("Download PDF (Coming Soon)", disabled=True)
    
    st.divider()
    st.markdown("### Database Maintenance")
    if st.button("Clear All Data", type="secondary"):
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        st.warning("All data cleared.")

# --- MAIN ROUTING ---
local_css()

if not st.session_state.authenticated:
    login_page()
else:
    sidebar_nav()
    if st.session_state.page == "Dashboard":
        dashboard_view()
    elif st.session_state.page == "Add Expense":
        add_expense_view()
    elif st.session_state.page == "AI Assistant":
        ai_assistant_view()
    elif st.session_state.page == "Export":
        export_view()
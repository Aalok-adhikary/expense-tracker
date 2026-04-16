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
st.set_page_config(page_title="Indian Smart Finance Hub", page_icon="🇮🇳", layout="wide")

def local_css():
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #008CFF; color: white; }
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
    # Seed some dummy data relevant to Indian spending
    dates = [datetime.now() - timedelta(days=x) for x in range(30)]
    categories = ["Food & Swiggy", "Transport/Petrol", "Rent", "OTT/Mobile Recharges", "Utilities", "Shopping/Amazon", "UPI Transfers"]
    st.session_state.expenses = pd.DataFrame({
        'Date': pd.to_datetime([d.date() for d in dates]),
        'Category': [np.random.choice(categories) for _ in range(30)],
        'Amount': [np.random.uniform(50, 5000) for _ in range(30)],
        'Description': ["Monthly expense" for _ in range(30)]
    })

# --- GEMINI AI INTEGRATION ---
async def get_ai_advice(query, context_data):
    api_key = "" # Environment provides key
    system_prompt = "You are an expert Indian Financial Advisor. Analyze the user's spending data in INR (₹) and provide advice relevant to Indian tax laws, savings schemes like PPF/ELSS, and local spending habits."
    user_query = f"Here is my Indian spending summary (all amounts in ₹): {context_data}. Question: {query}"
    
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
    try:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
        for delay in [1, 2, 4]:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
        return "The Indian AI assistant is currently busy. Please try again later."
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

# --- UTILITY FUNCTIONS ---
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
    st.markdown("<h1 style='text-align: center;'>🇮🇳 Indian Smart Finance Hub</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Login to Your Wallet")
        email = st.text_input("Email Address", placeholder="name@example.in")
        password = st.text_input("Password", type="password")
        if st.button("Secure Login"):
            if email and password:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Please enter your credentials.")
        st.markdown("</div>", unsafe_allow_html=True)

def sidebar_nav():
    with st.sidebar:
        st.markdown(f"### नमस्ते, \n**{st.session_state.user_email}**")
        st.divider()
        if st.button("📊 Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
        if st.button("💸 Add Expense"): st.session_state.page = "Add Expense"; st.rerun()
        if st.button("🤖 Finance Guru (AI)"): st.session_state.page = "AI Assistant"; st.rerun()
        if st.button("📥 Export Reports"): st.session_state.page = "Export"; st.rerun()
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

def dashboard_view():
    st.title("Indian Spending Insights")
    df = st.session_state.expenses
    
    # Top Stats
    total_spent = df['Amount'].sum()
    avg_spent = df['Amount'].mean()
    predicted = predict_future_expenses(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Monthly Spend", f"₹{total_spent:,.2f}")
    col2.metric("Avg Transaction", f"₹{avg_spent:,.2f}")
    col3.metric("Predicted Tomorrow", f"₹{predicted:,.2f}" if predicted else "N/A", delta_color="inverse")
    
    st.markdown("---")
    
    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Category Breakdown")
        fig = px.pie(df, values='Amount', names='Category', hole=.4, color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Daily Cash Flow")
        trend_df = df.groupby('Date')['Amount'].sum().reset_index()
        fig = px.area(trend_df, x='Date', y='Amount', line_shape='spline')
        fig.update_traces(fillcolor="rgba(0, 140, 255, 0.2)", line_color="#008CFF")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent UPI & Card Transactions")
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

def add_expense_view():
    st.title("Log a Transaction")
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("Transaction Date", datetime.now())
        category = col1.selectbox("Spending Category", 
            ["Food & Swiggy", "Transport/Petrol", "Rent", "OTT/Mobile Recharges", "Utilities", "Shopping/Amazon", "UPI Transfers", "Health", "Investment", "Other"])
        amount = col2.number_input("Amount (₹)", min_value=1.0, step=1.0)
        desc = col2.text_input("Transaction Note", placeholder="Paid via GPay/PhonePe")
        
        submitted = st.form_submit_button("Log in Ledger")
        if submitted:
            new_row = {'Date': pd.to_datetime(date), 'Category': category, 'Amount': amount, 'Description': desc}
            st.session_state.expenses = pd.concat([st.session_state.expenses, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Expense added to your Indian ledger!")

def ai_assistant_view():
    st.title("AI Finance Guru")
    st.info("Your AI assistant understands Indian tax sections (80C), savings schemes, and local cost of living.")
    
    query = st.text_input("Ask about your budget or Indian taxes:", placeholder="How can I save more under 80C based on my spending?")
    
    if query:
        summary = st.session_state.expenses.groupby('Category')['Amount'].sum().to_dict()
        with st.spinner("Analyzing your finances..."):
            import asyncio
            advice = asyncio.run(get_ai_advice(query, json.dumps(summary)))
            st.markdown(f"<div class='card'>{advice}</div>", unsafe_allow_html=True)

def export_view():
    st.title("Generate Financial Reports")
    df = st.session_state.expenses
    
    st.markdown("### Download Transactions")
    col1, col2 = st.columns(2)
    
    # CSV
    csv = df.to_csv(index=False).encode('utf-8')
    col1.download_button("Download as CSV", data=csv, file_name="indian_expenses.csv", mime="text/csv")
    
    # Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Expenses')
    excel_data = output.getvalue()
    col2.download_button("Download as Excel (xlsx)", data=excel_data, file_name="indian_expenses.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    st.divider()
    if st.button("Reset Entire Ledger", type="secondary"):
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        st.warning("All records deleted.")

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

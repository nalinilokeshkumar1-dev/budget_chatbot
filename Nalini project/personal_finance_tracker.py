import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random
import plotly.graph_obj
import google.generativeai as genai

genai.configure(api_key=st.secrets["gemini"]["api_key"])


# ---------- Helper Functions ----------
def ai_categorize(description):
    mapping = {
        "housing": "Housing",
        "rent": "Housing",
        "mortgage": "Housing",
        "food": "Food",
        "grocery": "Food",
        "restaurant": "Food",
        "meal": "Food",
        "car": "Transportation",
        "uber": "Transportation",
        "bus": "Transportation",
        "train": "Transportation",
        "movie": "Entertainment",
        "game": "Entertainment",
        "concert": "Entertainment",
        "subscription": "Subscriptions",
        "eth": "Crypto Investment",
        "btc": "Crypto Investment",
        "gas": "Sustainable Spending",
        "flight": "Travel",
        "shopping": "Shopping",
        "doctor": "Health"
    }
    desc_low = description.lower()
    for k, v in mapping.items():
        if k in desc_low:
            return v
    categories = [
        'Housing', 'Food', 'Transportation', 'Entertainment', 'Savings',
        'Other', 'Crypto Investment', 'Sustainable Spending', 'Subscriptions',
        'Travel', 'Shopping', 'Health'
    ]
    return random.choice(categories)


def ai_predict_expenses(df, months=12):
    now = pd.Timestamp.now()
    trend = []
    for i in range(months):
        date = (now - pd.DateOffset(months=months - i - 1)).replace(day=1)
        mask = (pd.to_datetime(df['Date']).dt.month == date.month) & \
               (pd.to_datetime(df['Date']).dt.year == date.year)
        total = df[mask]['Amount'].sum() + np.random.uniform(10, 100)
        multiplier = 1 + 0.02 * i + np.random.uniform(-0.01, 0.02)
        trend.append(max(total * multiplier, 0))
    return trend


# --------- Session State Setup ----------
DEFAULT_BUDGET = {
    "Housing": 1000,
    "Food": 400,
    "Transportation": 200,
    "Entertainment": 150,
    "Savings": 300,
    "Subscriptions": 80,
    "Shopping": 120,
    "Health": 90,
    "Crypto Investment": 150,
    "Sustainable Spending": 60,
    "Other": 100,
    "Travel": 120
}

if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])
if "budget" not in st.session_state:
    st.session_state["budget"] = DEFAULT_BUDGET.copy()
if "income" not in st.session_state:
    st.session_state["income"] = 4000
if "goal" not in st.session_state:
    st.session_state["goal"] = ""
if "enable_crypto" not in st.session_state:
    st.session_state["enable_crypto"] = False
if "track_sustainability" not in st.session_state:
    st.session_state["track_sustainability"] = False

# ----- Custom CSS for Landing Page Button -----
st.markdown("""
<style>
.btn-download {
    background-color: #fdd835;
    color: #000 !important;
    padding: 15px 30px;
    border: none;
    border-radius: 30px;
    font-size: 18px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)


# --------- Home / Landing page ---------
def home_page():
    st.markdown("""
    <div style="
        display:flex; 
        flex-direction:column; 
        align-items:center; 
        justify-content:center; 
        height:40vh; 
        text-align:center; 
        font-family: Arial, sans-serif;
        ">
        <div style="font-weight:bold; font-size:48px; margin-bottom:10px;">📊 Expense AI</div>
        <h1 style="font-size:48px; margin:10px 0;">Take control of your finances</h1>
        <p style="font-size:18px; color: #555;">Spend less time worrying about money. Use our AI-powered expense tracker app.</p>

    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


# --------- About Us section in Omnicard style ---------
def about_us():
    st.markdown("---")
    st.header("About Us & The Expense AI Platform")

    st.markdown("""
    <style>
    .about-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 36px;
        margin: 30px 0 60px 0;
        align-items: stretch;
    }
    .about-card {
        background: white;
        border-radius: 18px;
        box-shadow: 0 4px 22px rgba(0,0,0,0.06);
        padding: 28px 24px 24px 24px;
        text-align: left;
        transition: box-shadow 0.3s, transform 0.3s;
        opacity: 0;
        transform: translateY(30px);
        animation: fadeInUp 0.7s forwards;
        border-left: 5px solid #ffd60a;
        min-height: 210px;
        display: flex;
        flex-direction: column;
    }
    /* Stagger animations */
    .about-card:nth-child(1) { animation-delay: 0.1s; }
    .about-card:nth-child(2) { animation-delay: 0.2s; }
    .about-card:nth-child(3) { animation-delay: 0.3s; }
    .about-card:nth-child(4) { animation-delay: 0.4s; }
    .about-card:nth-child(5) { animation-delay: 0.5s; }
    .about-card:nth-child(6) { animation-delay: 0.6s; }

    .about-card:hover {
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
        transform: translateY(-6px);
    }
    .card-icon {
        font-size: 40px;
        color: #ffd60a;
        margin-bottom: 12px;
    }
    .card-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
        color: black;
    }
    .card-desc {
        font-size: 16px;
        color: black;
        flex-grow: 1;
    }

    @keyframes fadeInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    @media (max-width: 600px) {
        .about-grid {
            grid-template-columns: 1fr;
            margin: 20px 0 40px 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Icons to use from Unicode emojis or fontawesome (can enhance with images too)
    cards = [
        {"icon": "🚀", "title": "Our Mission",
         "desc": "Empower individuals globally with AI-driven financial insights to manage money smarter."},
        {"icon": "👩‍💻", "title": "The Team",
         "desc": "A dedicated group of fintech experts, AI researchers, and software engineers passionate about innovation."},
        {"icon": "🧠", "title": "Technology",
         "desc": "Leveraging state-of-the-art AI, ML, and blockchain technologies for next-generation finance tools."},
        {"icon": "🔒", "title": "Privacy Focus",
         "desc": "User data is secured with the highest standards, ensuring privacy and transparency at all times."},
        {"icon": "🌱", "title": "Sustainability",
         "desc": "Committed to promoting sustainable financial habits and environmental responsibility."},
        {"icon": "🤝", "title": "Community",
         "desc": "Building strong partnerships with users and experts to continuously improve and innovate."},
    ]

    st.markdown('<div class="about-grid">', unsafe_allow_html=True)
    for card in cards:
        st.markdown(f"""
            <div class="about-card">
                <div class="card-icon">{card['icon']}</div>
                <div class="card-title">{card['title']}</div>
                <div class="card-desc">{card['desc']}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------- Finance Tracker Sections ---------------------------
def user_profile_section():
    st.header("👤 User Profile & Settings")
    inc = st.number_input("Monthly Net Income ($)", min_value=0, step=100, value=st.session_state["income"])
    goal = st.text_input("Your main goal (e.g. buy a house, invest, be carbon neutral)", value=st.session_state["goal"])
    enable_crypto = st.checkbox("Enable Crypto Tracking", value=st.session_state["enable_crypto"])
    track_sustainability = st.checkbox("Track Carbon Footprint", value=st.session_state["track_sustainability"])
    st.session_state.update(
        {"income": inc, "goal": goal, "enable_crypto": enable_crypto, "track_sustainability": track_sustainability})


def add_expense_section():
    st.header("➕ Add New Expense")
    with st.form("expense_form"):
        date = st.date_input("Date", value=datetime.date.today())
        desc = st.text_input("Description")
        amt = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
        auto_cat = st.checkbox("AI Categorize Expense", value=True)
        category = ai_categorize(desc) if auto_cat and desc else st.selectbox("Select Category",
                                                                              list(st.session_state["budget"].keys()))
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            if not desc:
                st.warning("Please provide a description.")
                st.stop()
            if amt <= 0:
                st.warning("Amount must be > 0.")
                st.stop()
            cat = category if not (auto_cat and desc) else ai_categorize(desc)
            new_row = {"Date": date, "Category": cat, "Description": desc, "Amount": amt}
            st.session_state["expenses"] = pd.concat([st.session_state["expenses"], pd.DataFrame([new_row])],
                                                     ignore_index=True)
            st.success(f"Added '{desc}' under {cat}")


def budget_adjustment_section():
    st.header("⚙️ Budget Adjustment")
    new_budget = {}
    for cat, val in st.session_state["budget"].items():
        new_budget[cat] = st.number_input(f"{cat} Budget ($)", min_value=0.0, value=float(val), format="%.2f",
                                          key=f"budget_{cat}")
    if st.button("Update Budget"):
        st.session_state["budget"] = new_budget
        st.success("Budget updated!")


def expenses_filter_section():
    st.header("📄 Expenses History & Filter")
    start = st.date_input("Start Date", value=pd.Timestamp.now().replace(day=1))
    end = st.date_input("End Date", value=pd.Timestamp.now())
    cat_filter = st.selectbox("Filter by Category", ["All"] + list(st.session_state["budget"].keys()))
    expenses = st.session_state["expenses"]
    filt_expenses = expenses[
        (pd.to_datetime(expenses["Date"]) >= pd.to_datetime(start)) &
        (pd.to_datetime(expenses["Date"]) <= pd.to_datetime(end))
        ]
    if cat_filter != "All":
        filt_expenses = filt_expenses[filt_expenses["Category"] == cat_filter]

    if filt_expenses.empty:
        st.info("No expenses found for the selected filters.")
    else:
        st.dataframe(filt_expenses.sort_values("Date", ascending=False))
        csv_data = filt_expenses.to_csv(index=False).encode()
        st.download_button("Download Filtered Data as CSV", data=csv_data, file_name="filtered_expenses.csv")


def budget_vs_spent_section():
    st.header("📊 Budget vs Spending & Trends")
    expenses = st.session_state["expenses"]
    month = pd.Timestamp.now().month
    year = pd.Timestamp.now().year
    this_month_exp = expenses[
        (pd.to_datetime(expenses["Date"]).dt.month == month) & (pd.to_datetime(expenses["Date"]).dt.year == year)]
    grouped = this_month_exp.groupby("Category")["Amount"].sum().reindex(st.session_state["budget"].keys(),
                                                                         fill_value=0)
    budget_vals = [st.session_state["budget"][cat] for cat in st.session_state["budget"].keys()]
    spent_vals = grouped.values

    fig = go.Figure(data=[
        go.Bar(name="Budget", x=list(st.session_state["budget"].keys()), y=budget_vals),
        go.Bar(name="Spent", x=list(st.session_state["budget"].keys()), y=spent_vals)
    ], layout=go.Layout(barmode='group', title="Budget vs Spending This Month", xaxis_title="Category",
                        yaxis_title="Amount ($)"))
    st.plotly_chart(fig, use_container_width=True)

    # Trend Prediction
    st.subheader("🔮 12-Month Predicted Expense Trend")
    months_line = pd.date_range(pd.Timestamp.now() - pd.DateOffset(months=11), periods=12, freq='M').strftime("%b %y")
    pred_vals = ai_predict_expenses(expenses)
    trend_fig = go.Figure(data=[
        go.Scatter(x=months_line, y=pred_vals, mode='lines+markers', name='Predicted Expenses')
    ], layout=go.Layout(title='12-Month Expense Forecast', xaxis_title='Month', yaxis_title='Amount ($)'))
    st.plotly_chart(trend_fig, use_container_width=True)


# Advanced futuristics and AI modules
def advanced_features():
    st.header("✨ Advanced & Futuristic Features")

    st.markdown("""
    - *AI-Driven Financial Digital Twin:* Personalized scenario modeling for financial goals.
    - *Generative AI Coach:* Conversational assistant for budgeting, investment, and more.
    - *Intent-Based Saving:* Automatic micro-savings based on your plans and log data.
    - *Health & Finance Sync:* Budget adjustments considering wellness data.
    - *Peer Benchmarking:* Compare your spending to peer groups and environments.
    - *Eco-Friendly Investing:* AI recommendations for climate-conscious portfolio adjustments.
    - *Gig Economy Optimization:* Help managing fluctuations in freelance income.
    - *Emotional Spending Alerts:* AI detects patterns and nudges smarter choices.
    - *AR/VR Financial Dashboards:* Future immersive visualization of your finances.
    - *Adaptive Bill Payments:* Smart scheduling and deferrals based on cash flow risk.
    """)


def future_insights():
    st.header("🚀 The Future of Financial AI")
    st.markdown("""
    Expect finance management to be…

    - Adaptive and personalized,
    - Emotionally intelligent and context aware,
    - Sustainably and socially conscious,
    - Integrated with decentralized finance and real-time data,
    - With seamless conversational AI at your side.
    """)
    st.caption("Your AI-powered financial companion for life, work, and beyond.")


# ---------- Chatbot Section ----------
def finance_chatbot_section():
    st.header("🤖 Gemini Finance Chatbot Assistant")
    model = genai.GenerativeModel("gemini-2.5-flash")

    if "gemini_chat" not in st.session_state:
        st.session_state["gemini_chat"] = model.start_chat(history=[
            {"role": "user", "parts": ["You are a helpful financial assistant. "
                                       "Answer only questions about budgeting, expenses, and finance."]}
        ])
        st.session_state["chat_log"] = []

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask your finance question...")
        send = st.form_submit_button("Send")

    if send and user_input.strip():
        response = st.session_state["gemini_chat"].send_message(user_input)
        st.session_state["chat_log"].append(("You", user_input))
        st.session_state["chat_log"].append(("AI", response.text))

    for sender, msg in st.session_state["chat_log"]:
        if sender == "You":
            st.markdown(f"<div style='background:black;padding:8px;border-radius:8px;'><b>You:</b> {msg}</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:black;padding:8px;border-radius:8px;'><b>AI:</b> {msg}</div>",
                        unsafe_allow_html=True)


# ------------- Main Function -------------
def main():
    st.set_page_config(page_title="AI Expense Tracker & Budget Planner", layout="wide")

    home_page()
    about_us()
    user_profile_section()
    add_expense_section()
    budget_adjustment_section()
    expenses_filter_section()
    budget_vs_spent_section()
    advanced_features()
    future_insights()
    finance_chatbot_section()


if __name__ == "__main__":
    main()

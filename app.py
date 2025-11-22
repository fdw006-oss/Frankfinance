import streamlit as st
from finance_logic import (
    suggested_emergency_fund,
    suggested_investing_rate,
    future_value_monthly
)
from ai_client import ask_coach

# ---- Card UI Component ----
def card(content):
    st.markdown(f"""
    <div style="
        background-color: #FFFFFF;
        border-radius: 14px;
        padding: 20px 25px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.07);
    ">
        {content}
    </div>
    """, unsafe_allow_html=True)


st.set_page_config(page_title="FrankFinance – AI Investing Coach")

st.title("💸 FrankFinance – Your First Investing Coach")
st.write("Learning to invest should be simple. Answer a few questions and I'll build your starter plan.")

# ------------------------------
#        ONBOARDING FORM
# ------------------------------
# ------------------------------
#       STEP 1 — ONBOARDING
# ------------------------------

st.header("Step 1 — Tell Me About Yourself")

card("""
### 👋 Welcome!  
Let’s create a personalized investing plan based on your income, savings, and long-term goals.
""")

with st.form("user_profile_form"):
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Your Age", min_value=16, max_value=80, value=20)
        monthly_income = st.number_input("Monthly Income ($)", min_value=0, value=0)

    with col2:
        can_invest = st.number_input("How much can you invest monthly? ($)", min_value=0, value=50)
        years_horizon = st.number_input("Years you want to invest", min_value=1, max_value=60, value=10)

    risk = st.selectbox("Risk Preference", ["Low", "Medium", "High"])
    goal = st.text_input("What’s your big financial goal? (Example: retirement, buying a house, etc.)")

    submitted = st.form_submit_button("Create My Plan 🚀")

if submitted:
    st.session_state["user_profile"] = {
        "age": age,
        "monthly_income": monthly_income,
        "can_invest": can_invest,
        "years_horizon": years_horizon,
        "risk": risk,
        "goal": goal,
    }

    emergency = suggested_emergency_fund(monthly_income)
    invest_rate = suggested_investing_rate(risk) * monthly_income
    projected_value = future_value_monthly(can_invest, 0.07, years_horizon)

    st.session_state["plan_summary"] = {
        "emergency_fund_target": emergency,
        "suggested_monthly_invest": invest_rate,
        "future_value_7pct": projected_value,
        "years_horizon": years_horizon,
    }

    st.success("Your plan is ready below! 👇")


# ------------------------------
#         SHOW PLAN
# ------------------------------
# ------------------------------
#         SHOW PLAN (CARD UI)
# ------------------------------
if "plan_summary" in st.session_state:
    plan = st.session_state["plan_summary"]
    profile = st.session_state["user_profile"]

    st.header("Step 2 — Your Starter Investing Plan")

    # ---- Summary Card ----
    card(f"""
    ### 📌 Your Personalized Investing Summary  
    **Emergency Fund Target:** ${plan['emergency_fund_target']:,.0f}  
    **Suggested Monthly Investing Amount:** ${plan['suggested_monthly_invest']:,.0f}  
    **Projected Value in {plan['years_horizon']} Years:** ${plan['future_value_7pct']:,.0f}  
    """)

    # ---- Growth Projection Card ----
    card("""
    ### 📈 Growth Projection  
    Below is how your investment could grow over time at **4%**, **7%**, and **10%** annual returns.
    """)

    years_list = list(range(0, plan["years_horizon"] + 1))

    df = pd.DataFrame({
        "Years": years_list,
        "4% Return (Conservative)": [
            future_value_monthly(plan["suggested_monthly_invest"], 0.04, y) for y in years_list
        ],
        "7% Return (Typical Market)": [
            future_value_monthly(plan["suggested_monthly_invest"], 0.07, y) for y in years_list
        ],
        "10% Return (Optimistic)": [
            future_value_monthly(plan["suggested_monthly_invest"], 0.10, y) for y in years_list
        ],
    })

    st.line_chart(df, x="Years")

    # ---- Notes Card ----
    card("""
    ### 📘 How to Interpret These Projections  
    - **4%**: Slow growth, conservative outlook  
    - **7%**: Typical long-term stock market average  
    - **10%**: Strong market performance  
    <br>
    These scenarios help you visualize possible outcomes — the goal is consistency, not timing the market.
    """)


# ------------------------------
#         CHATBOT
# ------------------------------
# ------------------------------
#       STEP 3 — AI CHAT
# ------------------------------

st.header("Step 3 — Ask the Investing Coach Anything")

card("""
### 💬 Chat With Your AI Investing Coach  
Ask anything — Roth IRAs, ETFs, saving strategies, side hustles, or next steps.
""")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Render chat messages inside a card
with st.container():
    for role, message in st.session_state["chat_history"]:
        if role == "user":
            st.markdown(f"""
            <div style="
                background-color: #E0F2FE;
                padding: 10px 15px;
                border-radius: 12px;
                margin: 8px 0;
                text-align: right;
                color: #0C4A6E;
            ">{message}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""



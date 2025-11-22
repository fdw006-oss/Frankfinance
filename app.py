import streamlit as st
import pandas as pd

from finance_logic import (
    suggested_emergency_fund,
    suggested_investing_rate,
    future_value_monthly
)
from ai_client import ask_coach


# ------------------------------
#        CARD UI COMPONENT
# ------------------------------
def card(content: str):
    st.markdown(
        f"""
<div style="
    background-color: #FFFFFF;
    border-radius: 14px;
    padding: 20px 25px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.07);
">
{content}
</div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------
#       PAGE SETTINGS
# ------------------------------
st.set_page_config(page_title="FrankFinance – AI Investing Coach")
st.title("💸 FrankFinance – Your First Investing Coach")
st.write("Learning to invest should be simple. Answer a few questions and I'll build your starter plan.")


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
    risk_map = {"Low": 1, "Medium": 2, "High": 3}
    numeric_risk = risk_map[risk]

    st.session_state["user_profile"] = {
        "age": age,
        "monthly_income": monthly_income,
        "can_invest": can_invest,
        "years_horizon": years_horizon,
        "risk": risk,
        "numeric_risk": numeric_risk,
        "goal": goal,
    }

    emergency = suggested_emergency_fund(monthly_income)
    invest_rate = suggested_investing_rate(numeric_risk) * monthly_income
    projected_value = future_value_monthly(can_invest, 0.07, years_horizon)

    st.session_state["plan_summary"] = {

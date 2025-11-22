import streamlit as st
from finance_logic import (
    suggested_emergency_fund,
    suggested_investing_rate,
    future_value_monthly
)
from ai_client import ask_coach

st.set_page_config(page_title="N150 – AI Investing Coach")

st.title("💸 N150 – Your First Investing Coach")
st.write("Learning to invest should be simple. Answer a few questions and I'll build your starter plan.")

# ------------------------------
#        ONBOARDING FORM
# ------------------------------
st.header("Step 1 — Tell me about you")

with st.form("onboarding_form"):
    age = st.number_input("Your age:", min_value=13, max_value=80, value=20)
    monthly_income = st.number_input("Monthly income (after tax):", min_value=0.0, value=2000.0)
    can_invest = st.number_input("How much can you invest each month (now)?", min_value=0.0, value=150.0)
    stability = st.selectbox("Income stability:", ["stable", "unstable"])
    goal = st.selectbox("Main financial goal:", [
        "I don't know yet",
        "Retirement",
        "Build wealth long-term",
        "Save for a car/house",
    ])
    risk = st.slider("Comfort with risk:", 1, 5, 3)

    submitted = st.form_submit_button("Generate My Investing Plan")

# ------------------------------
#       COMPUTE PLAN
# ------------------------------
if submitted:
    # Build user profile stored in session
    st.session_state["user_profile"] = {
        "age": age,
        "monthly_income": monthly_income,
        "can_invest": can_invest,
        "stability": stability,
        "goal": goal,
        "risk": risk,
    }

    efund_target = suggested_emergency_fund(monthly_income, stability)
    invest_rate = suggested_investing_rate(risk)
    suggested_monthly = max(can_invest, monthly_income * invest_rate)

    years = 30
    fv_7pct = future_value_monthly(suggested_monthly, 0.07, years)

    st.session_state["plan_summary"] = {
        "emergency_fund_target": efund_target,
        "suggested_monthly_invest": suggested_monthly,
        "years_horizon": years,
        "future_value_7pct": fv_7pct,
    }

    st.success("Your plan has been created!")

# ------------------------------
#         SHOW PLAN
# ------------------------------
if "plan_summary" in st.session_state:
    st.header("Step 2 — Your Starter Investing Plan")

    plan = st.session_state["plan_summary"]
    profile = st.session_state["user_profile"]

    st.subheader("📌 Key Recommendations")
    st.write(f"• **Emergency fund target:** ${plan['emergency_fund_target']:,.0f}")
    st.write(f"• **Suggested monthly investing:** ${plan['suggested_monthly_invest']:,.0f}")
    st.write(
        f"• **If you invest this for {plan['years_horizon']} years at ~7%:** "
        f"**${plan['future_value_7pct']:,.0f}**"
    )

    # Simple growth chart
    st.subheader("Projected Growth Over Time 📈")
    import pandas as pd

    years_list = list(range(0, plan["years_horizon"] + 1))
    values = [future_value_monthly(plan["suggested_monthly_invest"], 0.07, y) for y in years_list]
    df = pd.DataFrame({"Years": years_list, "Portfolio Value ($)": values})
    st.line_chart(df, x="Years", y="Portfolio Value ($)")

# ------------------------------
#         CHATBOT
# ------------------------------
st.header("Step 3 — Ask the Investing Coach Anything")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_msg = st.text_input("Ask a question:")

if st.button("Send") and user_msg:
    st.session_state["chat_history"].append({"role": "user", "content": user_msg})

    profile = st.session_state.get("user_profile", {})
    plan = st.session_state.get("plan_summary", {})

    reply = ask_coach(profile, plan, st.session_state["chat_history"])
    st.session_state["chat_history"].append({"role": "assistant", "content": reply})

for msg in st.session_state["chat_history"]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Coach:** {msg['content']}")


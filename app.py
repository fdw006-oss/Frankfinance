import streamlit as st
import pandas as pd
import math

from finance_logic import (
    suggested_emergency_fund,
    suggested_investing_rate,
    future_value_monthly,
)
from ai_client import ask_coach

# ------------------------------
#       FORCE FULL LIGHT MODE
# ------------------------------

def force_light_mode():
    css = """
    <style>
        /* Force full app background to light */
        html, body, .stApp {
            background-color: white !important;
            color: black !important;
        }

        /* Make all text black */
        *, p, span, div {
            color: black !important;
        }

        /* Chat bubble fixes */
        .bubble-user {
            background-color: #E0F2FE !important;
            color: #0C4A6E !important;
        }

        .bubble-assistant {
            background-color: #F3F4F6 !important;
            color: #1F2937 !important;
        }

        /* Make Streamlit input boxes light */
        input, textarea, select, .stTextInput input, .stNumberInput input {
            background-color: white !important;
            color: black !important;
            border: 1px solid #d0d0d0 !important;
        }

        /* Make dropdown options readable */
        div[role="listbox"] div {
            background-color: white !important;
            color: black !important;
        }

        /* Fix the form labels */
        label, .stSelectbox label, .stTextInput label, .stNumberInput label {
            color: black !important;
        }

        /* Fix Streamlit cards/containers */
        .element-container, .stContainer, .stCard {
            background-color: white !important;
        }

        /* Remove dark mode shading */
        [data-testid="stDecoration"] {
            display: none !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

force_light_mode()




# ------------------------------
#        HELPER FUNCTIONS
# ------------------------------

def card(html_content: str):
    """Renders a white card with safe HTML."""
    st.markdown(
        f"""
<div style="
    background-color: #FFFFFF;
    border-radius: 14px;
    padding: 20px 25px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.07);
">
    {html_content}
</div>
""",
        unsafe_allow_html=True,
    )


def years_to_target(monthly_contribution: float, annual_rate: float, target_value: float):
    """Approximate years needed to reach a target value with monthly contributions."""
    if monthly_contribution <= 0 or target_value <= 0:
        return None

    r = annual_rate / 12
    if r == 0:
        # No growth, just linear saving
        n_months = target_value / monthly_contribution
    else:
        ratio = target_value * r / monthly_contribution + 1
        if ratio <= 0:
            return None
        n_months = math.log(ratio) / math.log(1 + r)

    return n_months / 12  # years


def generate_plan_text(profile: dict, plan: dict, target_amount: float):
    """Create a plain-text summary of the user's plan for download."""
    lines = []
    lines.append("FrankFinance – Your Starter Investing Plan")
    lines.append("=" * 50)
    lines.append("")
    lines.append("YOUR PROFILE")
    lines.append("-" * 50)
    lines.append(f"Age: {profile.get('age', 'N/A')}")
    lines.append(f"Monthly Income: ${profile.get('monthly_income', 0):,.0f}")
    lines.append(f"Can Invest Monthly: ${profile.get('can_invest', 0):,.0f}")
    lines.append(f"Investing Horizon: {profile.get('years_horizon', 0)} years")
    lines.append(f"Risk Preference: {profile.get('risk', 'N/A')}")
    lines.append(f"Big Goal: {profile.get('goal', 'Not specified')}")
    lines.append("")

    lines.append("RECOMMENDED BASELINES")
    lines.append("-" * 50)
    lines.append(f"Emergency Fund Target: ${plan.get('emergency_fund_target', 0):,.0f}")
    lines.append(
        f"Suggested Monthly Investing Amount (based on income & risk): "
        f"${plan.get('suggested_monthly_invest', 0):,.0f}"
    )
    lines.append("")

    lines.append("YOUR PLAN PROJECTION (USING YOUR CONTRIBUTION)")
    lines.append("-" * 50)
    lines.append(
        f"Projected Value in {plan.get('years_horizon', 0)} years at 7%: "
        f"${plan.get('future_value_7pct_can', 0):,.0f}"
    )
    lines.append(
        f"Estimated FIRE Number (25× yearly expenses): "
        f"${plan.get('fire_number', 0):,.0f}"
    )
    lines.append(
        f"Progress toward FIRE if you follow this plan for "
        f"{plan.get('years_horizon', 0)} years: "
        f"{plan.get('fire_progress', 0)*100:,.1f}%"
    )
    lines.append("")

    if target_amount and target_amount > 0:
        ytg = years_to_target(
            profile.get("can_invest", 0),
            0.07,
            target_amount,
        )
        lines.append("GOAL TIMELINE ESTIMATE")
        lines.append("-" * 50)
        lines.append(
            f"Target portfolio amount: ${target_amount:,.0f}"
        )
        if ytg is not None:
            lines.append(
                f"At your current monthly investing amount, it may take about "
                f"{ytg:,.1f} years to reach this target (assuming 7% annual returns)."
            )
        else:
            lines.append(
                "With the current monthly investing amount, this goal is not reachable. "
                "Try increasing your monthly contribution."
            )
        lines.append("")

    lines.append("GENERAL REMINDERS")
    lines.append("-" * 50)
    lines.append("- Stay consistent; time in the market beats timing the market.")
    lines.append("- Revisit your plan yearly or when your income/expenses change.")
    lines.append("- Avoid high-interest debt before ramping up investing.")
    lines.append("- This is educational, not individualized financial advice.")

    return "\n".join(lines)


# ------------------------------
#       PAGE SETTINGS
# ------------------------------
st.set_page_config(
    page_title="FrankFinance – AI Investing Coach",
    layout="wide",
)

st.title("💸 FrankFinance – Your First Investing Coach")
st.write(
    "Learning to invest should be simple. Answer a few questions and I'll build your starter plan."
)


# ------------------------------
#           SIDEBAR
# ------------------------------
with st.sidebar:
    st.markdown("## 🧭 FrankFinance")
    st.markdown("Use the steps on the right to build your starter plan, then chat with the coach.")

    if "plan_summary" in st.session_state and "user_profile" in st.session_state:
        plan = st.session_state["plan_summary"]
        profile = st.session_state["user_profile"]

        st.markdown("---")
        st.markdown("### Quick Snapshot")
        st.metric(
            "Your Monthly Investing",
            f"${profile['can_invest']:,.0f}",
        )
        st.metric(
            "Projected Value (7%, horizon)",
            f"${plan['future_value_7pct_can']:,.0f}",
        )
        if plan["fire_number"] > 0:
            st.metric(
                "FIRE Progress",
                f"{plan['fire_progress']*100:,.1f}%",
            )

        # Allow simple target in sidebar for download
        default_target = 1_000_000
        target_amount_sidebar = st.number_input(
            "Target portfolio for download plan ($)",
            min_value=10_000,
            max_value=50_000_000,
            value=default_target,
            step=10_000,
        )
        st.session_state["target_amount_for_download"] = target_amount_sidebar

        plan_text = generate_plan_text(
            profile,
            plan,
            target_amount_sidebar,
        )

        st.download_button(
            "📥 Download Your Plan (TXT)",
            data=plan_text,
            file_name="frankfinance_plan.txt",
            mime="text/plain",
        )


# ------------------------------
#       STEP 1 — ONBOARDING
# ------------------------------
st.header("Step 1 — Tell Me About Yourself")

card("""
<h3>👋 Welcome!</h3>
<p>Let’s create a personalized investing plan based on your income, savings, and long-term goals.</p>
""")

with st.form("user_profile_form"):
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Your Age", min_value=16, max_value=80, value=20)
        monthly_income = st.number_input("Monthly Income ($)", min_value=0, value=0)

    with col2:
        can_invest = st.number_input(
            "How much can you invest monthly? ($)", min_value=0, value=50
        )
        years_horizon = st.number_input(
            "Years you want to invest", min_value=1, max_value=60, value=10
        )

    risk = st.selectbox("Risk Preference", ["Low", "Medium", "High"])
    goal = st.text_input(
        "What’s your big financial goal? (Example: retirement, buying a house, etc.)"
    )

    submitted = st.form_submit_button("Create My Plan 🚀")

if submitted:
    # Map risk string → numeric value
    risk_map = {"Low": 1, "Medium": 2, "High": 3}
    numeric_risk = risk_map[risk]

    # Store profile
    st.session_state["user_profile"] = {
        "age": age,
        "monthly_income": monthly_income,
        "can_invest": can_invest,
        "years_horizon": years_horizon,
        "risk": risk,
        "numeric_risk": numeric_risk,
        "goal": goal,
    }

    # Core numbers
    emergency = suggested_emergency_fund(monthly_income)
    invest_rate = suggested_investing_rate(numeric_risk) * monthly_income

    future_value_7pct_can = future_value_monthly(can_invest, 0.07, years_horizon)

    # FIRE approximation: 25x yearly expenses, assume 70% of income = expenses
    est_expenses = 0.7 * monthly_income
    annual_expenses = est_expenses * 12
    fire_number = annual_expenses * 25
    fire_progress = (
        future_value_7pct_can / fire_number if fire_number > 0 else 0.0
    )

    st.session_state["plan_summary"] = {
        "emergency_fund_target": emergency,
        "suggested_monthly_invest": invest_rate,
        "future_value_7pct_can": future_value_7pct_can,
        "years_horizon": years_horizon,
        "fire_number": fire_number,
        "fire_progress": fire_progress,
    }

    st.success("Your plan is ready below! 👇")


# ------------------------------
#       STEP 2 — INVESTING PLAN
# ------------------------------
if "plan_summary" in st.session_state and "user_profile" in st.session_state:

    plan = st.session_state["plan_summary"]
    profile = st.session_state["user_profile"]

    st.header("Step 2 — Your Starter Investing Plan")

    # Summary card
    card(f"""
<h3>📌 Your Personalized Investing Summary</h3>
<p><b>Emergency Fund Target:</b> ${plan['emergency_fund_target']:,.0f}</p>
<p><b>Suggested Monthly Investing Amount (based on income & risk):</b> ${plan['suggested_monthly_invest']:,.0f}</p>
<p><b>Your Chosen Monthly Investing Amount:</b> ${profile['can_invest']:,.0f}</p>
<p><b>Projected Value in {plan['years_horizon']} Years (at 7% using your contribution):</b> ${plan['future_value_7pct_can']:,.0f}</p>
<p><b>Estimated FIRE Number (25× yearly expenses):</b> ${plan['fire_number']:,.0f}</p>
<p><b>Progress toward FIRE if you stick to this plan:</b> {plan['fire_progress']*100:,.1f}% of your FIRE target</p>
""")

    # Growth projection – your contribution at 4/7/10%
    card("""
<h3>📈 Growth Projection (Your Plan)</h3>
<p>Below is how your investment could grow over time at <b>4%</b>, <b>7%</b>, and <b>10%</b> annual returns using <b>your monthly contribution</b>.</p>
""")

    years = list(range(0, plan["years_horizon"] + 1))

    df_growth = pd.DataFrame({
        "Years": years,
        "4% Return (Conservative)": [
            future_value_monthly(profile["can_invest"], 0.04, y) for y in years
        ],
        "7% Return (Typical Market)": [
            future_value_monthly(profile["can_invest"], 0.07, y) for y in years
        ],
        "10% Return (Optimistic)": [
            future_value_monthly(profile["can_invest"], 0.10, y) for y in years
        ],
    })

    st.line_chart(df_growth.set_index("Years"))

    # Comparison chart: your plan vs suggested
    card("""
<h3>⚖️ Your Plan vs Suggested Amount</h3>
<p>This compares investing your chosen amount vs the suggested amount at a 7% annual return.</p>
""")

    df_compare = pd.DataFrame({
        "Years": years,
        "Your Plan (7%)": [
            future_value_monthly(profile["can_invest"], 0.07, y) for y in years
        ],
        "Suggested Amount (7%)": [
            future_value_monthly(plan["suggested_monthly_invest"], 0.07, y) for y in years
        ],
    })

    st.line_chart(df_compare.set_index("Years"))

    # Time-to-goal calculator
    st.subheader("🎯 How Long Until You Reach a Target Amount?")

    target_amount_main = st.number_input(
        "Target portfolio amount ($)",
        min_value=10_000,
        max_value=50_000_000,
        value=1_000_000,
        step=10_000,
    )

    years_to_goal = years_to_target(profile["can_invest"], 0.07, target_amount_main)

    if years_to_goal is not None:
        card(f"""
<h3>⏱️ Timeline Estimate</h3>
<p>With a monthly contribution of <b>${profile['can_invest']:,.0f}</b> and a <b>7% annual return</b>, it may take roughly:</p>
<p><b>{years_to_goal:,.1f} years</b> to reach <b>${target_amount_main:,.0f}</b>.</p>
<p>This is only an estimate — real markets move up and down.</p>
""")
    else:
        card("""
<h3>⏱️ Timeline Estimate</h3>
<p>With the current monthly investing amount, this target can't be reached using this simple model. Try increasing your monthly investing amount.</p>
""")


# ------------------------------
#       STEP 3 — AI CHAT
# ------------------------------
st.header("Step 3 — Ask the Investing Coach Anything")

card("""
<h3>💬 Chat With Your AI Investing Coach</h3>
<p>Ask anything — Roth IRAs, ETFs, saving strategies, side hustles, or next steps.</p>
""")


# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# Render chat history
for role, message in st.session_state["chat_history"]:
    if role == "user":
        st.markdown(
            f"""
<div style="
    background-color: #E0F2FE;
    padding: 10px 15px;
    border-radius: 12px;
    margin: 8px 0;
    text-align: right;
    color: #0C4A6E;
    font-size: 16px;
">
    {message}
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
<div style="
    background-color: #F3F4F6;
    padding: 10px 15px;
    border-radius: 12px;
    margin: 8px 0;
    text-align: left;
    color: #1F2937;
    font-size: 16px;
">
    {message}
</div>
""",
            unsafe_allow_html=True,
        )


# Chat input form (does NOT call OpenAI directly)
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask a question:")
    send = st.form_submit_button("Send")

if send and user_input:
    # Store pending message then rerun
    st.session_state["pending_user_message"] = user_input
    st.rerun()

# After rerun: process pending message
if "pending_user_message" in st.session_state:
    user_msg = st.session_state.pop("pending_user_message")

    st.session_state["chat_history"].append(("user", user_msg))

    profile = st.session_state.get("user_profile", {})
    plan = st.session_state.get("plan_summary", {})

    with st.spinner("Coach is thinking..."):
        reply = ask_coach(profile, plan, st.session_state["chat_history"])

    st.session_state["chat_history"].append(("assistant", reply))

    st.rerun()



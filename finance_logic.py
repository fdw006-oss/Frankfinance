def suggested_emergency_fund(monthly_income, stability="stable"):
    months = 3 if stability == "stable" else 6
    est_expenses = 0.7 * monthly_income
    return months * est_expenses

def suggested_investing_rate(risk_level: int):
    base = 0.10
    bonus = (risk_level - 3) * 0.02
    return max(0.05, min(0.20, base + bonus))

def future_value_monthly(contribution, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return contribution * n
    return contribution * ((1 + r)**n - 1) / r

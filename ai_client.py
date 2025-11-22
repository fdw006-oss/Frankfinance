from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are FrankFinance, an AI financial education coach for young people.
You explain money, investing, and planning in simple, encouraging steps.
You DO NOT give personalized stock recommendations, crypto tips, or buy/sell instructions.
You may talk about broad asset classes (“stock funds”, “bond funds”, “index funds”) but never specific ticker symbols.
Always be friendly, clear, and supportive.
"""

def ask_coach(user_profile, plan_summary, messages):
    # Format messages for the OpenAI client
    formatted_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"User profile: {user_profile}"},
        {"role": "system", "content": f"Plan summary: {plan_summary}"},
    ]

    for msg in messages:
        formatted_messages.append(msg)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=formatted_messages,
        temperature=0.4
    )

    return completion.choices[0].message.content


import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_document(text):
    prompt = f"""You are an audit AI.
Analyze this document and return JSON:
- summary
- risk (Low/Medium/High)
- compliance issues
- audit score (0-100)

Document:
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return response.choices[0].message.content

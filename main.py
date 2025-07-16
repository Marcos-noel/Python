from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import csv
import asyncio
import datetime
import os

app = FastAPI(
    title="KEPROBA Export Assistant",
    description="Official KEPROBA AI Chat Assistant for export, trade, and market advisory.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memory and History
chat_history = []

# Request model
class QuestionRequest(BaseModel):
    question: str

# CSV fallback data
csv_data = {}
try:
    with open("keproba_data.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            q = row["question"].strip().lower()
            csv_data[q] = row["answer"].strip()
except FileNotFoundError:
    print("⚠️ keproba_data.csv not found. CSV fallback will be disabled.")

# Caching
cache = {}

# Rule-based Q&A
def get_rule_based_answer(q: str) -> str | None:
    rules = {
        "export procedures":"Export procedures in Kenya typically involve: Obtaining export licenses, Registering with KRA and KEPHIS if needed, Completing customs documentation and Submitting trade declarations through the Single Window System.",
        "trade agreements":"Kenya participates in: AfCFTA, COMESA, EAC Customs Union and AGOA.",
        "market opportunities":"Market opportunities include horticultural exports to the EU, textiles under AGOA, and processed foods in regional markets.",
        "contact":"Contact KEPROBA: find us on our Website: www.makeitkenya.go.ke, Phone: +254-20-2228534, Email: info@brand.ke",
        "start exporting":"To start exporting, register your business, obtain an export permit, ensure compliance with quality standards, and prepare customs documents.",
        "documents required":"Typical documents:Commercial Invoice, Packing List, Certificate of Origin, Export Permit, Customs Declaration, Bill of Lading or Airway Bill.",
        "importers of kenyan tea":"Major importers are :Pakistan, Egypt, UK, UAE and Russia.",
        "export incentives":"Export incentives include: Duty drawbacks, Export Promotion Programs, VAT zero-rating and Preferential market access.",
        "find buyers":"To find buyers: Join trade fairs, Use B2B platforms, Network via embassies and chambers of commerce.",
        "quality standards":"Horticultural exports must comply with GlobalGAP, phytosanitary certification, and destination market residue regulations.",
        "keproba services":"KEPROBA provides: Market intelligence, Exporter training, Trade promotion, Branding support.",
        "cost of exporting":"Export costs include: Production & packaging, Inland transport, Customs fees, Freight & insurance.",
        "exporting cultural artifacts":"Exporting cultural artifacts requires permits from: National Museums of Kenya and Kenya Wildlife Service.",
        "processing time":"Permit processing times: Standard goods: ~3–5 days and Controlled goods: ~2–3 weeks.",
        "hey": "hello, I am KEPROBA's assistant. How can I assist you?",
        "hello":"Hey I am M KEPROBA's EXPORT ASSISTANT, how may I help You?"
        
    }
    for keyword, response in rules.items():
        if keyword in q:
            return response
    return None

# Department routing
DEPARTMENT_CONTACTS = {
    "branding": "branding@keproba.go.ke",
    "investment": "investment@keproba.go.ke",
    "promotion": "promotion@keproba.go.ke",
    "market": "market@keproba.go.ke",
    "registration": "registration@keproba.go.ke",
}

def get_department_redirect(q: str) -> str | None:
    for keyword, contact in DEPARTMENT_CONTACTS.items():
        if keyword in q:
            return f"Your question seems best suited for the {keyword} department. Contact: {contact}"
    return None

# ChatGPT API fallback
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Replace with actual key or .env loading if needed

async def get_chatgpt_answer(query: str) -> str:
    if not OPENAI_API_KEY:
        return "ChatGPT fallback is not configured properly."
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 300
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"ChatGPT API error: {e}")
    return "I couldn’t get an answer at the moment. Please try again later."

# DuckDuckGo fallback
async def get_google_fallback(query: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            params = {"q": query, "hl": "en"}
            headers = {"User-Agent": "Mozilla/5.0"}
            response = await client.get("https://html.duckduckgo.com/html/", params=params, headers=headers)
            if response.status_code == 200:
                content = response.text
                start = content.find("<a rel=\"nofollow\" class=\"result__a\"")
                if start != -1:
                    snippet_start = content.find(">", start) + 1
                    snippet_end = content.find("</a>", snippet_start)
                    snippet = content[snippet_start:snippet_end]
                    return f"Based on an online search: {snippet.strip()}"
    except Exception as e:
        return "I’m currently unable to retrieve additional info from online sources."
    return "No online results found."

# Main endpoint
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    q = request.question.lower().strip()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Return from cache
    if q in cache:
        return {"answer": cache[q]}

    # Rule-based answer
    rule_answer = get_rule_based_answer(q)
    if rule_answer:
        chat_history.append({"q": q, "a": rule_answer, "time": timestamp})
        cache[q] = rule_answer
        return {"answer": rule_answer}

    # Department redirect
    department_redirect = get_department_redirect(q)
    if department_redirect:
        chat_history.append({"q": q, "a": department_redirect, "time": timestamp})
        cache[q] = department_redirect
        return {"answer": department_redirect}

    # CSV match
    for keyword, answer in csv_data.items():
        if keyword in q:
            chat_history.append({"q": q, "a": answer, "time": timestamp})
            cache[q] = answer
            return {"answer": answer}

    # ChatGPT fallback
    gpt_response = await get_chatgpt_answer(q)
    if gpt_response:
        chat_history.append({"q": q, "a": gpt_response, "time": timestamp})
        cache[q] = gpt_response
        return {"answer": gpt_response}

    # DuckDuckGo fallback
    online_answer = await get_google_fallback(q)
    chat_history.append({"q": q, "a": online_answer, "time": timestamp})
    cache[q] = online_answer
    return {"answer": online_answer}

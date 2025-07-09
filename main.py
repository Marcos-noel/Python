from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import csv
import asyncio

app = FastAPI(
    title="KEPROBA Export Assistant",
    description="Official KEPROBA AI Chat Assistant for export, trade, and market advisory.",
    version="2.0.0"  # Upgraded to advanced version
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QuestionRequest(BaseModel):
    question: str

# Load CSV fallback data
csv_data = {}
try:
    with open("keproba_data.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            q = row["question"].strip().lower()
            csv_data[q] = row["answer"].strip()
except FileNotFoundError:
    print("⚠️ keproba_data.csv not found. CSV fallback will be disabled.")

# Cache responses
cache = {}

# Rule-based answers
def get_rule_based_answer(q: str) -> str | None:
    rules = {
        "hey": "hello,  I am M KEPROBA's assistant how can I assist you?",
        "export procedures": "Export procedures in Kenya typically involve:\n- Obtaining export licenses\n- Registering with KRA and KEPHIS if needed\n- Completing customs documentation\n- Submitting trade declarations through the Single Window System.\nPlease consult KEPROBA for up-to-date guidelines.",
        "trade agreements": "Kenya participates in:\n- AfCFTA\n- COMESA\n- EAC Customs Union\n- AGOA.",
        "market opportunities": "Market opportunities include horticultural exports to the EU, textiles under AGOA, and processed foods in regional markets.",
        "contact": "Contact KEPROBA:\nWebsite: www.makeitkenya.go.ke\nPhone: +254-20-2228534\nEmail: info@brand.ke",
        "start exporting": "To start exporting, register your business, obtain an export permit, ensure compliance with quality standards, and prepare customs documents.",
        "documents required": "Typical documents:\n- Commercial Invoice\n- Packing List\n- Certificate of Origin\n- Export Permit\n- Customs Declaration\n- Bill of Lading or Airway Bill.",
        "importers of kenyan tea": "Major importers:\n- Pakistan\n- Egypt\n- UK\n- UAE\n- Russia.",
        "export incentives": "Export incentives include:\n- Duty drawbacks\n- Export Promotion Programs\n- VAT zero-rating\n- Preferential market access.",
        "find buyers": "To find buyers:\n- Join trade fairs\n- Use B2B platforms\n- Network via embassies and chambers of commerce.",
        "quality standards": "Horticultural exports must comply with GlobalGAP, phytosanitary certification, and destination market residue regulations.",
        "keproba services": "KEPROBA provides:\n- Market intelligence\n- Exporter training\n- Trade promotion\n- Branding support.",
        "cost of exporting": "Export costs include:\n- Production & packaging\n- Inland transport\n- Customs fees\n- Freight & insurance.",
        "exporting cultural artifacts": "Exporting cultural artifacts requires permits from:\n- National Museums of Kenya\n- Kenya Wildlife Service.",
        "processing time": "Permit processing times:\n- Standard goods: ~3–5 days\n- Controlled goods: ~2–3 weeks."
    }
    for keyword, response in rules.items():
        if keyword in q:
            return response
    return None

# Simple keyword-based department routing
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
            return f"Your question seems best suited for the {keyword} department. Please contact them via {contact}."
    return None

# Google fallback using DuckDuckGo scraping
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
                    return f"I couldn't find an exact answer, but based on an online search: {snippet.strip()}"
    except Exception as e:
        return "I'm currently unable to retrieve additional info from online sources."
    return "No online results found."

# API endpoint
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    q = request.question.lower().strip()

    if q in cache:
        return {"answer": cache[q]}

    rule_answer = get_rule_based_answer(q)
    if rule_answer:
        cache[q] = rule_answer
        return {"answer": rule_answer}

    department_redirect = get_department_redirect(q)
    if department_redirect:
        cache[q] = department_redirect
        return {"answer": department_redirect}

    for keyword, answer in csv_data.items():
        if keyword in q:
            cache[q] = answer
            return {"answer": answer}

    # Google fallback
    online_answer = await get_google_fallback(q)
    cache[q] = online_answer
    return {"answer": online_answer}

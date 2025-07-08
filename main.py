from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import csv

app = FastAPI(
    title="KEPROBA Export Assistant",
    description="API to answer export, trade, and market advisory questions",
    version="1.0.0"
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
    if "export procedures" in q:
        return (
            "Export procedures in Kenya typically involve:\n"
            "- Obtaining export licenses\n"
            "- Registering with KRA and KEPHIS if needed\n"
            "- Completing customs documentation\n"
            "- Submitting trade declarations through the Single Window System.\n"
            "Please consult KEPROBA for up-to-date guidelines."
        )

    if "trade agreements" in q:
        return (
            "Kenya participates in:\n"
            "- AfCFTA\n"
            "- COMESA\n"
            "- EAC Customs Union\n"
            "- AGOA."
        )

    if "market opportunities" in q:
        return (
            "Market opportunities include horticultural exports to the EU, textiles under AGOA, and processed foods in regional markets."
        )

    if "contact" in q or "reach keproba" in q:
        return (
            "Contact KEPROBA:\n"
            "Website: www.makeitkenya.go.ke\n"
            "Phone: +254-20-2228534\n"
            "Email: info@brand.ke"
        )

    if "start exporting" in q or "how do i export" in q:
        return (
            "To start exporting, register your business, obtain an export permit, ensure compliance with quality standards, and prepare customs documents."
        )

    if "documents required" in q or "export clearance" in q:
        return (
            "Typical documents:\n"
            "- Commercial Invoice\n"
            "- Packing List\n"
            "- Certificate of Origin\n"
            "- Export Permit\n"
            "- Customs Declaration\n"
            "- Bill of Lading or Airway Bill."
        )

    if "importers of kenyan tea" in q or "who buys kenyan tea" in q:
        return (
            "Major importers:\n"
            "- Pakistan\n"
            "- Egypt\n"
            "- UK\n"
            "- UAE\n"
            "- Russia."
        )

    if "export incentives" in q or "benefits for exporters" in q:
        return (
            "Export incentives include:\n"
            "- Duty drawbacks\n"
            "- Export Promotion Programs\n"
            "- VAT zero-rating\n"
            "- Preferential market access."
        )

    if "find buyers" in q or "international buyers" in q:
        return (
            "To find buyers:\n"
            "- Join trade fairs\n"
            "- Use B2B platforms\n"
            "- Network via embassies and chambers of commerce."
        )

    if "quality standards" in q or "horticultural exports" in q:
        return (
            "Horticultural exports must comply with GlobalGAP, phytosanitary certification, and destination market residue regulations."
        )

    if "keproba services" in q or "what is keproba" in q:
        return (
            "KEPROBA provides:\n"
            "- Market intelligence\n"
            "- Exporter training\n"
            "- Trade promotion\n"
            "- Branding support."
        )

    if "cost of exporting" in q or "calculate export cost" in q:
        return (
            "Export costs include:\n"
            "- Production & packaging\n"
            "- Inland transport\n"
            "- Customs fees\n"
            "- Freight & insurance."
        )

    if "exporting cultural artifacts" in q or "restrictions on exports" in q:
        return (
            "Exporting cultural artifacts requires permits from:\n"
            "- National Museums of Kenya\n"
            "- Kenya Wildlife Service."
        )

    if "processing time" in q or "export permit time" in q:
        return (
            "Permit processing times:\n"
            "- Standard goods: ~3–5 days\n"
            "- Controlled goods: ~2–3 weeks."
        )
    return None
        


# API endpoint
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    q = request.question.lower().strip()

    # Check cache
    if q in cache:
        return {"answer": cache[q]}

    # Rule-based answer
    rule_answer = get_rule_based_answer(q)
    if rule_answer:
        cache[q] = rule_answer
        return {"answer": rule_answer}

    # Check CSV fallback
    for keyword, answer in csv_data.items():
        if keyword in q:
            cache[q] = answer
            return {"answer": answer}


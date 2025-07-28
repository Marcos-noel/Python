from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from difflib import get_close_matches
import httpx
import csv
import asyncio
import datetime
import os
import pandas as pd
from fastapi.responses import JSONResponse
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk
from textblob import TextBlob
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
import threading

nltk.download("punkt")
nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()

def correct_typos(text):
    return str(TextBlob(text).correct())

def normalize_text(text):
    tokens = word_tokenize(text.lower())
    return " ".join([lemmatizer.lemmatize(token) for token in tokens])

app = FastAPI(
    title="KEPROBA Export Assistant",
    description="Official KEPROBA AI Chat Assistant for export, trade, and market advisory.",
    version="5.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_history = []

class QuestionRequest(BaseModel):
    question: str

csv_data = {}
try:
    with open("keproba_data.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            q = row["question"].strip().lower()
            csv_data[q] = row["answer"].strip()
except FileNotFoundError:
    print("⚠️ keproba_data.csv not found. CSV fallback will be disabled.")

cache = {}

UNANSWERED_FILE = "unanswered_queries.csv"

def log_unanswered(q_raw, q_corrected):
    with open(UNANSWERED_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), q_raw, q_corrected])

def send_unanswered_report():
    if not os.path.exists(UNANSWERED_FILE):
        return

    sender_email = "your_email@example.com"
    receiver_email = "admin@example.com"
    password = "your_password"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Weekly Unanswered Chatbot Questions"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with open(UNANSWERED_FILE, "r", encoding="utf-8") as f:
        html = f"<html><body><h2>Unanswered Queries</h2><pre>{f.read()}</pre></body></html>"

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

schedule.every().monday.at("08:00").do(send_unanswered_report)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

from fastapi import Request

@app.post("/chat")
async def chat(req: QuestionRequest):
    question = req.question.strip()
    corrected = correct_typos(question)
    normalized = normalize_text(corrected)

    if normalized in cache:
        return {"answer": cache[normalized], "source": "cache"}

    if normalized in csv_data:
        answer = csv_data[normalized]
        cache[normalized] = answer
        return {"answer": answer, "source": "csv"}

    close_matches = get_close_matches(normalized, csv_data.keys(), n=1, cutoff=0.75)
    if close_matches:
        match = close_matches[0]
        answer = csv_data[match]
        cache[normalized] = answer
        return {"answer": answer, "source": "fuzzy match"}

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post("https://api.openai.com/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                                             "Content-Type": "application/json"},
                                    json={
                                        "model": "gpt-4",
                                        "messages": [
                                            {"role": "system", "content": "You are a helpful export advisory assistant for Kenya."},
                                            {"role": "user", "content": question}
                                        ]
                                    })
            res.raise_for_status()
            answer = res.json()['choices'][0]['message']['content']
            cache[normalized] = answer
            return {"answer": answer, "source": "openai"}

    except Exception as e:
        log_unanswered(question, normalized)
        return JSONResponse(content={"answer": "Sorry, I couldn't understand your question. Please rephrase it."}, status_code=500)


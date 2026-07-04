"""
main.py
-------
This is the entry point of the backend. It creates the FastAPI app and defines
the /chat endpoint, which is the first working path of the whole system:
a citizen's question comes in, we ground it, send it to Gemini, and return the reply.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from app.services.grounding import build_prompt
from app.services.llm_client import get_answer

# Create the FastAPI application.
app = FastAPI(title="Gov Agent API")


# This describes the SHAPE of the data the /chat endpoint expects to receive.
# The citizen sends a JSON object with a single field: "question".
class ChatRequest(BaseModel):
    question: str


# This describes the SHAPE of what we send back: a JSON object with "reply".
class ChatResponse(BaseModel):
    reply: str


# A simple health-check endpoint. Visiting the root URL confirms the server runs.
@app.get("/")
def root():
    return {"status": "Gov Agent API is running"}


# The main endpoint. It receives a question, grounds it, asks Gemini, returns the reply.
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # 1. Build the grounded prompt from the citizen's question.
    prompt = build_prompt(request.question)

    # 2. Send the grounded prompt to Gemini and get the answer.
    answer = get_answer(prompt)

    # 3. Return the answer in the agreed shape.
    return ChatResponse(reply=answer)
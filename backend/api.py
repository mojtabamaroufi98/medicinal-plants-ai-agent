from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_agent


app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Medicinal Plant AI Agent API is running"
    }


class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_agent(request: QuestionRequest):

    answer = run_agent(
        request.question
    )

    return {
        "answer": answer
    }
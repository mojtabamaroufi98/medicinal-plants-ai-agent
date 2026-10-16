from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.plant_data import PLANTS

from agent import (
    run_agent,
    identify_plant,
    stream_agent_response,
    build_plant_profile,
    search_disease,
    generate_diet_plan,
)


app = FastAPI(
    title="Medicinal Plant AI Agent API",
    version="1.0.0",
)


# --------------------------------------------------
# Models
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


class ChatRequest(BaseModel):
    message: str
    history: list = []


# --------------------------------------------------
# General
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Medicinal Plant AI Agent API is running"
    }


# --------------------------------------------------
# Chat
# --------------------------------------------------

@app.post("/ask")
def ask_agent(request: QuestionRequest):
    answer = run_agent(request.question)

    return {
        "answer": answer
    }


@app.post("/api/chat")
def chat_agent(request: ChatRequest):
    answer = run_agent(request.message)

    return {
        "reply": answer,
        "structured": None
    }


@app.post("/ask-stream")
async def ask_agent_stream(request: QuestionRequest):
    return StreamingResponse(
        stream_agent_response(request.question),
        media_type="text/plain; charset=utf-8"
    )


# --------------------------------------------------
# Plant Identification
# --------------------------------------------------

@app.post("/api/identify")
async def identify_plant_endpoint(
    image: UploadFile = File(...)
):
    contents = await image.read()

    file_path = "uploaded_plant.jpg"

    with open(file_path, "wb") as file:
        file.write(contents)

    identification = identify_plant(file_path)

    plant = build_plant_profile(identification)

    if plant is None:
        return {
            "error": "متأسفانه اطلاعات کافی برای شناسایی گیاه پیدا نشد."
        }

    plants = identification.get("plants", [])

    confidence = 0.0

    if plants:
        confidence = plants[0].get(
            "confidence",
            0.0
        )

    return {
        "plant": plant,
        "confidence": confidence
    }
@app.get("/api/plants")
def get_plants():
    return PLANTS


@app.get("/api/plants/{plant_id}")
def get_plant(plant_id: str):
    for plant in PLANTS:
        if plant["id"] == plant_id:
            return plant

    return {
        "error": "گیاه موردنظر پیدا نشد."
    }

@app.get("/api/diseases/search")
def disease_search(q: str):
    query = q.strip()

    if not query:
        return {
            "id": "empty",
            "title": "",
            "about": "لطفاً نام بیماری یا مشکل موردنظر را وارد کنید.",
            "relatedPlants": [],
            "nutritionTips": [],
            "cautions": []
        }

    return search_disease(query)


class DietRequest(BaseModel):
    age: int | None = None
    gender: str | None = None
    heightCm: int | None = None
    weightKg: int | None = None
    goal: str
    activityLevel: str
    restrictions: str | None = None
    allergies: str | None = None


@app.post("/api/diet")
def diet(request: DietRequest):
    return generate_diet_plan(request.model_dump())
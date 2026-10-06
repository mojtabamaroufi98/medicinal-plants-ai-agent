
from pydantic import BaseModel
from agent import run_agent,identify_plant,stream_agent_response

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse

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
@app.post("/ask-stream")
async def ask_agent_stream(request: QuestionRequest):

    return StreamingResponse(
        stream_agent_response(request.question),
        media_type="text/plain; charset=utf-8"
    )
@app.post("/identify")
async def identify_plant_endpoint(
    image: UploadFile = File(...)
):
    contents = await image.read()

    with open("uploaded_plant.jpg", "wb") as file:
        file.write(contents)

    result = identify_plant("uploaded_plant.jpg")

    return result
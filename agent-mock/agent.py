from typing import List, Optional
import uuid

from fastapi import FastAPI, status
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

import uvicorn
import requests
import json


app = FastAPI()


@app.get("/manifest.json")
async def get_manifest() -> Response:
    return FileResponse("manifest.json")


@app.get("/logo.png")
async def get_logo() -> Response:
    return FileResponse("logo.png")


class SessionBase(BaseModel):
    locales: List[str]


class Session(SessionBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


@app.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(req: SessionBase) -> Session:
    ret = Session(**req.model_dump())
    return ret


class QuestionRequest(BaseModel):
    question: Optional[str] = ""


class AgentStep(BaseModel):
    action: str = "message"
    value: str


class QuestionResponse(BaseModel):
    steps: List[AgentStep]


@app.post("/sessions/{session_id}/questions", status_code=status.HTTP_200_OK)
async def answer_question(session_id: str, req: QuestionRequest) -> QuestionResponse:
    return QuestionResponse(steps=[AgentStep(value=req.question)])


def test_agent():
    print("🟢 Creando sesión...")
    session_url = "http://localhost:8000/sessions"
    session_payload = {"locales": ["es"]}

    session_response = requests.post(session_url, json=session_payload)
    if session_response.status_code != 201:
        print("❌ Error al crear sesión:", session_response.text)
        return

    session_data = session_response.json()
    session_id = session_data["id"]
    print(f"✅ Sesión creada: {session_id}")

    print("💬 Enviando pregunta al agente...")
    question_url = f"http://localhost:8000/sessions/{session_id}/questions"
    question_payload = {"question": "¿Que hora es?"}

    question_response = requests.post(question_url, json=question_payload)
    if question_response.status_code != 200:
        print("❌ Error al enviar pregunta:", question_response.text)
        return

    answer_data = question_response.json()
    print("\n📦 Respuesta completa del agente (raw):")
    print(json.dumps(answer_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import uvicorn
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_agent()
    else:
        uvicorn.run(
            "agent:app", host="0.0.0.0", port=8000, log_level="info", reload=True
        )

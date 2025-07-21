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


def get_keycloak_token():
    keycloak_url = (
        "http://localhost:8080/realms/browser-copilot/protocol/openid-connect/token"
    )
    data = {
        "grant_type": "password",
        "client_id": "browser-copilot",
        "username": "test",
        "password": "test",
    }
    response = requests.post(keycloak_url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def parse_sse_response(text: str):
    """
    Extrae y parsea el JSON contenido en la línea que empieza con 'data:'
    de una respuesta SSE (Server-Sent Events).
    """
    lines = text.splitlines()
    for line in lines:
        if line.startswith("data: "):
            json_str = line[len("data: ") :]
            return json.loads(json_str)
    raise ValueError("No se encontró línea de datos en la respuesta SSE")


def test_agent():
    print("🟢 Obteniendo token de Keycloak...")
    token = get_keycloak_token()
    headers = {"Authorization": f"Bearer {token}"}

    print("🟢 Creando sesión...")
    session_url = "http://localhost:8000/sessions"
    session_payload = {"locales": ["es"]}

    session_response = requests.post(session_url, json=session_payload, headers=headers)
    if session_response.status_code != 201:
        print("❌ Error al crear sesión:", session_response.text)
        return

    session_data = session_response.json()
    session_id = session_data["id"]
    print(f"✅ Sesión creada: {session_id}")

    print("💬 Enviando pregunta al agente...")
    question_url = f"http://localhost:8000/sessions/{session_id}/questions"
    question_payload = {"question": "¿Qué hora es?"}

    question_response = requests.post(
        question_url, json=question_payload, headers=headers
    )

    print(f"Status code question response: {question_response.status_code}")
    print(f"Content question response: {question_response.text!r}")

    if question_response.status_code != 200:
        print("❌ Error al enviar pregunta:", question_response.text)
        return

    try:
        answer_data = parse_sse_response(question_response.text)
    except Exception as e:
        print(f"❌ Error parseando la respuesta SSE: {e}")
        return

    print("\n📦 Respuesta completa del agente (parsed JSON):")
    print(json.dumps(answer_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_agent()
    else:
        uvicorn.run(
            "agent:app", host="0.0.0.0", port=8000, log_level="info", reload=True
        )

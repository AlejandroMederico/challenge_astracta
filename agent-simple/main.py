import dotenv
import os
from fastapi import FastAPI, status
from fastapi.responses import FileResponse, Response
from fastapi import HTTPException

import uvicorn

from models import SessionBase, Session, QuestionRequest
import agent_logic

app = FastAPI()


@app.get("/manifest.json")
async def get_manifest() -> Response:
    return FileResponse("manifest.json")


@app.get("/logo.png")
async def get_logo() -> Response:
    return FileResponse("logo.png")


@app.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(req: SessionBase) -> Session:
    return Session(**req.model_dump())


@app.post("/sessions/{session_id}/questions", status_code=status.HTTP_200_OK)
async def answer_question(session_id: str, req: QuestionRequest):
    agent = agent_logic.build_agent()
    try:
        response = agent_logic.process_question(agent, req.question or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response


if __name__ == "__main__":
    dotenv.load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)

import asyncio
import datetime
import enum
import logging
import re
import os
from typing import List, AsyncIterator, Optional
from pydantic import BaseModel

from langchain.agents import Tool, OpenAIFunctionsAgent, AgentExecutor
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.memory import ConversationBufferMemory, FileChatMessageHistory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.tools import tool
from langchain_community.chat_models import AzureChatOpenAI, ChatOpenAI
from openai import OpenAI, AzureOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from gpt_agent.domain import Session
from gpt_agent.file_system_repos import get_session_path

logging.getLogger("openai").level = logging.DEBUG

_BULLET_RE = re.compile(r"^\s*(?:\d+[\.\-\)]|[•\-])\s*", re.MULTILINE)
_RE_FINAL = re.compile(r"\bRESPUESTA\s+FINAL\s*:\s*", re.I)
_RE_REASONING = re.compile(r"\bRAZONAMIENTO\s*:\s*", re.I)


# just a sample tool to showcase how you can create your own set of tools
@tool
def clock() -> str:
    """gets the current time"""
    razonamiento = f"Ejecutando la herramienta clock para obtener información."
    return (
        f"RAZONAMIENTO:\n{razonamiento}\n\nRESPUESTA FINAL:\n{datetime.datetime.now()}"
    )


class AgentAction(enum.Enum):
    MESSAGE = "message"
    CLICK = "click"
    FILL = "fill"
    GOTO = "goto"
    COT = "cot"
    FINAL_ANSWER = "final_answer"


class AgentStep(BaseModel):
    action: AgentAction
    selector: Optional[str] = None
    value: Optional[str] = None


class AgentFlow(BaseModel):
    steps: List[AgentStep]

    @staticmethod
    def message(text: str) -> "AgentFlow":
        return AgentFlow(steps=[AgentStep(action=AgentAction.MESSAGE, value=text)])


# a sample tool to showcase how you can automate navigation in the browser
@tool(return_direct=True)
def contact_abstracta(full_name: str) -> str:
    """navigates to abstracta.us and fills the contact form with the given full name"""
    return AgentFlow(
        steps=[
            AgentStep(action=AgentAction.GOTO, value="https://abstracta.us"),
            AgentStep(
                action=AgentAction.CLICK, selector='xpath://a[@href="./contact-us"]'
            ),
            AgentStep(action=AgentAction.FILL, selector="#fullname", value=full_name),
            AgentStep(
                action=AgentAction.MESSAGE,
                value="I have filled the contact form with your name.",
            ),
        ]
    ).model_dump_json()


def dict_to_agent_flow(step_dict: dict) -> AgentFlow:
    action_map = {
        "cot": AgentAction.COT,
        "final_answer": AgentAction.FINAL_ANSWER,
        "message": AgentAction.MESSAGE,
        "click": AgentAction.CLICK,
        "fill": AgentAction.FILL,
        "goto": AgentAction.GOTO,
    }
    action_enum = action_map.get(step_dict["action"], AgentAction.MESSAGE)
    agent_step = AgentStep(
        action=action_enum,
        value=step_dict.get("value"),
        selector=step_dict.get("selector"),
    )
    return AgentFlow(steps=[agent_step])


SYSTEM_PROMPT = """
Eres un asistente IA experto.
Siempre que respondas, sigue EXACTAMENTE este formato:

RAZONAMIENTO:
<explicación paso a paso aquí>

RESPUESTA FINAL:
<respuesta para el usuario>

No añadas texto fuera de las secciones indicadas.
"""


class Agent:

    def __init__(self, session: Session):
        self._session = session
        message_history = FileChatMessageHistory(
            get_session_path(session.id) + "/chat_history.json"
        )
        self._memory = ConversationBufferMemory(
            memory_key="chat_history", chat_memory=message_history, return_messages=True
        )
        self._agent = self._build_agent(self._memory, [clock, contact_abstracta])

    def _build_agent(
        self, memory: ConversationBufferMemory, tools: List[Tool]
    ) -> AgentExecutor:
        llm = self._build_llm()
        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=SystemMessage(content=SYSTEM_PROMPT),
            extra_prompt_messages=[
                MessagesPlaceholder(variable_name=memory.memory_key)
            ],
        )
        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            return_intermediate_steps=False,
            max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "3")),
        )

    def _build_llm(self):
        temperature = float(os.getenv("TEMPERATURE"))
        base_url = os.getenv("OPENAI_API_BASE")
        if self._is_azure(base_url):
            return AzureChatOpenAI(
                deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME"),
                temperature=temperature,
                verbose=True,
                streaming=True,
            )
        else:
            return ChatOpenAI(
                model_name=os.getenv("MODEL_NAME"),
                temperature=temperature,
                verbose=True,
                streaming=True,
            )

    @staticmethod
    def _is_azure(base_url: str) -> bool:
        return base_url and ".openai.azure.com" in base_url

    def start_session(self):
        self._memory.chat_memory.add_user_message(
            "this is my locale: " + self._session.locales[0]
        )

    def transcript(self, audio_file_path: str) -> str:
        base_url = os.getenv("OPENAI_WHISPER_API_BASE", os.getenv("OPENAI_API_BASE"))
        api_key = os.getenv("OPENAI_WHISPER_API_KEY", os.getenv("OPENAI_API_KEY"))
        api_version = os.getenv(
            "OPENAI_WHISPER_API_VERSION", os.getenv("OPENAI_API_VERSION")
        )
        deployment_name = os.getenv(
            "AZURE_WHISPER_DEPLOYMENT_NAME", os.getenv("AZURE_DEPLOYMENT_NAME")
        )
        client = (
            AzureOpenAI(
                azure_endpoint=base_url,
                api_version=api_version,
                api_key=api_key,
                azure_deployment=deployment_name,
            )
            if self._is_azure(base_url)
            else OpenAI(base_url=base_url, api_key=api_key)
        )
        locale = self._session.locales[0]
        lang_separator_pos = locale.find("-")
        language = locale[0:lang_separator_pos] if lang_separator_pos >= 0 else locale
        ret = client.audio.transcriptions.create(
            model="whisper-1", file=open(audio_file_path, "rb"), language=language
        )
        return ret.text

    async def ask(self, question: str) -> AsyncIterator[AgentFlow | str]:
        callback = AsyncIteratorCallbackHandler()
        task = asyncio.create_task(
            self._agent.arun(input=question, callbacks=[callback])
        )
        resp = ""
        async for token in callback.aiter():
            resp += token
            # Si querés hacer streaming token a token, aquí puedes hacer yield token
            # yield token
        ret = await task

        response_text = ret if ret != resp else resp
        cleaned_text = Agent.clean_response_text(response_text)

        if "RAZONAMIENTO:" in cleaned_text and "RESPUESTA FINAL:" in cleaned_text:
            try:
                pasos = Agent.parse_response_to_actions(cleaned_text)
                yield AgentFlow(steps=pasos)
            except Exception as e:
                logging.exception("Error parsing structured response", exc_info=e)
                yield cleaned_text
        else:
            yield cleaned_text

    @staticmethod
    def parse_response_to_actions(text: str) -> List[dict]:
        steps = []
        parts = _RE_FINAL.split(text, maxsplit=1)
        if len(parts) == 2:
            cot_block, final_answer = parts
            cot_block = _RE_REASONING.sub("", cot_block).strip()
            cot_steps = Agent.split_numbered_cot(cot_block)
            for step_text in cot_steps:
                steps.append({"action": "cot", "value": step_text})
            steps.append({"action": "final_answer", "value": final_answer.strip()})
        else:
            steps.append({"action": "final_answer", "value": text.strip()})
        return steps

    @staticmethod
    def split_numbered_cot(cot_block: str) -> List[str]:
        lines = cot_block.splitlines()

        if len(lines) == 1:
            # Dividir el único texto por oraciones terminadas en punto y espacio
            steps = [s.strip() for s in re.split(r"\.\s+", lines[0]) if s.strip()]
            # Volver a agregar el punto al final de cada oración (excepto la última si ya lo tiene)
            steps = [s if s.endswith(".") else s + "." for s in steps]
            return steps

        steps, current = [], []
        for line in lines:
            if _BULLET_RE.match(line):
                if current:
                    steps.append(" ".join(current).strip())
                    current = []
                line = _BULLET_RE.sub("", line, count=1)
            current.append(line.strip())
        if current:
            steps.append(" ".join(current).strip())
        return [s for s in steps if s]

    @staticmethod
    def clean_response_text(raw_text: str) -> str:
        # Quita los prefijos 'data:' y espacios iniciales
        lines = raw_text.splitlines()
        cleaned_lines = [
            line[len("data:") :].strip() if line.startswith("data:") else line
            for line in lines
        ]
        return "\n".join(cleaned_lines)

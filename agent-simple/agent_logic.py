import os
import re
from typing import List

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOpenAI

from models import AgentStep, QuestionResponse
from tools import clock

_BULLET_RE = re.compile(r"^\s*(?:\d+[\.\-\)]|[•\-])\s*", re.MULTILINE)
_RE_FINAL = re.compile(r"\bRESPUESTA\s+FINAL\s*:\s*", re.I)
_RE_REASONING = re.compile(r"\bRAZONAMIENTO\s*:\s*", re.I)


def split_numbered_cot(cot_block: str) -> List[str]:
    steps, current = [], []
    for line in cot_block.splitlines():
        if _BULLET_RE.match(line):
            if current:
                steps.append(" ".join(current).strip())
                current = []
            line = _BULLET_RE.sub("", line, count=1)
        current.append(line.strip())
    if current:
        steps.append(" ".join(current).strip())
    return [s for s in steps if s]


SYSTEM_PROMPT = """
Eres un asistente IA experto.
Siempre que respondas, sigue EXACTAMENTE este formato:

RAZONAMIENTO:
<explicación paso a paso aquí>

RESPUESTA FINAL:
<respuesta para el usuario>

No añadas texto fuera de las secciones indicadas.
"""


def build_agent() -> AgentExecutor:
    llm = ChatOpenAI(
        model_name=os.getenv("MODEL_NAME"),
        temperature=0.7,
        verbose=True,
    )
    tools = [clock]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        return_intermediate_steps=True,
        verbose=True,
        max_iterations=3,
    )
    return agent_executor


def process_question(agent: AgentExecutor, question: str) -> QuestionResponse:
    result = agent.invoke({"input": question, "chat_history": []})

    steps: list[AgentStep] = []
    observation_map = {}

    # Guardamos observaciones por acción para luego reemplazos
    for idx, (action, observation) in enumerate(result.get("intermediate_steps", [])):
        # Guardamos también como cot para mostrar razonamiento
        steps.append(AgentStep(action="cot", value=action.log.strip()))
        steps.append(AgentStep(action="cot", value=str(observation).strip()))

        # Mapeamos para reemplazo, por ejemplo usando nombre o índice
        observation_map[action.log.strip()] = str(observation).strip()

    raw_output: str = result["output"]

    # Reemplazar placeholders en raw_output con observaciones reales
    for placeholder, real_value in observation_map.items():
        if placeholder in raw_output:
            raw_output = raw_output.replace(placeholder, real_value)

    parts = _RE_FINAL.split(raw_output, maxsplit=1)

    if len(parts) == 2:
        cot_block, final_answer = parts
        cot_block = _RE_REASONING.sub("", cot_block).strip()

        if _BULLET_RE.match(cot_block):
            for sub in split_numbered_cot(cot_block):
                steps.append(AgentStep(action="cot", value=sub))
        elif cot_block:
            steps.append(AgentStep(action="cot", value=cot_block))

        steps.append(AgentStep(action="final_answer", value=final_answer.strip()))
    else:
        steps.append(AgentStep(action="final_answer", value=raw_output.strip()))

    return QuestionResponse(steps=steps)

# agent-simple

This is a simple example of an agent using OpenAI LLM for answering user messages. This agent has no proper support for multiple sessions handling.

This is a good example in case you want to create some agent with LLM integration. For a more complete example, refer to [agent-extended](./agent-extended/README.md).

# Run

Copy [sample.env](./sample.env) to [.env](./.env) and fill in the required values.

Then run this agent with the following commands:

```bash
devbox shell
poetry install --no-root && poetry run python main.py
```

    tambien puedes usar docker para ejecutar el agente

```bash
docker build -t agent-simple .
docker run -p 8000:8000 --name agent-simple agent-simple
```

# Resumen de Cambios - agent-simple

## 1. README.md

- Actualización en instrucciones para reflejar:
  - Cambios en la función `clock()` con soporte de zona horaria.
  - Ejecución sin dependencia de devbox.
  - Uso de Poetry para instalación de dependencias.
  - Explicación mejorada del razonamiento en las respuestas del agente.

## 2. poetry.lock y pyproject.toml

- Ajustes en dependencias para:
  - Soporte de zona horaria (`zoneinfo` o similar).
  - Compatibilidad con Python 3.11 y LangChain.
  - Evitar conflictos y mejorar estabilidad en el build.

## 3. sample.env

- Modificación de variables de entorno:
  - Configuración del modelo y parámetros de ejecución.
  - Ajustes para control de logging y debugging.

## 4. Dockerfile

- Eliminación de `devbox`.
- Instalación directa de Poetry en la imagen base.
- Copia de archivos y uso de Poetry para instalar dependencias.
- Exposición del puerto 8000 para FastAPI.
- Simplificación para facilitar construcción y despliegue.

## 5. agent_logic.py

- Modificación en `process_question` para:
  - Usar la última observación real como respuesta final.
  - Mostrar todos los pasos intermedios como razonamiento (`cot`).
  - Evitar mostrar placeholders literales en la respuesta.
- Mejor manejo de errores y logging.

## 6. models.py

- Ajustes en modelos para:
  - Mejor serialización y manejo de pasos (`AgentStep`, `QuestionResponse`).
  - Definición clara de tipos de pasos (`cot`, `final_answer`, etc.).

## 7. main.py

- Ajustes en el endpoint de preguntas para usar la lógica actualizada.
- Mejor manejo de excepciones y respuestas HTTP.
- Posible mejora en gestión de sesiones.

## 8. tools.py

- Corrección en la función `clock()`:
  - Importaciones corregidas.
- Garantiza la hora correcta y consistente.

---

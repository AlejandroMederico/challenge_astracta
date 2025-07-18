# agent-mock

This is just a simple example of an agent that has no integration with an LLM and only implements the basic contract of an agent.

This is a good example in case you want to create some agent mock that answers with fixed answer, or an agent that just doesn't use LLMs. For a more complete example, refer to [agent-extended](./agent-extended/README.md).

# Run

To run this agent, run the following commands in current directory:

```bash
devbox shell
poetry install --no-root && poetry run python agent.py
```

Se agrego un metodo test para probar el agente, pero se debe ejecutar de la siguiente manera:

```bash
poetry run python agent.py test
```

Antes se debe tener un agente corriendo en el puerto 8000.

### Resumen de Cambios - agent-mock

### 1. README.md

- Actualización en la documentación para reflejar cambios recientes.
- Posible ajuste en instrucciones y configuración del agente mock.

### 2. agent.py

- Cambios en la lógica del agente mock para mejorar simulaciones.
- Ajustes para alinearse con la estructura de pasos y respuestas del agente principal.
- Corrección de errores y refactorización para mayor claridad.

### 3. poetry.lock y pyproject.toml

- Actualización y alineación de dependencias con agent-simple.
- Inclusión de paquetes necesarios para mantener compatibilidad y estabilidad.

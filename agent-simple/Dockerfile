FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar archivos de poetry
COPY pyproject.toml poetry.lock ./

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

# Instalar dependencias con Poetry
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# Copiar todo el código
COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "main.py"]

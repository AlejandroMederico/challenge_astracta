FROM python:3.11-slim

# Instalar dependencias de compilación necesarias para algunas librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY gpt_agent ./gpt_agent

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh ./
RUN chmod +x wait-for-it.sh

COPY .env .env

ENTRYPOINT ["./entrypoint.sh"]

CMD ["poetry", "run", "python", "-m", "gpt_agent"]

FROM python:3.8-slim

RUN pip install ollama torch

WORKDIR /app
COPY . /app

CMD ["tail", "-f", "/dev/null"]

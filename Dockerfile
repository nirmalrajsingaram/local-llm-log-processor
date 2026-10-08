FROM python:3.12-slim

LABEL description="Local log analysis using Ollama and Phi-3 Mini"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY app.py ./app.py

RUN useradd --uid 10001 --create-home appuser \
    && mkdir -p /reports /logs \
    && chown -R appuser:appuser /app /reports /logs

USER appuser
VOLUME ["/logs", "/reports"]
ENTRYPOINT ["python", "/app/app.py"]
CMD ["/logs"]
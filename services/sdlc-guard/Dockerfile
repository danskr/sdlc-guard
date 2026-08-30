FROM python:3.13-slim
WORKDIR /workspace
COPY services/sdlc-guard/pyproject.toml ./services/sdlc-guard/pyproject.toml
COPY services/sdlc-guard/src ./services/sdlc-guard/src
COPY artifacts ./artifacts
COPY sample-project ./sample-project
RUN pip install --no-cache-dir ./services/sdlc-guard
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "sdlc_guard.main:app", "--host", "0.0.0.0", "--port", "8080"]

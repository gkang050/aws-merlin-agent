FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies only (not the project itself)
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --extras glue --only main --no-interaction --no-ansi --no-root

# Copy application code
COPY src /app/src
COPY .streamlit /app/.streamlit

ENV STREAMLIT_SERVER_PORT=8501
ENV PYTHONPATH=/app/src

ENTRYPOINT ["streamlit", "run", "src/aws_merlin_agent/ui/chat_app.py"]

FROM python:3.12-slim

LABEL maintainer="https://jiveturkey.rocks/about"
LABEL description="Rick MCP Server v1.0 — The server IS the resume."

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rick_mcp.py .

EXPOSE 8000

CMD ["python", "rick_mcp.py"]

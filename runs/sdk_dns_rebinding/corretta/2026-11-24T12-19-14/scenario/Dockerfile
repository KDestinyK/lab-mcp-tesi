FROM python:3.12-slim
ARG MCP_VERSION
RUN pip install --no-cache-dir "mcp==${MCP_VERSION}"
WORKDIR /app
COPY server.py verifica.py /app/
CMD ["python", "-u", "/app/server.py"]

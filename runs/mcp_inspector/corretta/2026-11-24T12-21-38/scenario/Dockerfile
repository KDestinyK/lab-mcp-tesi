# inspector-server usa shell-quote e spawn-rx senza dichiararli tra le dipendenze
FROM node:22-slim
ARG INSPECTOR_VERSION
RUN npm install -g \
      "@modelcontextprotocol/inspector-server@${INSPECTOR_VERSION}" \
      shell-quote@1.8.2 spawn-rx@5.1.2
WORKDIR /app
COPY client.js attacco.js salute.js /app/
CMD ["sh", "-c", "mkdir -p /condiviso && mcp-inspector-server 2>&1 | tee -a /condiviso/avvio.log"]

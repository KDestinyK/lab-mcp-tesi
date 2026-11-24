FROM node:22-slim
ARG FS_VERSION
RUN npm install -g @modelcontextprotocol/server-filesystem@${FS_VERSION}
COPY client.js /app/client.js
COPY prepara_dati.sh /app/prepara_dati.sh
RUN sed -i 's/\r$//' /app/prepara_dati.sh && sh /app/prepara_dati.sh
CMD ["sleep", "infinity"]
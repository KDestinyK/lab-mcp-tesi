import importlib.metadata
import os
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

CARTELLA_MARKER = "/tmp/eseguiti"
os.makedirs(CARTELLA_MARKER, exist_ok=True)

# transport_security non impostato: si prova il comportamento predefinito dell'SDK
mcp = FastMCP("laboratorio", host="127.0.0.1", port=8000, stateless_http=True, json_response=True)


@mcp.tool()
def registra_esecuzione(caso: str) -> str:
    """Registra l'esecuzione del tool creando un file marker con il nome del caso."""
    nome = "".join(c for c in caso if c.isalnum() or c in "_-")[:64] or "senza_nome"
    with open(os.path.join(CARTELLA_MARKER, nome), "w", encoding="utf-8") as f:
        f.write(datetime.now(timezone.utc).isoformat())
    print(f"tool eseguito per il caso {nome}", flush=True)
    return f"eseguito: {nome}"


if __name__ == "__main__":
    ts = mcp.settings.transport_security
    attiva = bool(ts and ts.enable_dns_rebinding_protection)
    print(f"mcp {importlib.metadata.version('mcp')}, protezione DNS rebinding attiva: {attiva}"
          + (f", host ammessi {ts.allowed_hosts}, origini ammesse {ts.allowed_origins}" if attiva else ""),
          flush=True)
    mcp.run(transport="streamable-http")

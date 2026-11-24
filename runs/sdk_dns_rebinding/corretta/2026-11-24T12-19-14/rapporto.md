# sdk_dns_rebinding, configurazione corretta

Esecuzione del 2026-11-24 11:19:14 UTC. Completata.
Docker 29.9.3, Compose 5.7.0, commit git: 5f4e67a, nessuna modifica non salvata.

Protezione dal DNS rebinding nell'SDK Python mcp (CVE-2025-66416): versione 1.22.0 contro 1.23.0, con un server FastMCP su Streamable HTTP in ascolto su 127.0.0.1:8000. Le richieste arrivano dalla stessa macchina con gli header Host e Origin del dominio dell'attaccante, separati o insieme. Il tool chiamato crea un file con il nome del caso, e l'esito dipende dalla presenza di quel file.

**Casi conformi all'atteso: 6/6**

## Esiti

| Caso | Tipo | Esito | Atteso | Conforme |
|---|---|---|---|---|
| controllo_host_locale | controllo | accettata | accettata | sì |
| controllo_origin_locale | controllo | accettata | accettata | sì |
| host_esterno | attacco | respinta | respinta | sì |
| origin_esterna | attacco | respinta | respinta | sì |
| host_e_origin_esterni | attacco | respinta | respinta | sì |
| origin_null | limite | respinta | respinta | sì |

Conforme: l'esito osservato coincide con quello atteso per questa configurazione (con la versione vulnerabile, per i casi di attacco l'atteso è che riescano).

## Casi

### controllo_host_locale (controllo)

Client locale: Host 127.0.0.1:8000, nessuna Origin.

Output del client:

```
HTTP/1.1 200 OK
date: Tue, 24 Nov 2026 11:19:22 GMT
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
< date: Tue, 24 Nov 2026 11:19:22 GMT
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
date: Tue, 24 Nov 2026 11:19:23 GMT
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
< date: Tue, 24 Nov 2026 11:19:23 GMT
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
HTTP/1.1 421 Misdirected Request
date: Tue, 24 Nov 2026 11:19:23 GMT
server: uvicorn
content-length: 19

Invalid Host header
421
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
< HTTP/1.1 421 Misdirected Request
< date: Tue, 24 Nov 2026 11:19:23 GMT
< server: uvicorn
< content-length: 19
< 
{ [19 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `non_eseguito`

Esito: **respinta**, atteso: respinta

### origin_esterna (attacco)

Origin del dominio dell'attaccante. Atteso con la 1.23.0: 403, tool non eseguito.

Output del client:

```
HTTP/1.1 403 Forbidden
date: Tue, 24 Nov 2026 11:19:24 GMT
server: uvicorn
content-length: 21

Invalid Origin header
403
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
< HTTP/1.1 403 Forbidden
< date: Tue, 24 Nov 2026 11:19:24 GMT
< server: uvicorn
< content-length: 21
< 
{ [21 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `non_eseguito`

Esito: **respinta**, atteso: respinta

### host_e_origin_esterni (attacco)

Host e Origin del dominio dell'attaccante insieme, come nella richiesta del browser dopo il rebinding. Atteso con la 1.23.0: 421 (l'Host è controllato per primo), tool non eseguito.

Output del client:

```
HTTP/1.1 421 Misdirected Request
date: Tue, 24 Nov 2026 11:19:24 GMT
server: uvicorn
content-length: 19

Invalid Host header
421
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
< HTTP/1.1 421 Misdirected Request
< date: Tue, 24 Nov 2026 11:19:24 GMT
< server: uvicorn
< content-length: 19
< 
{ [19 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `non_eseguito`

Esito: **respinta**, atteso: respinta

### origin_null (limite)

Origin 'null' (iframe in sandbox, file locali), non tra quelle ammesse dalla 1.23.0.

Output del client:

```
HTTP/1.1 403 Forbidden
date: Tue, 24 Nov 2026 11:19:25 GMT
server: uvicorn
content-length: 21

Invalid Origin header
403
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
< HTTP/1.1 403 Forbidden
< date: Tue, 24 Nov 2026 11:19:25 GMT
< server: uvicorn
< content-length: 21
< 
{ [21 bytes data]
* Connection #0 to host 127.0.0.1 left intact
```

Verifica sul container: `non_eseguito`

Esito: **respinta**, atteso: respinta

## Log del server

Estratto di `container.log`, con i traceback ridotti a una riga.

```
--- container usati per tutti i casi ---
target-1 11:19:17.915 /usr/local/lib/python3.12/site-packages/pydantic_settings/sources/utils.py:51: IncompleteFieldDefinitionWarning: Field 'lifespan' has an incomplete definition: its annotation contains an unresolved forward reference, so settings sources may fail to correctly resolve its value. Call `model_rebuild()`
target-1 11:19:17.915   warnings.warn(  # noqa: B028  (called from many sources at differing depths, so no stacklevel is correct)
target-1 11:19:17.918 mcp 1.23.0, protezione DNS rebinding attiva: True, host ammessi ['127.0.0.1:*', 'localhost:*', '[::1]:*'], origini ammesse ['http://127.0.0.1:*', 'http://localhost:*', 'http://[::1]:*']
target-1 11:19:17.936 INFO:     Started server process [1]
target-1 11:19:17.936 INFO:     Waiting for application startup.
target-1 11:19:17.936 StreamableHTTP session manager started
target-1 11:19:17.937 INFO:     Application startup complete.
target-1 11:19:17.937 INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
cattura-1 11:19:20.088 tcpdump: listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
target-1 11:19:23.661 Processing request of type CallToolRequest
target-1 11:19:23.661 tool eseguito per il caso controllo_host_locale
target-1 11:19:23.662 INFO:     127.0.0.1:50990 - "POST /mcp HTTP/1.1" 200 OK
target-1 11:19:23.663 Terminating session: None
target-1 11:19:23.668 Error in message router
target-1 11:19:23.668 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:19:24.208 Processing request of type CallToolRequest
target-1 11:19:24.209 tool eseguito per il caso controllo_origin_locale
target-1 11:19:24.209 INFO:     127.0.0.1:51000 - "POST /mcp HTTP/1.1" 200 OK
target-1 11:19:24.209 Terminating session: None
target-1 11:19:24.210 Error in message router
target-1 11:19:24.210 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:19:24.766 Invalid Host header: attaccante.example:8000
target-1 11:19:24.766 INFO:     127.0.0.1:51002 - "POST /mcp HTTP/1.1" 421 Misdirected Request
target-1 11:19:24.766 Terminating session: None
target-1 11:19:24.766 Error in message router
target-1 11:19:24.766 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:19:25.344 Invalid Origin header: http://attaccante.example
target-1 11:19:25.344 INFO:     127.0.0.1:51016 - "POST /mcp HTTP/1.1" 403 Forbidden
target-1 11:19:25.345 Terminating session: None
target-1 11:19:25.345 Error in message router
target-1 11:19:25.345 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:19:25.900 Invalid Host header: attaccante.example:8000
target-1 11:19:25.900 INFO:     127.0.0.1:51032 - "POST /mcp HTTP/1.1" 421 Misdirected Request
target-1 11:19:25.900 Terminating session: None
target-1 11:19:25.900 Error in message router
target-1 11:19:25.900 [traceback omesso, termina con: anyio.ClosedResourceError]
target-1 11:19:26.499 Invalid Origin header: null
target-1 11:19:26.499 INFO:     127.0.0.1:51038 - "POST /mcp HTTP/1.1" 403 Forbidden
target-1 11:19:26.499 Terminating session: None
target-1 11:19:26.499 Error in message router
target-1 11:19:26.499 [traceback omesso, termina con: anyio.ClosedResourceError]
cattura-1 11:19:27.177 90 packets captured
cattura-1 11:19:27.177 180 packets received by filter
cattura-1 11:19:27.177 0 packets dropped by kernel
target-1 11:19:27.362 INFO:     Shutting down
target-1 11:19:27.477 INFO:     Waiting for application shutdown.
target-1 11:19:27.477 StreamableHTTP session manager shutting down
target-1 11:19:27.477 INFO:     Application shutdown complete.
target-1 11:19:27.477 INFO:     Finished server process [1]
```

## Altri file di questa cartella

- `container.log`: log dei container con timestamp, una sezione per avvio
- `pcap/`: traffico di rete del servizio sotto test (Wireshark), vuoto se il server usa stdio
- `risultati.jsonl`: output completo di ogni caso e ripetizione, per i programmi
- `meta.json`, `immagini.json`, `immagini_base.json`, `pacchetti.txt`, `comandi.log`, `scenario/`: versioni, digest, comandi e file usati

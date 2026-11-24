# mcp_inspector, configurazione corretta

Esecuzione del 2026-11-24 11:21:38 UTC. Completata.
Docker 29.9.3, Compose 5.7.0, commit git: 5f4e67a, nessuna modifica non salvata.

Autenticazione nel proxy di MCP Inspector (CVE-2025-49596): versione 0.14.0, senza controlli, contro 0.14.1, che richiede un token di sessione e controlla l'Origin. I primi tre casi chiedono /config, che non esegue nulla; gli ultimi due chiedono /sse con transportType=stdio, che fa avviare al proxy il comando touch su un file del volume condiviso, una volta con l'Origin di un sito esterno e una senza Origin. Il token corretto, quando serve, è letto dal log di avvio del proxy.

**Casi conformi all'atteso: 5/5**

## Esiti

| Caso | Tipo | Esito | Atteso | Conforme |
|---|---|---|---|---|
| controllo_token_corretto | controllo | accettata | accettata | sì |
| limite_token_errato | limite | respinta | respinta | sì |
| attacco_senza_autenticazione | attacco | respinta | respinta | sì |
| attacco_esecuzione_comando | attacco | non_eseguito | non_eseguito | sì |
| attacco_processo_locale | attacco | non_eseguito | non_eseguito | sì |

Conforme: l'esito osservato coincide con quello atteso per questa configurazione (con la versione vulnerabile, per i casi di attacco l'atteso è che riescano).

## Casi

### controllo_token_corretto (controllo)

Richiesta locale con il token di sessione corretto, letto dal log di avvio, e Origin ammessa (http://localhost:6274, quella del client web dell'Inspector). Deve funzionare in entrambe le versioni.

Output del client:

```
token di sessione nel log di avvio: presente
richiesta: GET /config, Authorization presente, Origin http://localhost:6274
HTTP 200 OK
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","connection":"keep-alive","content-length":"146","content-type":"application/json; charset=utf-8","date":"Tue, 24 Nov 2026 11:21:49 GMT","etag":"W/\"92-cFuxgQ7bquGm9PXvUnsobnH6Fp8\"","keep-alive":"timeout=5","x-powered-by":"Express"}
{"defaultEnvironment":{"HOME":"/root","PATH":"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"},"defaultCommand":"","defaultArgs":""}
200
```

Esito: **accettata**, atteso: accettata

### limite_token_errato (limite)

Token presente ma sbagliato, stessa Origin del controllo.

Output del client:

```
token di sessione nel log di avvio: presente
richiesta: GET /config, Authorization presente (sbagliato), Origin http://localhost:6274
HTTP 401 Unauthorized
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","connection":"keep-alive","content-length":"130","content-type":"application/json; charset=utf-8","date":"Tue, 24 Nov 2026 11:21:49 GMT","etag":"W/\"82-2pzqacHfkEaeX7ONRIAANVlmWEk\"","keep-alive":"timeout=5","x-powered-by":"Express"}
{"error":"Unauthorized","message":"Authentication required. Use the session token shown in the console when starting the server."}
401
```

Esito: **respinta**, atteso: respinta

### attacco_senza_autenticazione (attacco)

Nessun token e Origin del dominio dell'attaccante, come la richiesta di una pagina web esterna.

Output del client:

```
token di sessione nel log di avvio: presente
richiesta: GET /config, Authorization assente, Origin http://attaccante.example
HTTP 403 Forbidden
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","connection":"keep-alive","content-length":"152","content-type":"application/json; charset=utf-8","date":"Tue, 24 Nov 2026 11:21:50 GMT","etag":"W/\"98-cIBoLymgB70E5ZgrmrDlxGAPp9M\"","keep-alive":"timeout=5","x-powered-by":"Express"}
{"error":"Forbidden - invalid origin","message":"Request blocked to prevent DNS rebinding attacks. Configure allowed origins via environment variable."}
403
```

Esito: **respinta**, atteso: respinta

### attacco_esecuzione_comando (attacco)

CVE-2025-49596: richiesta non autenticata a /sse con transportType=stdio e l'Origin del dominio dell'attaccante. Il comando touch crea un file nel volume condiviso, che la verifica cerca. Atteso: eseguito con 0.14.0, non eseguito con 0.14.1.

Output del client:

```
richiesta: GET /sse?transportType=stdio&command=touch&args=/condiviso/exploit-attacco_esecuzione_comando
header inviati: {"Origin":"http://attaccante.example"} (nessun token di sessione)
HTTP 403 Forbidden
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","connection":"keep-alive","content-length":"152","content-type":"application/json; charset=utf-8","date":"Tue, 24 Nov 2026 11:21:50 GMT","etag":"W/\"98-cIBoLymgB70E5ZgrmrDlxGAPp9M\"","keep-alive":"timeout=5","x-powered-by":"Express"}
{"error":"Forbidden - invalid origin","message":"Request blocked to prevent DNS rebinding attacks. Configure allowed origins via environment variable."}
403
```

Verifica sul container: `non_eseguito`

Esito: **non_eseguito**, atteso: non_eseguito

### attacco_processo_locale (attacco)

Stessa richiesta a /sse senza token e senza Origin, come quella di un processo locale. Atteso: eseguito con 0.14.0, non eseguito con 0.14.1 (401).

Output del client:

```
richiesta: GET /sse?transportType=stdio&command=touch&args=/condiviso/exploit-attacco_processo_locale
header inviati: {} (nessun token di sessione)
HTTP 401 Unauthorized
header della risposta: {"access-control-allow-origin":"*","access-control-expose-headers":"mcp-session-id","connection":"keep-alive","content-length":"130","content-type":"application/json; charset=utf-8","date":"Tue, 24 Nov 2026 11:21:51 GMT","etag":"W/\"82-2pzqacHfkEaeX7ONRIAANVlmWEk\"","keep-alive":"timeout=5","x-powered-by":"Express"}
{"error":"Unauthorized","message":"Authentication required. Use the session token shown in the console when starting the server."}
401
```

Verifica sul container: `non_eseguito`

Esito: **non_eseguito**, atteso: non_eseguito

## Log del server

Estratto di `container.log`, con i traceback ridotti a una riga.

```
--- container usati per tutti i casi ---
target-1 11:21:42.595 ⚙️ Proxy server listening on 127.0.0.1:6277
target-1 11:21:42.595 🔑 Session token: b8641949314208e6ccc4cd0e72bee9c37e53b458f6d3c6b8816ee002ff4b3667
target-1 11:21:42.595 Use this token to authenticate requests or set DANGEROUSLY_OMIT_AUTH=true to disable auth
target-1 11:21:42.595 
target-1 11:21:42.595 🔗 Open inspector with token pre-filled:
target-1 11:21:42.595    http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=b8641949314208e6ccc4cd0e72bee9c37e53b458f6d3c6b8816ee002ff4b3667
target-1 11:21:42.595    (Auto-open is disabled when authentication is enabled)
target-1 11:21:42.595 
cattura-1 11:21:44.907 tcpdump: listening on lo, link-type EN10MB (Ethernet), snapshot length 262144 bytes
target-1 11:21:50.247 Invalid origin: http://attaccante.example
target-1 11:21:50.735 Invalid origin: http://attaccante.example
cattura-1 11:21:52.973 90 packets captured
cattura-1 11:21:52.973 180 packets received by filter
cattura-1 11:21:52.973 0 packets dropped by kernel
```

## Altri file di questa cartella

- `container.log`: log dei container con timestamp, una sezione per avvio
- `pcap/`: traffico di rete del servizio sotto test (Wireshark), vuoto se il server usa stdio
- `risultati.jsonl`: output completo di ogni caso e ripetizione, per i programmi
- `meta.json`, `immagini.json`, `immagini_base.json`, `pacchetti.txt`, `comandi.log`, `scenario/`: versioni, digest, comandi e file usati

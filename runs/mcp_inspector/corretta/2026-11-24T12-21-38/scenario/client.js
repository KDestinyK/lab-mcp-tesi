#!/usr/bin/env node
"use strict";
const fs = require("node:fs");
const { execSync } = require("node:child_process");

const [, , , conToken, tokenErrato, origine] = process.argv;
const LOG = "/condiviso/avvio.log";
const URL_CONFIG = "http://127.0.0.1:6277/config";

function attendi(ms) {
  try { execSync(`sleep ${ms / 1000}`); } catch (e) {}
}

function leggiToken() {
  // nella 0.14.0 il log di avvio non contiene alcun token
  for (let i = 0; i < 50; i++) {
    const testo = fs.existsSync(LOG) ? fs.readFileSync(LOG, "utf8") : "";
    if (/Proxy server listening/.test(testo)) {
      const m = testo.match(/Session token: (\S+)/);
      return m ? m[1] : null;
    }
    attendi(200);
  }
  return null;
}

async function main() {
  const token = leggiToken();
  console.log(`token di sessione nel log di avvio: ${token ? "presente" : "assente"}`);

  const headers = {};
  if (conToken === "si") {
    headers["Authorization"] = "Bearer " + (tokenErrato === "si" ? "0".repeat(64) : (token || ""));
  }
  if (origine === "locale") headers["Origin"] = "http://localhost:6274";
  else if (origine === "esterna") headers["Origin"] = "http://attaccante.example";

  console.log(`richiesta: GET /config` +
              `, Authorization ${headers.Authorization ? "presente" + (tokenErrato === "si" ? " (sbagliato)" : "") : "assente"}` +
              `, Origin ${headers.Origin || "(nessuna)"}`);

  let risposta;
  try {
    risposta = await fetch(URL_CONFIG, { headers });
  } catch (e) {
    console.log("[errore di rete] " + e.message);
    console.log("indeterminato");
    return;
  }
  const corpo = await risposta.text();
  console.log(`HTTP ${risposta.status} ${risposta.statusText}`);
  console.log(`header della risposta: ${JSON.stringify(Object.fromEntries(risposta.headers))}`);
  console.log(corpo);
  console.log(risposta.status); // l'esito del caso si ricava dall'ultima riga
}

main();

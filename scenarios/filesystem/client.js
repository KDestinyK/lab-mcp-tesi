#!/usr/bin/env node
"use strict";
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const caso = process.argv[2] || "senza_nome";
const percorso = process.argv[3];
const CARTELLA_CONSENTITA = process.env.CARTELLA_CONSENTITA || "/dati/area_consentita";
const DIR_PROVE = process.env.DIR_PROVE || "/prove";

if (!percorso) {
  console.error("uso: node client.js <caso> <percorso_da_leggere>");
  process.exit(2);
}

function scriviProva(testo, nomeFile = caso + ".txt") {
  try {
    fs.mkdirSync(DIR_PROVE, { recursive: true });
    fs.writeFileSync(path.join(DIR_PROVE, nomeFile), testo);
  } catch (e) {
    console.log("[errore scrittura prova] " + e.message);
  }
}

console.log("cartella consentita del server: " + CARTELLA_CONSENTITA);
console.log("percorso richiesto a read_file:  " + percorso);

const srv = spawn("mcp-server-filesystem", [CARTELLA_CONSENTITA],
                  { stdio: ["pipe", "pipe", "pipe"] });

let bufOut = "";
let err = "";
let fatto = false;

srv.stdout.setEncoding("utf8");
srv.stdout.on("data", (d) => {
  bufOut += d;
  let i;
  while ((i = bufOut.indexOf("\n")) >= 0) {
    const riga = bufOut.slice(0, i).trim();
    bufOut = bufOut.slice(i + 1);
    if (!riga) continue;
    try {
      const msg = JSON.parse(riga);
      console.log("<< " + JSON.stringify(msg));
      gestisci(msg);
    } catch (e) {
      console.log("[stdout non JSON] " + riga);
    }
  }
});
srv.stderr.setEncoding("utf8");
srv.stderr.on("data", (d) => { err += d; });
srv.on("error", (e) => {
  console.log("[impossibile avviare il server] " + e.message);
  scriviProva("");
  process.exit(1);
});

function invia(msg) {
  console.log(">> " + JSON.stringify(msg));
  srv.stdin.write(JSON.stringify(msg) + "\n");
}

function gestisci(msg) {
  if (msg.id === 1) {
    invia({ jsonrpc: "2.0", method: "notifications/initialized" });
    invia({ jsonrpc: "2.0", id: 2, method: "tools/call",
            params: { name: "read_file", arguments: { path: percorso } } });
  } else if (msg.id === 2) {
    concludi(msg);
  }
}

function concludi(risposta) {
  if (fatto) return;
  fatto = true;
  // anche con isError: dati riservati segnalati come errore devono arrivare alla verifica
  let contenuto = "";
  const r = risposta.result;
  if (r && Array.isArray(r.content)) {
    contenuto = r.content.filter((c) => c.type === "text").map((c) => c.text).join("\n");
  }
  scriviProva(contenuto);
  scriviProva(JSON.stringify(risposta, null, 2) + "\n", caso + ".risposta.json");
  if (err.trim()) console.log("[stderr del server]\n" + err.trim());
  console.log("fine");
  try { srv.stdin.end(); } catch (e) {}
  setTimeout(() => { try { srv.kill(); } catch (e) {} process.exit(0); }, 150);
}

invia({ jsonrpc: "2.0", id: 1, method: "initialize",
        params: { protocolVersion: "2024-11-05", capabilities: {},
                  clientInfo: { name: "client-laboratorio", version: "1.0" } } });

setTimeout(() => {
  if (!fatto) {
    console.log("[timeout: nessuna risposta dal server]");
    if (err.trim()) console.log("[stderr del server]\n" + err.trim());
    scriviProva("");
    try { srv.kill(); } catch (e) {}
    process.exit(0);
  }
}, 15000);

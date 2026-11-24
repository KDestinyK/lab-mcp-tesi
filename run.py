#!/usr/bin/env python3
"""Esegue uno scenario del laboratorio e ne salva i risultati in runs/."""
import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

BASE = Path(__file__).resolve().parent


def ora():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


class Registro:
    def __init__(self, cartella: Path):
        self.cartella = cartella
        self.file = (cartella / "comandi.log").open("a", encoding="utf-8")

    def esegui(self, args, env=None, salva_in=None, aggiungi_a=None, controlla=True):
        inizio = time.monotonic()
        t0 = ora()
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=env)
        durata = int((time.monotonic() - inizio) * 1000)
        self.file.write(f"[{t0}] $ {' '.join(map(str, args))}\n"
                        f"    exit={p.returncode} durata_ms={durata}\n")
        if p.stderr.strip():
            self.file.write("    stderr: " + p.stderr.strip().replace("\n", "\n            ") + "\n")
        self.file.flush()
        if salva_in:
            (self.cartella / salva_in).write_text(p.stdout, encoding="utf-8")
        if aggiungi_a:
            with (self.cartella / aggiungi_a).open("a", encoding="utf-8") as f:
                f.write(f"### {' '.join(map(str, args))}\n{p.stdout}\n")
                if p.returncode != 0 and p.stderr.strip():
                    f.write(f"[exit {p.returncode}] {p.stderr.strip()}\n\n")
        if controlla and p.returncode != 0:
            raise RuntimeError(f"comando fallito ({p.returncode}): {' '.join(map(str, args))}\n{p.stderr}")
        return p, t0, ora(), durata

    def chiudi(self):
        self.file.close()


def sha256(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def versione_git():
    try:
        commit = subprocess.run(["git", "-C", str(BASE), "rev-parse", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
        stato = subprocess.run(["git", "-C", str(BASE), "status", "--porcelain", "--", ".",
                                ":(exclude)runs"], capture_output=True, text=True).stdout.strip()
        return {"commit": commit or None, "modifiche_non_salvate": bool(stato)} if commit else None
    except OSError:
        return None


def immagini_base(cartella: Path):
    trovate = []
    for df in sorted(cartella.rglob("Dockerfile*")):
        for riga in df.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*FROM\s+(?:--platform=\S+\s+)?(\S+)", riga, flags=re.IGNORECASE)
            if m and m.group(1) not in trovate:
                trovate.append(m.group(1))
    return trovate


def rimuovi_percorso_locale(cartella: Path):
    # i percorsi della macchina locale diventano relativi alla cartella del laboratorio
    radici = [json.dumps(str(BASE), ensure_ascii=False)[1:-1], str(BASE), BASE.as_posix()]
    for f in cartella.rglob("*"):
        if not f.is_file() or "pcap" in f.relative_to(cartella).parts:
            continue
        testo = f.read_text(encoding="utf-8", errors="surrogateescape")
        nuovo = testo
        for radice in radici:
            nuovo = re.sub(re.escape(radice), ".", nuovo, flags=re.IGNORECASE)
        if nuovo != testo:
            f.write_text(nuovo, encoding="utf-8", errors="surrogateescape")


def ultima_riga(testo):
    righe = testo.strip().splitlines()
    return righe[-1].strip() if righe else ""


# riga di `docker compose logs --timestamps`: "<servizio>  | <data>T<ora>Z <messaggio>"
RIGA_LOG = re.compile(r"^(?P<srv>\S+)\s+\|\s+(?P<dt>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(?P<fr>\d+))?Z ?(?P<msg>.*)$")


def log_leggibile(run_dir, massimo=150):
    # Compose unisce i log dei servizi senza ordinarli per orario
    f = run_dir / "container.log"
    if not f.exists():
        return []
    sezioni = [(None, {})]
    for testo in f.read_text(encoding="utf-8", errors="replace").splitlines():
        m = RIGA_LOG.match(testo)
        if m:
            fr = (m["fr"] or "").ljust(9, "0")[:9]
            ora = m["dt"][11:] + ("." + fr[:3] if m["fr"] else "")
            sezioni[-1][1].setdefault(m["srv"], []).append((f"{m['dt']}.{fr}", ora, m["msg"]))
        elif testo.startswith("====="):
            sezioni.append((testo.strip("= "), {}))
    out = []
    for titolo, per_servizio in sezioni:
        if not per_servizio:
            continue
        if titolo:
            out.append(f"--- {titolo} ---")
        voci = []
        for srv, righe in per_servizio.items():
            i = 0
            while i < len(righe):
                istante, ora, msg = righe[i]
                if msg.startswith("Traceback (most recent call last):"):
                    j = i + 1
                    while j < len(righe) and righe[j][2].startswith((" ", "\t")):
                        j += 1
                    fine = j < len(righe)
                    voci.append((istante, srv, ora,
                                 "[traceback omesso" + (f", termina con: {righe[j][2]}]" if fine else "]")))
                    i = j + 1 if fine else j
                else:
                    voci.append((istante, srv, ora, msg))
                    i += 1
        voci.sort(key=lambda v: v[0])
        out += [f"{srv} {ora} {msg[:300]}" for _, srv, ora, msg in voci]
    if len(out) > massimo:
        out = out[:massimo] + [f"[... altre {len(out) - massimo} righe in container.log]"]
    return out


def blocco(testo, limite=2500):
    testo = (testo or "").strip()
    if not testo:
        return "(vuoto)"
    if len(testo) > limite:
        testo = testo[:limite].rstrip() + "\n[...troncato: l'output completo è in risultati.jsonl]"
    return "```\n" + testo + "\n```"


def scrivi_rapporto(run_dir, meta, riepilogo, risultati):
    primo = {}
    for r in risultati:
        primo.setdefault(r["caso"], r)
    g = meta.get("git")
    git = "non disponibile" if not g else g["commit"][:7] + (
        ", con modifiche non salvate" if g["modifiche_non_salvate"] else ", nessuna modifica non salvata")
    docker = ((meta.get("docker") or {}).get("Server") or {}).get("Version", "?")

    L = [f"# {meta['scenario']}, configurazione {meta['configurazione']}", ""]
    if meta["completata"]:
        stato = "Completata."
    else:
        prima_riga = (meta.get("errore") or "errore sconosciuto").splitlines()[0]
        stato = f"NON completata: {prima_riga} (dettagli in errore.txt e comandi.log)."
    L.append(f"Esecuzione del {meta['inizio_utc'][:19].replace('T', ' ')} UTC. {stato}")
    L.append(f"Docker {docker}, Compose {meta.get('compose', '?')}, commit git: {git}.")
    if meta["ripetizioni_per_caso"] > 1:
        L.append(f"Ogni caso è stato ripetuto {meta['ripetizioni_per_caso']} volte per controllarne la "
                 "riproducibilità; il dettaglio mostra la prima ripetizione.")
    if meta.get("descrizione"):
        L += ["", meta["descrizione"]]
    esito = f"**Casi conformi all'atteso: {riepilogo['casi_conformi']}/{riepilogo['casi_totali']}**"
    if riepilogo["casi_saltati"]:
        esito += f" (saltati perché da completare: {', '.join(riepilogo['casi_saltati'])})"
    L += ["", esito, "", "## Esiti", "",
          "| Caso | Tipo | Esito | Atteso | Conforme |", "|---|---|---|---|---|"]
    for caso, c in riepilogo["casi"].items():
        esiti = ", ".join(e if n == 1 else f"{e} x{n}" for e, n in c["esiti"].items())
        L.append(f"| {caso} | {c['tipo']} | {esiti} | {c['atteso']} | {'sì' if c['conforme'] else '**NO**'} |")
    L += ["", "Conforme: l'esito osservato coincide con quello atteso per questa configurazione "
              "(con la versione vulnerabile, per i casi di attacco l'atteso è che riescano)."]

    L += ["", "## Casi"]
    for r in primo.values():
        L += ["", f"### {r['caso']} ({r['tipo']})", ""]
        if r.get("descrizione"):
            L += [r["descrizione"], ""]
        if r.get("saltato"):
            L.append("Non eseguito: il comando contiene il segnaposto DA_COMPLETARE.")
            continue
        L += ["Output del client:", "", blocco(r["output"]), ""]
        if r.get("stderr", "").strip():
            L += ["Stderr del client:", "", blocco(r["stderr"], 800), ""]
        if "verifica_output" in r:
            L += [f"Verifica sul container: `{ultima_riga(r['verifica_output']) or '(nessun output)'}`", ""]
        L.append(f"Esito: **{r['esito']}**, atteso: {r['atteso']}"
                 + ("" if r["conforme"] else " (**diverso dall'atteso**)"))

    log = log_leggibile(run_dir)
    if log:
        L += ["", "## Log del server", "",
              "Estratto di `container.log`, con i traceback ridotti a una riga.",
              "", "```"] + log + ["```"]

    L += ["", "## Altri file di questa cartella", "",
          "- `container.log`: log dei container con timestamp, una sezione per avvio",
          "- `pcap/`: traffico di rete del servizio sotto test (Wireshark), vuoto se il server usa stdio",
          "- `risultati.jsonl`: output completo di ogni caso e ripetizione, per i programmi",
          "- `meta.json`, `immagini.json`, `immagini_base.json`, `pacchetti.txt`, `comandi.log`, `scenario/`: "
          "versioni, digest, comandi e file usati"]
    (run_dir / "rapporto.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    # evita errori di codifica sulla console di Windows
    sys.stdout.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(description="Esegue uno scenario del laboratorio MCP")
    ap.add_argument("scenario")
    ap.add_argument("configurazione")
    ap.add_argument("--ripetizioni", type=int, default=1,
                    help="ripetizioni di ogni caso, solo per controllarne la riproducibilità (predefinito 1)")
    a = ap.parse_args()

    dir_scen = BASE / "scenarios" / a.scenario
    spec = json.loads((dir_scen / "scenario.json").read_text(encoding="utf-8"))
    if a.configurazione not in spec["configurazioni"]:
        sys.exit(f"configurazione sconosciuta: {a.configurazione} "
                 f"(disponibili: {', '.join(spec['configurazioni'])})")
    conf = spec["configurazioni"][a.configurazione]
    if isinstance(conf, str):
        conf = {"file": conf}
    compose = dir_scen / conf["file"]

    try:
        pre = subprocess.run(["docker", "version", "--format", "{{json .Server}}"], capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
        docker_ok = pre.returncode == 0 and pre.stdout.strip() not in ("", "null")
        dettaglio = pre.stderr.strip()
    except OSError as e:
        docker_ok, dettaglio = False, str(e)
    if not docker_ok:
        sys.exit("Docker non risponde: avvia Docker Desktop, aspetta che risulti avviato e riprova.\n"
                 f"Dettaglio: {dettaglio}")

    stamp = dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    run_dir = BASE / "runs" / a.scenario / a.configurazione / stamp
    (run_dir / "pcap").mkdir(parents=True)
    reg = Registro(run_dir)

    shutil.copytree(dir_scen, run_dir / "scenario")
    hashes = {str(f.relative_to(dir_scen)): sha256(f)
              for f in sorted(dir_scen.rglob("*")) if f.is_file()}

    progetto = f"lab_{a.scenario}_{a.configurazione}".lower().replace("-", "_")
    env = dict(os.environ, CAPTURE_DIR=(run_dir / "pcap").resolve().as_posix())
    env.update({k: str(v) for k, v in conf.get("env", {}).items()})
    dc = ["docker", "compose", "-p", progetto, "-f", str(compose)]
    dc_tutti = ["docker", "compose", "--profile", "*", "-p", progetto, "-f", str(compose)]
    # --progress quiet: senza, Compose mette il log di build nell'output di ogni `run`
    dc_run = ["docker", "compose", "--progress", "quiet", "-p", progetto, "-f", str(compose)]

    def comando_in(servizio, comando, modo="exec"):
        # --no-deps: run lascia com'è il target già avviato
        if modo == "exec":
            return dc + ["exec", "-T", servizio] + comando
        return dc_run + ["run", "--rm", "-T", "--no-deps", servizio] + comando

    meta = {
        "scenario": a.scenario, "configurazione": a.configurazione,
        "descrizione": spec.get("descrizione", ""),
        "variabili_configurazione": conf.get("env", {}),
        "ripetizioni_per_caso": a.ripetizioni,
        "inizio_utc": ora(), "sistema": platform.platform(), "python": sys.version,
        "file_scenario_sha256": hashes,
        "run_py_sha256": sha256(Path(__file__).resolve()),
        "git": versione_git(),
    }
    meta["docker"] = json.loads(reg.esegui(["docker", "version", "--format", "{{json .}}"])[0].stdout)
    meta["compose"] = reg.esegui(["docker", "compose", "version", "--short"])[0].stdout.strip()

    esiti_globali = spec.get("esiti", {})
    risultati = []
    precedente = None
    completata, errore = False, None

    def avvia(ricrea=False):
        args = dc + ["up", "-d", "--wait"] + (["--force-recreate"] if ricrea else ["--build"])
        reg.esegui(args, env=env)
        time.sleep(spec.get("attesa_secondi", 2))

    def salva_log(etichetta):
        # da chiamare prima di ricreare i container, altrimenti i log si perdono
        with (run_dir / "container.log").open("a", encoding="utf-8") as f:
            f.write(f"===== {etichetta} =====\n")
        reg.esegui(dc_tutti + ["logs", "--timestamps", "--no-color"], env=env,
                   aggiungi_a="container.log", controlla=False)

    try:
        reg.esegui(dc_tutti + ["config"], env=env, salva_in="compose.risolto.yml")
        reg.esegui(dc_tutti + ["pull", "--ignore-pull-failures"], env=env, controlla=False)
        avvia()

        for v in spec.get("comandi_versioni", []):
            reg.esegui(comando_in(v["servizio"], v["comando"], v.get("modo", "exec")), env=env,
                       aggiungi_a="pacchetti.txt", controlla=False)

        precedente = None
        for caso in spec["casi"]:
            if precedente and spec.get("riavvia_tra_casi", False):
                salva_log(f"container usati per il caso {precedente}")
                avvia(ricrea=True)
            precedente = caso["id"]
            servizio = caso.get("servizio", spec.get("servizio_client", "client"))
            esiti = {**esiti_globali, **caso.get("esiti", {})}
            atteso = caso.get("atteso", {}).get(a.configurazione)
            verifica = caso.get("verifica")
            sost = lambda lista: [x.replace("{caso}", caso["id"]) for x in lista]
            if any("DA_COMPLETARE" in x for x in sost(caso["comando"])):
                r = {"caso": caso["id"], "tipo": caso.get("tipo", ""),
                     "descrizione": caso.get("descrizione", ""), "ripetizione": 0,
                     "esito": "da_completare", "atteso": atteso,
                     "conforme": None, "saltato": True}
                risultati.append(r)
                with (run_dir / "risultati.jsonl").open("a", encoding="utf-8") as f:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                print(f"  {caso['id']} [{r['tipo']}]: SALTATO (da completare)")
                continue
            for i in range(1, a.ripetizioni + 1):
                p, t0, t1, durata = reg.esegui(
                    comando_in(servizio, sost(caso["comando"]), "run"), env=env, controlla=False)
                r = {"caso": caso["id"], "tipo": caso.get("tipo", ""), "descrizione": caso.get("descrizione", ""),
                     "ripetizione": i, "inizio_utc": t0, "fine_utc": t1, "durata_ms": durata,
                     "exit_code": p.returncode, "output": p.stdout, "stderr": p.stderr}
                if verifica:
                    v = reg.esegui(comando_in(verifica["servizio"], sost(verifica["comando"]),
                                              verifica.get("modo", "exec")), env=env, controlla=False)[0]
                    r.update({"verifica_comando": sost(verifica["comando"]), "verifica_exit_code": v.returncode,
                              "verifica_output": v.stdout, "verifica_stderr": v.stderr})
                    esito = {**esiti, **verifica.get("esiti", {})}.get(ultima_riga(v.stdout), "indeterminato")
                else:
                    esito = esiti.get(ultima_riga(p.stdout), "indeterminato")
                r.update({"esito": esito, "atteso": atteso, "conforme": esito == atteso})
                risultati.append(r)
                with (run_dir / "risultati.jsonl").open("a", encoding="utf-8") as f:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                segno = "ok" if r["conforme"] else "DIVERSO DALL'ATTESO"
                print(f"  {caso['id']} [{r['tipo']}] rip. {i}: {esito} (atteso {atteso}) {segno}")
        completata = True
    except KeyboardInterrupt:
        errore = "esecuzione interrotta dall'utente"
    except Exception as e:
        errore = f"{type(e).__name__}: {e}"
        (run_dir / "errore.txt").write_text(traceback.format_exc(), encoding="utf-8")
    finally:
        # digest letti a fine prova, quando tutte le immagini sono in locale
        try:
            immagini = reg.esegui(dc_tutti + ["config", "--images"], env=env, controlla=False)[0].stdout.split()
            info = {}
            for img in immagini:
                p = reg.esegui(["docker", "image", "inspect", "--format",
                                "{{json .RepoDigests}}|{{.Id}}", img], controlla=False)[0]
                digests, _, ident = p.stdout.strip().partition("|")
                info[img] = {"repo_digests": json.loads(digests) if digests else None,
                             "id": ident or None}
            (run_dir / "immagini.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        except Exception as e:
            (run_dir / "immagini.json").write_text(json.dumps({"errore": str(e)}), encoding="utf-8")
        try:
            base = {}
            for img in immagini_base(dir_scen):
                p = reg.esegui(["docker", "image", "inspect", "--format",
                                "{{json .RepoDigests}}|{{.Id}}|{{.Created}}", img], controlla=False)[0]
                digests, _, resto = p.stdout.strip().partition("|")
                ident, _, creata = resto.partition("|")
                base[img] = {"repo_digests": json.loads(digests) if digests else None,
                             "id": ident or None, "creata": creata or None}
            (run_dir / "immagini_base.json").write_text(json.dumps(base, indent=2), encoding="utf-8")
        except Exception as e:
            (run_dir / "immagini_base.json").write_text(json.dumps({"errore": str(e)}), encoding="utf-8")
        reg.esegui(dc + ["stop", "-t", "5"], env=env, controlla=False)  # tcpdump chiude il file pcap
        salva_log(f"container usati per il caso {precedente}" if spec.get("riavvia_tra_casi") and precedente
                  else "container usati per tutti i casi")
        reg.esegui(dc_tutti + ["down", "-v", "--remove-orphans"], env=env, controlla=False)
        meta["fine_utc"] = ora()
        meta["completata"] = completata
        meta["errore"] = errore
        (run_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

        casi = {}
        for r in risultati:
            if r.get("saltato"):
                continue
            c = casi.setdefault(r["caso"], {"tipo": r["tipo"], "atteso": r["atteso"], "esiti": {}})
            c["esiti"][r["esito"]] = c["esiti"].get(r["esito"], 0) + 1
        for c in casi.values():
            c["conforme"] = list(c["esiti"]) == [c["atteso"]]
        saltati = [r["caso"] for r in risultati if r.get("saltato")]
        riepilogo = {"scenario": a.scenario, "configurazione": a.configurazione,
                     "completata": completata, "errore": errore,
                     "ripetizioni_per_caso": a.ripetizioni, "casi": casi,
                     "casi_conformi": sum(c["conforme"] for c in casi.values()),
                     "casi_totali": len(casi), "casi_saltati": saltati}
        (run_dir / "riepilogo.json").write_text(json.dumps(riepilogo, indent=2, ensure_ascii=False),
                                                encoding="utf-8")
        try:
            scrivi_rapporto(run_dir, meta, riepilogo, risultati)
        except Exception as e:  # il rapporto non deve far fallire l'esecuzione
            (run_dir / "rapporto.md").write_text(f"Rapporto non generato: {type(e).__name__}: {e}\n",
                                                 encoding="utf-8")
        reg.chiudi()
        rimuovi_percorso_locale(run_dir)
        print(f"Esecuzione salvata in {run_dir} (da leggere: rapporto.md)")
        if completata:
            print(f"Casi conformi all'atteso: {riepilogo['casi_conformi']}/{riepilogo['casi_totali']}")
            if saltati:
                print(f"Casi saltati (da completare): {len(saltati)} ({', '.join(saltati)})")
        else:
            print(f"ESECUZIONE NON COMPLETATA: {errore}")
            print("Dettagli in errore.txt e comandi.log; i casi eseguiti fino a quel punto sono in risultati.jsonl.")
    if not completata:
        sys.exit(1)


if __name__ == "__main__":
    main()

// /health non richiede autenticazione in nessuna delle due versioni
fetch("http://127.0.0.1:6277/health")
  .then((r) => process.exit(r.ok ? 0 : 1))
  .catch(() => process.exit(1));

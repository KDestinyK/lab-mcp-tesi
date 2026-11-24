#!/bin/sh
set -e
mkdir -p /dati/area_consentita /dati/area_riservata
printf 'documento di lavoro. MARCATORE_CONSENTITO_7f3a\n' > /dati/area_consentita/documento.txt
printf 'dati sensibili fuori dalla cartella consentita. MARCATORE_RISERVATO_9b21\n' > /dati/area_riservata/segreto.txt

# CVE-2025-53110 (prefisso)
mkdir -p /dati/area_consentita_riservata
printf 'dati sensibili fuori dalla cartella consentita. MARCATORE_RISERVATO_9b21\n' \
  > /dati/area_consentita_riservata/segreto.txt

# CVE-2025-53109 (symlink)
ln -sf /dati/area_riservata/segreto.txt /dati/area_consentita/link_segreto
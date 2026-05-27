# HubSpot RAG Autoresponder

Standalone HubSpot ticket autoresponder with knowledge-base retrieval.

## V1 scope
- read HubSpot tickets
- load markdown/text knowledge-base files
- retrieve relevant KB snippets
- generate a grounded reply draft
- attach drafted notes back to HubSpot tickets when dry-run is off
- support local no-HubSpot reply testing

## Initial focus
- HubSpot tickets first
- draft/recommendation-first workflow
- no blind auto-send in v1


## Runnable v1 additions
This project now includes:
- processed ticket ledger
- dry-run mode
- log file output
- continuous polling
- installer script
- systemd service template
- local no-HubSpot test harness

## Run HubSpot tickets once
```bash
./.venv/bin/python scripts/run_tickets.py --limit 3 --dry-run
```

## Continuous polling
```bash
./.venv/bin/python scripts/run_tickets.py --loop --dry-run --poll-seconds 120
```

## Logs
Ticket processing writes to:
- `logs/hubspot-tickets.log`

## Installer
```bash
./scripts/install.sh
```

## systemd
A sample service file is included:
- `systemd/hubspot-rag-autoresponder.service`

## Local ticket reply testing
```bash
./.venv/bin/python scripts/test_ticket_reply.py --input samples/access_issue_ticket.json
```

## Self-signed certificates
If your in-house LLM endpoint uses a self-signed certificate, use one of these in `.env`:
```bash
LLM_VERIFY_SSL=false
```
or
```bash
LLM_CA_BUNDLE=/path/to/your-ca.pem
```


## HubSpot note writeback
When `--dry-run` is off, the runner now creates a HubSpot note and associates it with the ticket.

Example:
```bash
./.venv/bin/python scripts/run_tickets.py --limit 3
```

Dry-run still avoids touching HubSpot writeback:
```bash
./.venv/bin/python scripts/run_tickets.py --limit 3 --dry-run
```

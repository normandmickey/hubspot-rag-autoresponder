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


## Multi-user support
The project now supports multiple HubSpot user/queue instances under `instances/<name>/`.
Each instance can have its own:
- `HUBSPOT_OWNER_ID`
- `HUBSPOT_TICKET_PIPELINE`
- `knowledge_base/`
- `data/state.json`

Example runs:
```bash
./.venv/bin/python scripts/run_tickets.py --instance user-a --dry-run
./.venv/bin/python scripts/run_tickets.py --instance user-b --dry-run
./.venv/bin/python scripts/run_tickets.py --all-instances --dry-run
```

Each instance writes its own log file:
- `logs/hubspot-user-a.log`
- `logs/hubspot-user-b.log`


## Owner lookup helper
List HubSpot owners so you can map email/name to `HUBSPOT_OWNER_ID`:
```bash
./.venv/bin/python scripts/list_owners.py
```

## Instance scaffolder
Create a new multi-user instance folder automatically:
```bash
./.venv/bin/python scripts/create_instance.py user-c --owner-id 123456 --pipeline support-pipeline --stage new
```

## Stage filtering
Instances can now also filter by ticket stage using `HUBSPOT_TICKET_STAGE`.

Example `.env.example` for an instance:
```bash
HUBSPOT_OWNER_ID=123456
HUBSPOT_TICKET_PIPELINE=support-pipeline
HUBSPOT_TICKET_STAGE=new
KB_PATH=./instances/user-c/knowledge_base
DATA_PATH=./instances/user-c/data
```


## PGVector knowledge base
If your KB already lives in Postgres with PGVector, set:
```bash
KB_BACKEND=pgvector
KB_DATABASE_URL=postgresql://...
KB_TABLE=kb_chunks
KB_QUERY_EMBED_MODEL=your-embedding-model
```

Optional column overrides:
- `KB_DOCUMENT_ID_COLUMN`
- `KB_TEXT_COLUMN`
- `KB_EMBEDDING_COLUMN`
- `KB_METADATA_COLUMN`
- `KB_SOURCE_COLUMN`
- `KB_COLLECTION_TABLE`
- `KB_COLLECTION_ID_COLUMN`
- `KB_COLLECTION_NAME_COLUMN`
- `KB_EMBEDDING_COLLECTION_ID_COLUMN`
- `KB_COLLECTION_NAME`
- `KB_TOP_K`

Markdown retrieval remains available as a fallback with:
```bash
KB_BACKEND=markdown
```


## Workflow + runbook docs
- Workflow diagram and step-by-step flow: `docs/workflow.md`
- Deployment / usage runbook: `docs/runbook.md`


## Separate LLM and embedding providers
This repo supports using different providers for generation and embedding lookup.

Example split setup:
```bash
LLM_API_KEY=local
LLM_BASE_URL=https://your-local-llm/v1
LLM_MODEL=your-local-chat-model

EMBED_API_KEY=YOUR_OPENAI_API_KEY
EMBED_BASE_URL=
KB_QUERY_EMBED_MODEL=text-embedding-3-large
```

Notes:
- `LLM_*` is used for reply generation
- `EMBED_*` is used for KB query embeddings
- `OPENAI_API_KEY` can still act as a fallback if you leave the split keys blank

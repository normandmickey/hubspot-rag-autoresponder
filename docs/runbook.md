# HubSpot Ticket Autoresponder Runbook

## 1. Clone and install

```bash
git clone git@github.com:normandmickey/hubspot-rag-autoresponder.git
cd hubspot-rag-autoresponder
./scripts/bootstrap_venv.sh
```

## 2. Configure root env

Copy `.env.example` to `.env` and set:
- `HUBSPOT_ACCESS_TOKEN`
- `LLM_BASE_URL`
- `LLM_MODEL`
- optional TLS settings
- optional KB backend settings

### Example markdown KB mode

```bash
KB_BACKEND=markdown
KB_PATH=./knowledge_base
```

### Example PGVector mode

```bash
KB_BACKEND=pgvector
KB_DATABASE_URL=postgresql://user:pass@host/dbname
KB_TABLE=kb_chunks
KB_QUERY_EMBED_MODEL=your-embedding-model
```

## 3. Discover HubSpot owner IDs

```bash
./.venv/bin/python scripts/list_owners.py
```

Use the results to map the correct `HUBSPOT_OWNER_ID` for each user/queue.

## 4. Create an instance

```bash
./.venv/bin/python scripts/create_instance.py support-alice --owner-id 123456 --pipeline support-pipeline --stage new
```

This creates:
- `instances/support-alice/.env.example`
- `instances/support-alice/knowledge_base/`
- `instances/support-alice/data/`

Copy `instances/support-alice/.env.example` to `instances/support-alice/.env` if you want a real instance-local env file.

## 5. Load KB content

### Markdown mode
Add files under:
- `knowledge_base/`
- or instance-specific `instances/<name>/knowledge_base/`

### PGVector mode
Make sure the DB already contains:
- chunk text
- embeddings
- source/metadata fields if you want richer traceability

## 6. Test locally without HubSpot

```bash
./.venv/bin/python scripts/test_ticket_reply.py --input samples/access_issue_ticket.json
```

Use this to validate:
- retrieval quality
- tone
- prompt behavior
- TLS/LLM connectivity

## 7. Dry-run a real HubSpot instance

```bash
./.venv/bin/python scripts/run_tickets.py --instance support-alice --dry-run
```

This will:
- fetch matching tickets
- retrieve KB context
- generate reply previews
- log the results
- **not** attach notes
- **not** mark tickets processed

## 8. Run real writeback

```bash
./.venv/bin/python scripts/run_tickets.py --instance support-alice
```

This will:
- create a HubSpot note
- associate the note with the matching ticket
- mark that ticket processed in local state

## 9. Run all instances

```bash
./.venv/bin/python scripts/run_tickets.py --all-instances --dry-run
```

Or real mode:

```bash
./.venv/bin/python scripts/run_tickets.py --all-instances
```

## 10. Continuous polling

```bash
./.venv/bin/python scripts/run_tickets.py --all-instances --loop --dry-run --poll-seconds 120
```

## 11. Logs and state

Logs:
- `logs/hubspot-<instance>.log`

State:
- `instances/<name>/data/state.json`
- or root `data/state.json` for the default instance

## 12. systemd deployment

Install the sample service:

```bash
sudo cp systemd/hubspot-rag-autoresponder.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now hubspot-rag-autoresponder
```

You may want to edit the service first so it runs:
- a specific instance
- or `--all-instances`
- with or without `--dry-run`

## 13. Safety recommendation

Recommended rollout path:
1. local test harness
2. dry-run against real HubSpot tickets
3. limited real writeback for one owner/stage
4. broaden to more users/queues after reviewing logs

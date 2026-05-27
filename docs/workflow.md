# HubSpot Ticket Autoresponder Workflow

## Diagram

```text
HubSpot Tickets
      |
      v
Fetch recent tickets from HubSpot
      |
      v
Filter by configured instance rules
(owner / pipeline / stage)
      |
      v
Build ticket query
(subject + body)
      |
      v
Retrieve KB context
  - markdown search, or
  - Postgres + PGVector search
      |
      v
Policy / confidence pass
      |
      v
LLM generates reply draft
      |
      v
+-------------------------------+
| if --dry-run                  |
|   log preview only            |
|   do not attach note          |
|   do not mark processed       |
+-------------------------------+
              |
              | else
              v
Create HubSpot note
      |
      v
Associate note with ticket
      |
      v
Mark ticket processed
      |
      v
Write instance log output
```

## Step-by-step workflow

1. **Start a run**
   - Run a single instance or all configured instances.
   - Optional loop mode repeats the scan on a fixed interval.

2. **Load instance config**
   - Each instance can define:
     - `HUBSPOT_OWNER_ID`
     - `HUBSPOT_TICKET_PIPELINE`
     - `HUBSPOT_TICKET_STAGE`
     - KB path or PGVector settings
     - separate state/log directories

3. **Fetch tickets from HubSpot**
   - The runner pulls recent tickets from HubSpot.
   - Tickets are filtered to the correct user/queue slice.

4. **Skip already-processed tickets**
   - Processed ticket IDs are tracked per instance.
   - This avoids duplicate writeback on repeated runs.

5. **Retrieve KB context**
   - If `KB_BACKEND=markdown`, local `.md` / `.txt` files are searched.
   - If `KB_BACKEND=pgvector`, the query is embedded and searched against Postgres/PGVector.

6. **Classify the ticket**
   - A lightweight policy pass sets confidence and reasons.
   - Sensitive topics stay in draft-first behavior.

7. **Generate the reply**
   - The prompt includes:
     - ticket subject/body
     - requester context when available
     - KB hits
     - decision context
   - The LLM returns a grounded draft reply.

8. **Handle writeback**
   - **Dry-run mode**:
     - logs preview only
     - does not create notes
     - does not mark processed
   - **Real mode**:
     - creates a HubSpot note
     - associates the note to the ticket
     - marks the ticket as processed

9. **Log results**
   - Each instance writes its own log file.
   - Logs include ticket ID, confidence, KB hits, note status, and reply preview.

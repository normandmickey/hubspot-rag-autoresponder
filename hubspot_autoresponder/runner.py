import time
from pathlib import Path

from .hubspot_client import get_recent_tickets, create_ticket_note
from .kb import load_kb_documents, simple_search
from .policy import classify_ticket
from .responder import generate_reply
from .models import TicketMessage
from .storage import is_processed, mark_processed
from . import config


def normalize_ticket(row):
    props = row.get('properties') or {}
    return TicketMessage(
        ticket_id=row.get('id', ''),
        subject=props.get('subject', ''),
        requester_email='',
        requester_name='',
        body_text=props.get('content', '') or '',
    )


def log_line(line: str):
    log_dir = config.BASE_DIR / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / 'hubspot-tickets.log').open('a') as fh:
        fh.write(line.rstrip() + '\n')
    print(line)


def process_ticket(ticket, docs, dry_run: bool = True):
    hits = simple_search(f"{ticket.subject} {ticket.body_text}", docs)
    decision = classify_ticket(ticket, hits)
    reply = generate_reply(ticket, hits, decision)
    note_result = {'status': 'dry-run'} if dry_run else create_ticket_note(ticket.ticket_id, reply)
    if not dry_run:
        mark_processed(ticket.ticket_id)
    block = [
        f"TICKET={ticket.ticket_id}",
        f"SUBJECT={ticket.subject}",
        f"CONFIDENCE={decision.confidence}",
        f"REASONS={','.join(decision.reasons)}",
        f"KB_HITS={len(hits)}",
        f"WRITEBACK_STATUS={note_result.get('status', 'unknown')}",
        f"NOTE_ID={note_result.get('note_id', '')}",
        'REPLY_PREVIEW_START',
        reply,
        'REPLY_PREVIEW_END',
        '---',
    ]
    for line in block:
        log_line(line)



def run_once(limit: int = 3, dry_run: bool = True):
    docs = load_kb_documents(config.KB_PATH)
    rows = get_recent_tickets(limit=limit)
    processed = 0
    for row in rows:
        ticket = normalize_ticket(row)
        if not ticket.ticket_id or is_processed(ticket.ticket_id):
            continue
        process_ticket(ticket, docs, dry_run=dry_run)
        processed += 1
    log_line(f"PROCESSED={processed}")


def run_loop(limit: int = 3, dry_run: bool = True, poll_seconds: int = 120):
    while True:
        try:
            run_once(limit=limit, dry_run=dry_run)
        except Exception as exc:
            log_line(f"LOOP_ERROR={exc}")
        time.sleep(poll_seconds)


if __name__ == '__main__':
    run_once()

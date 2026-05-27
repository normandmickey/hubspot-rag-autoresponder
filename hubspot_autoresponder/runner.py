import time
from pathlib import Path

from .hubspot_client import get_recent_tickets, create_ticket_note
from .kb import search_kb
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


def discover_instances():
    if not config.INSTANCES_DIR.exists():
        return []
    return [path.name for path in sorted(config.INSTANCES_DIR.iterdir()) if path.is_dir()]


def log_line(instance_name: str, line: str):
    log_dir = config.BASE_DIR / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / f'hubspot-{instance_name}.log').open('a') as fh:
        fh.write(line.rstrip() + '\n')
    print(line)


def process_ticket(instance, ticket, dry_run: bool = True):
    hits = search_kb(f"{ticket.subject} {ticket.body_text}", instance['kb_path'])
    decision = classify_ticket(ticket, hits)
    reply = generate_reply(ticket, hits, decision)
    note_result = {'status': 'dry-run'} if dry_run else create_ticket_note(ticket.ticket_id, reply)
    if not dry_run:
        mark_processed(instance['data_path'], ticket.ticket_id)
    block = [
        f"INSTANCE={instance['instance_name']}",
        f"TICKET={ticket.ticket_id}",
        f"SUBJECT={ticket.subject}",
        f"CONFIDENCE={decision.confidence}",
        f"REASONS={','.join(decision.reasons)}",
        f"KB_HITS={len(hits)}",
        f"WRITEBACK_STATUS={note_result.get('status', 'unknown')}",
        f"FALLBACK_ONLY={'fallback_only' in decision.reasons}",
        f"NOTE_ID={note_result.get('note_id', '')}",
        'REPLY_PREVIEW_START',
        reply,
        'REPLY_PREVIEW_END',
        '---',
    ]
    for line in block:
        log_line(instance['instance_name'], line)



def process_instance(limit: int = 3, instance_name: str | None = None, dry_run: bool = True):
    instance = config.load_instance(instance_name)
    rows = get_recent_tickets(
        limit=limit,
        pipeline=instance['hubspot_ticket_pipeline'],
        owner_id=instance['hubspot_owner_id'],
        stage=instance['hubspot_ticket_stage'],
    )
    processed = 0
    log_line(instance['instance_name'], f"PIPELINE={instance['hubspot_ticket_pipeline']}")
    log_line(instance['instance_name'], f"OWNER_ID={instance['hubspot_owner_id']}")
    log_line(instance['instance_name'], f"STAGE={instance['hubspot_ticket_stage']}")
    log_line(instance['instance_name'], f"KB_PATH={instance['kb_path']}")
    log_line(instance['instance_name'], f"KB_BACKEND={config.KB_BACKEND}")
    log_line(instance['instance_name'], f"DATA_PATH={instance['data_path']}")
    for row in rows:
        ticket = normalize_ticket(row)
        if not ticket.ticket_id or is_processed(instance['data_path'], ticket.ticket_id):
            continue
        process_ticket(instance, ticket, dry_run=dry_run)
        processed += 1
    log_line(instance['instance_name'], f"PROCESSED={processed}")
    return processed


def run_once(limit: int = 3, dry_run: bool = True, instance_name: str | None = None, all_instances: bool = False):
    if all_instances:
        total = 0
        for name in discover_instances():
            total += process_instance(limit=limit, instance_name=name, dry_run=dry_run)
        print(f"ALL_INSTANCES_PROCESSED={total}")
        return total
    return process_instance(limit=limit, instance_name=instance_name, dry_run=dry_run)


def run_loop(limit: int = 3, dry_run: bool = True, poll_seconds: int = 120, instance_name: str | None = None, all_instances: bool = False):
    while True:
        try:
            run_once(limit=limit, dry_run=dry_run, instance_name=instance_name, all_instances=all_instances)
        except Exception as exc:
            print(f"LOOP_ERROR={exc}")
        time.sleep(poll_seconds)


if __name__ == '__main__':
    run_once()

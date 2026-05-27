#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hubspot_autoresponder.models import TicketMessage
from hubspot_autoresponder.kb import search_kb
from hubspot_autoresponder.policy import classify_ticket
from hubspot_autoresponder.responder import generate_reply, llm_connection_help_text
from hubspot_autoresponder import config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Path to JSON ticket fixture')
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text())
    ticket = TicketMessage(
        ticket_id=payload.get('ticket_id', 'local-ticket'),
        subject=payload.get('subject', ''),
        requester_email=payload.get('requester_email', ''),
        requester_name=payload.get('requester_name', ''),
        body_text=payload.get('body_text', ''),
    )
    hits = search_kb(f"{ticket.subject} {ticket.body_text}", config.KB_PATH)
    decision = classify_ticket(ticket, hits)
    try:
        reply = generate_reply(ticket, hits, decision)
    except Exception as exc:
        print(f'LLM_ERROR={exc}')
        print(llm_connection_help_text())
        raise
    print(f"TICKET={ticket.ticket_id}")
    print(f"SUBJECT={ticket.subject}")
    print(f"CONFIDENCE={decision.confidence}")
    print(f"REASONS={','.join(decision.reasons)}")
    print('--- REPLY ---')
    print(reply)


if __name__ == '__main__':
    print('TEST_START')
    main()

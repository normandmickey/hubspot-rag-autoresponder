import json
from pathlib import Path
from . import config

STATE_PATH = config.DATA_PATH / 'state.json'


def _ensure():
    config.DATA_PATH.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        STATE_PATH.write_text(json.dumps({'processed_ticket_ids': []}, indent=2))


def load_state():
    _ensure()
    return json.loads(STATE_PATH.read_text())


def save_state(state):
    _ensure()
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True))


def is_processed(ticket_id: str) -> bool:
    state = load_state()
    return ticket_id in state.get('processed_ticket_ids', [])


def mark_processed(ticket_id: str):
    state = load_state()
    ids = state.setdefault('processed_ticket_ids', [])
    if ticket_id not in ids:
        ids.append(ticket_id)
    save_state(state)

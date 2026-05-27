import time
import requests
from . import config


def _headers():
    return {
        'Authorization': f'Bearer {config.HUBSPOT_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }


def get_recent_tickets(limit: int = 10, pipeline: str = '', owner_id: str = ''):
    url = f"{config.HUBSPOT_BASE_URL}/crm/v3/objects/tickets"
    params = {
        'limit': limit,
        'properties': 'subject,content,hs_pipeline,hubspot_owner_id',
    }
    resp = requests.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    rows = resp.json().get('results', [])
    filtered = []
    for row in rows:
        props = row.get('properties') or {}
        if pipeline and props.get('hs_pipeline', '') != pipeline:
            continue
        if owner_id and props.get('hubspot_owner_id', '') != owner_id:
            continue
        filtered.append(row)
    return filtered


def create_note(body_text: str):
    url = f"{config.HUBSPOT_BASE_URL}/crm/v3/objects/notes"
    payload = {
        'properties': {
            'hs_note_body': body_text,
            'hs_timestamp': str(int(time.time() * 1000)),
        }
    }
    resp = requests.post(url, headers=_headers(), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def associate_note_to_ticket(note_id: str, ticket_id: str):
    url = (
        f"{config.HUBSPOT_BASE_URL}/crm/v3/objects/notes/{note_id}"
        f"/associations/tickets/{ticket_id}/note_to_ticket"
    )
    resp = requests.put(url, headers=_headers(), timeout=30)
    resp.raise_for_status()
    return {'status': 'associated', 'note_id': note_id, 'ticket_id': ticket_id}


def create_ticket_note(ticket_id: str, body_text: str):
    note = create_note(body_text)
    note_id = note.get('id')
    if not note_id:
        raise RuntimeError('HubSpot note creation did not return an id')
    association = associate_note_to_ticket(note_id, ticket_id)
    return {
        'status': 'attached',
        'note_id': note_id,
        'ticket_id': ticket_id,
        'association': association,
    }

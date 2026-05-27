import requests
from . import config


def _headers():
    return {
        'Authorization': f'Bearer {config.HUBSPOT_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }


def get_recent_tickets(limit: int = 10):
    url = f"{config.HUBSPOT_BASE_URL}/crm/v3/objects/tickets"
    params = {
        'limit': limit,
        'properties': 'subject,content,hs_pipeline,hubspot_owner_id',
    }
    resp = requests.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get('results', [])


def create_ticket_note(ticket_id: str, body_text: str):
    # Placeholder for future HubSpot note engagement writeback.
    return {
        'ticket_id': ticket_id,
        'status': 'not-implemented',
        'preview': body_text[:200],
    }

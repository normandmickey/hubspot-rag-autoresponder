from .models import ReplyDecision

SENSITIVE_MARKERS = ['refund', 'chargeback', 'invoice', 'legal', 'contract', 'termination']


def classify_ticket(message, kb_hits):
    text = f"{message.subject} {message.body_text}".lower()
    decision = ReplyDecision(action='draft', confidence='low', reasons=[])
    if any(marker in text for marker in SENSITIVE_MARKERS):
        decision.reasons.append('sensitive_topic')
    if kb_hits:
        decision.confidence = 'medium'
        decision.reasons.append('kb_match_found')
    else:
        decision.reasons.append('no_kb_match')
        decision.reasons.append('fallback_only')
    return decision

from dataclasses import dataclass, field
from typing import List


@dataclass
class TicketMessage:
    ticket_id: str
    subject: str
    requester_email: str
    requester_name: str
    body_text: str


@dataclass
class KnowledgeHit:
    path: str
    text: str
    score: int = 0


@dataclass
class ReplyDecision:
    action: str = 'draft'
    confidence: str = 'low'
    reasons: List[str] = field(default_factory=list)

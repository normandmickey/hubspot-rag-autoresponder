import httpx
from openai import OpenAI
from . import config


def build_reply_prompt(message, kb_docs, decision):
    kb_blob = '\n\n'.join(f"Source: {doc.path}\n{doc.text[:2000]}" for doc in kb_docs)
    fallback_only = 'fallback_only' in decision.reasons
    fallback_instruction = ''
    if fallback_only:
        fallback_instruction = (
            'The knowledge base does not contain enough verified information to answer directly. '
            'Do not provide outside facts, phone numbers, websites, policies, or recommendations. '
            'Instead, write a short reply that clearly says you do not have enough verified information in the knowledge base to answer confidently, and ask for clarification or offer escalation.'
        )
    return f"""You are drafting a HubSpot support reply grounded in the provided knowledge base.

Ticket subject: {message.subject}
Requester: {message.requester_name} <{message.requester_email}>
Ticket body:
{message.body_text}

Decision context:
- action: {decision.action}
- confidence: {decision.confidence}
- reasons: {', '.join(decision.reasons)}

Knowledge base:
{kb_blob}

Rules:
- Use only information supported by the knowledge base.
- If the knowledge base is insufficient, do not invent policy, facts, contacts, URLs, or recommendations.
- Keep the reply concise and professional.
- Prefer 3 short paragraphs or fewer.

Fallback rule:
{fallback_instruction or 'If the KB supports an answer, respond using only that support.'}
"""


def fallback_reply(message):
    return (
        f"Hi {message.requester_name or 'there'},\n\n"
        "Thanks for reaching out. I do not have enough verified information in the knowledge base to answer that confidently. "
        "If you can share a little more detail, or if you want this routed to the right person for review, I can help with that.\n\n"
        "Best,\nSupport"
    )


def generate_reply(message, kb_docs, decision):
    if 'fallback_only' in decision.reasons and not kb_docs:
        return fallback_reply(message)
    if not config.LLM_BASE_URL or not config.LLM_MODEL:
        raise RuntimeError('LLM_BASE_URL and LLM_MODEL must be set in your local .env')
    verify = config.LLM_CA_BUNDLE or config.LLM_VERIFY_SSL
    http_client = httpx.Client(verify=verify, timeout=120.0)
    client = OpenAI(
        api_key=config.LLM_API_KEY or 'local',
        base_url=config.LLM_BASE_URL,
        http_client=http_client,
    )
    prompt = build_reply_prompt(message, kb_docs, decision)
    resp = client.responses.create(
        model=config.LLM_MODEL,
        input=prompt,
        temperature=config.LLM_TEMPERATURE,
        max_output_tokens=config.LLM_MAX_TOKENS,
    )
    return (resp.output_text or '').strip()


def llm_connection_help_text():
    return (
        'LLM connection failed. If your in-house endpoint uses a self-signed certificate, either '
        'set LLM_VERIFY_SSL=false for local testing or set LLM_CA_BUNDLE to a PEM file that trusts that cert.'
    )

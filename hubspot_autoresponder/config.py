from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_KB_PATH = BASE_DIR / 'knowledge_base'
DEFAULT_DATA_PATH = BASE_DIR / 'data'
INSTANCES_DIR = BASE_DIR / 'instances'

load_dotenv()

HUBSPOT_ACCESS_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN', '')
HUBSPOT_BASE_URL = os.getenv('HUBSPOT_BASE_URL', 'https://api.hubapi.com').strip()
HUBSPOT_TICKET_PIPELINE = os.getenv('HUBSPOT_TICKET_PIPELINE', '').strip()
HUBSPOT_TICKET_STAGE = os.getenv('HUBSPOT_TICKET_STAGE', '').strip()
HUBSPOT_OWNER_ID = os.getenv('HUBSPOT_OWNER_ID', '').strip()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
LLM_BASE_URL = os.getenv('LLM_BASE_URL', '').strip()
LLM_MODEL = os.getenv('LLM_MODEL', '').strip()
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.10'))
LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '1500'))
LLM_CA_BUNDLE = os.getenv('LLM_CA_BUNDLE', '').strip()
LLM_VERIFY_SSL = os.getenv('LLM_VERIFY_SSL', 'true').strip().lower() not in {'0', 'false', 'no'}
KB_BACKEND = os.getenv('KB_BACKEND', 'markdown').strip().lower()
KB_DATABASE_URL = os.getenv('KB_DATABASE_URL', '').strip()
KB_TABLE = os.getenv('KB_TABLE', 'kb_chunks').strip()
KB_DOCUMENT_ID_COLUMN = os.getenv('KB_DOCUMENT_ID_COLUMN', 'document_id').strip()
KB_TEXT_COLUMN = os.getenv('KB_TEXT_COLUMN', 'chunk_text').strip()
KB_EMBEDDING_COLUMN = os.getenv('KB_EMBEDDING_COLUMN', 'embedding').strip()
KB_METADATA_COLUMN = os.getenv('KB_METADATA_COLUMN', 'metadata').strip()
KB_SOURCE_COLUMN = os.getenv('KB_SOURCE_COLUMN', 'source').strip()
KB_COLLECTION_TABLE = os.getenv('KB_COLLECTION_TABLE', 'langchain_pg_collection').strip()
KB_COLLECTION_ID_COLUMN = os.getenv('KB_COLLECTION_ID_COLUMN', 'uuid').strip()
KB_COLLECTION_NAME_COLUMN = os.getenv('KB_COLLECTION_NAME_COLUMN', 'name').strip()
KB_EMBEDDING_COLLECTION_ID_COLUMN = os.getenv('KB_EMBEDDING_COLLECTION_ID_COLUMN', 'collection_id').strip()
KB_COLLECTION_NAME = os.getenv('KB_COLLECTION_NAME', '').strip()
KB_TOP_K = int(os.getenv('KB_TOP_K', '5'))
KB_QUERY_EMBED_MODEL = os.getenv('KB_QUERY_EMBED_MODEL', '').strip()


def load_instance(instance_name: str | None = None):
    instance_name = (instance_name or '').strip()
    if instance_name:
        instance_dir = INSTANCES_DIR / instance_name
        instance_env = instance_dir / '.env'
        if instance_env.exists():
            load_dotenv(instance_env, override=True)
        kb_path = Path(os.getenv('KB_PATH', instance_dir / 'knowledge_base'))
        data_path = Path(os.getenv('DATA_PATH', instance_dir / 'data'))
    else:
        kb_path = Path(os.getenv('KB_PATH', DEFAULT_KB_PATH))
        data_path = Path(os.getenv('DATA_PATH', DEFAULT_DATA_PATH))
    return {
        'instance_name': instance_name or 'default',
        'kb_path': kb_path,
        'data_path': data_path,
        'hubspot_ticket_pipeline': os.getenv('HUBSPOT_TICKET_PIPELINE', HUBSPOT_TICKET_PIPELINE).strip(),
        'hubspot_ticket_stage': os.getenv('HUBSPOT_TICKET_STAGE', HUBSPOT_TICKET_STAGE).strip(),
        'hubspot_owner_id': os.getenv('HUBSPOT_OWNER_ID', HUBSPOT_OWNER_ID).strip(),
    }

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH = Path(os.getenv('KB_PATH', BASE_DIR / 'knowledge_base'))
DATA_PATH = Path(os.getenv('DATA_PATH', BASE_DIR / 'data'))
HUBSPOT_ACCESS_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN', '')
HUBSPOT_BASE_URL = os.getenv('HUBSPOT_BASE_URL', 'https://api.hubapi.com').strip()
HUBSPOT_TICKET_PIPELINE = os.getenv('HUBSPOT_TICKET_PIPELINE', '').strip()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
LLM_BASE_URL = os.getenv('LLM_BASE_URL', '').strip()
LLM_MODEL = os.getenv('LLM_MODEL', '').strip()
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.10'))
LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '1500'))
LLM_CA_BUNDLE = os.getenv('LLM_CA_BUNDLE', '').strip()
LLM_VERIFY_SSL = os.getenv('LLM_VERIFY_SSL', 'true').strip().lower() not in {'0', 'false', 'no'}

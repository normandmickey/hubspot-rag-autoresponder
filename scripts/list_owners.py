#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hubspot_autoresponder.hubspot_client import get_owners


def main():
    rows = get_owners()
    for row in rows:
        print(f"OWNER_ID={row.get('id', '')}")
        print(f"EMAIL={row.get('email', '')}")
        print(f"NAME={row.get('firstName', '')} {row.get('lastName', '')}".strip())
        print('---')


if __name__ == '__main__':
    main()

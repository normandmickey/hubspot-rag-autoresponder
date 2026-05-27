#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hubspot_autoresponder.runner import run_once, run_loop


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=3)
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--poll-seconds', type=int, default=120)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--instance', default='', help='Instance name under instances/<name>/')
    parser.add_argument('--all-instances', action='store_true', help='Run all configured instances in sequence')
    args = parser.parse_args()
    if args.loop:
        run_loop(
            limit=args.limit,
            dry_run=args.dry_run,
            poll_seconds=args.poll_seconds,
            instance_name=args.instance or None,
            all_instances=args.all_instances,
        )
    else:
        run_once(
            limit=args.limit,
            dry_run=args.dry_run,
            instance_name=args.instance or None,
            all_instances=args.all_instances,
        )


if __name__ == '__main__':
    main()

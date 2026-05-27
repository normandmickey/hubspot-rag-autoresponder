#!/usr/bin/env python3
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTANCES = ROOT / 'instances'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='Instance name')
    parser.add_argument('--owner-id', default='')
    parser.add_argument('--pipeline', default='')
    parser.add_argument('--stage', default='')
    args = parser.parse_args()

    instance_dir = INSTANCES / args.name
    kb_dir = instance_dir / 'knowledge_base'
    data_dir = instance_dir / 'data'
    kb_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    env_text = '\n'.join([
        f'HUBSPOT_OWNER_ID={args.owner_id}',
        f'HUBSPOT_TICKET_PIPELINE={args.pipeline}',
        f'HUBSPOT_TICKET_STAGE={args.stage}',
        f'KB_PATH=./instances/{args.name}/knowledge_base',
        f'DATA_PATH=./instances/{args.name}/data',
        '',
    ])
    (instance_dir / '.env.example').write_text(env_text)
    (kb_dir / 'README.md').write_text(f'Knowledge base files for {args.name} go here.\n')
    print(f'Created instance scaffold at {instance_dir}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Create a new Canvas archive from the bundled blank project files."""

import argparse
import json
from pathlib import Path


def initialize(project):
    root = Path(project).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ValueError('The project path must be a directory.')
    markers = (
        'AGENTS.md', '课程资源目录.md',
        'Canvas每日扫描计划.md', 'Canvas 每日扫描计划.md',
        '.planning/canvas-resources/inventory.json',
        'Canvas邮件记录/发送记录.json', 'Canvas 邮件记录/发送记录.json',
    )
    if any((root / name).exists() for name in markers):
        return {'status': 'existing_project', 'project': str(root), 'created': []}
    assets = Path(__file__).resolve().parents[1] / 'assets' / 'project'
    sources = sorted(path for path in assets.rglob('*') if path.is_file())
    if not sources:
        raise FileNotFoundError('The bundled project assets are missing.')
    root.mkdir(parents=True, exist_ok=True)
    created = []
    preserved = []
    for source in sources:
        relative = source.relative_to(assets)
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with destination.open('xb') as stream:
                stream.write(source.read_bytes())
            created.append(relative.as_posix())
        except FileExistsError:
            preserved.append(relative.as_posix())
    return {'status': 'initialized', 'project': str(root),
            'created': created, 'preserved': preserved}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, help='Directory for the course archive.')
    args = parser.parse_args()
    try:
        result = initialize(args.project)
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()

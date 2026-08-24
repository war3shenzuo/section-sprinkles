#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description='Verify generated images against manifest.json.')
    parser.add_argument('--update', action='store_true', help='Update item status and image metadata.')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    manifest_path = root / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    generated = 0
    errors = []

    for item in manifest['items']:
        image_path = root / item['image']
        if not image_path.is_file():
            item['status'] = 'pending'
            item.pop('width', None)
            item.pop('height', None)
            item.pop('bytes', None)
            continue

        try:
            with Image.open(image_path) as image:
                image.verify()
            with Image.open(image_path) as image:
                width, height = image.size
                image_format = image.format
            if image_format != 'WEBP':
                errors.append(f'{item["id"]}: expected WEBP, got {image_format}')
                continue
            if width < 900 or height < 500:
                errors.append(f'{item["id"]}: image is too small ({width}x{height})')
                continue
            generated += 1
            item['status'] = 'generated'
            item['width'] = width
            item['height'] = height
            item['bytes'] = image_path.stat().st_size
        except Exception as error:
            errors.append(f'{item["id"]}: {error}')

    if args.update:
        manifest_path.write_text(f'{json.dumps(manifest, ensure_ascii=False, indent=2)}\n', encoding='utf-8')

    print(json.dumps({
        'expected': manifest['total'],
        'generated': generated,
        'pending': manifest['total'] - generated,
        'errors': errors
    }, ensure_ascii=False, indent=2))

    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()


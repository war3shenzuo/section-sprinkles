#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    taxonomy = json.loads((ROOT / 'tag-taxonomy.json').read_text(encoding='utf-8'))
    dimensions = taxonomy['dimensions']

    parser = argparse.ArgumentParser(description='Filter Section Sprinkles by structured tags.')
    parser.add_argument('--category', action='append', choices=[row['slug'] for row in manifest['categories']])
    parser.add_argument('--layout', action='append', choices=dimensions['layout'])
    parser.add_argument('--style', action='append', choices=dimensions['style'])
    parser.add_argument('--element', action='append', choices=dimensions['elements'])
    parser.add_argument('--density', choices=dimensions['density'])
    parser.add_argument('--tone', action='append', choices=dimensions['tone'])
    parser.add_argument('--use-case', dest='use_case', action='append', choices=dimensions['useCases'])
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--json', action='store_true', help='Emit matching manifest items as JSON.')
    args = parser.parse_args()

    if args.limit < 1:
        parser.error('--limit must be positive')

    requested = {
        'layout': args.layout or [],
        'style': args.style or [],
        'elements': args.element or [],
        'tone': args.tone or [],
        'useCases': args.use_case or []
    }
    matches = []
    for item in manifest['items']:
        tags = item.get('tags', {})
        if args.category and item['category'] not in args.category:
            continue
        if args.density and tags.get('density') != args.density:
            continue
        if any(not set(values).issubset(tags.get(dimension, [])) for dimension, values in requested.items()):
            continue
        matches.append(item)

    matches = matches[:args.limit]
    if args.json:
        print(json.dumps(matches, ensure_ascii=False, indent=2))
        return

    if not matches:
        print('No matching references.')
        return

    for item in matches:
        tags = item['tags']
        layout = '、'.join(dimensions['layout'][value]['zh'] for value in tags['layout'])
        style = '、'.join(dimensions['style'][value]['zh'] for value in tags['style'])
        elements = '、'.join(dimensions['elements'][value]['zh'] for value in tags['elements'])
        density = dimensions['density'][tags['density']]['zh']
        print(f'{item["id"]}\t{item["image"]}\t{layout}\t{style}\t{density}\t{elements}')


if __name__ == '__main__':
    main()

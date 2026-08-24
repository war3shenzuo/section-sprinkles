#!/usr/bin/env python3

import argparse
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser(description='Build a contact sheet for gallery QA.')
    parser.add_argument('output', type=Path)
    parser.add_argument('images', nargs='+', type=Path)
    parser.add_argument('--columns', type=int, default=4)
    parser.add_argument('--thumb-width', type=int, default=384)
    args = parser.parse_args()

    label_height = 36
    thumb_height = round(args.thumb_width * 2 / 3)
    rows = ceil(len(args.images) / args.columns)
    sheet = Image.new('RGB', (args.columns * args.thumb_width, rows * (thumb_height + label_height)), '#f2f2f2')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=18)

    for index, path in enumerate(args.images):
        with Image.open(path) as source:
            image = source.convert('RGB')
            image.thumbnail((args.thumb_width, thumb_height), Image.Resampling.LANCZOS)
        column = index % args.columns
        row = index // args.columns
        x = column * args.thumb_width
        y = row * (thumb_height + label_height)
        sheet.paste(image, (x, y))
        draw.text((x + 10, y + thumb_height + 8), path.stem, fill='#111111', font=font)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, format='PNG', optimize=True)
    print(args.output)


if __name__ == '__main__':
    main()


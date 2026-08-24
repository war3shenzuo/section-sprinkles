#!/usr/bin/env python3

import argparse
from pathlib import Path

from PIL import Image, ImageOps


def main():
    parser = argparse.ArgumentParser(description='Normalize a generated gallery image as WebP.')
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--reference', type=Path, help='Match the source canvas size and aspect ratio.')
    parser.add_argument('--max-width', type=int, default=1600)
    parser.add_argument('--quality', type=int, default=84)
    args = parser.parse_args()

    if not args.source.is_file():
        raise SystemExit(f'Source image does not exist: {args.source}')

    args.destination.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(args.source) as source:
        image = ImageOps.exif_transpose(source).convert('RGB')
        if args.reference:
            with Image.open(args.reference) as reference:
                target_size = reference.size
            image = ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)
        elif image.width > args.max_width:
            height = round(image.height * args.max_width / image.width)
            image = image.resize((args.max_width, height), Image.Resampling.LANCZOS)
        image.save(
            args.destination,
            format='WEBP',
            quality=args.quality,
            method=6,
            exif=b'',
            xmp=b''
        )

    with Image.open(args.destination) as result:
        if result.width < 900 or result.height < 500:
            raise SystemExit(f'Output is unexpectedly small: {result.width}x{result.height}')
        print(f'{args.destination}: {result.width}x{result.height}, {args.destination.stat().st_size} bytes')


if __name__ == '__main__':
    main()

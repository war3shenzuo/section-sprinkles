#!/usr/bin/env python3

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageFilter, ImageStat


ROOT = Path(__file__).resolve().parents[1]
TAG_KEYS = ('layout', 'style', 'elements', 'density', 'tone', 'useCases')

CATEGORY_TAGS = {
    'hero': {
        'layout': [],
        'elements': ['headline', 'body-copy', 'cta'],
        'tone': ['modern', 'decisive', 'professional'],
        'useCases': ['product-marketing', 'saas', 'startup']
    },
    'pricing': {
        'layout': ['cards', 'grid'],
        'elements': ['headline', 'pricing', 'comparison', 'cta'],
        'tone': ['analytical', 'decisive', 'trustworthy'],
        'useCases': ['saas', 'product-marketing', 'ecommerce']
    },
    'contact': {
        'layout': [],
        'elements': ['headline', 'form', 'contact-info', 'cta'],
        'tone': ['friendly', 'approachable', 'trustworthy'],
        'useCases': ['lead-generation', 'corporate', 'local-business']
    },
    'comparison': {
        'layout': ['table'],
        'elements': ['headline', 'comparison', 'table', 'cta'],
        'tone': ['analytical', 'informative', 'professional'],
        'useCases': ['saas', 'b2b', 'product-marketing']
    },
    'faq': {
        'layout': ['cards'],
        'elements': ['headline', 'faq', 'accordion'],
        'tone': ['informative', 'friendly', 'trustworthy'],
        'useCases': ['customer-support', 'saas', 'ecommerce']
    },
    'cta': {
        'layout': [],
        'elements': ['headline', 'cta'],
        'tone': ['decisive', 'friendly', 'modern'],
        'useCases': ['lead-generation', 'product-marketing', 'saas']
    },
    'support': {
        'layout': ['cards'],
        'elements': ['headline', 'contact-info', 'icons'],
        'tone': ['trustworthy', 'informative', 'friendly'],
        'useCases': ['customer-support', 'saas', 'b2b']
    },
    'case-studies': {
        'layout': [],
        'elements': ['headline', 'testimonial', 'metrics'],
        'tone': ['professional', 'trustworthy', 'human'],
        'useCases': ['b2b', 'corporate', 'consulting']
    },
    'features': {
        'layout': ['cards'],
        'elements': ['headline', 'product-ui', 'icons'],
        'tone': ['informative', 'modern', 'professional'],
        'useCases': ['saas', 'product-marketing', 'b2b']
    },
    'onboarding-flow': {
        'layout': ['process-flow'],
        'elements': ['headline', 'steps', 'progress', 'icons'],
        'tone': ['informative', 'friendly', 'professional'],
        'useCases': ['saas', 'customer-support', 'product-marketing']
    },
    'about': {
        'layout': [],
        'elements': ['headline', 'body-copy'],
        'tone': ['professional', 'human', 'inspiring'],
        'useCases': ['corporate', 'startup', 'portfolio']
    },
    'clients': {
        'layout': ['grid'],
        'elements': ['headline', 'logo-grid'],
        'tone': ['trustworthy', 'professional', 'informative'],
        'useCases': ['corporate', 'b2b', 'consulting']
    },
    'metrics': {
        'layout': ['dashboard'],
        'elements': ['headline', 'metrics', 'chart'],
        'tone': ['analytical', 'professional', 'trustworthy'],
        'useCases': ['corporate', 'b2b', 'product-marketing']
    },
    'team': {
        'layout': [],
        'elements': ['headline', 'portrait'],
        'tone': ['human', 'approachable', 'professional'],
        'useCases': ['recruitment', 'corporate', 'startup']
    },
    'culture': {
        'layout': [],
        'elements': ['headline', 'body-copy'],
        'tone': ['human', 'collaborative', 'inspiring'],
        'useCases': ['recruitment', 'corporate', 'community']
    },
    'footer': {
        'layout': ['multi-column', 'full-width'],
        'elements': ['navigation', 'contact-info', 'legal-links'],
        'tone': ['informative', 'professional', 'calm'],
        'useCases': ['corporate', 'saas', 'product-marketing']
    }
}


def unique(values):
    return list(dict.fromkeys(values))


def load_analysis(path):
    rows = {}
    with path.open(encoding='utf-8') as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            image_path = Path(row['path'])
            try:
                key = image_path.resolve().relative_to(ROOT.resolve()).as_posix()
            except ValueError:
                key = image_path.as_posix()
            if key in rows:
                raise ValueError(f'Duplicate analysis row for {key} at line {line_number}')
            rows[key] = row
    return rows


def image_metrics(path):
    with Image.open(path) as source:
        image = source.convert('RGB')
        image.thumbnail((320, 180), Image.Resampling.LANCZOS)
        gray = image.convert('L')
        histogram = gray.histogram()
        pixels = image.width * image.height
        white_ratio = sum(histogram[245:]) / pixels
        midtone_ratio = sum(histogram[45:225]) / pixels
        saturation = ImageStat.Stat(image.convert('HSV')).mean[1] / 255
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_histogram = edges.histogram()
        edge_ratio = sum(edge_histogram[42:]) / pixels

        dark_thirds = []
        for index in range(3):
            left = round(index * image.width / 3)
            right = round((index + 1) * image.width / 3)
            region = gray.crop((left, 0, right, image.height))
            region_histogram = region.histogram()
            region_pixels = region.width * region.height
            dark_thirds.append(sum(region_histogram[:225]) / region_pixels)

    return {
        'whiteRatio': white_ratio,
        'midtoneRatio': midtone_ratio,
        'saturation': saturation,
        'edgeRatio': edge_ratio,
        'darkThirds': dark_thirds
    }


def has_any(text, patterns):
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def infer_layout(category, texts, metrics, face_count):
    layout = list(CATEGORY_TAGS[category]['layout'])
    centers = [entry['box']['x'] + entry['box']['width'] / 2 for entry in texts]
    left = sum(center < 0.42 for center in centers)
    middle = sum(0.42 <= center <= 0.58 for center in centers)
    right = sum(center > 0.58 for center in centers)
    occupied_bins = sum(
        any(start <= center < end for center in centers)
        for start, end in ((0, .25), (.25, .5), (.5, .75), (.75, 1.01))
    )

    if left >= 3 and right >= 3 and middle <= max(4, len(centers) * .28):
        layout.append('split')
    if occupied_bins >= 3 and len(centers) >= 12:
        layout.append('multi-column')
    if centers and sum(abs(center - .5) for center in centers) / len(centers) < .21:
        layout.append('centered')
    if face_count and abs(metrics['darkThirds'][0] - metrics['darkThirds'][2]) > .035:
        layout.append('asymmetric')

    joined = ' '.join(entry['text'] for entry in texts)
    years = set(re.findall(r'(?<!\d)20\d{2}(?!\d)', joined))
    if has_any(joined, [r'时间线', r'历程', r'沿革', r'发展史']) or len(years) >= 2:
        layout.append('timeline')
    if has_any(joined, [r'表格', r'比较', r'方案', r'项目.*状态', r'类别.*数量']):
        if category in {'comparison', 'pricing', 'metrics', 'support'}:
            layout.append('table')
    if category in {'pricing', 'faq', 'support', 'features', 'team', 'clients'} and len(texts) >= 14:
        layout.append('cards')
    if category in {'clients', 'team'} and (occupied_bins >= 3 or face_count >= 3):
        layout.append('grid')

    return unique(layout)[:3] or ['full-width']


def infer_elements(item_id, category, texts, faces, barcodes, metrics):
    elements = list(CATEGORY_TAGS[category]['elements'])
    joined = ' '.join(entry['text'] for entry in texts)
    character_count = sum(len(entry['text']) for entry in texts)

    if character_count >= 90:
        elements.append('body-copy')
    if faces:
        elements.extend(['portrait', 'photography'])
    if len(faces) >= 3:
        elements.append('team-photo')
    if metrics['midtoneRatio'] > .24 and metrics['edgeRatio'] > .055:
        elements.append('photography')
    elif category in {'onboarding-flow', 'culture', 'features'} and metrics['edgeRatio'] > .045:
        elements.append('illustration')
    if barcodes or item_id in {'cta-10', 'footer-10'}:
        elements.append('qr-code')

    keyword_elements = [
        ('search', [r'搜索', r'查找', r'search']),
        ('form', [r'输入', r'提交', r'申请', r'注册', r'表单']),
        ('contact-info', [r'联系', r'咨询', r'电话', r'邮箱', r'邮件', r'@']),
        ('newsletter', [r'订阅', r'电子报', r'邮件地址', r'邮箱地址', r'newsletter']),
        ('download', [r'下载', r'资料', r'白皮书']),
        ('video', [r'视频', r'播放', r'观看']),
        ('audio', [r'音频', r'播客', r'语音']),
        ('map', [r'地图', r'交通路线', r'所在地', r'办公地点']),
        ('calendar', [r'日历', r'预约', r'日期', r'时段']),
        ('status', [r'状态', r'正常运行', r'维护', r'故障']),
        ('testimonial', [r'客户心声', r'客户评价', r'访谈', r'用户评价']),
        ('timeline', [r'历程', r'沿革', r'时间线', r'发展史']),
        ('social-links', [r'Instagram', r'LinkedIn', r'YouTube', r'\bX\b']),
        ('product-ui', [r'仪表盘', r'项目', r'设置', r'工作区', r'产品界面'])
    ]
    for element, patterns in keyword_elements:
        if has_any(joined, patterns):
            elements.append(element)
    if len(set(re.findall(r'(?<!\d)20\d{2}(?!\d)', joined))) >= 2:
        elements.append('timeline')

    return unique(elements)


def infer_style(category, layout, elements, metrics):
    style = []
    if metrics['saturation'] < .085:
        style.append('monochrome')
    if metrics['whiteRatio'] > .53:
        style.append('minimal')
    if metrics['whiteRatio'] > .71:
        style.append('airy')
    if 'photography' in elements:
        style.append('photography-led')
    if 'illustration' in elements and 'photography' not in elements:
        style.append('illustration-led')
    if category in {'support', 'features', 'onboarding-flow'} or 'product-ui' in elements:
        style.append('interface-led')
    if category == 'metrics' or 'chart' in elements:
        style.append('data-driven')
    if category in {'about', 'culture', 'case-studies', 'team'} and 'photography' in elements:
        style.append('editorial')
    if 'cards' in layout:
        style.append('card-based')
    return unique(style)[:5]


def infer_density(texts, metrics):
    character_count = sum(len(entry['text']) for entry in texts)
    score = len(texts) + character_count / 75 + (1 - metrics['whiteRatio']) * 28
    if score < 19:
        return 'low'
    if score < 37:
        return 'medium'
    return 'high'


def infer_use_cases(category, joined):
    use_cases = list(CATEGORY_TAGS[category]['useCases'])
    keyword_cases = [
        ('recruitment', [r'招聘', r'加入我们', r'职位', r'成员募集']),
        ('healthcare', [r'医疗', r'健康', r'诊疗', r'患者']),
        ('finance', [r'金融', r'银行', r'投资', r'资产', r'保险']),
        ('manufacturing', [r'制造', r'工厂', r'生产', r'工业']),
        ('education', [r'教育', r'学习', r'课程', r'培训']),
        ('ecommerce', [r'购物', r'商品', r'订单', r'配送', r'购买']),
        ('events', [r'活动', r'研讨会', r'讲座', r'报名', r'演示']),
        ('community', [r'社区', r'社群', r'成员交流']),
        ('consulting', [r'咨询服务', r'顾问', r'专业咨询', r'专业人士']),
        ('customer-support', [r'帮助中心', r'支持中心', r'客服', r'故障']),
        ('local-business', [r'门店', r'营业时间', r'办公室', r'交通'])
    ]
    for use_case, patterns in keyword_cases:
        if has_any(joined, patterns):
            use_cases.append(use_case)
    return unique(use_cases)[:5]


def build_tags(item, analysis):
    category = item['category']
    texts = analysis['texts']
    faces = analysis['faces']
    barcodes = analysis['barcodes']
    metrics = image_metrics(ROOT / item['image'])
    layout = infer_layout(category, texts, metrics, len(faces))
    elements = infer_elements(item['id'], category, texts, faces, barcodes, metrics)
    style = infer_style(category, layout, elements, metrics)
    joined = ' '.join(entry['text'] for entry in texts)
    tone = list(CATEGORY_TAGS[category]['tone'])
    if faces and 'human' not in tone:
        tone.append('human')

    return {
        'layout': layout,
        'style': style,
        'elements': elements,
        'density': infer_density(texts, metrics),
        'tone': unique(tone)[:4],
        'useCases': infer_use_cases(category, joined)
    }


def validate(manifest, taxonomy):
    allowed = {
        dimension: set(values)
        for dimension, values in taxonomy['dimensions'].items()
    }
    errors = []
    coverage = Counter()
    category_fingerprints = defaultdict(set)

    for item in manifest['items']:
        tags = item.get('tags')
        if not isinstance(tags, dict):
            errors.append(f'{item["id"]}: missing tags')
            continue
        if set(tags) != set(TAG_KEYS):
            errors.append(f'{item["id"]}: expected tag keys {TAG_KEYS}, got {tuple(tags)}')
            continue
        for dimension in TAG_KEYS:
            value = tags[dimension]
            values = [value] if dimension == 'density' else value
            if dimension != 'density' and (not isinstance(value, list) or not value):
                errors.append(f'{item["id"]}: {dimension} must be a non-empty list')
                continue
            if len(values) != len(set(values)):
                errors.append(f'{item["id"]}: duplicate {dimension} tags')
            unknown = set(values) - allowed[dimension]
            if unknown:
                errors.append(f'{item["id"]}: unknown {dimension} tags {sorted(unknown)}')
            for tag in values:
                coverage[f'{dimension}:{tag}'] += 1
        fingerprint = json.dumps(tags, sort_keys=True, ensure_ascii=False)
        category_fingerprints[item['category']].add(fingerprint)

    for category, fingerprints in category_fingerprints.items():
        if len(fingerprints) < 2:
            errors.append(f'{category}: all items have identical tags')

    return errors, coverage, category_fingerprints


def main():
    parser = argparse.ArgumentParser(description='Generate and validate structured gallery tags.')
    parser.add_argument('--analysis', type=Path, help='NDJSON from analyze-images.swift.')
    parser.add_argument('--write', action='store_true', help='Write generated tags to manifest.json.')
    parser.add_argument('--check', action='store_true', help='Validate existing manifest tags only.')
    args = parser.parse_args()

    manifest_path = ROOT / 'manifest.json'
    taxonomy_path = ROOT / 'tag-taxonomy.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    taxonomy = json.loads(taxonomy_path.read_text(encoding='utf-8'))

    if not args.check:
        if not args.analysis:
            parser.error('--analysis is required unless --check is used')
        analysis = load_analysis(args.analysis)
        missing = [item['image'] for item in manifest['items'] if item['image'] not in analysis]
        if missing:
            raise SystemExit(f'Missing analysis for {len(missing)} images; first: {missing[0]}')
        for item in manifest['items']:
            item['tags'] = build_tags(item, analysis[item['image']])
        manifest['version'] = 2
        manifest['tagTaxonomy'] = 'tag-taxonomy.json'
        manifest['tagDimensions'] = list(TAG_KEYS)

    errors, coverage, category_fingerprints = validate(manifest, taxonomy)
    report = {
        'items': len(manifest['items']),
        'tagged': sum('tags' in item for item in manifest['items']),
        'dimensions': list(TAG_KEYS),
        'distinctTagsUsed': len(coverage),
        'density': {
            level: coverage[f'density:{level}']
            for level in ('low', 'medium', 'high')
        },
        'variantsByCategory': {
            category: len(fingerprints)
            for category, fingerprints in sorted(category_fingerprints.items())
        },
        'errors': errors
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if errors:
        raise SystemExit(1)
    if args.write:
        manifest_path.write_text(
            f'{json.dumps(manifest, ensure_ascii=False, indent=2)}\n',
            encoding='utf-8'
        )


if __name__ == '__main__':
    main()

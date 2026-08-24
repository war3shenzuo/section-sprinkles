import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const manifestPath = join(root, 'manifest.json');
const previousManifest = existsSync(manifestPath)
  ? JSON.parse(readFileSync(manifestPath, 'utf8'))
  : null;
const previousItems = new Map(
  (previousManifest?.items || []).map((item) => [item.id, item])
);

const categories = [
  ['hero', '首屏', 'Hero', 33, '建立清晰的第一印象，并把核心价值与主要行动放在视觉焦点上。'],
  ['pricing', '定价', 'Pricing', 33, '帮助用户快速理解方案差异、价格结构与推荐选择。'],
  ['contact', '联系', 'Contact', 33, '降低沟通门槛，用友好的表单或联系入口开启对话。'],
  ['comparison', '对比', 'Comparison', 33, '用可扫描的结构比较选项、能力与适用场景。'],
  ['faq', '常见问题', 'FAQ', 33, '组织高频疑问，减少决策阻力并建立信任。'],
  ['cta', '行动号召', 'Call to action', 33, '用单一明确的下一步推动用户行动。'],
  ['support', '支持', 'Support', 33, '呈现帮助渠道、响应承诺与自助资源。'],
  ['case-studies', '客户案例', 'Case studies', 33, '通过问题、过程与结果讲述真实价值。'],
  ['features', '功能介绍', 'Features', 33, '把核心能力转化为容易理解的用户收益。'],
  ['onboarding-flow', '使用流程', 'Onboarding flow', 33, '用少量步骤解释开始使用产品的路径。'],
  ['about', '关于我们', 'About', 33, '表达团队的使命、方法与独特视角。'],
  ['clients', '合作客户', 'Clients', 33, '用客户组合、行业分布或合作关系建立可信度。'],
  ['metrics', '数据成果', 'Metrics', 33, '用关键数字强调规模、效率或业务成果。'],
  ['team', '团队', 'Team', 41, '介绍一起创造产品的人，并传递专业感与亲和力。'],
  ['culture', '文化', 'Culture', 33, '用场景、原则和日常细节呈现组织文化。'],
  ['footer', '页脚', 'Footer', 33, '在页面结尾组织导航、联系信息与最后一次行动机会。']
];

const items = [];
let sequence = 1;

for (const [slug, zh, en, count, purpose] of categories) {
  for (let number = 1; number <= count; number += 1) {
    const id = `${slug}-${String(number).padStart(2, '0')}`;
    const previous = previousItems.get(id);
    const item = {
      sequence,
      id,
      category: slug,
      categoryZh: zh,
      categoryEn: en,
      image: `gallery/${slug}/${id}.webp`,
      status: previous?.status || 'pending'
    };
    for (const key of ['width', 'height', 'bytes', 'tags']) {
      if (previous?.[key] !== undefined) {
        item[key] = previous[key];
      }
    }
    items.push(item);
    sequence += 1;
  }
}

const manifest = {
  name: 'Section Sprinkles',
  version: previousManifest?.version || 1,
  language: 'zh-CN',
  total: items.length,
  categories: categories.map(([slug, zh, en, count, purpose]) => ({
    slug,
    nameZh: zh,
    nameEn: en,
    count,
    purpose
  })),
  items
};

for (const key of ['tagTaxonomy', 'tagDimensions']) {
  if (previousManifest?.[key] !== undefined) {
    manifest[key] = previousManifest[key];
  }
}

if (manifest.total !== 536) {
  throw new Error(`Expected 536 items, received ${manifest.total}`);
}

writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`Wrote ${manifest.total} items to manifest.json`);

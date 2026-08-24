# Query examples

Read this file when a request needs help narrowing the gallery.

## By intent

- Strong first impression: `hero`
- Plan selection or monetization: `pricing`, `comparison`, `faq`
- Product explanation: `features`, `onboarding-flow`, `metrics`
- Trust building: `clients`, `case-studies`, `team`, `about`
- Conversion or help: `cta`, `contact`, `support`
- Employer brand: `team`, `culture`, `about`
- Page completion: `footer`

## By structured tags

Use `scripts/query-gallery.py` from the repository root. Multiple values in the same dimension are matched together.

```bash
# Low-density hero references with people and a split layout
python3 scripts/query-gallery.py \
  --category hero \
  --layout split \
  --element portrait \
  --density low

# Analytical B2B references with charts
python3 scripts/query-gallery.py \
  --tone analytical \
  --element chart \
  --use-case b2b \
  --json

# Friendly support references with search
python3 scripts/query-gallery.py \
  --category support \
  --tone friendly \
  --element search
```

Tag slugs and their Chinese and English labels are defined in `tag-taxonomy.json`.

## Selection heuristics

1. Match information structure before visual style.
2. Prefer a reference with similar content density to the target product.
3. Check whether its emphasis still works at mobile width.
4. Use palette as inspiration only after hierarchy and layout fit.
5. If two references are useful, assign each a distinct role such as hierarchy versus color; avoid vague style blending.

## Prompt recipes

```text
$section-sprinkles 帮我找 3 个低信息密度、带人物照片的首屏，并说明各自适合什么产品。

$section-sprinkles 对比 pricing-04 和 pricing-19 的信息层级，推荐一个更适合 B2B SaaS 的方向。

$section-sprinkles 把 hero-07 中的文字替换成下面这组中文文案；除文字外，版式、风格、颜色、图片和尺寸都不要改变。

$section-sprinkles 参考 hero-05，为精品旅行服务做一个可直接打开的响应式 HTML/CSS 首屏 Demo。

$section-sprinkles 从首屏、功能介绍和 CTA 各挑一张风格一致的参考，组成一套落地页设计方向。
```

# Section Sprinkles ✨

[简体中文](README.md) · [English](README_EN.md)

## **An open gallery of Chinese web-section ideas for product and design teams**

**536 Chinese web-section references · 16 common patterns · fully tagged**

Quickly compare hierarchy, layout, color, and visual rhythm, then turn references into your own design direction.

Use the images as inspiration for new designs. For text-only localization, preserve the original style, layout, colors, imagery, and dimensions.

## How to use it

- Browse `gallery/` by section category.
- Search `manifest.json` by category, item ID, or tag.
- Combine filters with `scripts/query-gallery.py`.

Every image has layout, style, element, density, tone, and use-case tags. See `tag-taxonomy.json` for definitions.

```bash
python3 scripts/query-gallery.py \
  --category hero \
  --layout split \
  --element portrait \
  --density low
```

## Use it with AI tools

Works with Codex, Claude Code, WorkBuddy / CodeBuddy Code, and other AI tools that support Skills.

Send this sentence to your AI tool to install it:

> Install the `section-sprinkles` Skill from this GitHub repository, then show me how to use it directly with natural language: https://github.com/war3shenzuo/section-sprinkles

After installation, use natural language:

- “Find three low-density Chinese hero references with portraits.”
- “Replace the text in `hero-07` with Chinese copy and preserve every other visual element.”
- “Use `hero-07` as inspiration for an original Chinese product hero.”

## Demos

### Demo 1: minimal hero candidates

`hero + minimal` returns six candidates. [View the selection record](demo/search-results/).

<img src="demo/search-results/preview.webp" width="100%" alt="Six minimal Chinese hero candidates">

### Demo 2: B2B metrics candidates

`metrics + chart + B2B + analytical` returns six candidates. [View the selection record](demo/b2b-metrics/).

<img src="demo/b2b-metrics/preview.webp" width="100%" alt="Six B2B metrics-section candidates">

A separate [working responsive frontend demo](demo/travel-search/) is also available.

## License

Released under the [MIT License](LICENSE).

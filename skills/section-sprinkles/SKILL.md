---
name: section-sprinkles
description: Find and apply design references from the Section Sprinkles gallery when planning, localizing, or implementing Chinese web sections. Use for selecting layouts, comparing section patterns, translating text in a reference without changing its visual style, or turning a reference into an original interface; do not use for unrelated illustration work.
---

# Section Sprinkles

Use the gallery to accelerate design decisions. Preserve a reference exactly when the user requests text-only localization; create an original expression when the user requests a new design or implementation.

## Choose the mode

- **Select:** Find, compare, and explain suitable references without modifying them.
- **Localize:** Translate or replace text in a specified image. Preserve its composition, spacing, typography character, colors, imagery, effects, dimensions, and all non-text content. Change only the requested text.
- **Implement:** Turn one or more references into an original, responsive interface for the user's actual brand and content.

## Workflow

1. Locate the repository root and read `manifest.json` plus `tag-taxonomy.json`.
2. Filter by the requested section type, layout, style, elements, density, tone, or use case. Prefer `python3 scripts/query-gallery.py` for reproducible filtering. Start with one category and shortlist no more than three images.
3. Inspect the shortlisted images before recommending one. Describe the useful hierarchy, grid, spacing, color relationship, and interaction pattern rather than merely naming a file.
4. Ask for missing brand or content constraints only when they would materially change the direction. Otherwise, make a reasonable choice and proceed.
5. Complete the selected mode:
   - For text-only localization, transcribe the visible copy, translate it for meaning and available space, edit only the text regions, and visually verify the result against the original.
   - For a new design or implementation, use the selected references as principles while adapting copy, density, colors, components, accessibility, and responsive behavior to the actual product.
6. Report the selected image paths and explain briefly what each contributed.

## Gallery map

The gallery contains 536 images across these category slugs:

- `hero`, `pricing`, `contact`, `comparison`, `faq`, `cta`
- `support`, `case-studies`, `features`, `onboarding-flow`
- `about`, `clients`, `metrics`, `team`, `culture`, `footer`

Use `manifest.json` as the source of truth for IDs, Chinese and English category names, generation status, dimensions, image paths, and per-image tags. Use `tag-taxonomy.json` to translate tag slugs into Chinese or English labels. Inspect shortlisted images themselves before making a final recommendation. Read [references/query-examples.md](references/query-examples.md) only when a request needs example filters or selection heuristics.

## Constraints

- Treat gallery images as references, not drop-in production assets unless the user explicitly asks to use or localize one.
- For text-only localization, do not redesign, restyle, rearrange, crop, or replace non-text elements.
- For new implementations, do not reproduce a reference verbatim. Preserve the underlying design idea while changing the expression for the product at hand.
- Prefer real product copy over placeholder text.
- When implementing, include responsive behavior and accessible contrast instead of reproducing only the screenshot's desktop appearance.
- Never invent permission to publish, deploy, or alter an external repository.

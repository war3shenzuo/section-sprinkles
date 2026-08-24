# 极简首屏筛选 Demo

这个 Demo 展示 `$section-sprinkles` 如何根据关键词筛选多个可采纳案例。为了便于横向比较，README 将这次筛选出的 6 个候选集中展示在一张预览图中。

## 输入

```text
$section-sprinkles 搜索 6 个极简中文首屏参考，并说明每个案例值得借鉴的地方。
```

## 筛选条件

```bash
python3 scripts/query-gallery.py \
  --category hero \
  --style minimal \
  --limit 6
```

## 候选结果

[`hero-01`](../../gallery/hero/hero-01.webp)、[`hero-02`](../../gallery/hero/hero-02.webp)、[`hero-03`](../../gallery/hero/hero-03.webp)、[`hero-05`](../../gallery/hero/hero-05.webp)、[`hero-06`](../../gallery/hero/hero-06.webp)、[`hero-07`](../../gallery/hero/hero-07.webp)

## README 展示截图

![6 个极简中文首屏候选的 3×2 拼图](preview.webp)

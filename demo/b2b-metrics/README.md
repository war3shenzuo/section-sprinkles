# B2B 数据成果区块筛选 Demo

这个 Demo 展示 `$section-sprinkles` 如何根据业务场景、元素和语气筛选设计参考，并在 README 中集中展示候选结果。

## 输入

```text
$section-sprinkles 查找 6 个适合 B2B SaaS、包含图表且语气理性的数据成果区块，并说明各自适合展示什么指标。
```

## 筛选条件

```bash
python3 scripts/query-gallery.py \
  --category metrics \
  --element chart \
  --tone analytical \
  --use-case b2b \
  --limit 6
```

## 候选结果

[`metrics-01`](../../gallery/metrics/metrics-01.webp)、[`metrics-02`](../../gallery/metrics/metrics-02.webp)、[`metrics-03`](../../gallery/metrics/metrics-03.webp)、[`metrics-04`](../../gallery/metrics/metrics-04.webp)、[`metrics-05`](../../gallery/metrics/metrics-05.webp)、[`metrics-06`](../../gallery/metrics/metrics-06.webp)

## README 展示截图

![6 个 B2B 数据成果区块候选](preview.webp)

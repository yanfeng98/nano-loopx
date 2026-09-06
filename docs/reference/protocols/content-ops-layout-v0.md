# Content-Ops 布局 v0

`content_ops_layout_*_v0` 使内容呈现成为可评审的 LoopX 契约。它分离三个 owner：

- LoopX core 拥有内置模板、类型化页面角色、确定性紧凑性阈值与验收结果。
- 写作或平台适配器拥有文案、页面选择、叙事结构、作者语气与渲染。
- 渲染器拥有像素并发出紧凑测量包；LoopX 不增加图像处理依赖，也不摄取草稿正文。

这是机器强制的验收检查，不是可选的散文指导。

## 模板库

```bash
loopx content-ops template-list --format json
loopx content-ops template-show \
  --template-id light-serif-longform \
  --format json
```

内置 `content_ops_layout_template_catalog_v0` 目前包含：

- `light-serif-longform` 用于密集的分析型叙事；
- `monochrome-editorial` 用于高对比技术评论；
- `product-brief` 用于问题/机制/边界摘要；
- `control-plane-hybrid` 用于散文加状态、gate 与 evidence 工件。

模板定义画布尺寸、安全区、密度限制、页面原型与可移植样式 token。它们不包含项目名、私有路径、草稿正文或 provider 凭据。

所有内置模板把 `density.role_overrides.cover.min` 设为 `0.90`、`max` 设为 `0.98`。封面默认刻意比普通页面严格：安全区高度的至少 90% 必须被有意义的内容边界占据。装饰性规则线、索引、页码与页脚不计入该密度。

每个内置模板还暴露相同的 `page_sequence` 默认值：

```json
{
  "first_role": "cover",
  "density_order": "first_page_maximum",
  "interior_min": 0.80
}
```

首个规划页必须是封面，且其测量密度必须至少与后续每一页相同。封面与末页之间的页面以 `0.80` 为密度下限，或采用更严格的角色/模板下限（若存在）。末页保持其自己的收尾/CTA 角色限制，使有意的综合页无需模仿密集的分析中间页。

这些默认值改变了先前合法但现在稀疏或错序页集的验收结果：封面低于 `0.90`、内部页低于 `0.80`、非封面首页，或后续页比封面更密，现在都返回类型化修订失败。发布权限保持不变。

## 类型化的计划

渲染前构建计划：

```bash
loopx content-ops layout-plan \
  --item-id plugin-scaling-note \
  --template-id light-serif-longform \
  --page p01:cover:source-system \
  --page p02:argument:source-system \
  --page p03:evidence:source-system \
  --page p04:closing:creator-system \
  --required-role cover \
  --required-role argument \
  --required-role evidence \
  --required-role closing \
  --closing-role closing \
  --generated-at 2026-08-15T12:00:00+08:00 \
  --format json
```

角色被类型化为 `cover`、`argument`、`mechanism`、`evidence`、`boundary`、`closing` 或 `cta`。项目特定的叙事义务——例如以创作者语气结尾或从一个命名主题桥接到另一个——仍留在写作适配器或 item 局部评审计划中。LoopX 不把它们普遍化，也不从散文子串中推断它们。

## 渲染器测量

渲染器发出 `content_ops_layout_measurement_v0`：

```json
{
  "schema_version": "content_ops_layout_measurement_v0",
  "plan_id": "layout:plugin-scaling-note:light-serif-longform",
  "template_id": "light-serif-longform",
  "pages": [
    {
      "page_id": "p01",
      "asset_ref": "images/p01.jpg",
      "canvas": {"width": 1440, "height": 1920},
      "meaningful_content_bounds": {"top": 154, "bottom": 1364},
      "checks": {
        "overflow": false,
        "collision": false,
        "single_character_line": false
      }
    }
  ]
}
```

`asset_ref` 必须是相对公开安全引用。有意义边界排除装饰性规则线、页码与页脚，使它们无法让稀疏页面显得充实。

## 验收

```bash
loopx content-ops layout-check \
  --plan-json layout-plan.json \
  --measurement-json layout-measurement.json \
  --format json
```

`content_ops_layout_check_packet_v0` 仅在以下条件满足时返回 `pass`：

- 测量页面 id 与计划精确匹配；
- 首页面角色为 `cover`，且密度至少不低于每个后续页面；
- 每个内部页满足内置 `0.80` 密度下限；
- 所有必需角色都存在，且末页具有规划的收尾角色；
- 画布与密度满足所选模板与角色；
- overflow、collision 与单字符行检查显式为 false；
- 每个渲染器安全检查显式满足。

该包始终保持 `autopublish_allowed=false`。布局验收绝不授予 provider 访问、发布权限或对内容正文的批准。

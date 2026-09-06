# 创作者-操作者假数据 Storyboard

> [English](creator-ops-fake-data-storyboard.md)

这个 storyboard 把创作者-操作者案例转成一个前端就绪的公开 demo 流程。它只使用合成数据。它不是爬虫、发布工具,也不是关于真实创作者表现的声明。

目标是展示 LoopX 如何让长程创作者 agent Loop 清晰可读:

- 研究可以继续;
- 发布保持关卡化;
- 反馈改变计划;
- 私有素材与公开 demo 数据保持分离。

## 界面形态

第一个 mock 应渲染为一个工作界面,而不是营销落地页。使用七个相互连接的面板:

1. 趋势发现
2. 偏好地图
3. 洞察板
4. 草稿队列
5. 素材库
6. 人类反馈
7. 受控 replan

每个面板应展示一个控制面对象或一次转换。避免原始 agent 日志、提示文本、截图、平台数据和实时浏览输出。

## 假数据 Fixture

这个 mock 可以直接使用这个小 fixture。

```json
{
  "goal": "Keep a weekly creator-operator research loop moving.",
  "mode": "safe_side_path",
  "gate": {
    "label": "Publishing decision",
    "status": "waiting_on_user",
    "question": "Approve tone and source policy before publishing?"
  },
  "trend_candidates": [
    {
      "id": "trend_ai_note_workflows",
      "title": "AI note workflows for solo operators",
      "fit": "high",
      "boundary": "synthetic_public_demo"
    },
    {
      "id": "trend_research_to_shortform",
      "title": "Short-form content from long research notes",
      "fit": "medium",
      "boundary": "synthetic_public_demo"
    },
    {
      "id": "trend_human_approval_before_publish",
      "title": "Human approval before agent publication",
      "fit": "high",
      "boundary": "synthetic_public_demo"
    }
  ],
  "preference_map": [
    "practical case studies",
    "plain evidence boundaries",
    "avoid growth-hack language",
    "show what the agent will not do"
  ],
  "insight_board": [
    {
      "insight": "A long-running creator agent needs a dashboard, not another hidden prompt.",
      "source_status": "synthetic"
    },
    {
      "insight": "The user gate is not a failure; it is the product boundary.",
      "source_status": "synthetic"
    },
    {
      "insight": "Safe side paths keep research useful while publishing waits.",
      "source_status": "synthetic"
    }
  ],
  "draft_queue": [
    {
      "title": "How I keep a research agent from waiting forever",
      "status": "outline_ready",
      "gate": "tone_review"
    },
    {
      "title": "What a creator agent should show before it publishes",
      "status": "idea_only",
      "gate": "publish_policy"
    },
    {
      "title": "Material libraries as memory for creative work",
      "status": "source_map_needed",
      "gate": "no_publish_yet"
    }
  ],
  "material_library": [
    "reusable hooks",
    "source summaries",
    "phrasing examples",
    "rejected angles with reasons",
    "boundary notes"
  ],
  "feedback_options": [
    {
      "label": "This angle is useful",
      "effect": "reward_preference_hint"
    },
    {
      "label": "Too salesy",
      "effect": "draft_revision_todo"
    },
    {
      "label": "Do not use this source",
      "effect": "boundary_correction"
    },
    {
      "label": "Publish after tone review",
      "effect": "user_gate_decision"
    }
  ],
  "controlled_replan": {
    "next_action": "Revise the first draft angle using the practical-case-study preference.",
    "safe_side_path": "Continue organizing synthetic material-library examples.",
    "blocked_route": "Publishing waits for tone and source-policy approval."
  }
}
```

## 面板细节

### 1. 趋势发现

目的:展示候选主题以及它们为什么可能重要。

渲染:

- 三行候选;
- 契合度指示;
- 来源边界徽标。

不要渲染原始社交帖子或实时平台名。重点在于控制面可读性,而不是数据采集。

### 2. 偏好地图

目的:展示用户品味可以引导规划,而不必变成硬性关卡。

渲染:

- 偏好芯片;
- 一句话说明偏好是规划提示;
- 将硬权限关卡单独放一个徽标。

### 3. 洞察板

目的:把研究转化为可复用的候选洞察。

渲染:

- 洞察卡片;
- 来源状态;
- 当来源状态不是公开安全时,显示"需要审查"标记。

### 4. 草稿队列

目的:让草稿就绪度与关卡可见。

渲染:

- 草稿标题;
- 就绪状态;
- 关卡标签;
- 允许的安全旁路工作。

### 5. 素材库

目的:把记忆展示为受治理的素材,而不是原始转录转储。

渲染:

- 素材类别;
- 来源状态;
- 被拒绝角度说明。

### 6. 人类反馈

目的:让用户不必手动编辑状态即可引导。

把反馈按钮渲染为明确的控制面效果:

| 按钮 | 效果 |
| --- | --- |
| 这个角度有用 | reward / 偏好提示 |
| 太销售腔了 | 草稿修订 todo |
| 不要使用这个来源 | 边界修正 |
| 语调审查后发布 | 关卡决定 |

反馈类别与来源状态规则在
[creator-ops-feedback-boundary-contract.md](creator-ops-feedback-boundary-contract.md) 中定义。

### 7. 受控 Replan

目的:展示反馈如何改变 agent 的下一步动作。

渲染:

- 下一步动作;
- 安全旁路;
- 被阻塞路线;
- 验证预期。

replan 面板应清楚表明:在发布仍然等待时,agent 可以继续整理安全的合成素材。

## 前端验收标准

当以下条件满足时,第一个静态 mock 就合格:

- 每个可见数据项都来自假 fixture 或目录字段;
- 没有任何卡片需要实时平台访问;
- 没有用户反馈被当作隐藏记忆;
- 发布关卡在首屏可见;
- 安全旁路在被阻塞的发布路线旁边保持可见;
- 趋势、洞察、草稿与素材面板都显示来源边界;
- 该案例仍然能从 `docs/showcases/showcase-catalog.json` 渲染,而不抓取叙事案例页。

## 边界

这个 storyboard 可用于公共 README 图片、网站 mock 或静态 HTML demo。它不得包含真实用户草稿、私有偏好、平台截图、原始浏览痕迹、本地路径、凭据,或关于参与度、触达、转化、收入或模型质量提升的声明。

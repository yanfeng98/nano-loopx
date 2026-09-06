# 受守卫的上游 Issue 升级

> [English](upstream-issue-escalation.md)

使用此路由把已确认、可复用的 LoopX 产品缺口变成紧凑的上游 issue，而不泄漏
用户项目状态或制造 issue 刷屏。调用 self-repair 是诊断同意，不是发布同意。

## 1. 认定候选

issue 候选应满足以下全部条件：

- 负责层是公开 LoopX 产品、CLI、skill、安装器或控制面，而非用户项目；
- 行为在受支持的干净安装、公开/合成 fixture 或重复独立公开安全证据上复现；
- 对用户或操作员有具体影响；
- 持久跟踪或协调在直接修复或 PR 之外增加价值。

以下情况不要发布 issue：

- 一次性 agent 判断错误、陈旧本地状态或用户项目缺陷；
- docs 或直接回答可以解决的支持问题；
- 需要私有名称、任务标识符、仓库细节、本地路径、内部 URL、原始日志、轨迹或
  verifier 输出的报告；
- 凭据、疑似漏洞或其他安全敏感材料。停止并使用仓库的私有安全渠道。

当修复已经理解且 issue 只会重复该工作时，优先直接、可评审的 PR。

## 2. 确立发布权限

仅当以下之一为真时允许自动提交：

- 用户在当前任务中显式要求打开该 issue；或
- 所有者通过当前环境中的 `LOOPX_SELF_REPAIR_AUTO_ISSUE=1` 提供了持久
  opt-in。

该 opt-in 授权发布行为，而非特定报告的内容。认定、公共安全、认证与去重关卡
每次都适用。仓库标签、self-repair 调用、可写检出或已认证的 `gh` 会话都不是
发布权限。

没有权限时，渲染精确公开安全的标题与正文，然后询问一次是/否确认。在候选通过
认定、扫描与重复搜索之前，不要创建用户 todo，也不要打断用户。

## 3. 构建最小公开包

issue 正文应只包含：

1. 可观察症状与用户影响；
2. 预期与实际行为；
3. 最小合成或公开复现；
4. LoopX 版本或公开提交及相关运行时版本；
5. 收窄的疑似产品界面，明确标记为假设；
6. 已运行的公开安全验证。

添加由规范化受影响界面、症状与原因类别派生的稳定标记。fingerprint 输入中
不得包含私有标识符：

```text
<!-- loopx-self-repair:fingerprint=<12-hex-sha256> -->
```

把草稿写到仓库外的临时文件，并在任何 GitHub 写入前扫描它：

```bash
loopx check --scan-path "$draft_file"
```

扫描通过是必要但不充分。阅读最终标题与正文，移除私有项目名、客户或团队名、
任务 ID、本地路径、内部链接、凭据、原始日志、轨迹、verifier 输出与私有生产
细节。

## 4. 创建前搜索

在规范上游仓库中按 fingerprint 标记搜索已打开与已关闭的 issue：

```bash
gh issue list \
  --repo huangruiteng/loopx \
  --state all \
  --search "$fingerprint in:body" \
  --limit 20 \
  --json number,title,state,url
```

如果存在匹配 issue，记录其 URL 并停止。不要打开重复项或在既有 issue 下评论，
除非评论发布被单独授权。如果搜索失败或结果不明确，保留草稿并在发布前停止。

## 5. 提交一次，然后写回

验证认证，并仅在每个先前关卡都通过后创建：

```bash
gh auth status
gh issue create \
  --repo huangruiteng/loopx \
  --title "$title" \
  --body-file "$draft_file"
```

每个修复轮次最多创建一个 issue，并且最多提交一次尝试。认证或提交失败时，
保留草稿并提供具体恢复步骤；不要循环重试。

找到或创建 issue 后，把其 URL 与结果
（`upstream_issue_deduplicated` 或 `upstream_issue_opened`）写入相关
LoopX todo/证据记录。仅有草稿不是持久交付，也不应消耗交付 quota。

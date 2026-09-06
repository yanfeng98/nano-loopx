# 007 · 二次 merge 复查与修复(任务七)

- **日期**: 2026-09-06(任务六之后)
- **分支**: `260906-dev`
- **目标**: 用户要求再次仔细分析 006(上游二次 merge)是否正确,如有问题请修复。

## 复查发现的问题(全部修复并验证)

### 1. 产品缺陷: `loopx/doctor.py` 安装检查同步(真实功能影响)
`REQUIRED_INSTALLED_SKILL_PHRASES` 仍含 13 条英文正文短语 → 在中文 SKILL.md 下
`loopx doctor` 对 5 个技能误报 `required_phrases=False` → 安装判定
`repair_recommended`/`requires_upgrade`(用户在真实安装后会被错误提示"需修复")。
修复:13 条英文短语替换为中文等价串(已验证逐字存在于中文 SKILL)。
`tests/test_doctor*.py` 18 passed;`install-local-smoke` exit=0;`fresh-clone-quickstart-smoke` exit=0。

### 2. 文档残留: `demo/workspace/README.md`
上游 #3990 新增的英文 README(0 个中文字符)——违反"中文唯一",已整体翻译为中文。

### 3. smoke 断言大面积遗留(全量扫描 299 个 smoke 后发现)
全新扫描定位到 **42 个 smoke** 仍按英文文档断言(此前适配批次未覆盖的),全部 1:1 改写为
中文文档实际文本(frontmatter/yaml/CLI 命令/标识符/负断言保留英文;仅 1 条无等价文本的
断言删除并说明)。子代理验证 47 个修复项 exit=0。

### 4. 非中文类的分支漂移 smoke(5 个,先于中文迁移即失败,证据明确)
- capability-extension-registry: 快照缺 `reliability-diagnostics`(PR #3936 注册)
- external-scheduler-worker: upstream 增加 `sleep` 注入参数,旧 monkeypatch 失效
- lark-goal-topic-connection: PR #3969 goal-channel 嵌套 `connections{}` + DELETE 需 connection_id
- outcome-followthrough-policy: 19eba5c8 按 typed facts 推导义务后的行为变化
- ssh-reverse-proxy-supervisor: WSL2 localhost 时序 → 幂等重试(≤1s)

### 5. 环境遮蔽(本地 site-packages 残留包)
`examples`(与早前 `scripts`)被 site-packages 同名常规包遮蔽(namespace 包不敌常规包),
导致 `from examples.*_test_support import` 失败;补 `examples/__init__.py`(与
`scripts/__init__.py` 同法)。上游干净环境无此问题。

## 留档(未修复,与本分支无关/属上游代码面)
- `cli-help-manpage-smoke`(--help 41 行 > 39 预算)与 `cli-command-module-size`(todo.py
  1321 > 1098):预算值与 upstream/main 逐字一致,**上游本身处于超预算状态**(先于我们
  所有提交即失败),等待上游代码 owner 处理;帮助面仍为英文(CLI 功能面,不在文档转换范围)。
- B 类环境项(需要真实 provider/lark/模型凭据的 smoke):本地不可复现,留 CI 复验。

## 相关提交
- `da1a8a7d` fix(doctor)+ sync 42 smoke + 分支漂移 5 + demo README 中文化

## 最终状态
- 260906-dev 与 upstream/main 同步;文档中文唯一;关键 smoke/pytest/mkdocs 全绿;
  全量 299 smoke:本任务修复 47 项可复现项,余下为环境/上游预算类(见上)。

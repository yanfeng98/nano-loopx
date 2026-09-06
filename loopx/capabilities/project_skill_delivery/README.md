# Project Skill Delivery


LoopX 可以交付 canonical skill,而无需把它加到每个用户的全局 agent 配置。
Release 自有的 skill 通过添加以下内容选择项目交付:

```text
skills/<skill-id>/.loopx-skill-scope
```

确切内容为:

```text
project
```

全局 installer 把该 source 保留在版本化的 LoopX release 中,跳过全局 skill
安装。已连接项目随后可以安装一个或多个 host 原生托管副本:

```bash
loopx project-skill install \
  --project . \
  --skill <skill-id> \
  --surface codex \
  --surface claude-code \
  --surface opencode \
  --execute
```

## Surface 映射

| Surface | 项目目标 |
| --- | --- |
| `codex` | `.agents/skills/<skill-id>/` |
| `claude-code` | `.claude/skills/<skill-id>/` |
| `opencode` | `.opencode/skills/<skill-id>/` |
| `pi` | `.pi/skills/<skill-id>/` |

这些位置遵循 [Codex](https://developers.openai.com/codex/skills)、
[Claude Code](https://code.claude.com/docs/en/slash-commands#where-skills-live)
与 [OpenCode](https://opencode.ai/docs/skills/#place-files) 记录的 host 发现契约。

## 生命周期

所有变更都是 preview-first:

```bash
loopx project-skill status \
  --project . \
  --skill <skill-id> \
  --surface codex

loopx project-skill install \
  --project . \
  --skill <skill-id> \
  --surface codex

loopx project-skill uninstall \
  --project . \
  --skill <skill-id> \
  --surface codex
```

只在审查计划后添加 `--execute`。托管标记记录 release 版本、源 digest、skill id
与 host surface。对未托管目标、本地修改、symlink 逃逸、缺失项目连接或 digest
回读失败的 install 与 uninstall 会 fail closed。

多 surface 安装在替换前 staging 每个目标,后面的替换失败时恢复前面的目标。
实现复制整个 skill 目录,而不是链接 `SKILL.md`,因此支撑脚本、references 与
host 元数据保持完整。

## Authority 边界

Project skill delivery 控制可发现性,不是领域 authority。项目本地 skill 不能
创建 LoopX goal、todo、写作用域、operator gate、material-store authority 或外部
权限。每个消费者 capability 仍声明自己的激活与变更契约。

`loopx-material` 是第一个消费者:skill 可以在项目中可见,而 Material Lifecycle
对每个未显式激活它的 goal 保持默认关闭。

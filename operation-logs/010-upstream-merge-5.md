# 010 · 上游五次 merge(3 commits)(任务十)

- **日期**: 2026-09-06(任务九之后)
- **分支**: `260906-dev`
- **背景**: 分支落后 `huangruiteng/loopx` 3 个 commit。

## 上游 3 个 commit
| Commit | 内容 | 类型 |
|---|---|---|
| 255295f4 | lark agent goal channel 绑定隔离(#3992) | Bug 修复 |
| 64a0ab6b | 长程定位精修 + 1.0 工作区指南(#4008,含上游官方中文 README) | 文档 |
| 89ac4d51 | workspace Goal 目录优先渲染(#4007) | 前端 |

## 冲突与解决(3 个)
1. **README.md** — 上游 #4008 更新英文版并维护官方中文版(README.zh-CN.md
   678 行/37 节):采用官方中文全文升为主文件,删 zh-CN;清理内部残留
   (English 导航链接、book/en 链接、"双语学习路径"、11 处 .zh-CN.md
   链接目标 → .md、中文指南文案);链接检查无坏链。
2. **README.zh-CN.md**(modify/delete)— 维持删除(中文在主文件)。
3. **readme-demo-surface-smoke.py** — 断言按新官方中文内容适配
   (保留仍存在条目 + 按上游语义替换:如 "不等于 200 小时连续模型执行" →
   "不是连续模型执行时长或无人值守的生产自治"、新增 `## 能力`/`## 用户群与反馈`
   标题断言、`<a id="快速开始">`/`<a id="看几个例子">` 中文锚点等);exit=0。

## 顺带修复
- **test_chat_server_cors.py**(上游新增 7 用例):同样"服务器线程未就绪"时序
  (WSL)连接被拒 → 加 5 秒就绪探测(与 chat_completed_todos 同法),9 passed。

## 验证
- mkdocs exit=0;zh-CN 残留 0;lark/channel/cors 测试 9 passed;
  smoke readme-demo-surface ok;工作树干净。

## 提交
- `5d310b43` Merge upstream/main(3 commits)
- `e4898466` test(chat-server-cors): 就绪等待修复

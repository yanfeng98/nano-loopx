# Workspace 故事

在真实的 LoopX 个人工作区中探索三个关联项目:一个 120 人的社区活动、一份家庭能源购买指南,以及一个社区网站发布。每个项目有四个工作角色、跨多个阶段的 18 个交付任务、两个 owner 决策与两个定时关注。

从含 Python 3.11+ 与 Node 22.6+ 的源码 checkout 开始:

```bash
python -m demo.workspace serve
```

打开打印出的 loopback URL。该命令会创建一个可丢弃目录,并通过标准 Chat 后端服务已有的打包前端。如需可复现的位置:

```bash
python -m demo.workspace prepare --root /tmp/workspace-stories
python -m demo.workspace serve --root /tmp/workspace-stories --port 8791
```

只接受新建的空目录或本 demo 的匹配 manifest。Prepare 保留已有回放;重头再来请选择新目录。旧版 manifest 需要新目录。

## 项目与决策

| 项目 | 工作与约束 | 决策 |
| --- | --- | --- |
| Riverside Community Day | 三个场馆对比、$6000 预算、$5400 计划、$600 应急金、修订后的餐饮报价、访问审查、18 个志愿者班次与两个急救缺口 | 场馆预订;邀请批准 |
| Home Energy Buying Guide | 12 张来源卡、三个家庭概况、27 种电价/效率组合、互相矛盾的假设、五部分编辑计划 | 成本假设;发布批准 |
| Riverside Neighborhood Website | 六个页面、18-route 清单、24 项无障碍标准、导航/表单评审发现、内容权限、回滚与交接 | 内容冻结;部署批准 |

每个项目有七个重放完成检查点、五个就绪任务、四个阻塞任务与两个延迟跟进。依赖备注保留前驱 id;延迟任务使用真实 `todo_done` 恢复条件。两个仅观察的 monitor 具有节奏与下次到期元数据。demo 不会启动任何 scheduler 或在线 Agent。

切换 看板/列表、按 Agent 筛选、展开已完成历史、查看 owner 决策与定时关注。`BRIEF.md`、`working-table.csv`、`calculations.json` 与 `DELIVERY-PLAN.md` 保留规划输入与依赖。能源敏感性表与活动应急金在准备工作区时计算。

重放一次决策:

```bash
python -m demo.workspace advance --root /tmp/workspace-stories \
  --story research-brief --decision assumptions
```

之后刷新 UI。只有该决策及其直接阻塞的后继被推进。其他 owner 决策与下游阻塞保持不变。该命令不购买、不发布、不部署,也不启动 Agent。

## 数据与隔离

这些是使用真实 LoopX API 与状态转换编写的场景回放,不是客户案例研究,也不是在线 Agent 执行的收据。自然的项目标题保持界面可读;manifest 与完成证据保留来源出处。来源卡清单与网站检查表是规划输入,不是对外部研究或已执行网站测试的主张。活动资金是项目预算,不是模型支出。

该 demo 不导入个人注册表、会话历史或凭据,也不同步进全局注册表。loopback 服务器使用独立的 HOME/CODEX_HOME、最小环境与不可用的 Agent/Lark 二进制。Chat 与 Lark 连接错误是刻意的隔离,不代表在线 IM 行为。用 Ctrl-C 停止。

这仍然是 `demo/` 下的源码 checkout demo,不在已安装 wheel 与能力目录内。截图与录屏归被忽略的 `output/playwright/`;真实运行的统计请单独按计数范围打时间戳。

验证:`python -m pytest tests/test_workspace_story_demo.py -q` 覆盖真实状态、目录隔离、可复现 prepare、计算产物与决策限定转换。常规 Workspace 浏览器 smoke 覆盖共享看板/列表与已完成历史行为,包括 #3961。

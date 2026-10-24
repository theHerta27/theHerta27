<p align="center">
<picture>
  <source media="(max-width: 600px) and (prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="./profile/header-mobile-dark.svg">
  <source media="(max-width: 600px) and (prefers-reduced-motion: reduce)" srcset="./profile/header-mobile-light.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="./profile/header-dark.svg">
  <source media="(prefers-reduced-motion: reduce)" srcset="./profile/header-light.svg">
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="./profile/header-mobile-dark.gif">
  <source media="(max-width: 600px) and (prefers-color-scheme: light)" srcset="./profile/header-mobile-light.gif">
  <source media="(prefers-color-scheme: dark)" srcset="./profile/header-dark.gif">
  <source media="(prefers-color-scheme: light)" srcset="./profile/header-light.gif">
  <img alt="Tan Junlin / theHerta27 · Python · AI Agent" src="./profile/header-light.svg" width="100%">
</picture>
</p>

# 谭俊林 · theHerta27

**2028届 · 西安电子科技大学硕士在读（2025.09—2028.06）**

关注 Python 与 AI Agent 开发，围绕工具调用、执行审批、代码检查和会话恢复做工程实践。以下项目采用 AI 辅助开发，具体实现与验证范围见项目说明和公开案例。

[灰塔](#graytower) · [Herta](#herta) · [精选文章](#articles) · [联系方式](#contact)

<a id="graytower"></a>

## 灰塔

**面向游戏规则的代码修复 Agent · 2026.05—2026.09**

基于官方 Codex Runtime Python SDK 构建单 Agent 流程：在受限的 Git 候选副本中修改代码，通过 Docker 运行真实检查，再由人决定采用或恢复。

- **候选与检查**：限制候选修改范围，将检查结果绑定到对应的候选代码版本。
- **人工交付**：采用与恢复由人工确认，保留可核查的变更和检查记录。
- **验证范围**：99 项指游戏基线测试；已在临时副本中通过手工修改注释走通检查、采用与恢复流程。新主线的真实模型修复质量仍待验证。

[公开案例与验证记录](https://herta27.top/posts/graytower-agent-case-study/) · [源码分支（按仓库权限访问）](https://github.com/theHerta27/mihoyo-agent-project/tree/feature/reliable-game-agent)

<a id="herta"></a>

## Herta

**Python 简化 CLI Agent Harness · 2026.04—2026.07**

实现简化的 CLI Harness，用唯一的 Agent Loop 串起模型、工具、审批与会话状态，观察一次任务如何从工具调用走到可验证结果。

- **工具与审批**：注册 5 个工具，用 Pydantic 定义参数并校验输入；结合 diff 与 SHA-256 核对待执行内容，对有副作用的操作逐次审批。
- **上下文与恢复**：按完整轮次管理上下文并估算 Token，用 SQLite 保存和恢复会话，不重放已执行的工具操作。
- **真实任务**：DeepSeek 在自建项目中修复两个结算模块、增加 JSON 输出，分别通过 7 项和 8 项测试及独立核查；保留新增测试断言失败后修正的记录。
- **验证范围**：120 项 CLI 测试通过，包含原有 113 项和新增 7 项检查器测试；拒绝、外部编辑冲突与中断恢复均有真实记录。少量案例不代表整体修复成功率。

[公开案例与验证记录](https://herta27.top/posts/herta-cli-case-study/) · [真实任务演示](https://herta27.top/demos/#herta) · [源码分支（按仓库权限访问）](https://github.com/theHerta27/herta-agent/tree/learning/unit-01-cli-read)

<a id="articles"></a>

## 精选文章

- [Herta：工具调用与执行审批](https://herta27.top/posts/herta-tool-call/)
- [Herta：恢复会话时如何避免重复执行](https://herta27.top/posts/herta-session-resume/)
- [灰塔：让检查结果对应候选代码版本](https://herta27.top/posts/graytower-check-version/)

更多工程记录见 [个人博客 herta27.top](https://herta27.top/)。

## 技术

- **Agent 开发**：Python · Pydantic · Codex Runtime Python SDK · OpenAI-compatible API
- **工程与验证**：Git · Docker · SQLite · GitHub Actions

## GitHub Activity

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./profile/stats-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./profile/stats.svg">
    <img height="165" alt="Tan Junlin 的 GitHub 活动统计" src="./profile/stats.svg">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./profile/top-langs-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./profile/top-langs.svg">
    <img height="165" alt="Tan Junlin 公开仓库的语言构成" src="./profile/top-langs.svg">
  </picture>
</div>

<p align="center"><sub>贡献数取自 GitHub 近一年统计，其他数据来自公开仓库；语言占比反映仓库构成，不代表熟练程度。</sub></p>

<a id="contact"></a>

## 联系方式

[个人博客 herta27.top](https://herta27.top/) · [1404758168@qq.com](mailto:1404758168@qq.com)

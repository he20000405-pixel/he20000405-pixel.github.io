---
title: "ChatGPT 找不到 GPT-6.2？Astra 与 Sol 切换教程、真实评测与额度避坑指南"
description: "详解 GPT-6.2 Astra 与 Sol 的 ChatGPT Work、Codex 入口排查、基准与实测对照、Ultrafast 6 倍扣量规则及 API 定价规格。"
keywords: ["GPT-6.2 Astra","GPT-6.2 Sol","ChatGPT 找不到 GPT-6.2","ChatGPT Work","Codex 模型切换","Ultrafast 6 倍扣量","GPT-6.2 API 定价"]
permalink: /docs/gpt-6-2-astra-sol-guide/
lang: zh-CN
schema_type: Article
date_published: 2026-11-18
last_modified_at: 2026-11-18
---

# ChatGPT 找不到 GPT-6.2？Astra 与 Sol 切换教程、真实评测与额度避坑指南

> **30 秒核心结论（TL;DR）**
> * **去哪找模型**：OpenAI 未将 GPT-6.2 加入普通 Chat 菜单，网页与客户端需切换至 **Work（工作）** 模式，或在最新版 **Codex** 桌面端 / CLI（`/model`）中调用。
> * **选哪款模型**：日常编码与多步骤办公首选 **GPT-6.2 Sol**（Work 默认启用，API 单价仅为 Astra 的 1/4，多项编程与日常基准紧咬甚至反超旗舰）；复杂长流程、科研分析、3D/CAD 与高难度代码审查再切 **GPT-6.2 Astra**。
> * **避什么大坑**：Plus、Pro 100 与 Business 不支持 Ultrafast；Pro 200（仅限 Codex 中的 Sol）与 Pro 500 开启 Ultrafast 时，生成速度上限为 4.5 倍，但套餐额度按 **6 倍**扣除。

> **文档元信息**
> * **OpenAI 官方发布日期**：2026 年 11 月 17 日
> * **核查与整理日期**：2026 年 11 月 18 日（UTC+8）
> * **数据口径声明**：本文严格区分「OpenAI 官方公告与文档」「第三方机构标准基准」与「开发者单次实测样例」。文中涉及的 **API token 单价、单任务总成本、Token 生成速度倍率、套餐额度扣减倍率** 分属不同计量口径，已在对应章节单独标注。

---

## 目录

- [1. GPT-6.2 Astra 与 Sol 有什么区别？（核心定位与规格速览）](#1-gpt-62-astra-与-sol-有什么区别核心定位与规格速览)
- [2. 为什么 ChatGPT 找不到 GPT-6.2？（Plus / Pro / Codex 四步排查）](#2-为什么-chatgpt-找不到-gpt-62plus--pro--codex-四步排查)
- [3. GPT-6.2 真实表现如何？（基准评测、一线实测与客观短板）](#3-gpt-62-真实表现如何基准评测一线实测与客观短板)
- [4. 订阅套餐用量与 Ultrafast 6 倍扣量规则怎么算？](#4-订阅套餐用量与-ultrafast-6-倍扣量规则怎么算)
- [5. GPT-6.2 API 接口规格与百万 Token 定价参考](#5-gpt-62-api-接口规格与百万-token-定价参考)
- [6. 业务场景选型矩阵与使用建议](#6-业务场景选型矩阵与使用建议)
- [7. 高频问题速答（FAQ）](#7-高频问题速答faq)
- [8. 官方文档与出处索引（References）](#8-官方文档与出处索引references)

---

## 1. GPT-6.2 Astra 与 Sol 有什么区别？（核心定位与规格速览）

2026 年 11 月 17 日，OpenAI 正式发布 **GPT-6.2 Astra** 与 **GPT-6.2 Sol**，首发渠道限定为 **ChatGPT Work**、**Codex** 与 **API 平台**（普通 Chat 菜单未同步开放）。**GPT-6.2 Sol** 是官方默认的高性价比主力模型，API 单价仅为 GPT-6.2 Astra 的四分之一，适合日常编码与多步骤办公；**GPT-6.2 Astra** 则是重型旗舰模型，专攻超长上下文推理、科研工作流、3D/CAD 交互以及高难度代码审查。

| 对比维度                       | GPT-6.2 Astra                                                | GPT-6.2 Sol                                                  |
| :----------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| **API 模型 ID**                | `gpt-6.2-astra`                                              | `gpt-6.2-sol`                                                |
| **核心应用场景**               | 复杂、长流程专业工作（深度文档、工作簿、模板幻灯片、科学分析、计算机操作 CAD / 3D 工具） | 低成本日常专业工作、软件编程与多步骤任务                     |
| **Work 模式默认规则**          | 需在模型控件中手动切换                                       | 受支持个人套餐新建对话默认 `Sol`（`Light` 推理）；已启用模型的 Enterprise 默认 `Sol`（`Medium` 推理） |
| **上下文窗口**                 | 1,050,000 tokens（最大输入 922K / 最大输出 128K）            | 1,050,000 tokens（最大输入 922K / 最大输出 128K）            |
| **知识截止日期**               | 2026 年 5 月 18 日                                           | 2026 年 6 月 1 日                                            |
| **API 短上下文 Standard 单价** | 输入 `$8.00` / 缓存读取 `$0.40` / 输出 `$40.00`（每百万 tokens） | 输入 `$2.00` / 缓存读取 `$0.10` / 输出 `$10.00`（每百万 tokens） |
| **安全准备度分级**             | `AI Self-Improvement` 达到 **High** 阈值（OpenAI 首个触及该提前防护预警线并公开发布的模型） | `AI Self-Improvement` 低于 High 阈值                         |

---

## 2. 为什么 ChatGPT 找不到 GPT-6.2？（Plus / Pro / Codex 四步排查）

在 ChatGPT 中找不到 GPT-6.2，核心原因是 OpenAI 本轮未将其加入普通 Chat（聊天）模型菜单，用户必须手动切换至 **ChatGPT Work（工作）** 模式或更新 **Codex** 客户端才能看到新选项。

新模型上线后，[Reddit](https://www.reddit.com/r/ChatGPT/comments/1xyrw6y/im_not_seeing_62_sol_or_62_astra_in_the_model/) 与 [LINUX DO](https://linux.do/t/topic/3194438) 等社区有用户反馈「刷新后菜单里没有 6.2」。结合 [OpenAI 更新日志](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) 与实际账号界面核查，可按以下四步快速排查：

### 2.1 ChatGPT 端：普通 Chat 不开放，需切换至 Work 模式
OpenAI 在更新日志中明确说明，本轮未将 GPT-6.2 Astra 或 GPT-6.2 Sol 加入普通 Chat 菜单，ChatGPT 端（网页、桌面、移动端）的可用入口统一限定在 **Work（工作）** 模式。

以 2026 年 11 月 18 日同一已登录 Pro 账号的 Chrome 网页端实测为例，新建对话时两种模式的界面表现截然不同：
* **普通「聊天（Chat）」模式**：展开「选择 ChatGPT 模型」后，仅可见 `GPT-6（已选）` 与 `GPT-5.6 Sol`，两款 GPT-6.2 均未出现在列表中。
* **切换至「工作（Work）」模式**：收起状态下的模型按钮仍显示旧型号 `GPT-6.1 Sol`，但点开下拉列表后，`默认`、`GPT-6.2 Astra`、`GPT-6.2 Sol` 与 `GPT-6.1 Sol（已选）` 均已就位。

> **界面状态提示**：「收起按钮显示已选旧型号」与「展开列表已包含新型号」会在同一会话中同时发生，切勿仅凭按钮折叠文字判断未推送。若 Work 界面显示的是 `Power` 滑杆，点击旁边的 **Advanced** 即可查看当前账号可选的具体模型与推理级别。

### 2.2 Codex 端：更新桌面应用或使用 CLI `/model` 命令
在已获授权且收到推送的 Codex 客户端中，可通过以下入口调用 GPT-6.2 Astra 与 GPT-6.2 Sol：
* **Codex 桌面应用**：模型控件位于输入框附近；若列表缺项，执行顶部菜单 `Menu → Check for Updates` 更新至最新版本后重启客户端。
* **交互式 Codex CLI**：在终端输入 `/model` 命令查看并切换模型，同样需确认 CLI 已更新至当前版本。

### 2.3 套餐覆盖范围与工作区管理员开关
根据 [ChatGPT Work 与 Codex 帮助文档](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex) 及 [Business 模型说明](https://help.openai.com/en/articles/12003714-chatgpt-business-models-and-limits)，Plus、Pro、Business、Enterprise、Edu（以及 ChatGPT for Healthcare、FedRAMP 工作区）均在逐步推出名单内，OpenAI 未公布全球账号的统一开放时间。其中 Business 受席位类型与工作区设置影响，**Enterprise 与 Edu 工作区必须由管理员在后台手动开启模型**。

### 2.4 常见边缘状态与误区排查
* **ChatGPT 订阅认证 ≠ API Key 认证**：根据 [OpenAI 认证文档](https://learn.chatgpt.com/docs/auth)，在 Codex 中使用 ChatGPT 账号登录与使用 API 密钥登录（走 API 计费）分属两套独立的权限作用域。[LINUX DO 社区](https://linux.do/t/topic/3194329?page=2) 中出现的「API 模型列表已显示 GPT-6.2，但 Codex 订阅列表尚未显示」说明两种入口的可见性可能不同。该帖未确认具体登录方式和缺项原因。
* **历史对话模型锁定**：在已收到推送的个人套餐中，新建 Work 对话默认启用 `GPT-6.2 Sol`（`Light` 推理强度）。若打开的是历史 Work 对话，且该对话此前已锁定具体旧模型或 Default 处于 `Luna` 状态（历史对话残留的旧默认模型标识），页面可能不会主动弹出升级提示，直接展开菜单手动切换即可。
* **第三方客户端适配延迟**：部分用户通过第三方客户端（如 [Codex++](https://linux.do/t/topic/3194438)）挂载自有订阅时刷新不到 GPT-6.2，可先检查第三方工具是否已适配。该帖未确认模型缺项的具体原因。

---

## 3. GPT-6.2 真实表现如何？（基准评测、一线实测与客观短板）

GPT-6.2 系列最大的工程改进在于**单任务总成本的降幅远大于 token 单价降幅**。由于 GPT-6.2 Astra 与 GPT-6.2 Sol 收敛了推理路径与输出冗余，在多步骤长流程、代码库修改和日常任务中均表现出显著的效率提升。

### 3.1 复杂工作流、3D 交互与科研分析（重点看 GPT-6.2 Astra）

| 评估来源与基准                                               | 核心测试结果与对比                                           | 口径与边界说明                                               |
| :----------------------------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| **[Agents’ Last Exam](https://agents-last-exam.org/leaderboard)**<br>（[OpenAI 发布稿](https://openai.com/index/introducing-gpt-6-2-astra-sol/)） | GPT-6.2 Astra 综合评分较 GPT-6 Astra 提升 **5.2 个百分点**，单任务成本降至 GPT-6 Astra 的 **1/3 以下** | 官方脚注注明：同期对比的 Claude Fable 5.2 结果排除了 9 个使用后备模型的任务 |
| **GDPval v2**<br>（OpenAI 自有基准）                         | GPT-6.2 Astra 较 GPT-6 Astra 提高 **6.2 个百分点**，平均输出 token 减少 **22%**；GPT-6.2 Sol 较 GPT-6.1 Sol 提高 **5.3 个百分点** | 衡量长流程知识工作交付质量与输出精简度                       |
| **Terminal-Bench-Science 0.1**<br>（OpenAI 发布稿）          | GPT-6.2 Astra 较 GPT-6 Astra 高出 **9 个百分点**，单任务成本同样低于 GPT-6 Astra 的 **1/3** | 衡量终端环境下的科学研究工作流执行能力                       |
| **Intelligence Index v5**<br>（[Artificial Analysis](https://artificialanalysis.ai/articles/openai-has-the-2-model-in-the-intelligence-index-with-the-release-of-gpt-6-2-astra-and-gpt-6-2-sol)） | 最高推理档下 GPT-6.2 Astra 获 **62 分**（较 GPT-6 Astra `+5` 分，按模型维度位列综合榜**第二**）；GPT-6.2 Sol 获 **57 分**（较 GPT-6.1 Sol `+2` 分） | 2026 年 11 月 17 日发布日报告数据                            |
| **[AA-3D 人工盲评](https://artificialanalysis.ai/methodology/aa-3d)**<br>（Artificial Analysis） | GPT-6.2 Astra 获 **1318 Elo**，领先于 Claude Fable 5.2（**1271 Elo**）与 GPT-6.2 Sol（**1259 Elo**） | 仅反映该机构 3D 生成评测范围内的盲评偏好                     |
| **Automation Reports**<br>（[Epoch AI 人工评分](https://epoch.ai/publications/how-good-are-fable-5-2-and-gpt-6-2-astra-at-real-work)） | GPT-6.2 Astra 平均得分 **65%**，低于 Claude Fable 5.2（约 **82%**）17 个百分点；但在「AI 数据中心分析」专项任务上较 GPT-6 Astra 提升 **25 个百分点** | 以 100% 为人类员工交付标准，受测六款模型整体最高分均未达到 100% |

* **一线实测细节补充**：
  * **HTML 数据仪表盘（[DataCamp / Josef Waples](https://www.datacamp.com/zh/blog/gpt-6-2-astra-and-sol)）**：基于 173 个美国大学专业 CSV 数据，在统一提示、固定工具与高推理强度下单次运行，GPT-6.2 Astra 消耗 27,821 输出 tokens、花费 **$1.79**，低于 GPT-6 Astra 的 35,298 输出 tokens 与 **$2.93**；不过 GPT-6.2 Astra 与 GPT-6 Astra 对专业人数是否加权的统计处理不同，作者认为 GPT-6 Astra 的加权口径更契合该业务需求。
  * **3D 交互场景（[APPSO / 36 氪](https://www.36kr.com/p/4074475449062281)）**：作者实测了 GPT-6.2 Astra 生成第三人称水下探索游戏、动画风乡村骑行与基础 WebGL 交互场景，整体还原度获得正面评价。

### 3.2 软件编程、代码审查与日常任务（重点看 GPT-6.2 Sol）

| 评估来源与基准                                               | 核心测试结果与对比                                           | 口径与边界说明                                               |
| :----------------------------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| **[FrontierCode 2.0](https://cognition.com/frontiercode)**<br>（Cognition 真实代码库） | GPT-6.2 Astra 加权得分 **44.2%**（单次运行平均 **$5.97**），GPT-6.2 Sol 加权得分 **43.8%**（单次平均 **$1.29**）；两款完全通过率同为 **48.2%** | 统一采用 `Codex harness`（官方评测执行框架）与 Max 推理档，GPT-6.2 Sol 单次成本不到 GPT-6.2 Astra 的 1/4 |
| **[LifeVal](https://cdn.openai.com/pdf/lifeval.pdf)**<br>（OpenAI 自有基准） | GPT-6.2 Sol 得分高于 GPT-6 Astra，单任务成本约为 GPT-6 Astra 的 **1/7** | 评估包含个人情境限制的日常多步骤任务                         |
| **Coding Agent Index**<br>（Artificial Analysis）            | GPT-6.2 Astra 与前代 GPT-6 Astra 持平；GPT-6.2 Sol 较前代 GPT-6.1 Sol 下降 **3 分** | 同样采用 `Codex harness` 与 Max 推理档，任务集与综合智力榜不同 |

* **一线开发者实测补充**：
  * **代码审查检出率（[数字生命卡兹克](https://tech.ifeng.com/c/8y7WiMENt8f)）**：在作者自建简易代码审查题集上统一开启 `xhigh` 推理档，GPT-6.1 Sol 检出率为 **65%**，GPT-6.2 Sol 提升至 **84%**，GPT-6.2 Astra 达到 **96%**；在作者的样本任务中，GPT-6.2 Astra 耗时约为 GPT-6.2 Sol 的 **2 倍**，花费约为 **4 倍**。（核查注：该文正文提及 GPT-6.2 Astra 在 Artificial Analysis 综合榜上涨 6 分，经核对原始报告实为 5 分。）
  * **Three.js 专项代码测试（[Reddit `u/k1rd`](https://www.reddit.com/r/OpenAI/comments/1xz037w/gpt62_sol_results_on_a_standard_threejs_eval_16/)）**：在 [`threejseval.com`](https://threejseval.com/models/gpt-6.2-sol-high) 的 16 道 Three.js 题集与统一执行框架下，`GPT-6.2 Sol High` 首次生成即有 **15 个**可直接运行，余下 **1 个**经一次修复后成功运行。
  * **模板幻灯片重建（[DataCamp / Josef Waples](https://www.datacamp.com/zh/blog/gpt-6-2-astra-and-sol)）**：经 OpenRouter 以高推理强度单次调用生成五页幻灯片，GPT-6.2 Astra 花费 **$0.22**，GPT-6 Astra 花费 **$0.59**，GPT-6.2 Sol 仅花费 **$0.07**；三款模型均成功还原模板风格，但本次测试中唯有 GPT-6.2 Sol 的字号准确命中原模板。

### 3.3 客观局限与已知边界汇总
在投入实际生产环境前，以下三项官方披露与第三方观察边界值得关注：
1. **关键前提遗漏风险**：OpenAI 在发布稿中明确提示，GPT-6.2 Astra 与 GPT-6.2 Sol 在部分对齐评估中仍可能遗漏影响任务完成的关键条件（例如文件缺失或工具不可用）。
2. **复杂职场交付仍未达到人类基线**：在 Epoch AI 的真实职场人工评估中，GPT-6.2 Astra 平均得分（65%）不仅距人类员工交付标准（100%）仍有距离，也落后于 Claude Fable 5.2（约 82%）；此外，部分外部开发者也反馈其在长流程编程中偶有问询中断的情况。
3. **特定编程基准出现小幅回撤**：在 Artificial Analysis 的 Coding Agent Index 中，GPT-6.2 Sol 较前代 GPT-6.1 Sol 下降了 3 分，说明其优势主要体现在综合性价比与常规代码修改（如 FrontierCode 2.0）上，并非所有子项全面碾压前代。

---

## 4. 订阅套餐用量与 Ultrafast 6 倍扣量规则怎么算？

目前 ChatGPT Work 与 Codex 共用对应订阅套餐的用量额度；启用 **Ultrafast** 极速模式时，Token 生成速度上限为同模型 Standard 模式的 **4.5 倍**，但个人订阅端均按 Standard 模式的 **6 倍**扣除套餐内用量。

此外，根据 [OpenAI 12 月用量独立公告](https://help.openai.com/en/articles/20001625-understanding-chatgpt-and-codex-usage-limits)，**自 2026 年 12 月起，ChatGPT 与 Codex 的共享用量范围将进一步扩大至 Plus、Pro 与 Business 套餐（Instant 聊天除外）**，具体生效日与各档位的绝对额度有待后续公布。

| 订阅 / 计费类型                 | GPT-6.2 模型准入                         | Ultrafast 极速权限                           | 用量 / 费用折算倍率（相对同模型 Standard）                   |
| :------------------------------ | :--------------------------------------- | :------------------------------------------- | :----------------------------------------------------------- |
| **Plus / Pro 100 / Business**   | 符合条件且收到推送后可用（Work / Codex） | **不支持**（购买额外 credits 亦无法开通）    | 适用入口下 Fast 模式按 **2 倍**扣除套餐用量                  |
| **Pro 200**                     | 可用（Work / Codex）                     | 仅限 **Codex 中的 GPT-6.2 Sol**              | 使用 Ultrafast 按 **6 倍**扣除套餐用量                       |
| **Pro 500**                     | 可用（Work / Codex）                     | 支持 **GPT-6.2 Astra 与 GPT-6.2 Sol 双模型** | 使用 Ultrafast 按 **6 倍**扣除套餐用量                       |
| **Enterprise / Edu**            | 需工作区管理员在后台开启                 | 符合条件的工作区可由管理员开启               | 按工作区 credits 或适用按量方案计费                          |
| **合格购入 Credits / 企业按量** | 按对应入口规则适用                       | 适用入口支持                                 | 截至 **2027 年 2 月 28 日**（PT，含当天）享受 **3 倍**优惠计费，3 月 1 日起恢复为 **6 倍**（Fast 为 **2 倍**） |

---

## 5. GPT-6.2 API 接口规格与百万 Token 定价参考

> **读者分流提示**：本节面向直接调用 OpenAI API 的开发者；仅使用 ChatGPT 网页/桌面端或 Codex 订阅套餐的用户可直接跳至第 6 节。

根据 [GPT-6.2 Astra API 文档](https://developers.openai.com/api/docs/models/gpt-6.2-astra) 与 [GPT-6.2 Sol API 文档](https://developers.openai.com/api/docs/models/gpt-6.2-sol)，两款 API 模型（`gpt-6.2-astra` 与 `gpt-6.2-sol`）均支持 **1,050,000 tokens** 上下文窗口（最大输入 922K / 最大输出 128K），接收文本与图像输入、输出文本，同时兼容 **Responses API** 与 **Chat Completions** 接口。**若业务涉及工具调用（Tool Calling），官方要求必须使用 Responses API**。

### 5.1 短上下文 Standard 定价（输入 ≤ 272K tokens）

| 计费项目（单位：美元 / 百万 tokens） | `gpt-6.2-astra` | `gpt-6.2-sol` | 价格变动说明（据 Artificial Analysis 对比）                  |
| :----------------------------------- | :-------------- | :------------ | :----------------------------------------------------------- |
| **输入（Input）**                    | **$8.00**       | **$2.00**     | GPT-6.2 Astra 较 GPT-6 Astra 降价 **20%**；GPT-6.2 Sol 与 GPT-6.1 Sol 持平 |
| **缓存输入读取（Cached Read）**      | **$0.40**       | **$0.10**     | GPT-6.2 Astra 较 GPT-6 Astra 的 `$1.00` 降价 **60%**（缓存写入另有独立费率） |
| **输出（Output）**                   | **$40.00**      | **$10.00**    | GPT-6.2 Astra 较 GPT-6 Astra 降价 **20%**；GPT-6.2 Sol 与 GPT-6.1 Sol 持平 |

### 5.2 长上下文加价、速率倍率与数据驻留
* **长上下文阶梯定价**：当单次请求输入超过 **272K tokens** 时，整次请求的输入与缓存费率按对应短上下文价格的 **2 倍**计算，输出按 **1.5 倍**计算。
* **API 速率模式费率**：`Batch` 模式为同条件 Standard 价格的 **0.5 倍**（半价）；`Fast` 模式为 **2 倍**；API `Ultrafast` 沿用与合格 Credits 相同的阶梯优惠窗口。截至 **2027 年 2 月 28 日**（太平洋时间，含当天）按 **3 倍**计费，次日起恢复为 **6 倍**。
* **数据驻留（Data Residency）**：使用 API 数据驻留功能时，`Standard`、`Fast` 与 `Batch` 可选择受支持的**美国或欧盟**区域驻留，而 `Ultrafast` 的区域驻留**仅限美国**（[API 更新日志](https://developers.openai.com/api/docs/changelog#november-2026) 另提供全球处理选项）。

---

## 6. 业务场景选型矩阵与使用建议

| 典型业务场景                           | 推荐模型与配置                     | 核心决策依据                                                 |
| :------------------------------------- | :--------------------------------- | :----------------------------------------------------------- |
| **日常编码、代码库修改、前端组件生成** | **GPT-6.2 Sol**（Standard / Fast） | 在 FrontierCode 2.0 上与 GPT-6.2 Astra 完全通过率持平（48.2%），但单次成本不到 GPT-6.2 Astra 的 1/4；Three.js 实测首次可运行率达 15/16 |
| **轻量级办公自动化、日常多步骤任务**   | **GPT-6.2 Sol**（Work 默认配置）   | LifeVal 日常情境基准得分高于 GPT-6 Astra，单任务成本约为 GPT-6 Astra 的 1/7 |
| **高难度代码审查、超长上下文深度分析** | **GPT-6.2 Astra**（高推理档）      | 自建代码审查实测检出率达 96%（GPT-6.2 Sol 为 84%），且较 GPT-6 Astra 输出 token 减少 22%、单价下调 20% |
| **3D 交互场景、CAD/科研复杂工作流**    | **GPT-6.2 Astra**                  | AA-3D 盲评（1318 Elo）与终端科研基准（+9 个百分点）均显著领先 |
| **需要极速响应的交互式调试**           | 仅在必要时开启 **Ultrafast**       | 订阅端触发 Ultrafast 按 **6 倍**扣除套餐用量（最高提速 4.5 倍），建议避免在后台长任务中常驻开启 |

---

## 7. 高频问题速答（FAQ）

### Q1：ChatGPT Plus 会员怎么使用 GPT-6.2 Astra 和 Sol？
Plus 套餐在 OpenAI 逐步推送名单内，但普通 Chat 菜单不显示新模型。收到推送后，需在 ChatGPT 网页或客户端中切换至 **Work（工作）** 模式（新建对话默认启用 `GPT-6.2 Sol`），或在更新后的 **Codex** 客户端中使用。

### Q2：为什么切换了 Work 模式，按钮上还是显示 GPT-6.1 Sol？
这是正常的前端折叠显示现象。在已收到推送的账号中，Work 模式下收起状态的模型按钮可能仍显示旧型号 `GPT-6.1 Sol`，但点击展开下拉菜单后即可看到 `GPT-6.2 Astra` 与 `GPT-6.2 Sol`；若界面显示 `Power` 滑杆，点击旁边的 **Advanced** 即可选择具体模型。

### Q3：为什么 API 模型列表里已有 GPT-6.2，但 Codex 里看不到？
在 Codex 中使用 ChatGPT 订阅账号登录与使用 API Key 登录分属两套独立的权限与计费作用域。API 列表可见仅代表对应 API 组织已获得访问权限，ChatGPT 订阅端的 Codex 入口仍需等待账号推送并确认桌面端或 CLI 已更新至最新版本。

### Q4：Pro 200 和 Pro 500 的 Ultrafast 极速模式有什么区别，怎么扣用量？
Plus、Pro 100 与 Business 不支持 Ultrafast（购买额外 credits 亦无法开通）；**Pro 200** 仅支持 **Codex 中的 GPT-6.2 Sol** 开启 Ultrafast；**Pro 500** 支持 **GPT-6.2 Astra 与 GPT-6.2 Sol 双模型**开启 Ultrafast。Pro 200 与 Pro 500 启用 Ultrafast 时，生成速度上限为 4.5 倍，但套餐内用量均按 Standard 模式的 **6 倍**扣除。

### Q5：GPT-6.2 Astra 和 GPT-6.2 Sol 的 API 价格差多少，长上下文怎么加价？
在短上下文（输入 ≤ 272K tokens）Standard 模式下，`gpt-6.2-astra` 为输入 `$8` / 缓存读取 `$0.40` / 输出 `$40`（每百万 tokens），`gpt-6.2-sol` 为输入 `$2` / 缓存读取 `$0.10` / 输出 `$10`，两者相差 4 倍。当单次请求输入超过 272K tokens 时，整次请求的输入与缓存费率按短上下文的 **2 倍**计费，输出按 **1.5 倍**计费。

---

## 8. 官方文档与出处索引（References）

### OpenAI 官方发布与文档
* **发布公告**：[Introducing GPT-6.2 Astra and Sol](https://openai.com/index/introducing-gpt-6-2-astra-sol/)
* **系统卡与安全分级**：[GPT-6.2 Astra & Sol System Card](https://deploymentsafety.openai.com/gpt-6-2-astra-sol)、[Preparedness Assessment](https://deploymentsafety.openai.com/gpt-6-2-astra-sol/preparedness-assessment)
* **ChatGPT Work 与 Codex 指南**：[ChatGPT Work and Codex](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex)、[What's New: GPT-6.2 Astra & Sol](https://learn.chatgpt.com/docs/whats-new/gpt-62-astra-sol)
* **更新日志与套餐权限**：[ChatGPT Release Notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)、[Business Models and Limits](https://help.openai.com/en/articles/12003714-chatgpt-business-models-and-limits)、[Understanding ChatGPT and Codex Usage Limits](https://help.openai.com/en/articles/20001625-understanding-chatgpt-and-codex-usage-limits)
* **速度档位与认证说明**：[Agent Configuration: Speed](https://learn.chatgpt.com/docs/agent-configuration/speed)、[Codex Pricing (Ultrafast)](https://learn.chatgpt.com/docs/pricing?codex-pricing-speed=ultrafast)、[Authentication Docs](https://learn.chatgpt.com/docs/auth)
* **API 模型与定价文档**：[gpt-6.2-astra](https://developers.openai.com/api/docs/models/gpt-6.2-astra)、[gpt-6.2-sol](https://developers.openai.com/api/docs/models/gpt-6.2-sol)、[API Pricing](https://developers.openai.com/api/docs/pricing)、[API Changelog (Nov 2026)](https://developers.openai.com/api/docs/changelog#november-2026)

### 第三方基准机构报告
* **Artificial Analysis**：[OpenAI has the #2 model in the Intelligence Index with the release of GPT-6.2 Astra and GPT-6.2 Sol](https://artificialanalysis.ai/articles/openai-has-the-2-model-in-the-intelligence-index-with-the-release-of-gpt-6-2-astra-and-gpt-6-2-sol)、[AA-3D Methodology](https://artificialanalysis.ai/methodology/aa-3d)
* **Epoch AI**：[How good are Fable 5.2 and GPT-6.2 Astra at real work?](https://epoch.ai/publications/how-good-are-fable-5-2-and-gpt-6-2-astra-at-real-work)
* **其他基准原榜**：[Agents’ Last Exam Leaderboard](https://agents-last-exam.org/leaderboard)、[Cognition FrontierCode 2.0](https://cognition.com/frontiercode)、[LifeVal Paper](https://cdn.openai.com/pdf/lifeval.pdf)

### 开发者与媒体实测引用
* **DataCamp（Josef Waples）**：[GPT-6.2 Astra and Sol 实测分析](https://www.datacamp.com/zh/blog/gpt-6-2-astra-and-sol)
* **APPSO（36 氪授权发布）**：[GPT-6.2 Astra 场景实测](https://www.36kr.com/p/4074475449062281)
* **数字生命卡兹克（凤凰网转载）**：[GPT-6.2 代码审查与实测报告](https://tech.ifeng.com/c/8y7WiMENt8f)
* **Reddit Three.js Eval（`u/k1rd`）**：[GPT-6.2 Sol Results on a Standard Three.js Eval](https://www.reddit.com/r/OpenAI/comments/1xz037w/gpt62_sol_results_on_a_standard_threejs_eval_16/)、[threejseval.com](https://threejseval.com/models/gpt-6.2-sol-high)

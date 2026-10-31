# 发布前自动验收

GitHub Pages 的发布来源必须是 **GitHub Actions**（`build_type: workflow`）。不要改回 `Deploy from a branch`，否则旧的分支发布流程可能绕过检查。

## 每次更新的流程

工作流 `Validate and publish knowledge base` 在 `main` 提交、面向 `main` 的 Pull Request、`ci-check/` 开头的隔离测试分支及手动运行时触发。

1. 固定当前候选提交和另外四个知识库当次获取的 `main` 提交。
2. 使用固定摘要的 GitHub 官方 Pages/Jekyll 232 镜像构建五库；分别设置各库身份与提交号。
3. 验收器自测、站内链接/资源/锚点、页面元数据/站点地图、搜索数据及已有搜索行为测试全部成功后，才能打包当前仓库的构建结果。
4. 无写权限的 `release-ready` 任务依赖验收成功。部署任务依赖验收和该任务，只能在 `main` 上运行。
5. 部署使用同次运行中验收过的产物，不重新构建。失败时保留现有线上版本；修正后重新提交。

PR 和隔离测试分支只验收，绝不部署。验收任务只有读取权限；仅部署任务可以写 Pages 和申请部署身份令牌。不要增加能够绕过门禁的独立发布工作流，也不要使用 `pull_request_target` 执行候选代码。

## 看哪里、怎么修

在仓库 **Actions → Validate and publish knowledge base** 查看失败步骤。检查器输出含页面和目标地址的错误；`validation-evidence` 附件保存构建镜像、五库实际提交、文件清单和检查报告，保留 30 天。源码/构建失败时报告可能不完整，以该次日志为准。

本地可在构建完成后运行：

```text
python .github/scripts/check_site.py --build-root <包含portal、chatgpt、grok、claude、gemini的构建目录> --report <报告路径>
python .github/scripts/test_check_site.py
node <主库目录>/scripts/test_search.cjs
```

## 判断边界

- 不依赖外部网站 HTTP 请求，不因外站 403、临时限流或 Google 收录延迟阻止发布。
- 搜索索引中已有条目失效会阻止发布；新文章尚未进入门户搜索目录只提醒，避免跨库先后发布互相阻塞。新增文章先发布产品库，再更新主库搜索及推荐入口。
- 其他四库的 `main` 快照不保证已经上线；这不是五库原子发布。涉及新跨库链接时，仍须按顺序发布并检查真实目标页面。
- 文章事实、实际视觉效果、搜索收录与排名需另行核查。自动验收不保证覆盖所有错误。
- 管理员仍能改动工作流和仓库设置；本配置不是防止管理员主动绕过的安全边界。

## 故障演练与维护

在 `ci-check/` 隔离分支加入不存在的站内链接，检查应失败，`release-ready` 应随 `needs` 被跳过；修正后该任务应成功。两次运行都不允许部署。不要在生产 `main` 中故意放置坏内容。

五库的 `.github/workflows/pages.yml` 和 `.github/scripts/` 使用相同版本。维护共享规则时同步五库并重新进行正向/反向验收。镜像与 Actions 均固定版本摘要；升级前须核对网站产物及门禁测试。

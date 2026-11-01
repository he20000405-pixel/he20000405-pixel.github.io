# 发布与收录步骤

## 一、首次发布根站

1. 在 GitHub 账号 `he20000405-pixel` 下创建公开仓库，名称必须是 `he20000405-pixel.github.io`。
2. 将本地仓库的 `main` 分支推送到该远程仓库。
3. 打开仓库的 `Settings → Pages`。
4. 在 `Build and deployment` 中将 `Source` 设为 `GitHub Actions`，使用仓库内的发布前检查工作流。
5. 按 [发布前检查说明](.github/PUBLISHING-CHECKS.md) 确认 `github-pages` 部署环境仅允许 `main`，不要切回分支直接发布。
6. 在 `Actions` 中确认本次 `main` 的正常运行依次通过 `verify` → `release-ready` → `deploy`，再打开 `https://he20000405-pixel.github.io/`。

`release-ready` 是无权限哨兵任务，依赖 `verify` 成功；PR 和 `ci-check` 测试分支只验收，不发布。只有 `main` 的正常检查通过后才部署同一次运行已检查的产物。检查失败时不执行发布，线上保留上一次成功版本。

## 二、上线验收

依次打开：

- `https://he20000405-pixel.github.io/`
- `https://he20000405-pixel.github.io/search/`
- `https://he20000405-pixel.github.io/en/`
- `https://he20000405-pixel.github.io/robots.txt`
- `https://he20000405-pixel.github.io/sitemap.xml`
- `https://he20000405-pixel.github.io/llms.txt`

搜索页分别测试：`Claude`、`Gemini`、`Pro`、`Max`、`Free`、`续费`、`User ID`、`session`、`403`、`Claude Code`。

## 三、Google Search Console

1. 新增网址前缀资源：`https://he20000405-pixel.github.io/`。
2. 选择 HTML 文件或 HTML 标记验证，不需要域名 DNS 权限。
3. 如果使用 HTML 文件，将 Google 提供的原始验证文件放在仓库根目录并重新发布。
4. 验证成功后提交：
   - `sitemap.xml`
   - `chatgpt-plus-pro-china-guide/sitemap.xml`
   - `supergrok-china-guide/sitemap.xml`
   - `claude-pro-max-china-guide/sitemap.xml`
   - `gemini-google-ai-pro-china-guide/sitemap.xml`
5. 从五库当前专题目录、站点地图及独立资源页整理规范 URL 清单，逐篇核对实际索引状态，不只检查首页和入口。正式文章、资源指南与首页、目录、搜索页分别计数，优先处理正文页面。
6. 对未收录且实际网址测试可抓取、允许索引的页面，以及本次新增或重要更新的页面，按后台配额请求编入索引。发现抓取、noindex 或规范地址问题时先修复；已提交待处理的 URL 不作无意义重复请求。
7. 记录每篇的索引状态、Google 选择的规范地址、最后抓取时间、核查时间、请求结果及待办。地图“提交成功”不等于读取成功，地图读取成功或请求已受理也不等于文章已编入索引。

## 四、Bing Webmaster Tools

1. 优先从 Google Search Console 导入根站资源。
2. 确认 Bing 网站地图页面发现根站和四个产品知识库 sitemap。
3. 使用 URL 检查逐篇对账当前正文与独立资源页，记录 Bing 的实际索引、抓取状态和核查时间，优先处理正文页面。
4. 对未收录且可抓取、允许索引，或本次新增、重要更新的 URL，按后台配额请求索引；已收录且未变的页面不重复提交。配额不足、受限或仍在处理的页面保留为待办。
5. 将网站地图成功读取、URL 提交受理和实际编入索引分别记录，不用发现 URL 数代替收录数量。

## 五、日常维护

- 新增 ChatGPT、Grok、Claude 或 Gemini 专题后，同步更新根站 `_data/guides.yml` 和 `llms.txt`。
- 产品页 H1（页面大标题）或搜索收录发生变化时，先发布对应产品知识库，再重新构建并发布门户；门户搜索索引会从本次五库构建结果自动提取 H1。产品仓库发布成功不会自动更新已经上线的门户索引，需在门户发布后用页面完整标题和搜索简称各验收一次。
- 四个产品知识库均已接入；产品入口或服务说明变化时，同步核对 `_data/products.yml` 和对应搜索数据。
- 不移动四个产品仓库的文章，不修改已经收录的 permalink。
- 套餐、价格、功能或版本信息更新前先核对产品官方页面。

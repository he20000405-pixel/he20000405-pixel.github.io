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

搜索页分别测试：`Claude`、`Pro`、`Max`、`Free`、`续费`、`User ID`、`session`、`403`、`Claude Code`。

## 三、Google Search Console

1. 新增网址前缀资源：`https://he20000405-pixel.github.io/`。
2. 选择 HTML 文件或 HTML 标记验证，不需要域名 DNS 权限。
3. 如果使用 HTML 文件，将 Google 提供的原始验证文件放在仓库根目录并重新发布。
4. 验证成功后提交：
   - `sitemap.xml`
   - `chatgpt-plus-pro-china-guide/sitemap.xml`
   - `supergrok-china-guide/sitemap.xml`
   - `claude-pro-max-china-guide/sitemap.xml`
5. 只请求根首页、`/search/` 和 `/en/` 编入索引一次，不重复提交既有专题。

## 四、Bing Webmaster Tools

1. 优先从 Google Search Console 导入根站资源。
2. 确认 Bing 网站地图页面发现根站和三个产品知识库 sitemap。
3. 只对根首页和必要入口请求一次索引。

## 五、日常维护

- 新增 ChatGPT、Grok 或 Claude 专题后，同步更新根站 `_data/guides.yml` 和 `llms.txt`。
- Gemini 知识库完成后，在 `_data/products.yml` 增加产品项，再补对应搜索数据。
- 不移动三个产品仓库的文章，不修改已经收录的 permalink。
- 套餐、价格、功能或版本信息更新前先核对产品官方页面。

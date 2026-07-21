---
title: "Windows Codex Desktop 动态换肤教程"
description: "在 Windows 11 上使用 Codex Dream Skin 通过本机 loopback CDP 加载动态星河背景，并完成安装、验证、安全检查和官方外观恢复。"
permalink: /labs/codex-dream-skin-windows/
lang: zh-CN
schema_type: TechArticle
image: "https://he20000405-pixel.github.io/assets/images/labs/codex-dream-skin-windows-social.png"
image_alt: "Windows Codex Desktop 动态星河换肤教程"
date_published: 2026-07-21
last_modified_at: 2026-07-21
faq:
  - question: "Codex Dream Skin 会修改 WindowsApps 或 app.asar 吗？"
    answer: "本次审核的固定版本通过本机 Chromium DevTools Protocol 注入 CSS 和装饰 DOM，不修改 WindowsApps、app.asar、官方二进制或应用签名。"
  - question: "只监听 127.0.0.1 是否代表完全安全？"
    answer: "不是。loopback 可以阻止局域网直接访问，但 CDP 不对同一 Windows 用户下的其他本地进程提供独立认证。主题运行期间应只运行可信软件，不用时执行恢复关闭调试会话。"
  - question: "为什么安装后没有马上出现主题？"
    answer: "普通方式启动 Codex 不会打开主题需要的调试会话。应从 Dream Skin 启动入口打开；Store 应用较慢时，CDP 端点也可能晚于默认检测窗口出现。"
  - question: "Codex 更新后主题失效怎么办？"
    answer: "先退出 Codex 和托盘，再更新或重新下载上游源码，重新运行安装和启动脚本。脚本会重新发现当前注册的官方 Store 包。"
  - question: "如何完整恢复官方外观？"
    answer: "运行 restore-dream-skin.ps1 的 RestoreBaseTheme 模式。它会关闭已保存的 CDP 会话、移除注入并选择性恢复由主题管理的外观设置。"
---

<section class="lab-hero">
  <div>
    <p class="eyebrow">Windows 11 · Codex Desktop · Tested Workflow</p>
    <h1>Windows 11 Codex Desktop 动态换肤教程：安装、验证、安全边界与完整恢复</h1>
    <p class="lead">这不是替换安装包或把整张假界面盖在窗口上，而是通过本机 loopback CDP 给官方 Codex Desktop 注入背景层与样式，同时保留原生侧栏、任务和输入框。</p>
    <div class="intro-actions">
      <a class="button-link primary" href="https://github.com/Fei-Away/Codex-Dream-Skin/tree/e776fa6d5361a2bdd5c1614674397681e7b00874">查看固定上游源码</a>
      <a class="button-link" href="{{ '/assets/downloads/labs/codex-dream-skin-galaxy-animated.webp' | relative_url }}" download>下载动态星河 WebP</a>
      <a class="button-link" href="{{ '/assets/downloads/labs/codex-dream-skin-galaxy-static.jpg' | relative_url }}" download>下载静态备用图</a>
    </div>
  </div>
  <figure class="lab-preview">
    <img src="{{ '/assets/images/labs/codex-dream-skin-windows-social.png' | relative_url }}" alt="深蓝紫星河 Codex Desktop 换肤实测教程封面" width="1200" height="630">
    <figcaption>公开封面只使用无 UI 星河素材；真实运行截图含本机任务信息，因此不公开。</figcaption>
  </figure>
</section>

## 先说结论

在本次测试环境中，固定版本的 Codex Dream Skin 可以给 Windows Store 版 Codex 加载静态或动态背景，原生侧栏、项目、任务和输入框仍然可用。完整恢复可以关闭 CDP 调试会话并恢复由主题管理的外观设置。

但它仍属于第三方、非 OpenAI 官方的本地调试方案。**不修改官方安装包不等于零风险，监听 `127.0.0.1` 也不等于 CDP 具备本地进程认证。**

## 本次实测基线

| 项目 | 实测值 |
| --- | --- |
| 系统 | Windows 11 家庭中文版 64 位 |
| Codex | Microsoft Store 包，安装前 26.707.9564.0，测试期间更新到 26.715.8383.0 |
| Node.js | v24.10.0 |
| Windows PowerShell | 5.1.26100.8875 |
| Git | 2.51.2 |
| 上游提交 | `e776fa6d5361a2bdd5c1614674397681e7b00874` |
| 动态素材 | 1920×1080 WebP，约 4.65 MB，8 秒循环 |
| 静态素材 | 2560×1440 JPEG，约 0.51 MB |

上游当前没有与本次环境对应的正式 Release，因此教程固定到已经审核和测试的提交。未来更新上游代码时，应重新运行测试和恢复闭环，不能默认最新 `main` 与当前 Codex 版本兼容。

## 它是怎么工作的

<div class="flow-line" aria-label="Codex Dream Skin 工作流程">
  <div><strong>1. 官方 Store Codex</strong><span>动态发现已注册包</span></div>
  <div><strong>2. Loopback CDP</strong><span>仅绑定 127.0.0.1</span></div>
  <div><strong>3. CSS 与 DOM</strong><span>注入装饰层，不替换原生控件</span></div>
  <div><strong>4. Restore</strong><span>移除注入并关闭调试会话</span></div>
</div>

脚本会检查 Store 包身份、监听进程、Browser ID、WebSocket 地址和 Codex 页面结构。注入器保持原 Browser WebSocket 作为身份锚；浏览器关闭或端口被其他进程复用时，它会退出，而不是自动连接新的未知端点。

## 一、安装前检查

先完全退出 Codex，然后在 PowerShell 中检查环境：

```powershell
node --version
git --version
Get-AppxPackage -Name OpenAI.Codex | Select-Object Name, Version, SignatureKind, InstallLocation
Get-NetTCPConnection -LocalPort 9335 -State Listen -ErrorAction SilentlyContinue
```

需要满足：

- Node.js 22 或更高；
- 当前用户已注册官方 Microsoft Store `OpenAI.Codex` 包；
- 安装期间 Codex 已完全退出；
- 默认端口没有被身份不明的进程占用。

不要为了安装主题取得 WindowsApps 所有权，也不要关闭未知监听进程。默认端口被占用时，使用脚本支持的其他端口。

## 二、固定源码并先运行测试

```powershell
git clone https://github.com/Fei-Away/Codex-Dream-Skin.git
Set-Location .\Codex-Dream-Skin
git checkout e776fa6d5361a2bdd5c1614674397681e7b00874

powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\windows\tests\run-tests.ps1
node --check .\windows\scripts\injector.mjs
node --check .\windows\assets\renderer-inject.js
```

测试覆盖的不只是语法，还包括：

- UTF-8 配置读写、原子替换和并发修改拒绝；
- `[desktop]` 外观键的选择性恢复；
- Store 包、进程、端口和 Browser ID 身份校验；
- loopback WebSocket URL 拒绝规则；
- 图片 16 MB、16384 像素单边和 5000 万总像素限制；
- junction、符号链接和路径逃逸拒绝；
- 透明辅助窗口不被错误铺上主题；
- renderer reload 后的重新注入与代际检查。

如果测试失败，应先停止安装并保留输出，不要通过删除检查代码继续。

## 三、安装并启动主题

进入上游 `windows` 目录：

```powershell
Set-Location .\windows

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\install-dream-skin.ps1

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\start-dream-skin.ps1 -PromptRestart
```

安装命令的 `Bypass` 只作用于本次明确发起的 PowerShell 进程。安装后的快捷方式使用进程级 `RemoteSigned`，不应永久修改用户或系统执行策略。

默认运行状态位于：

```text
%LOCALAPPDATA%\CodexDreamSkin
```

主题正在使用时不要移动或删除该目录。恢复脚本、状态、当前主题、已保存主题和日志都依赖它。

## 四、导入动态星河或静态背景

本页提供两份不含人物、文字、按钮或官方 Logo 的测试素材：

- [动态星河 WebP]({{ '/assets/downloads/labs/codex-dream-skin-galaxy-animated.webp' | relative_url }})：用于验证动画背景；
- [静态星河 JPEG]({{ '/assets/downloads/labs/codex-dream-skin-galaxy-static.jpg' | relative_url }})：性能或兼容性异常时使用。

打开 `Codex Dream Skin - Tray`，选择“更换背景图”，导入图片并保存为本地主题。背景图应该是纯视觉素材，不应包含伪造的 Codex 侧栏、输入框、按钮或账号信息。

主题素材的构图把主要亮区放在右侧，左侧保留较暗的文字安全区。普通任务页应使用更强的安静遮罩，避免背景降低正文和输入框可读性。

## 五、验证主题不是一张假截图

运行上游验证脚本：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\verify-dream-skin.ps1 `
  -ScreenshotPath "$env:TEMP\codex-dream-skin.png"
```

自动验证至少应确认：

- CDP 监听地址只有 loopback；
- 监听进程属于当前官方 Store Codex 包；
- 页面存在预期版本的主题标记；
- 原生侧栏和输入框仍存在；
- 装饰层使用 `pointer-events: none`，不会拦截点击；
- 首页和普通任务页使用正确的可读性处理。

随后手动检查：

1. 打开项目选择菜单；
2. 进入一个真实任务再返回首页；
3. 在输入框中输入但不发送测试文字；
4. 调整窗口宽度，检查控件是否被遮挡；
5. 暂停和恢复主题；
6. 重新加载 renderer 后检查主题是否重新出现。

### 动态效果如何证明

本次测试在同一个持续 CDP page 会话中，两次调用 `Page.captureScreenshot`，间隔 1375ms，只比较右侧背景区域：

| 指标 | 结果 |
| --- | --- |
| 发生变化的颜色通道 | 775,296 |
| 比较的总颜色通道 | 2,154,960 |
| 平均绝对差 | 1.1789 |
| 判断 | 动态背景通过 |

这比只检查文件扩展名更可靠。两张原始验证帧含本机账号、项目和任务信息，因此不公开。

## 六、真实失败记录

第一次安装并没有立即成功：启动脚本在 45 秒内没有看到 `127.0.0.1:9335` 的已验证 CDP 端点，因此按设计回滚并正常打开 Codex。随后确认 Store 应用实际在检测窗口结束后才开始监听，才在验证当前官方 Codex 进程身份后继续连接。

完整恢复测试也经历过两次失败：一次是 Codex 关闭后端口仍短暂监听，另一次是恢复判断比配置归档更早结束。脚本没有静默宣称成功，而是保留状态和日志。修正等待和校验后，最终闭环确认：

- 受管理的外观键恢复；
- CDP 端口在恢复阶段关闭；
- `auth.json` 哈希不变；
- 动态星河可以重新应用。

这些失败说明 Store 应用启动和退出存在时序差异。教程不能承诺所有机器都在固定秒数内完成，也不能把一次成功泛化成所有 Codex 版本永久兼容。

## 七、完整恢复官方外观

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\restore-dream-skin.ps1 `
  -RestoreBaseTheme -PromptRestart
```

如需同时删除 Dream Skin 创建的快捷方式：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\restore-dream-skin.ps1 `
  -RestoreBaseTheme -PromptRestart -Uninstall
```

普通恢复只处理 Dream Skin 管理的外观键，并保留 Codex 后来写入的其他合法设置。因此不应要求整个 `config.toml` 与安装前逐字节相同。认证文件应单独确认未被修改。

`-RecoverConfigBackup` 是配置损坏时的完整备份恢复手段，不是普通卸载步骤。使用前应先保留当前配置。

## 风险与隐私边界

<div class="notice warning">
  <strong>Loopback 不是身份认证。</strong>它阻止局域网直接访问调试端口，但同一 Windows 用户下的其他本地进程仍可能尝试连接 CDP。主题运行期间只运行可信软件，不用时执行 Restore。
</div>

- 不需要管理员权限，也不应接管 WindowsApps。
- 不应改写 API Key、Base URL、模型供应商或 `auth.json` 内容。
- 日志和截图中不要保留密钥、认证内容、私人任务或完整本机路径。
- 不公开主题运行截图前必须逐项脱敏；本页没有用伪造截图代替真实证据。
- 上游人物或 IP 预设的 MIT 软件许可不自动授予肖像、商标或素材再分发权。
- 本页与上游项目均不是 OpenAI 官方产品或官方教程。

## 常见问题

### 端口 9335 被占用怎么办？

未显式指定端口时，上游启动器会从默认端口向后寻找空闲端口。显式端口被占用时换一个端口，不要终止身份不明的监听进程。

### 更新 Codex 后主题消失正常吗？

可能发生。重新退出托盘和 Codex，更新上游源码后运行测试与安装。不要直接复用旧版本 WindowsApps 路径。

### 动态 WebP 不播放怎么办？

先换用静态 JPEG，确认注入和交互本身正常，再检查 WebP 文件、大小限制和当前 renderer 兼容性。

### 会影响 ChatGPT 会员或 API 配置吗？

主题工具与会员订阅是不同层面。审核版本不应写入 API Key、Base URL 或认证内容；ChatGPT 会员状态仍以官方账号页面为准。

## 来源与延伸阅读

- [Fei-Away/Codex-Dream-Skin 上游仓库](https://github.com/Fei-Away/Codex-Dream-Skin)
- [本次固定审核提交](https://github.com/Fei-Away/Codex-Dream-Skin/tree/e776fa6d5361a2bdd5c1614674397681e7b00874)
- [Windows 安装说明](https://github.com/Fei-Away/Codex-Dream-Skin/blob/e776fa6d5361a2bdd5c1614674397681e7b00874/windows/README.md)
- [Windows 运行时安全说明](https://github.com/Fei-Away/Codex-Dream-Skin/blob/e776fa6d5361a2bdd5c1614674397681e7b00874/windows/references/runtime-notes.md)
- [Windows QA 清单](https://github.com/Fei-Away/Codex-Dream-Skin/blob/e776fa6d5361a2bdd5c1614674397681e7b00874/windows/references/qa-inventory.md)
- [ChongGrok ChatGPT 会员与付款排障知识库](https://he20000405-pixel.github.io/chatgpt-plus-pro-china-guide/)

如果当前问题不是换肤，而是 ChatGPT Plus / Pro 的开通、付款或订阅状态，可以查看 [ChongGrok ChatGPT 服务入口](https://chonggrok.com/chatgpt?utm_source=github_pages&amp;utm_medium=referral&amp;utm_campaign=technical_lab&amp;utm_content=codex_dream_skin)。已存在扣款或有效订阅时，应先排查，不要重复购买。

<p class="meta">首次发布：2026-07-21 · 实测内容会在 Codex 或上游实现发生实质变化后更新。</p>

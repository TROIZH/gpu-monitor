# GPU Monitor

GPU Monitor 是一个本地优先的 macOS 菜单栏硬件监控工具，面向 AI 编程、Voice Coding、多 Agent、本地模型、浏览器重度使用、视频剪辑和长时间编译等场景。

当前版本是原型：它会安装一个 macOS 菜单栏 App，并在本机启动 localhost 后端和前端页面。默认不会上传指标、代码、提示词、语音、截图、网页内容或文件内容。

## 首页两个仪表盘是什么意思

首页左边是「健康值」，右边是「综合使用率」。

- 健康值：0-100 分，越高代表当前设备越稳定、越不容易被瓶颈拖慢。
- 综合使用率：0-100%，越高代表当前 CPU、内存、存储和可用 GPU 资源越忙。
- 健康值不是 CPU 使用率，也不是 GPU 使用率。
- 单项资源情况请看下方 CPU、GPU、内存、存储、散热和进程卡片。

健康值会综合 CPU 压力、单核心压力、内存压力、swap、存储空间、散热状态和 GPU 授权状态来估算。综合使用率会把 CPU、内存、存储和已授权 GPU 的当前占用合并成一个更接近“这台电脑现在有多忙”的数值。

## 一键安装

如果你是从 GitHub 下载源码或 clone 仓库，直接运行：

```bash
./install.command
```

这个脚本会构建 `GPU Monitor.app`，安装到 `~/Applications/GPU Monitor.app`，并自动打开。启动后，macOS 顶部菜单栏会出现一个仪表盘图标。左键点击打开监控下拉面板，右键点击可以打开 Dashboard、查看 GPU 授权说明、检查更新或退出。

如果脚本提示缺少 Swift 编译器，先安装 Xcode Command Line Tools：

```bash
xcode-select --install
```

## 本地开发快速安装

从 Terminal 运行：

```bash
git clone https://github.com/TROIZH/gpu-monitor.git
cd gpu-monitor
./install.command
```

## 从 0 到 1 安装 SOP

1. 下载或克隆仓库。

```bash
git clone https://github.com/TROIZH/gpu-monitor.git
cd gpu-monitor
```

2. 构建并安装菜单栏 App。

```bash
./install.command
```

3. 打开 App。

```bash
open "$HOME/Applications/GPU Monitor.app"
```

4. 验证本地服务。

```bash
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/dashboard/current
```

## GPU 授权 SOP

结论先说清楚：当前原型还没有完成 GPU 精准监控授权，所以 GPU 会显示「需要授权」，不会显示假数据。

macOS 没有提供类似相机、麦克风那种“允许访问 GPU 使用率”的普通权限弹窗。精确 GPU 功耗、频率和进程 GPU 时间通常要通过 `powermetrics` 采样，而 `powermetrics` 必须以管理员权限运行。

开发者可以先用下面这条命令验证自己的 Mac 是否支持 GPU sampler：

```bash
sudo powermetrics --samplers gpu_power --show-process-gpu -n 1 -i 1000
```

预期行为：

- Terminal 会要求输入 macOS 管理员密码。
- 如果输出里有 GPU power、GPU frequency 或 process GPU 数据，说明这台机器具备接入精准 GPU 监控的基础。
- 如果输出提示 sampler 不支持，或者没有 GPU 字段，App 应该继续显示「需要授权」或「当前设备不支持」。

当前原型已支持：

- CPU 总负载。
- CPU 每核心负载。
- 内存、swap、存储空间。
- 散热状态。
- 进程级 CPU 和内存占用。
- GPU 状态占位：明确显示需要授权，不用 mock 数据冒充真实数据。

正式开源版应该这样做 GPU 授权：

1. 主 App 内提供「启用精准 GPU 监控」按钮。
2. 使用 Apple ServiceManagement 安装一个受限的 privileged helper。
3. macOS 弹出系统管理员授权窗口。
4. helper 只运行窄范围 `powermetrics` sampler。
5. helper 只把 GPU 指标通过本地 IPC 返回给主 App。
6. 设置页提供停用和卸载 helper 的入口。

不要让用户把管理员密码粘贴进 App，也不要让普通前端页面直接请求密码。管理员授权必须通过 macOS 系统授权流程，开发验证阶段才使用 Terminal 的 `sudo` 命令。

相关官方文档：

- Apple ServiceManagement: https://developer.apple.com/documentation/servicemanagement
- Apple SMAppService: https://developer.apple.com/documentation/servicemanagement/smappservice

## 不通过菜单栏运行

后端：

```bash
cd local-resource-monitor-backend
.venv/bin/python -m resource_monitor_backend --port 8765
```

前端：

```bash
cd gpu-monitor-frontend-inspect
python3 -m http.server 8000 --bind 127.0.0.1
```

浏览器打开：

```bash
open "http://127.0.0.1:8000/Resource%20Monitor.live.html"
```

菜单栏嵌入模式：

```bash
open "http://127.0.0.1:8000/Resource%20Monitor.live.html?embed=1"
```

## 开源发布 SOP

公开发布建议走这条流程：

1. 创建 GitHub 仓库，加入源码、LICENSE、截图和 README。
2. 用 CI 跑后端测试并构建 macOS App。
3. 用 release build 脚本产出安装包。

```bash
scripts/package-release.command
```

脚本会生成：

```text
dist/GPU-Monitor-v<version>.zip
dist/GPU-Monitor-v<version>.dmg
```

4. 使用 Apple Developer ID 签名。
5. 通过 Apple notary service 公证。
6. 打包为 `.dmg` 或 `.zip`。
7. 发布 GitHub Release。
8. 可选：添加 Homebrew Cask，方便用户 `brew install --cask gpu-monitor`。
9. 把 GPU helper 授权流程写进用户文档，并和普通安装流程分开。

开发阶段的未签名本地 build 可以自己用。给普通用户使用时，应该提供签名和公证过的包，否则 Gatekeeper 会拦截。

## 自动更新 SOP

自动更新分两层：当前原型的轻量检测，以及正式产品的安全自动更新。

### 当前原型：轻量版本检测

本版本已经在菜单栏右键菜单里加入「Check for Updates...」，并且 App 启动后会每 6 小时静默检查一次更新。

它需要一个更新 feed。发布前在 `macos-menu-bar/Info.plist` 里配置：

```xml
<key>GPMUpdateFeedURL</key>
<string>https://raw.githubusercontent.com/<owner>/<repo>/main/releases/latest.json</string>
```

`latest.json` 建议格式：

```json
{
  "version": "0.2.0",
  "download_url": "https://github.com/<owner>/<repo>/releases/download/v0.2.0/GPU-Monitor.dmg",
  "html_url": "https://github.com/<owner>/<repo>/releases/tag/v0.2.0",
  "notes": "修复 GPU 授权引导，优化菜单栏面板。"
}
```

当本地版本低于 feed 版本时，App 会提示发现新版本，并让用户打开下载页。当前原型不会静默替换本地 App，也不会绕过 Gatekeeper。

GitHub Releases 适合放安装包；GitHub Pages 或 raw GitHub 文件适合放 `latest.json`。小红书适合做发布公告，不建议作为 App 自动更新源，因为页面结构不稳定，也不适合做机器可验证的版本 feed。

### 正式产品：Sparkle 2

如果要实现用户熟悉的 macOS 自动更新体验，建议接入 Sparkle 2：

1. 把当前 `swiftc` 脚本构建迁移到 Xcode project 或 Swift Package App。
2. 添加 Sparkle 2 framework。
3. 生成 Sparkle EdDSA 更新签名密钥。
4. 每次 release 都签名更新包。
5. 发布 appcast XML。
6. App 定期读取 appcast，发现新版本后提示用户更新。
7. 用户确认后由 Sparkle 下载、校验签名并替换 App。

Sparkle 适合正式分发，因为它会校验更新包签名，避免“有人替换下载链接后用户自动安装恶意版本”的风险。

相关文档：

- Sparkle documentation: https://sparkle-project.org/documentation/
- Sparkle publishing updates: https://sparkle-project.org/documentation/publishing/

## 隐私默认值

- 后端只监听 localhost。
- 指标数据库只存本机。
- 默认不联网做硬件推荐。
- 不采集源码内容。
- 不采集 prompt、终端内容、语音、截图、网页正文或文件内容。
- 升级建议页的搜索按钮只有用户主动点击时才会打开默认浏览器。

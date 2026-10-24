# 原生 iPhone 安装验证

本次源码已由 GitHub macOS Runner 实际编译成功，尚未在 iPhone 安装。

- 构建记录：https://github.com/klein7syd/klein7syd.github.io/actions/runs/40096411931
- 测试分支：native-install-probe
- 工程目录：native-validation/NativeInstallProbe.xcodeproj
- 固定原始 Bundle ID：org.todowallpaper.nativeinstallprobe
- App 版本 0.0.1；本次构建号 1；最低 iOS 17。

## 已验证结果

Xcode 26.6 / iOS 26.5 SDK；Swift 编译目标 arm64-apple-ios17.0。
构建日志出现 BUILD SUCCEEDED；IPA 内可执行文件是 ARM64 Mach-O，LC_BUILD_VERSION 平台值为 2（iOS 真机）。没有 LC_CODE_SIGNATURE、embedded.mobileprovision 或 _CodeSignature，属于供后续签名使用的未签名设备包，不能直接安装。

IPA SHA256：b207c6c7be30c4f7f2ab0523f3986ef90d56b3e93d4bc246b6b7a888fdfbc87b。

## Windows：只需进行签名和安装

1. 下载实际构建的 NativeInstallProbe-unsigned.ipa。若从 GitHub 下载 Artifact ZIP，先解压出里面的 IPA，不要把外层 ZIP 拖入签名工具。
2. 从 https://sideloadly.io/ 获取 Sideloadly；根据官网要求准备 Apple 官网版 iTunes/iCloud。已有可用驱动时先检查设备是否识别，不要盲目卸载系统软件。
3. USB 连接 iPhone、解锁，手机上点“信任此电脑”。打开 Sideloadly，选择设备和这个 IPA，使用 Apple ID Sideload 模式。
4. 由本人在 Sideloadly 输入免费 Apple Account 及验证信息，然后开始。凭据不要填入 GitHub，也不需要发送给开发助手。
5. 手机如提示未受信任开发者，到“设置 → 通用 → VPN 与设备管理”信任对应账号。如提示需要开发者模式，到“设置 → 隐私与安全 → 开发者模式”开启并按提示重启确认。
6. 主屏幕打开“原生安装测试”。看到“SwiftUI 已运行”、构建号 1 后计数三次，完全退出再打开，核对仍为 3。

如 Sideloadly 提供自动刷新，可在首次签名安装成功后启用并保留其所需的运行/连接条件；自动刷新配置结果不代替 App 安装测试。

## 覆盖更新与固定身份

源码 Bundle ID 固定。签名工具如果生成了账号后缀或重写了 ID，要记录实际 ID，后续使用同一账号、同一实际 ID 和同一映射。不要为了更新先卸载旧 App。下一构建覆盖安装后，验证构建号增加而计数保留。

注意：本次界面中的 Bundle ID 文案为源码原始 ID，不能用于证明工具重签名后的实际 ID；实际 ID 要以签名工具/已签名包为准。

## 当前限制

仅验证原生启动、按钮、本地保存、安装及后续覆盖更新。WidgetKit、App Intents、App Groups、Liquid Glass、壁纸和完整待办功能没有加入这个最小测试 App，等待真实安装成功后再单独验证。

旧 Windows 项目尚未上传至本次环境，因此本次成功不代表原有 TodoWallpaper-iOS 全部源码已修复或编译通过。博客 main 分支未修改；验证文件仅在专用测试分支。

日志仍有两条非致命构建警告：未引用 AppIntents.framework 而跳过其元数据提取；未声明全套界面方向。Actions 另有旧 Node 版本迁移提示。它们不影响本次构建成功，但不能宣称 Zero Warnings。

## 后续构建

只修改此测试分支中的独立原生目录。推送后工作流自动构建；构建号使用 GitHub run_number，Bundle ID 不随构建变动。
已有真实 .xcodeproj 与共享 Scheme，不依赖 XcodeGen 或其他第三方 App 运行库。编译、签名、设备安装分别记录结果。

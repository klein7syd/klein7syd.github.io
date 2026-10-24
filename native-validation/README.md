# 原生 iPhone 安装验证

本次源码已由 GitHub macOS Runner 实际编译成功。2026-10-24，用户反馈使用 iPASide，并提供 iPhone 截图，确认构建 1 的原生 SwiftUI App 已启动。

- 构建记录：https://github.com/klein7syd/klein7syd.github.io/actions/runs/40096411931
- 测试分支：native-install-probe
- 工程目录：native-validation/NativeInstallProbe.xcodeproj
- 固定原始 Bundle ID：org.todowallpaper.nativeinstallprobe
- App 版本 0.0.1；本次构建号 1；最低 iOS 17。

## 已验证结果

Xcode 26.6 / iOS 26.5 SDK；Swift 编译目标 arm64-apple-ios17.0。
构建日志出现 BUILD SUCCEEDED；IPA 内可执行文件是 ARM64 Mach-O，LC_BUILD_VERSION 平台值为 2（iOS 真机）。没有 LC_CODE_SIGNATURE、embedded.mobileprovision 或 _CodeSignature，属于供后续签名使用的未签名设备包，不能直接安装。

IPA SHA256：b207c6c7be30c4f7f2ab0523f3986ef90d56b3e93d4bc246b6b7a888fdfbc87b。

## iPhone 实机反馈

用户使用的安装工具是 **iPASide**。截图显示“原生安装测试”“SwiftUI 已运行”、构建号 1、计数 1，因此可以确认原生 App 已安装并启动。截图不能独立证明签名账号类型或重签名后的实际 Bundle ID。

已走通的操作链为：GitHub macOS 编译 → 下载未签名 IPA → 用户在 Windows 使用 iPASide 完成签名安装 → iPhone 启动。未签名 IPA 本身仍不能直接安装。

下一步只做保存验证：点击“计数 +1”至 3，在应用切换器划掉 App，再从主屏幕打开，核对是否仍为 3。等待用户反馈；尚未确认退出重开保存、覆盖更新保存或自动刷新。

后续继续使用同一 iPASide 签名账号和实际 Bundle ID。签名凭据由用户自行输入，不需要放入 GitHub 或发给开发助手。

## 覆盖更新与固定身份

源码 Bundle ID 固定。签名工具如果生成了账号后缀或重写了 ID，要记录实际 ID，后续使用同一账号、同一实际 ID 和同一映射。不要为了更新先卸载旧 App。下一构建覆盖安装后，验证构建号增加而计数保留。

注意：本次界面中的 Bundle ID 文案为源码原始 ID，不能用于证明工具重签名后的实际 ID；实际 ID 要以签名工具/已签名包为准。

## 当前限制

原生安装和启动已有实机截图；按钮操作已有计数变化的用户截图。退出重开保存与覆盖更新保存仍待实测。WidgetKit、App Intents、App Groups、Liquid Glass、壁纸和完整待办功能没有加入这个最小测试 App，待最小安装测试反馈完成后再单独验证。

旧 Windows 项目尚未上传至本次环境，因此本次成功不代表原有 TodoWallpaper-iOS 全部源码已修复或编译通过。博客 main 分支未修改；验证文件仅在专用测试分支。

日志仍有两条非致命构建警告：未引用 AppIntents.framework 而跳过其元数据提取；未声明全套界面方向。Actions 另有旧 Node 版本迁移提示。它们不影响本次构建成功，但不能宣称 Zero Warnings。

## 后续构建

只修改此测试分支中的独立原生目录。推送后工作流自动构建；构建号使用 GitHub run_number，Bundle ID 不随构建变动。
已有真实 .xcodeproj 与共享 Scheme，不依赖 XcodeGen 或其他第三方 App 运行库。编译、签名、设备安装分别记录结果。

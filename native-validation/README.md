# 最小原生安装验证

此包尚未实际云端编译或真机安装。固定 Bundle ID：org.todowallpaper.nativeinstallprobe。

## 编译

将本目录内容（包括 .github）上传到独立 GitHub 测试仓库根目录，不是放进下一层 github-project 目录。公共仓库的标准 macOS Runner 可免费运行。进入 Actions → Build unsigned native probe → Run workflow。工作流用 XcodeGen 生成真正的 Xcode 工程，再调用 xcodebuild 编译 iPhone ARM64 程序，不是模拟器包。XcodeGen 仅是构建工具，不是 App 运行依赖。

运行通过后在该次运行底部下载 native-probe-N Artifact ZIP，解压取 NativeInstallProbe-unsigned.ipa。检查 build.log、toolchain.txt、platform.txt、status.json；失败日志不能算通过。IPA 尚未签名，不能直接在手机点击安装。不要给 GitHub 添加 Apple 密码、证书或验证码。

## Windows 签名和安装

从 https://sideloadly.io/ 下载 Sideloadly。按官网要求准备 Apple 官网版 iTunes/iCloud。USB 连接 iPhone、解锁并信任电脑。选择下载出的 unsigned.ipa 和设备，Apple ID Sideload 模式，由本人输入 Apple Account 和验证信息后开始。

不要随机改变 Bundle ID。若工具自动生成带账号后缀的 ID，记录实际 ID，后续始终使用同一账号和同一映射。不卸载旧 App，覆盖安装更新。这样才具备保留沙盒数据的条件，必须实测确认。

手机按提示信任开发者，iOS 16+ 在 设置→隐私与安全→开发者模式 开启并重启确认。首次看不到开关时先完成开发签名安装/配对再检查，不能用企业签名或网页图标替代。

## 真机验收

1. 从主屏幕启动“原生安装测试”，看到 SwiftUI 已运行与构建号。
2. 计数三次，完全退出并重开，计数仍是 3。
3. 下一构建使用同一账号/实际 Bundle ID 覆盖安装，确认构建号增加、计数保留。
4. 记录设备型号、iOS 版本、构建号、Sideloadly 成功/错误日志和结果。不向聊天发送密码或验证码。

首次成功安装前不增加 Widget、App Intents、App Groups 或界面美化；这些能力在后续独立技术验证中检查。

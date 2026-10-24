import SwiftUI

@main
struct NativeInstallProbeApp: App {
    var body: some Scene {
        WindowGroup { ProbeView() }
    }
}

struct ProbeView: View {
    @AppStorage("nativeProbe.counter.v1") private var counter = 0
    var body: some View {
        NavigationStack {
            Form {
                Section("原生安装验证") {
                    Text("SwiftUI 已运行")
                    Text("Bundle ID: org.todowallpaper.nativeinstallprobe")
                    Text("构建：\(Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String ?? "unknown")")
                }
                Section("保存与覆盖更新验证") {
                    Text("计数：\(counter)")
                    Button("计数 +1") { if counter < Int.max { counter += 1 } }
                    Text("退出重开及同标识覆盖安装后，核对计数是否保留。")
                }
            }
            .navigationTitle("原生安装测试")
        }
    }
}

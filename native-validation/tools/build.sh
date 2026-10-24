#!/bin/bash
set -euo pipefail
mkdir -p out
{ sw_vers; xcodebuild -version; xcrun --sdk iphoneos --show-sdk-version; } > out/toolchain.txt
plutil -lint NativeInstallProbe.xcodeproj/project.pbxproj
xcodebuild -list -json -project NativeInstallProbe.xcodeproj > out/project.json
xcodebuild build -project NativeInstallProbe.xcodeproj -scheme NativeInstallProbe -configuration Release -sdk iphoneos -destination 'generic/platform=iOS' -derivedDataPath "$RUNNER_TEMP/native-probe-derived" ARCHS=arm64 CURRENT_PROJECT_VERSION="$GITHUB_RUN_NUMBER" CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY='' DEVELOPMENT_TEAM='' 2>&1 | tee out/build.log
APP="$RUNNER_TEMP/native-probe-derived/Build/Products/Release-iphoneos/NativeInstallProbe.app"
test -f "$APP/NativeInstallProbe"
test ! -f "$APP/embedded.mobileprovision"
test ! -d "$APP/_CodeSignature"
lipo -archs "$APP/NativeInstallProbe" | tee out/architectures.txt
xcrun vtool -show-build "$APP/NativeInstallProbe" | tee out/platform.txt
grep -q arm64 out/architectures.txt
grep -Eq 'platform[[:space:]]+IOS([[:space:]]|$)' out/platform.txt
mkdir -p out/package/Payload
ditto "$APP" out/package/Payload/NativeInstallProbe.app
(cd out/package && ditto -c -k --keepParent Payload ../NativeInstallProbe-unsigned.ipa)
shasum -a 256 out/NativeInstallProbe-unsigned.ipa > out/checksum.sha256
python3 - <<'CHECK'
import json, os, plistlib, zipfile
from pathlib import Path
with zipfile.ZipFile('out/NativeInstallProbe-unsigned.ipa') as z:
    p=plistlib.loads(z.read('Payload/NativeInstallProbe.app/Info.plist'))
    assert p['CFBundleIdentifier']=='org.todowallpaper.nativeinstallprobe'
    assert not any(n.endswith('embedded.mobileprovision') for n in z.namelist())
Path('out/status.json').write_text(json.dumps({'compilation':'succeeded','signing':'not_performed','iphone_installation':'not_verified','commit':os.environ['GITHUB_SHA'],'run':os.environ['GITHUB_RUN_ID']},indent=2))
CHECK
# Upload only IPA/logs, not the redundant expanded app.
python3 - <<'CLEAN'
from pathlib import Path
import shutil
p=Path('out/package').resolve()
assert p.parent==Path('out').resolve() and p.name=='package'
shutil.rmtree(p)
CLEAN
echo 'Unsigned IPA generated. Windows signing and iPhone installation are still required.' >> "$GITHUB_STEP_SUMMARY"

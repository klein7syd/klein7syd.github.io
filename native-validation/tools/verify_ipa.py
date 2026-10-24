"""Structural checks only: these never claim iPhone installation or signature trust."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import plistlib
import struct
import zipfile

BASE_ID = 'org.todowallpaper.nativeinstallprobe'
GROUP_ID = 'group.' + BASE_ID
ROOT = 'Payload/NativeInstallProbe.app/'
EXT = ROOT + 'PlugIns/NativeProbeWidget.appex/'


def require(value, message):
    if not value:
        raise ValueError(message)


def profile_plist(data):
    start, end = data.find(b'<?xml'), data.find(b'</plist>')
    require(start >= 0 and end > start, 'Cannot read provisioning profile XML')
    return plistlib.loads(data[start:end + len(b'</plist>')])


def macho_info(data):
    require(len(data) >= 32 and data[:4] == b'\xcf\xfa\xed\xfe', 'Expected thin little-endian Mach-O 64')
    _, cpu, _, filetype, ncmds, sizeofcmds, _, _ = struct.unpack_from('<8I', data)
    require(cpu == 0x0100000C and filetype == 2, 'Expected ARM64 MH_EXECUTE')
    offset, platforms, signature = 32, [], None
    require(offset + sizeofcmds <= len(data), 'Truncated Mach-O commands')
    for _ in range(ncmds):
        command, size = struct.unpack_from('<II', data, offset)
        require(size >= 8 and offset + size <= 32 + sizeofcmds, 'Invalid load command')
        if command == 0x32:
            platforms.append(struct.unpack_from('<I', data, offset + 8)[0])
        if command == 0x1D:
            start, length = struct.unpack_from('<II', data, offset + 8)
            require(start + length <= len(data), 'Truncated signature')
            signature = data[start:start + length]
        offset += size
    require(platforms == [2], 'Not an iOS DEVICE executable')
    entitlements = None
    if signature:
        magic, length, count = struct.unpack_from('>III', signature)
        require(magic == 0xFADE0CC0 and length <= len(signature), 'Invalid signature superblob')
        for index in range(count):
            slot, position = struct.unpack_from('>II', signature, 12 + index * 8)
            if slot == 5:
                blob_magic, blob_size = struct.unpack_from('>II', signature, position)
                require(blob_magic == 0xFADE7171 and position + blob_size <= length, 'Invalid entitlement blob')
                entitlements = plistlib.loads(signature[position + 8:position + blob_size])
    return {'architecture':'arm64', 'platform':'iOS device', 'signature_present':signature is not None,
            'entitlements':entitlements}


def verify(path, *, unsigned=False, expected_app_id=BASE_ID, expected_group=GROUP_ID):
    results = []
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, 'ZIP CRC failure')
        for name in z.namelist():
            require(not name.startswith('/') and '..' not in PurePosixPath(name).parts, 'Unsafe ZIP entry')
        require({n for n in z.namelist() if n.startswith(ROOT + 'PlugIns/') and n.endswith('.appex/Info.plist')}
                == {EXT + 'Info.plist'}, 'Expected exactly one embedded Widget extension')
        versions = []
        for prefix, bundle_id in [(ROOT, expected_app_id), (EXT, expected_app_id + '.widget')]:
            info = plistlib.loads(z.read(prefix + 'Info.plist'))
            require(info['CFBundleIdentifier'] == bundle_id, 'Unexpected Bundle ID: ' + info['CFBundleIdentifier'])
            require(info.get('ProbeAppGroupIdentifier') == expected_group, 'App Group Info.plist mismatch')
            if prefix == EXT:
                require(info.get('NSExtension', {}).get('NSExtensionPointIdentifier') == 'com.apple.widgetkit-extension', 'Not a WidgetKit extension')
            versions.append((info['CFBundleShortVersionString'], info['CFBundleVersion']))
            binary = macho_info(z.read(prefix + info['CFBundleExecutable']))
            embedded = prefix + 'embedded.mobileprovision' in z.namelist()
            if unsigned:
                require(not binary['signature_present'] and not embedded, 'IPA is not unsigned')
                require(not any(n.startswith(prefix + '_CodeSignature/') for n in z.namelist()), 'Unexpected signature directory')
            else:
                require(binary['signature_present'] and embedded, 'Missing local signature/profile')
                grant = profile_plist(z.read(prefix + 'embedded.mobileprovision'))['Entitlements']
                signed = binary['entitlements'] or {}
                for source in [grant, signed]:
                    require(expected_group in source.get('com.apple.security.application-groups', []), 'App Group not granted/signed')
                    require(source.get('application-identifier', '').endswith('.' + bundle_id), 'Signing App ID mismatch')
                require(signed['application-identifier'] == grant['application-identifier'], 'Signature/profile identity mismatch')
            results.append({'bundle_id':bundle_id, 'version':versions[-1][0], 'build':versions[-1][1],
                            'app_group':info['ProbeAppGroupIdentifier'], 'embedded_profile':embedded, **binary})
        require(versions[0] == versions[1], 'App and extension versions differ')
    return {'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(), 'bundles':results,
            'structural_verification':'passed', 'cryptographic_signature_verification':'not_performed',
            'iphone_installation':'not_verified', 'device_capabilities':'not_verified'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ipa')
    parser.add_argument('--unsigned', action='store_true')
    parser.add_argument('--app-id', default=BASE_ID)
    parser.add_argument('--group', default=GROUP_ID)
    parser.add_argument('--report')
    args = parser.parse_args()
    report = verify(args.ipa, unsigned=args.unsigned, expected_app_id=args.app_id, expected_group=args.group)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(output + '\n', encoding='utf-8')
    print(output)

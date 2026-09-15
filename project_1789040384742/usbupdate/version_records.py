"""Resolve a target version from records bound to the selected package."""
import json
import re
from pathlib import Path


def explicit_versions(text):
    keys = {'qnx_version', 'qnx_system_version', 'qnx system version',
            'qnx version', 'ro.vendor.version.qnx.full.name'}
    values = set()
    def walk(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key.lower() in keys and isinstance(value, str) and value.strip():
                    values.add(value.strip())
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)
    try:
        walk(json.loads(text))
    except ValueError:
        pass
    for line in text.splitlines():
        match = re.fullmatch(r'\s*(?:QNX(?:[ _]system)?[ _]version|ro\.vendor\.version\.qnx\.full\.name)\s*[:=]\s*(\S.*?)\s*', line, re.I)
        if match:
            values.add(match[1].strip())
    return values


def unique_version(candidates):
    values = {value.strip() for value in candidates if isinstance(value, str) and value.strip()}
    if len(values) > 1:
        raise RuntimeError('本次升级包的目标 QNX 版本记录存在冲突：' + ', '.join(sorted(values)))
    if any(value.upper().startswith('REPLACE') for value in values):
        raise RuntimeError('目标 QNX 版本记录仍为占位值')
    return next(iter(values), '')


def resolve_expected(cfg, event):
    receipt_path = Path('prepared_package.json')
    if not receipt_path.is_file():
        raise RuntimeError('缺少本次升级记录 prepared_package.json；无法确定应核对哪个包。可用 -ExpectedQnx 指定目标。')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
    sha = receipt.get('sha256', '').lower()
    if not re.fullmatch(r'[0-9a-f]{64}', sha):
        raise RuntimeError('本次升级记录缺少有效安装包 SHA256')
    records = [receipt]
    manifest = Path(cfg.get('package_manifest', 'packages.json'))
    if manifest.is_file():
        records.extend(item for item in json.loads(manifest.read_text(encoding='utf-8-sig'))
                       if item.get('sha256', '').lower() == sha)
    folders = {item['folder'] for item in records if item.get('folder', '').startswith('/')}
    if len(folders) > 1:
        raise RuntimeError('同一包对应多个构建目录，无法唯一选择发布信息')
    folder = next(iter(folders), '')
    values = [item.get('expected_qnx', '') for item in records]
    if folder:
        values.append(cfg.get('cloud', {}).get('expected_qnx_by_build', {}).get(folder.rsplit('/', 1)[-1], ''))
    cache = Path('version_records.json')
    if cache.is_file():
        values.extend(item.get('expected_qnx', '') for item in json.loads(cache.read_text(encoding='utf-8-sig'))
                      if item.get('sha256', '').lower() == sha and item.get('folder') == folder)
    expected = unique_version(values)
    source = 'package_records'
    if not expected and folder:
        from cloud_download import fetch_release_version
        expected = fetch_release_version(cfg, folder, event)
        source = 'cloud_release_notes'
    if not expected:
        raise RuntimeError('本次包的记录及发布信息未提供明确 QNX 版本；无法自动判定版本正确，请补充对应发布信息或使用 -ExpectedQnx。')
    if source == 'cloud_release_notes':
        cached = json.loads(cache.read_text(encoding='utf-8-sig')) if cache.is_file() else []
        cached = [item for item in cached if not (item.get('sha256', '').lower() == sha and item.get('folder') == folder)]
        cached.append({'sha256': sha, 'folder': folder, 'expected_qnx': expected, 'source': source})
        temporary = cache.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(cached, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(cache)
    event('EXPECTED_QNX_RESOLVED', expected=expected, folder=folder, sha256=sha, source=source)
    print('自动取得目标 QNX：' + expected, flush=True)
    return expected

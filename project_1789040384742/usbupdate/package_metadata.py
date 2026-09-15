"""Read explicit QNX version fields only; never derive a version from a date."""
import json
import re
import zipfile
import xml.etree.ElementTree as ET

KEYS = {'qnx_version', 'qnx_system_version', 'qnx system version', 'ro.vendor.version.qnx.full.name'}

def qnx_version(path):
    values = set()
    def record(key, value):
        if key.lower() in KEYS and isinstance(value, str) and value.strip():
            values.add(value.strip())
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                record(key, item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    with zipfile.ZipFile(path) as archive:
        budget = 16 * 1024 * 1024
        for item in archive.infolist():
            if not item.filename.lower().endswith(('.json','.xml','.prop','.properties','.txt','.ini')) or item.file_size > 1024*1024:
                continue
            budget -= item.file_size
            if budget < 0:
                raise RuntimeError('包内元数据超过读取上限，无法确认唯一 QNX 版本')
            try:
                text = archive.read(item).decode('utf8')
            except UnicodeError:
                continue
            if item.filename.lower().endswith('.json'):
                try: walk(json.loads(text))
                except ValueError: pass
            elif item.filename.lower().endswith('.xml'):
                try:
                    for node in ET.fromstring(text).iter():
                        record(node.tag.split('}')[-1], node.text)
                        record(node.get('name',''), node.get('value') or node.text)
                except ET.ParseError:
                    pass
            else:
                for line in text.splitlines():
                    match = re.fullmatch(r'\s*([^=:#]+)\s*[=:]\s*([^#]+?)\s*', line)
                    if match: record(match[1].strip(), match[2].strip())
    if len(values) != 1:
        raise RuntimeError('包内未找到唯一、明确的 QNX 版本字段；需提供该构建的真实 expected_qnx_by_build，不能从包名猜测')
    return values.pop()

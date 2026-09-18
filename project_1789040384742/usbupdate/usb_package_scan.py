"""Discover original A/B ZIPs; expected date comes only from their filenames."""
import datetime as dt
import os
from pathlib import Path
import re


def filename_date(path):
    name = Path(path).name
    # Four-digit year formats avoid guessing month/day or a year from today's date.
    tokens = re.findall(r'(?<!\d)(20\d{2})[-_.]?(0[1-9]|1[0-2])[-_.]?([0-3]\d)(?!\d)', name)
    if not tokens:
        raise ValueError('包名没有日期（支持 YYYYMMDD、YYYY-MM-DD、YYYY_MM_DD）：' + name)
    dates = set()
    for year, month, day in tokens:
        try:
            dates.add(dt.date(int(year), int(month), int(day)).isoformat())
        except ValueError as exc:
            raise ValueError('包名日期无效：' + name) from exc
    if len(dates) != 1:
        raise ValueError('包名含有多个不同日期，无法确定目标版本：' + name)
    return dates.pop()


def discover_pair(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise RuntimeError('U盘目录不存在：' + str(root))
    candidates = []
    ignored = []
    def scan_error(error):
        raise RuntimeError('无法读取U盘目录：' + str(error)) from error
    for folder, directories, files in os.walk(root, followlinks=False, onerror=scan_error):
        directories[:] = [name for name in directories
                          if name.casefold() not in ('usb_update', 'system volume information', '$recycle.bin')
                          and not name.startswith('.') and not Path(folder, name).is_symlink()
                          and not getattr(Path(folder, name), 'is_junction', lambda: False)()]
        for name in files:
            path = Path(folder, name)
            if path.suffix.lower() != '.zip' or path.is_symlink():
                continue
            try:
                date = filename_date(path)
            except ValueError as exc:
                ignored.append(str(exc))
                continue
            candidates.append({'path': path.as_posix(), 'expected_date': date,
                               'date_source': 'filename', 'original_name': name})
    for message in ignored:
        print('未选入：' + message, flush=True)
    if len(candidates) != 2:
        names = '\n'.join(item['path'] for item in candidates)
        raise RuntimeError(f'U盘需恰好放入2个包名含日期的原始ZIP（USB_UPDATE除外），发现{len(candidates)}个。'
                           '请移走多余包或放入带完整日期的原始包，不会猜选版本。\n' + names)
    candidates.sort(key=lambda item: (item['expected_date'], item['path'].casefold()))
    if candidates[0]['expected_date'] == candidates[1]['expected_date']:
        raise RuntimeError('两个包的日期相同，按日期不能确认A/B切换，请使用不同日期的版本。')
    return candidates

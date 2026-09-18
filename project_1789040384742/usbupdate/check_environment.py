"""Read-only deployment check: no device commands, formatting or cloud login."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys


def main():
    errors = []
    print('Python:', sys.executable, sys.version.split()[0])
    if os.name != 'nt' or sys.version_info < (3, 10):
        errors.append('需要 Windows 和 Python 3.10+')
    for name in ('autocar', 'tkinter', 'playwright', 'uiautomator2', 'pytest', 'allure_pytest'):
        found = importlib.util.find_spec(name) is not None
        print(name + ': ' + ('OK' if found else 'MISSING'))
        if not found:
            errors.append('缺少模块 ' + name)
    for name in ('config.json', 'usb_stress_config.json'):
        try:
            cfg = json.loads(Path(name).read_text(encoding='utf-8-sig'))
            adb = cfg.get('adb', 'adb')
            if not (Path(adb).is_file() or shutil.which(adb)):
                errors.append(name + ': ADB 路径不存在')
            if not cfg.get('usb_serial') or cfg['usb_serial'].startswith('REPLACE'):
                errors.append(name + ': 请填写真实有线 ADB 序列号')
            print(name + ': JSON OK; USB=' + cfg['usb_root'])
            if cfg.get('smoke', {}).get('enabled'):
                from smoke_runner import discover
                root, files = discover(cfg)
                print('ATS:', root, '用例数:', len(files))
        except Exception as exc:
            errors.append(name + ': ' + str(exc))
    for error in errors:
        print('CHECK:', error)
    print('只检查本机文件/依赖；未验证驱动通信、供电、ADB授权、云盘会话或ATS扩展。')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())

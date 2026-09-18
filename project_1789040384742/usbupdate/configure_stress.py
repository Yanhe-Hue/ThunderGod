"""Interactive local A/B configuration only; never switches or flashes hardware."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from package_metadata import qnx_version

ROOT = Path(__file__).resolve().parent


def ask(label, default='', valid=lambda value: bool(value)):
    while True:
        value = input(f'{label} [{default}]: ').strip().strip('"') or str(default)
        if valid(value):
            return value
        print('输入无效，请重新填写。')


def package_date(path):
    version = qnx_version(path)
    match = re.search(r'-(\d{8}|\d{6})_\d{6}$', version)
    if not match:
        raise ValueError('QNX 字段中没有可识别的构建日期')
    digits = match[1]
    return dt.datetime.strptime(digits, '%Y%m%d' if len(digits) == 8 else '%y%m%d').date().isoformat()


def valid_date(value):
    try:
        return dt.date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def online_serials(output):
    return [parts[0] for line in output.splitlines()
            if len(parts := line.split()) >= 2 and parts[1] == 'device'
            and ':' not in parts[0]]


def save_config(path, cfg):
    # Write completely before replacing; cancel/errors before this leave config intact.
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if path.exists():
        backup = ROOT / 'deployment_logs' / ('config_backup_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        backup.mkdir(parents=True)
        shutil.copy2(path, backup / path.name)
        print('旧配置备份：', backup)
    os.replace(temporary, path)


def main():
    from tkinter import Tk, filedialog
    path = ROOT / 'usb_stress_config.json'
    source = path if path.exists() else ROOT / 'usb_stress_config.example.json'
    cfg = json.loads(source.read_text(encoding='utf-8-sig'))
    print('A/B 压测配置向导：只保存配置，不格式化、不升级、不运行用例。Ctrl+C 取消。')
    smoke = ask('每轮升级后执行 ATS 冒烟？y/n', 'y' if cfg.get('smoke', {}).get('enabled') else 'n', lambda x: x in ('y', 'n')) == 'y'
    bundled = ROOT / 'tools/platform-tools/adb.exe'
    default_adb = str(bundled) if bundled.is_file() else cfg.get('adb', 'adb')
    adb = ask('ADB 路径', default_adb, lambda x: Path(x).is_file() or bool(shutil.which(x)))
    result = subprocess.run([adb, 'devices', '-l'], capture_output=True, text=True, timeout=20, check=True)
    print(result.stdout)
    serials = online_serials(result.stdout)
    if not serials:
        raise RuntimeError('没有在线的独立有线 ADB，请先连接设备并允许调试后重试。')
    serial = ask('确认目标 ADB 序列号', serials[0] if len(serials) == 1 else '', lambda x: x in serials)
    usb = ask('确认目标 U 盘根目录（请先将 U 盘接到电脑）', cfg.get('usb_root', 'F:/'),
              lambda x: bool(re.fullmatch(r'[D-Zd-z]:[/\\]', x)) and Path(x).is_dir())
    switch = cfg.setdefault('usb_switch', {})
    switch['port'] = ask('USB 切换器 COM 号（以设备管理器为准）', switch.get('port', 'COM14'), lambda x: bool(re.fullmatch(r'COM[1-9]\d*', x)))
    switch['pc_usb_port'] = int(ask('电脑通道', switch.get('pc_usb_port', 3), lambda x: x in ('1', '2', '3', '4')))
    switch['car_usb_port'] = int(ask('车机通道', switch.get('car_usb_port', 2), lambda x: x in ('1', '2', '3', '4') and int(x) != switch['pc_usb_port']))
    power = cfg.setdefault('power', {})
    power['resource'] = ask('电源资源名（必须核对实际设备）', power.get('resource', 'ASRL13::INSTR'))
    window = Tk()
    window.withdraw()
    try:
        print('A/B包将在压测启动时自动扫描U盘，原名保留，目标日期取自包名。无需填写包路径和日期。')
        smoke_cfg = cfg.setdefault('smoke', {})
        smoke_cfg['enabled'] = smoke
        if smoke:
            project = filedialog.askdirectory(parent=window, title='选择完整 ATS 工程根目录（含 tests_scripts）', initialdir=smoke_cfg.get('project_root') or str(ROOT.parent))
            if not project or not (Path(project) / 'tests_scripts').is_dir():
                raise RuntimeError('必须选择含 tests_scripts 的完整 ATS 工程，配置未保存。')
            smoke_cfg.update(project_root=Path(project).as_posix(), case_directory='tests_scripts', select_before_stress=True)
            smoke_cfg.pop('case_files', None)
    finally:
        window.destroy()
    cfg.update(adb=adb, usb_serial=serial, usb_root=usb.replace('\\', '/'), wired_adb_independent=True)
    cfg.setdefault('stress', {}).update(mode='usb_pair_smoke' if smoke else 'local_pair', package_source='usb_scan', packages=[])
    print(json.dumps({key: cfg[key] for key in ('adb', 'usb_serial', 'usb_root', 'usb_switch', 'power', 'stress', 'smoke')}, ensure_ascii=False, indent=2))
    if ask('保存以上配置？y/n', 'y', lambda x: x in ('y', 'n')) != 'y':
        print('已取消，配置未保存。')
        return
    save_config(path, cfg)
    print('已保存：', path)
    print('开始压测请另行执行 .\\run_stress.ps1；硬件驱动、接线及 ATS 环境仍须提前准备。')


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as exc:
        print('配置未完成：', str(exc) or '用户取消')
        raise SystemExit(1)

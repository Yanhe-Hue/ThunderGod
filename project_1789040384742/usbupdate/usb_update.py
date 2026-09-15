"""USB upgrade coordinator with wired ADB and AutoCar hardware control."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

from hardware import AutoCarHardware


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def confirm(message):
    require(input(message + ' [输入 YES 继续]: ').strip() == 'YES', '用户取消')


def is_renault_package(name):
    return name.endswith(('update_all_renault', 'update_all_renault.zip'))


def build_timestamp(folder):
    match = re.match(r'^(\d{8}_\d{6})_', folder.rstrip('/').split('/')[-1])
    return dt.datetime.strptime(match[1], '%Y%m%d_%H%M%S') if match else None


def choose_package(entries, variant, today_only=False, require_version=True):
    require(variant in ('gas', 'no_gas'), 'variant 只能是 gas 或 no_gas')
    candidates = []
    for entry in entries:
        folder = entry['folder'].rstrip('/').split('/')[-1]
        gas = folder.endswith('full_userdebug')
        no_gas = folder.endswith('userdebug') and not gas and 'full' not in folder
        if not (gas if variant == 'gas' else no_gas):
            continue
        if not is_renault_package(entry['name']):
            continue
        date = dt.date.fromisoformat(entry['build_date'])
        if date <= dt.date.today():
            candidates.append((date, entry))
    require(candidates, '未找到符合版本分类和文件后缀的升级包')
    latest = max(date for date, _ in candidates)
    require(not today_only or latest == dt.date.today(), '没有今天的包；禁止静默回退旧包')
    matches = [entry for date, entry in candidates if date == latest]
    if len(matches) > 1:
        timestamps = [build_timestamp(entry['folder']) for entry in matches]
        require(all(timestamps), '同日多包但目录没有可比较的完整构建时间戳')
        require(all(stamp.date() == latest for stamp in timestamps), '目录时间戳与 build_date 不一致')
        latest_stamp = max(timestamps)
        matches = [entry for entry, stamp in zip(matches, timestamps) if stamp == latest_stamp]
    require(len(matches) == 1, '同一天有多个候选包，请在清单中明确保留目标构建')
    require(not require_version or bool(matches[0].get('expected_qnx')), '清单缺少 expected_qnx，无法核验目标版本')
    require(re.fullmatch(r'[0-9a-fA-F]{64}', matches[0].get('sha256', '')), '清单需要可信 SHA256')
    return matches[0]


def digest(path):
    result = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


class Upgrade:
    def gate(self, message):
        confirm(message)

    def __init__(self, cfg):
        self.cfg = cfg
        self.adb = cfg.get('adb', 'adb')
        self.serial = cfg.get('usb_serial', '')
        self._hardware = None
        self.logs = Path('logs') / dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        self.logs.mkdir(parents=True)

    def event(self, state, **data):
        print(state, flush=True)
        with (self.logs / 'events.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'time': dt.datetime.now().isoformat(), 'state': state, **data}, ensure_ascii=False) + '\n')

    def command(self, args, timeout=30):
        result = subprocess.run(args, capture_output=True, timeout=timeout)
        if result.returncode:
            stdout = result.stdout.decode('utf-8', errors='replace')[-1000:]
            stderr = result.stderr.decode('utf-8', errors='replace')[-1000:]
            self.event('COMMAND_FAILED', command=args, exit_code=result.returncode, stdout=stdout, stderr=stderr)
            raise RuntimeError(f'命令失败（退出码 {result.returncode}）：{subprocess.list2cmdline(args)}；'
                               + (stderr or stdout or '未返回错误文本，请查看 COMMAND_FAILED 日志'))
        return result.stdout.decode('utf-8', errors='replace').strip()

    def adb_run(self, *args, serial=None, timeout=30):
        return self.command([self.adb, '-s', serial or self.serial, *args], timeout)

    def check(self, cloud_login=True):
        self.event('ENVIRONMENT_CHECK')
        self.command([self.adb, 'version'])
        require(self.serial and not self.serial.startswith('REPLACE') and ':' not in self.serial, '请配置有线 ADB 的 usb_serial，不能使用 IP:端口')
        import importlib.util
        require(importlib.util.find_spec('autocar') is not None, '当前 Python 未安装 AutoCar，请使用 AUTOCAR_PYTHON 指向的环境')
        require(importlib.util.find_spec('playwright') is not None, '缺少云盘自动化依赖，请运行 setup.ps1 -InstallCloud')
        if cloud_login:
            from cloud_download import ensure_cloud_login
            ensure_cloud_login(self.cfg, self.event)
        self.event('ENVIRONMENT_CHECK_PASSED' if cloud_login else 'DEPENDENCIES_CHECK_PASSED')

    def connect(self):
        # USB serial selection only; never issue adb connect/tcpip.
        require(self.serial and not self.serial.startswith('REPLACE') and ':' not in self.serial, '请填写真实有线 ADB 序列号')
        require(self.adb_run('get-state') == 'device', '有线 ADB 未就绪，请检查数据线、授权和 USB 路由')
        remote_time = self.adb_run('shell', 'date', '+%s')
        require(remote_time.isdigit(), '无法读取车机时间')
        require(abs(int(remote_time) - time.time()) < self.cfg.get('max_clock_skew_seconds', 120), '车机与电脑时间偏差过大，请完成时间同步后重试')
        self.event('WIRED_ADB_READY')

    def hardware(self):
        if self._hardware is None:
            self._hardware = AutoCarHardware(self.cfg, self.event)
        return self._hardware

    def switch_to_pc(self):
        self.hardware().switch_usb('pc')
        print('等待电脑识别 U 盘：' + self.cfg['usb_root'], flush=True)
        deadline = time.monotonic() + self.cfg['usb_switch']['enumeration_timeout']
        while time.monotonic() < deadline:
            if Path(self.cfg['usb_root']).is_dir():
                self.event('USB_PC_ENUMERATED', root=self.cfg['usb_root'])
                return
            time.sleep(1)
        from volume import removable_roots
        visible = removable_roots()
        self.event('USB_PC_ENUMERATION_TIMEOUT', configured_root=self.cfg['usb_root'], visible_removable_roots=visible)
        raise RuntimeError(f"切换器已回读切到电脑成功，但配置盘符 {self.cfg['usb_root']} 未出现；"
                           f"当前可移动盘：{', '.join(visible) or '未检测到'}。请核对 usb_root；这不等同于切换指令失败。")

    def switch_to_car(self):
        require(self.cfg.get('wired_adb_independent') is True,
                '需先确认 U 盘接到车机时有线 ADB 可保持连接，再设置 wired_adb_independent=true')
        self.gate('请确认 Windows 已完成 U 盘安全弹出（写入缓存已落盘）')
        self.hardware().switch_usb('car')
        # A switch ACK is not evidence that the car mounted the update package.
        deadline = time.monotonic() + self.cfg['usb_switch']['enumeration_timeout']
        while time.monotonic() < deadline:
            if not Path(self.cfg['usb_root']).exists():
                break
            time.sleep(1)
        else:
            raise RuntimeError('切到车机后电脑仍能看到 U 盘盘符，请检查通道映射')
        self.connect()
        self.gate('请确认车机已识别 U 盘及 USB_UPDATE/Update.zip')

    def prepare(self, entry):
        self.switch_to_pc()
        root = Path(self.cfg['usb_root']).resolve()
        require(root.exists() and root.is_dir(), 'U 盘路径不存在')
        require(os.name == 'nt' and root == Path(root.anchor), 'usb_root 必须是 Windows 盘符根目录，例如 E:/')
        import ctypes
        require(ctypes.windll.kernel32.GetDriveTypeW(str(root)) == 2, '目标盘必须被 Windows 识别为可移动磁盘')
        target = root / 'USB_UPDATE' / 'Update.zip'
        self.gate(f"目标构建：{entry['folder']}；目标 QNX：{entry['expected_qnx']}；将写入 {target}，请确认 U 盘盘符")
        require(getattr(self, 'automatic', False) or not target.exists(), 'Update.zip 已存在，请先人工备份或移走再运行')
        target.parent.mkdir(exist_ok=True)
        partial = target.with_suffix('.zip.part')
        require(not partial.exists(), '发现上次未完成的 .part 文件，请检查并移走')
        source = entry['source']
        try:
            if source.startswith('https://'):
                headers = {}
                token_env = self.cfg.get('download_token_env')
                if token_env:
                    token = os.environ.get(token_env)
                    require(token, '下载令牌环境变量未设置')
                    headers['Authorization'] = 'Bearer ' + token
                request = urllib.request.Request(source, headers=headers)
                with urllib.request.urlopen(request, timeout=120) as response, partial.open('xb') as out:
                    shutil.copyfileobj(response, out, 4 * 1024 * 1024)
                    out.flush()
                    os.fsync(out.fileno())
            else:
                require('://' not in source, '下载地址只支持 HTTPS')
                source_path = Path(source)
                require(source_path.is_file(), '本地升级包不存在')
                require(shutil.disk_usage(root).free > source_path.stat().st_size, 'U 盘空间不足')
                with source_path.open('rb') as inp, partial.open('xb') as out:
                    shutil.copyfileobj(inp, out, 4 * 1024 * 1024)
                    out.flush()
                    os.fsync(out.fileno())
            require(digest(partial).lower() == entry['sha256'].lower(), '升级包 SHA256 不匹配')
            require(zipfile.is_zipfile(partial), '升级包不是有效 ZIP，可能下载到了登录页面')
            with zipfile.ZipFile(partial) as archive:
                require(archive.testzip() is None, 'ZIP CRC 校验失败')
            if target.exists():
                target.rename(target.with_name('Update.' + dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.zip.bak'))
            partial.rename(target)
        except Exception:
            # Preserve partial file for diagnosis; never silently replace an existing package.
            raise
        self.event('PACKAGE_READY', target=str(target), sha256=entry['sha256'])
        Path('prepared_package.json').write_text(json.dumps({
            'folder': entry['folder'], 'sha256': entry['sha256'],
            'expected_qnx': entry['expected_qnx'], 'target': str(target)
        }, ensure_ascii=False, indent=2), encoding='utf-8')

    def snapshot(self):
        if getattr(self, '_ui_reader', None) is not None:
            xml = self._ui_reader.dump_hierarchy()
        else:
            try:
                self.adb_run('shell', 'uiautomator', 'dump', '/sdcard/usb_update_window.xml')
                xml = self.adb_run('shell', 'cat', '/sdcard/usb_update_window.xml')
                ET.fromstring(xml)
            except (RuntimeError, subprocess.TimeoutExpired, ET.ParseError) as original:
                self.event('UI_DUMP_FALLBACK', reason=str(original), reader='uiautomator2')
                try:
                    import uiautomator2
                    reader = uiautomator2.connect_usb(self.serial)
                    xml = reader.dump_hierarchy()
                    self._ui_reader = reader
                except Exception as exc:
                    raise RuntimeError(f'页面读取失败；ADB dump：{original}；uiautomator2：{exc}') from exc
        root = ET.fromstring(xml)
        require(next(root.iter('node'), None) is not None, '页面树为空，无法识别升级状态')
        (self.logs / 'last_ui.xml').write_text(xml, encoding='utf-8')
        return root

    def nodes(self, root, selector):
        require(selector and set(selector) <= {'text', 'resource-id', 'content-desc'}, '控件选择器只支持精确 text/resource-id/content-desc')
        return [n for n in root.iter('node') if all(n.get(k) == v for k, v in selector.items())]

    def click(self, selector):
        nodes = self.nodes(self.snapshot(), selector)
        require(len(nodes) == 1, '控件未唯一匹配: ' + str(selector))
        require(nodes[0].get('enabled') == 'true', '控件尚未启用')
        bounds = re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', nodes[0].get('bounds', ''))
        require(bounds, '无法解析控件坐标')
        x1, y1, x2, y2 = map(int, bounds.groups())
        require(x2 > x1 and y2 > y1, '控件区域为空')
        self.adb_run('shell', 'input', 'tap', str((x1 + x2)//2), str((y1 + y2)//2))

    def wait_new_state(self, selector, timeout, description):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            root = self.snapshot()
            for failure in self.cfg['ui'].get('failure_selectors', []):
                require(not self.nodes(root, failure), '车机显示失败状态，停止执行')
            if self.nodes(root, selector):
                self.event(description)
                return
            time.sleep(2)
        raise RuntimeError(description + ' 超时；请检查车机，禁止自动重新刷写或断电')

    def phase(self, action, completion, description, timeout):
        selector = self.cfg['ui'].get(completion)
        if selector:
            require(not self.nodes(self.snapshot(), selector), '完成标记在操作前已存在，无法判断本次状态变化')
        self.click(self.cfg['ui'][action])
        if selector:
            self.wait_new_state(selector, timeout, description)
        else:
            confirm(description + '：请根据车机页面确认操作确实完成且没有错误')
            self.event(description + '_MANUAL_CONFIRMED')

    def flash(self):
        self.switch_to_car()
        # Entry navigation needs device-specific evidence, not guessed coordinates.
        confirm('请点击左侧应用图标，向下滑动找到 USBUpdating Btn，进入 USB Upgrade 的 Start Update 页面')
        self.phase('start', 'validation_done', 'VALIDATION_COMPLETE', self.cfg['validation_timeout'])
        confirm('即将第二次点击 Start Update 开始刷写，请确认校验成功且当前页面允许刷写')
        self.phase('start', 'flash_done', 'FLASH_COMPLETE', self.cfg['flash_timeout'])
        self.phase('activate', 'activation_done', 'ACTIVATION_COMPLETE', self.cfg['activation_timeout'])
        confirm('请确认车机明确提示激活完成并要求重启，此时允许断电重启')
        previous_boot_id = self.adb_run('shell', 'cat', '/proc/sys/kernel/random/boot_id')
        require(bool(previous_boot_id), '无法读取重启前 boot_id')
        self.hardware().power_cycle()
        self.wait_after_power_on()
        deadline = time.monotonic() + self.cfg['boot_timeout']
        self.event('WAITING_FOR_REBOOT')
        while time.monotonic() < deadline:
            try:
                boot_id = self.adb_run('shell', 'cat', '/proc/sys/kernel/random/boot_id', timeout=10)
                if boot_id and boot_id != previous_boot_id and self.adb_run('shell', 'getprop', 'sys.boot_completed', timeout=10) == '1':
                    self.event('BOOT_COMPLETE')
                    return
            except (RuntimeError, subprocess.TimeoutExpired):
                pass
            time.sleep(5)
        raise RuntimeError('重启后未检测到新的启动实例或有线 ADB 未恢复。不要再次刷写')

    def wait_after_power_on(self):
        self.event('WAITING_BEFORE_ADB', seconds=60)
        print('上电后等待 60 秒，再连接 ADB。', flush=True)
        time.sleep(60)

    def verify(self, expected):
        confirm('请打开 ThunderSoft 工程模式 → Version Date Information，显示 QNX system version')
        selector = self.cfg['ui'].get('qnx_value')
        if selector:
            nodes = self.nodes(self.snapshot(), selector)
            require(len(nodes) == 1, 'QNX 版本值控件未唯一匹配')
            actual = nodes[0].get('text', '').strip()
        else:
            actual = input('请输入页面中 QNX system version 的完整版本值: ').strip()
        require(actual == expected.strip(), f'QNX 版本不匹配，预期 {expected!r}，实际 {actual!r}')
        self.event('VERSION_VERIFIED', expected=expected, actual=actual, evidence='ui' if selector else 'manual')


def main():
    parser = argparse.ArgumentParser(description='U 盘升级：check 检查环境并完成云盘登录，通过后运行 auto。其他子命令用于分阶段排查。')
    parser.add_argument('action', choices=['check', 'auto', 'local', 'resume', 'verify-version', 'verify-adb', 'smoke', 'smoke-plan', 'stress', 'login', 'plan', 'connect', 'cloud', 'prepare', 'upgrade', 'verify'])
    parser.add_argument('--config', default='config.json')
    parser.add_argument('--variant', choices=['gas', 'no_gas'], help='本次选择 GAS 或 no_gas；省略时使用配置值')
    parser.add_argument('--expected-qnx', help='安装后的完整目标 QNX 版本；提供时严格核对')
    parser.add_argument('--skip-smoke', action='store_true', help='只验证版本，不执行后续冒烟用例')
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    if args.skip_smoke:
        cfg.setdefault('smoke', {})['enabled'] = False
    if args.variant:
        cfg['variant'] = args.variant
    if args.expected_qnx is not None:
        cfg['verify_expected_qnx'] = args.expected_qnx.strip()
    runner = Upgrade(cfg)
    try:
        if args.action == 'stress':
            from stress_update import run_stress
            run_stress(cfg)
            return 0
        if args.action == 'smoke':
            from smoke_runner import run_smoke
            run_smoke(cfg, runner.logs, runner.event)
            return 0
        if args.action == 'smoke-plan':
            from smoke_runner import discover
            root, files = discover(cfg)
            for index, path in enumerate(files, 1):
                print(f'{index:03d} {path.relative_to(root)}')
            return 0
        if args.action in ('verify-version', 'verify-adb'):
            from auto_update import AutomaticUpgrade
            AutomaticUpgrade(cfg).verify_installed_version(wait_before_adb=args.action == 'verify-version')
            return 0
        if args.action == 'resume':
            from auto_update import AutomaticUpgrade
            AutomaticUpgrade(cfg).resume()
            return 0
        if args.action in ('auto', 'local'):
            from auto_update import AutomaticUpgrade
            AutomaticUpgrade(cfg).run(local=args.action == 'local')
            return 0
        if args.action == 'login':
            from cloud_download import login
            login(cfg)
            return 0
        if args.action in ('check', 'connect', 'upgrade'):
            runner.check(cloud_login=args.action == 'check')
        if args.action == 'check':
            return
        if args.action == 'connect':
            runner.connect()
            return
        if args.action == 'cloud':
            from cloud_download import download_latest
            download_latest(cfg, runner.event)
            return
        entries = json.loads(Path(cfg['package_manifest']).read_text(encoding='utf-8-sig'))
        entry = choose_package(entries, cfg['variant'], cfg.get('today_only', False))
        if args.action == 'plan':
            print(json.dumps({k: entry[k] for k in ('folder', 'name', 'build_date', 'expected_qnx')}, ensure_ascii=False, indent=2))
        elif args.action == 'prepare':
            runner.prepare(entry)
        elif args.action == 'upgrade':
            receipt = json.loads(Path('prepared_package.json').read_text(encoding='utf-8'))
            require(all(receipt[k] == entry[k] for k in ('folder', 'sha256', 'expected_qnx')), '本次清单与 prepare 记录不一致，请核实 U 盘中的包')
            runner.event('TARGET_SELECTED', folder=entry['folder'], expected_qnx=entry['expected_qnx'])
            confirm('请确认车机 U 盘中的包来自本次 prepare 结果，且目标构建与上述记录一致')
            runner.flash()
            runner.verify(entry['expected_qnx'])
        elif args.action == 'verify':
            runner.connect()
            runner.verify(entry['expected_qnx'])
    except (Exception, KeyboardInterrupt) as exc:
        runner.event('STOPPED', reason=str(exc))
        print('流程停止：' + (str(exc) or '用户中断'))
        print('详细日志：', runner.logs)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

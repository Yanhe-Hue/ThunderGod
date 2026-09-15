"""Non-interactive upgrade. Missing evidence is an error, never a prompt."""
import json
from pathlib import Path
import re
import subprocess
import os
import ctypes
import time
import zipfile
import datetime as dt

from usb_update import Upgrade, choose_package, require, digest
from volume import eject, format_exfat


def qnx_build_date(version):
    match = re.search(r'-(\d{8}|\d{6})_\d{6}$', version.strip())
    require(match is not None, 'QNX 版本中没有可识别的日期后缀：' + version)
    value = match[1]
    if len(value) == 6:
        value = '20' + value
    try:
        return dt.datetime.strptime(value, '%Y%m%d').date()
    except ValueError as exc:
        raise RuntimeError('QNX 版本日期无效：' + version) from exc


class AutomaticUpgrade(Upgrade):
    automatic = True

    def snapshot(self):
        root = super().snapshot()
        # Observed non-security-setting information page; Back only dismisses it.
        if any(n.get('resource-id') == 'com.google.android.gms:id/auth_uncertified_notification_description'
               for n in root.iter('node')):
            self.adb_run('shell', 'input', 'keyevent', '4')
            self.event('CERTIFICATION_NOTICE_DISMISSED')
            root = super().snapshot()
        return root

    def gate(self, message):
        # prepare's volume/hash checks remain active. Switch gates are replaced below.
        self.event('AUTOMATIC_PREPARE')

    def preflight(self, local=False):
        missing = []
        for key in ('start', 'install', 'activate', 'validation_done', 'flash_done', 'activation_done', 'reboot_prompt'):
            if not self.cfg['ui'].get(key):
                missing.append('ui.' + key)
        for key in ('upgrade_navigation', 'version_navigation'):
            if not self.cfg.get('automation', {}).get(key):
                missing.append('automation.' + key)
        if not self.cfg['ui'].get('qnx_value') and not self.cfg['ui'].get('qnx_text_prefix'):
            missing.append('ui.qnx_value 或 ui.qnx_text_prefix')
        require(not missing, '自动流程缺少已核实配置：' + '、'.join(missing))
        for key in ('upgrade_navigation', 'version_navigation'):
            for step in self.cfg['automation'][key]:
                require((step.get('selector') or step.get('component')) and step.get('arrived'), key + ' 每步必须配置导航目标和到达锚点')
        require(self.cfg.get('wired_adb_independent') is True, '必须使用独立有线 ADB')
        require(local or Path(self.cfg['cloud'].get('auth_state', '.auth/cloud.json')).is_file(),
                '云盘尚未初始化登录，请先运行 check；auto 不会等待扫码')

    def on_upgrade_page(self, root):
        return bool(self.nodes(root, {'text': 'USB Upgrade'}) and self.nodes(
            root, {'resource-id': 'com.alliance.engineering.fota:id/usb_tv_title'}))

    def wait_navigation(self, arrived, timeout, allow_upgrade_page=False):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            root = self.snapshot()
            for failure in self.cfg['ui'].get('failure_selectors', []):
                require(not self.nodes(root, failure), '页面出现升级失败状态')
            if allow_upgrade_page and self.on_upgrade_page(root):
                self.event('NAVIGATION_DESTINATION_READY', evidence='upgrade_title_and_status')
                return True
            if self.nodes(root, arrived):
                self.event('NAVIGATION_READY', arrived=arrived)
                return False
            time.sleep(1)
        raise RuntimeError('导航等待超时，目标：' + str(arrived))

    def navigate(self, steps):
        upgrade_route = steps == self.cfg.get('automation', {}).get('upgrade_navigation')
        for step in steps:
            root = self.snapshot()
            for failure in self.cfg['ui'].get('failure_selectors', []):
                require(not self.nodes(root, failure), '页面出现升级失败状态')
            if upgrade_route and self.on_upgrade_page(root):
                self.event('NAVIGATION_ALREADY_AT_DESTINATION', evidence='upgrade_title_and_status')
                return
            if step.get('component'):
                require(re.fullmatch(r'[A-Za-z0-9_.$]+/[A-Za-z0-9_.$]+', step['component']), 'Activity 名称不合法')
                self.adb_run('shell', 'am', 'start', '-n', step['component'])
                if self.wait_navigation(step['arrived'], 30, upgrade_route):
                    return
                continue
            selector = step['selector']
            for attempt in range(step.get('max_scrolls', 0) + 1):
                root = self.snapshot()
                if self.nodes(root, selector):
                    break
                require(attempt < step.get('max_scrolls', 0), '导航目标不存在：' + str(selector))
                scroll = [n for n in root.iter('node') if n.get('scrollable') == 'true']
                require(len(scroll) == 1, '滚动容器不唯一')
                x1,y1,x2,y2 = map(int, re.findall(r'\d+', scroll[0].get('bounds', '')))
                self.adb_run('shell', 'input', 'swipe', str((x1+x2)//2), str(y2-30), str((x1+x2)//2), str(y1+30), '500')
                time.sleep(1)
            for retry in range(2):
                self.click(selector)
                try:
                    if self.wait_navigation(step['arrived'], 10, upgrade_route):
                        return
                    break
                except RuntimeError:
                    # Retry navigation only when the original menu is still present.
                    if retry or not self.nodes(self.snapshot(), selector):
                        raise

    def prepare(self, entry):
        self.entry = entry
        super().prepare(entry)

    def switch_to_car(self):
        eject(self.cfg['usb_root'])
        self.event('USB_EJECTED')
        self.hardware().switch_usb('car')
        self.connect()
        deadline = time.monotonic() + self.cfg['usb_switch']['enumeration_timeout']
        last_errors = {}
        observed_paths = []
        while time.monotonic() < deadline:
            observed_paths = self.car_package_paths()
            found = []
            for path in observed_paths:
                try:
                    result = self.adb_run('shell', 'sha256sum', path, timeout=600)
                except (RuntimeError, subprocess.TimeoutExpired) as exc:
                    last_errors[path] = str(exc)
                    continue
                if result.split() and result.split()[0].lower() == self.entry['sha256'].lower():
                    found.append(path)
                    # Android may expose one USB volume through multiple aliases.
                    break
                last_errors[path] = 'SHA256 不匹配：' + result[:100]
            if found:
                self.event('CAR_PACKAGE_VERIFIED', path=found[0])
                return
            time.sleep(2)
        self.event('CAR_PACKAGE_CHECK_FAILED', paths=observed_paths, errors=last_errors)
        raise RuntimeError('车机安装包检测失败：' +
                           ('未发现支持的 U 盘挂载目录' if not observed_paths else str(last_errors)))

    def car_package_paths(self):
        paths = []
        for base in ('/storage', '/mnt/media_rw'):
            try:
                names = self.adb_run('shell', 'ls', base).splitlines()
            except RuntimeError as exc:
                self.event('CAR_STORAGE_SCAN_FAILED', base=base, reason=str(exc))
                continue
            for name in names:
                name = name.strip()
                if re.fullmatch(r'(?:[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}|usb\d+)', name):
                    paths.append(base + '/' + name + '/USB_UPDATE/Update.zip')
        return paths

    def phase(self, action, completion, description, timeout):
        selector = self.cfg['ui'][completion]
        stages = ('validation_done', 'flash_done', 'activation_done')
        completed_stages = stages[stages.index(completion):] if completion in stages else (completion,)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            root = self.snapshot()
            for failure in self.cfg['ui'].get('failure_selectors', []):
                require(not self.nodes(root, failure), '页面出现升级失败状态')
            for completed in reversed(completed_stages):
                marker = self.cfg['ui'].get(completed)
                if marker and self.nodes(root, marker):
                    require(not self.cfg.get('_stress_round') or completed == 'validation_done',
                            '压测要求每轮实际重新安装：页面保留安装/激活完成状态，停止以免把旧结果计为成功')
                    self.event('PHASE_ALREADY_COMPLETE', action=action, completion=completion,
                               observed=completed, evidence='current_ui')
                    print(f'检测到 {completed}，跳过 {action}，继续下一步。', flush=True)
                    return
            buttons = self.nodes(root, self.cfg['ui'][action])
            require(len(buttons) <= 1, '动作按钮不唯一')
            if buttons and buttons[0].get('enabled') == 'true':
                break
            time.sleep(1)
        else:
            raise RuntimeError('未等到可用的动作按钮：' + action)
        self.click(self.cfg['ui'][action])
        self.wait_new_state(selector, timeout, description)

    def flash(self, package_ready=False):
        if not package_ready:
            self.switch_to_car()
        self.navigate(self.cfg['automation']['upgrade_navigation'])
        for action, completion, timeout in [('start','validation_done','validation_timeout'),
                                             ('install','flash_done','flash_timeout'),
                                             ('activate','activation_done','activation_timeout')]:
            self.phase(action, completion, completion.upper(), self.cfg[timeout])
        self.wait_new_state(self.cfg['ui']['reboot_prompt'], 30, 'REBOOT_REQUEST_CONFIRMED')
        old = self.adb_run('shell', 'cat', '/proc/sys/kernel/random/boot_id')
        require(bool(old), '无法读取重启前 boot_id')
        self.hardware().power_cycle()
        self.wait_after_power_on()
        deadline = time.monotonic() + self.cfg['boot_timeout']
        while time.monotonic() < deadline:
            try:
                new = self.adb_run('shell', 'cat', '/proc/sys/kernel/random/boot_id', timeout=10)
                if new and new != old and self.adb_run('shell', 'getprop', 'sys.boot_completed', timeout=10) == '1':
                    return
            except (RuntimeError, subprocess.TimeoutExpired):
                pass
            time.sleep(5)
        raise RuntimeError('自动重启验证超时')

    def resume(self):
        try:
            self.preflight(local=True)
            self.connect()
            self.event('RESUME_STARTED', package_checks='skipped', usb_switch='skipped')
            print('从车机升级页面继续：不下载、不格式化、不切换 USB、不校验安装包文件。', flush=True)
            self.flash(package_ready=True)
            # No verified package identity: do not reuse a previous package's target version.
            self.verify_and_smoke(self.cfg.get('verify_expected_qnx', ''))
            self.event('RESUME_COMPLETE')
        except BaseException as exc:
            self.event('RESUME_STOPPED', reason=str(exc))
            raise

    def verify_installed_version(self, wait_before_adb=True):
        if wait_before_adb:
            self.wait_after_power_on()
        self.connect()
        self.verify_and_smoke('')

    def verify_and_smoke(self, expected=''):
        self.verify(expected, date_only=not bool(expected))
        from smoke_runner import run_smoke
        run_smoke(self.cfg, self.logs, self.event)

    def verify(self, expected, date_only=False):
        self.navigate(self.cfg['automation']['version_navigation'])
        root = self.snapshot()
        selector = self.cfg['ui'].get('qnx_value')
        if selector:
            nodes = self.nodes(root, selector)
            require(len(nodes) == 1, 'QNX 值控件不唯一')
            actual = nodes[0].get('text', '').strip()
        else:
            prefix = self.cfg['ui']['qnx_text_prefix']
            values = [line[len(prefix):].strip() for n in root.iter('node')
                      for line in n.get('text','').splitlines() if line.startswith(prefix)]
            require(len(values) == 1 and values[0], '工程模式中的 QNX 版本行不唯一')
            actual = values[0]
        if date_only:
            actual_date = qnx_build_date(actual)
            today = dt.date.fromisoformat(self.cfg['_stress_expected_date']) if self.cfg.get('_stress_expected_date') else dt.date.today()
            self.event('VERSION_DATE_READ', actual=actual, actual_date=actual_date.isoformat(),
                       expected_date=today.isoformat())
            require(actual_date == today, f'QNX 日期不符：预期 {today}，实际 {actual_date}（{actual}）')
            self.event('VERSION_DATE_VERIFIED', actual=actual, date=today.isoformat())
            print(f'QNX 日期核对通过：{actual_date}', flush=True)
            return
        if not expected:
            self.event('VERSION_RECORDED_NOT_VERIFIED', actual=actual, evidence='ui')
            print('升级后 QNX：' + actual + '；未提供目标版本，仅记录，不判定版本一致。', flush=True)
            return
        require(actual == expected.strip(), f'QNX 不符：预期 {expected!r}，实际 {actual!r}')
        self.event('VERSION_VERIFIED', expected=expected, actual=actual, evidence='ui')

    def local_package(self, root):
        from tkinter import Tk, filedialog
        window = Tk()
        window.withdraw()
        try:
            selected = filedialog.askopenfilename(
                parent=window, title='选择已有升级包（ZIP 或下载完成的 PART）',
                initialdir=str(root / 'USB_UPDATE' if (root / 'USB_UPDATE').is_dir() else root),
                filetypes=[('升级包', '*.zip *.part'), ('所有文件', '*.*')])
        finally:
            window.destroy()
        if not selected:
            self.event('LOCAL_SELECTION_CANCELLED')
            return None
        source = Path(selected).resolve()
        require(source.is_file() and zipfile.is_zipfile(source), '所选文件不是完整 ZIP 升级包')
        print('正在校验已有安装包：' + str(source), flush=True)
        with zipfile.ZipFile(source) as archive:
            require(archive.testzip() is None, 'ZIP CRC 校验失败，不能使用未完整下载的包')
        expected = ''
        from package_metadata import qnx_version
        try:
            expected = qnx_version(source)
        except RuntimeError as exc:
            self.event('TARGET_VERSION_UNAVAILABLE', reason=str(exc))
        entry = {'folder': 'local/' + source.name, 'source': str(source),
                 'sha256': digest(source), 'expected_qnx': expected}
        target = root / 'USB_UPDATE' / 'Update.zip'
        if source != target.resolve():
            self.prepare(entry)
        entry['source'] = str(target)
        self.event('LOCAL_PACKAGE_SELECTED', source=str(source), sha256=entry['sha256'])
        return entry

    def run(self, local=False):
        try:
            self.preflight(local=local)
            self.connect()
            from cloud_download import download_latest
            self.switch_to_pc()
            root = Path(self.cfg['usb_root']).resolve()
            require(os.name == 'nt' and root == Path(root.anchor), 'usb_root 必须是 Windows 盘符根目录')
            require(ctypes.windll.kernel32.GetDriveTypeW(str(root)) == 2, '只允许写入可移动 U 盘')
            # Download into the final USB directory; no second manual copy/rename step.
            if local:
                entry = self.local_package(root)
                if entry is None:
                    return False
            else:
                def initialize_usb():
                    print('初始化 U 盘为 exFAT（清除全盘文件）：' + str(root), flush=True)
                    self.event('USB_FORMAT_STARTED', root=str(root))
                    format_exfat(root)
                    self.event('USB_FORMAT_COMPLETE', root=str(root), filesystem='exFAT')
                entry = download_latest(self.cfg, self.event, automatic=True,
                                        destination=root / 'USB_UPDATE', target_name='Update.zip',
                                        prepare_destination=initialize_usb)
                entry = choose_package([entry], self.cfg['variant'], self.cfg.get('today_only', False),
                                       require_version=False)
            self.entry = entry
            Path('prepared_package.json').write_text(json.dumps({
                'folder': entry['folder'], 'sha256': entry['sha256'],
                'expected_qnx': entry['expected_qnx'], 'target': entry['source']
            }, ensure_ascii=False, indent=2), encoding='utf-8')
            self.event('PACKAGE_READY', target=entry['source'])
            self.flash()
            self.verify_and_smoke(self.cfg.get('verify_expected_qnx', ''))
            self.event('AUTO_COMPLETE')
            return True
        except BaseException as exc:
            self.event('AUTO_STOPPED', reason=str(exc))
            raise

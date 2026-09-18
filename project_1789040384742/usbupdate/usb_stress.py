"""Independent unlimited USB stress, with optional USB A/B plus ATS smoke."""
import argparse
import copy
import datetime as dt
import itertools
import json
import os
from pathlib import Path
import shutil
import time
import zipfile
import hashlib

from auto_update import AutomaticUpgrade, qnx_build_date
from package_metadata import qnx_version
from usb_update import digest, require


def hash_progress(path, label):
    total = path.stat().st_size
    done = 0
    start = last = time.monotonic()
    sha = hashlib.sha256()
    print(f'{label}：{path.name}，{total / 1024**3:.2f} GiB', flush=True)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            sha.update(block)
            done += len(block)
            if time.monotonic() - last >= 5:
                print(f'{label} {done / max(total, 1):.0%}，{done / 1024**2 / max(time.monotonic()-start, .001):.1f} MiB/s', flush=True)
                last = time.monotonic()
    print(f'{label}完成，耗时 {time.monotonic()-start:.1f} 秒', flush=True)
    return sha.hexdigest()


def expected_date(path, supplied='', fallback=''):
    if supplied:
        return dt.date.fromisoformat(supplied).isoformat()
    try:
        return qnx_build_date(qnx_version(path)).isoformat()
    except RuntimeError:
        require(bool(fallback), '包内无法读取 QNX 日期，请在独立配置的 expected_date 填写该包日期：' + str(path))
        return dt.date.fromisoformat(fallback).isoformat()


def choose_files(count):
    from tkinter import Tk, filedialog
    window = Tk()
    window.withdraw()
    try:
        paths = []
        for index in range(count):
            path = filedialog.askopenfilename(parent=window,
                title=f'选择版本 {"AB"[index]} 安装包', filetypes=[('安装包', '*.zip *.part'), ('所有文件', '*.*')])
            require(bool(path), '用户取消选包')
            paths.append({'path': path, 'expected_date': ''})
        return paths
    finally:
        window.destroy()


def validate_settings(settings):
    mode = settings['mode']
    require(mode in ('cloud', 'local_single', 'local_pair', 'usb_pair_smoke'), '未知压测模式')
    if mode in ('local_pair', 'usb_pair_smoke') and settings.get('package_source') == 'usb_scan':
        return mode  # Ignore stale manual package paths/dates in automatic discovery mode.
    packages = settings.get('packages', [])
    require(isinstance(packages, list), 'packages 必须是数组')
    if mode != 'cloud' and packages:
        require(len(packages) == (2 if mode in ('local_pair', 'usb_pair_smoke') else 1), '本地包数量与模式不符')
        for package in packages:
            require(bool(package.get('path')), '安装包 path 不能为空；弹窗选包时将 packages 设为 []')
            if package.get('expected_date'):
                dt.date.fromisoformat(package['expected_date'])
    return mode


def usb_package(spec, root):
    source = Path(spec['path']).resolve()
    active_dir = root / 'USB_UPDATE'
    require(source.is_relative_to(root) and not source.is_relative_to(active_dir),
            '原始 A/B 包必须位于目标 U 盘内、USB_UPDATE 目录外，例如 F:/versions/A.zip')
    require(source.is_file() and zipfile.is_zipfile(source), 'U 盘安装包不是完整 ZIP：' + str(source))
    print(f'首次 ZIP 完整性检查：{source.name}（解压校验大包可能需要数分钟）', flush=True)
    with zipfile.ZipFile(source) as archive:
        require(archive.testzip() is None, '安装包 CRC 校验失败')
    full_version = spec.get('expected_qnx', '').strip()
    date = expected_date(source, spec.get('expected_date') or (qnx_build_date(full_version).isoformat() if full_version else ''))
    return {'source': str(source), 'original_source': str(source), 'sha256': hash_progress(source, '首次SHA256'),
            'expected_date': date, 'expected_qnx': full_version, 'folder': 'usb/' + source.name}


def cache_package(spec, cache, index, fallback=''):
    source = Path(spec['path']).resolve()
    require(source.is_file() and zipfile.is_zipfile(source), '不是完整 ZIP：' + str(source))
    with zipfile.ZipFile(source) as archive:
        require(archive.testzip() is None, 'ZIP CRC 错误：' + str(source))
    date = expected_date(source, spec.get('expected_date', ''), fallback)
    require(shutil.disk_usage(cache).free > source.stat().st_size, '电脑压测缓存空间不足')
    sha = digest(source)
    target = cache / f'package_{index}.zip'
    shutil.copyfile(source, target)
    require(digest(target) == sha, '缓存复制校验失败')
    return {'source': str(target), 'original_source': str(source), 'sha256': sha,
            'expected_date': date, 'expected_qnx': '', 'folder': 'stress/' + source.name}


class PackageRound(AutomaticUpgrade):
    def __init__(self, cfg, package):
        super().__init__(cfg)
        self.package = package

    def verify_and_smoke(self, expected=''):
        # Version failure remains fatal; only completed ATS case results may be tolerated.
        self.verify(expected, date_only=not bool(expected))
        from smoke_runner import run_smoke
        from ats_client import SmokeResultFailure
        self._smoke_started = True
        try:
            self.smoke_result = run_smoke(self.cfg, self.logs, self.event)
        except SmokeResultFailure as exc:
            self.smoke_result = {'status': 'failed', 'reason': str(exc),
                                 'response': exc.response, 'report': exc.report}
            self.event('STRESS_SMOKE_FAILED_CONTINUING', **self.smoke_result)
            print('本轮冒烟未全部通过，已保存失败结果，继续下一轮压测。报告：' + exc.report, flush=True)

    def local_package(self, root):
        entry = copy.deepcopy(self.package)
        source = Path(entry['source'])
        target = root / 'USB_UPDATE' / 'Update.zip'
        target.parent.mkdir(exist_ok=True)
        force_replace = getattr(self, 'cfg', {}).get('_stress_replace', False)
        if force_replace or not target.is_file() or hash_progress(target, '检查当前活动包') != entry['sha256']:
            partial = target.with_name('Update.zip.part')
            require(not partial.exists(), '存在未完成 Update.zip.part，请检查后移走')
            require(shutil.disk_usage(root).free > source.stat().st_size, 'U 盘剩余空间不足以原子替换安装包')
            sha = hashlib.sha256()
            total = source.stat().st_size
            done = 0
            start = last = time.monotonic()
            self.event('PACKAGE_COPY_STARTED', source=str(source), bytes=total)
            with source.open('rb') as inp, partial.open('xb') as out:
                for block in iter(lambda: inp.read(4 * 1024 * 1024), b''):
                    sha.update(block)
                    out.write(block)
                    done += len(block)
                    if time.monotonic() - last >= 5:
                        print(f'复制并校验 {source.name}：{done / max(total, 1):.0%}，{done / 1024**2 / max(time.monotonic()-start, .001):.1f} MiB/s', flush=True)
                        last = time.monotonic()
                out.flush()
                os.fsync(out.fileno())
            require(sha.hexdigest() == entry['sha256'], '原始安装包被修改，保留临时文件并停止')
            self.event('PACKAGE_COPY_FINISHED', seconds=round(time.monotonic()-start, 2))
            require(hash_progress(partial, '复制后读回校验') == entry['sha256'], 'U 盘复制哈希不匹配')
            partial.replace(target)
        else:
            require(hash_progress(source, '复用原包校验') == entry['sha256'], '原始安装包被修改，停止压测')
        entry['source'] = str(target)
        self.event('STRESS_PACKAGE_READY', sha256=entry['sha256'], expected_date=entry['expected_date'])
        return entry


def run(cfg):
    settings = cfg['stress']
    mode = validate_settings(settings)
    cfg = copy.deepcopy(cfg)
    with_smoke = mode == 'usb_pair_smoke'
    cfg.setdefault('smoke', {})['enabled'] = with_smoke
    if with_smoke:
        cfg['smoke'].setdefault('case_directory', 'usbupdate/smoke_cases')
        if cfg['smoke'].get('select_before_stress', False):
            from smoke_picker import select_smoke_files
            cfg['smoke']['case_files'] = select_smoke_files(cfg)
        from smoke_runner import discover
        discover(cfg)  # Reject an empty plan before touching hardware.
    cfg.pop('verify_expected_qnx', None)
    controller = AutomaticUpgrade(cfg)
    report = controller.logs / 'stress_summary.json'
    state = {'mode': mode, 'status': 'preparing', 'smoke': with_smoke,
             'selected_cases': cfg.get('smoke', {}).get('case_files'), 'rounds': [],
             'started': dt.datetime.now().isoformat()}
    def save():
        temp = report.with_suffix('.tmp')
        temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(report)
    save()
    record = None
    runner = None
    started = time.monotonic()
    try:
        # Keep both originals on the PC before replacing the active USB package.
        usb_root = Path(cfg['usb_root']).resolve()
        if not with_smoke:
            cache_root = Path(settings.get('cache_dir', 'stress_cache')).resolve()
            require(not cache_root.is_relative_to(usb_root), 'cache_dir 必须在电脑磁盘，不能位于目标 U 盘')
            cache = cache_root / controller.logs.name
            cache.mkdir(parents=True, exist_ok=False)
        controller.preflight(local=mode != 'cloud')
        controller.connect()
        controller.switch_to_pc()
        fallback = ''
        if mode == 'cloud':
            from cloud_download import download_latest
            from volume import format_exfat
            entry = download_latest(cfg, controller.event, automatic=True,
                destination=usb_root / 'USB_UPDATE', target_name='Update.zip',
                prepare_destination=lambda: format_exfat(cfg['usb_root']))
            specs = [{'path': entry['source'], 'expected_date': settings.get('cloud_expected_date', '')}]
            fallback = entry['build_date']
        elif mode in ('local_pair', 'usb_pair_smoke') and settings.get('package_source') == 'usb_scan':
            from usb_package_scan import discover_pair
            specs = discover_pair(usb_root)
            state['detected_packages'] = specs
            save()
            controller.event('USB_PACKAGES_DISCOVERED', packages=specs)
            for label, spec in zip('AB', specs):
                print(f'自动识别{label}：{spec["original_name"]}；目标日期 {spec["expected_date"]}', flush=True)
        else:
            specs = settings.get('packages') or choose_files(2 if mode in ('local_pair', 'usb_pair_smoke') else 1)
        validation_start = time.monotonic()
        controller.event('PACKAGE_VALIDATION_STARTED', count=len(specs))
        packages = ([usb_package(spec, usb_root) for spec in specs] if with_smoke else
                    [cache_package(spec, cache, index, fallback) for index, spec in enumerate(specs)])
        controller.event('PACKAGE_VALIDATION_FINISHED', seconds=round(time.monotonic()-validation_start, 2))
        if mode in ('local_pair', 'usb_pair_smoke'):
            require(packages[0]['sha256'] != packages[1]['sha256'], 'A/B 包内容相同，不能作为两个版本交替升级')
        state.update(status='running', packages=packages)
        save()
        for index in itertools.count(1):
            package = packages[(index - 1) % len(packages)]
            round_cfg = copy.deepcopy(cfg)
            round_cfg['_stress_round'] = index
            round_cfg['_stress_replace'] = mode in ('local_pair', 'usb_pair_smoke')
            round_cfg['_stress_expected_date'] = package['expected_date']
            if with_smoke and package.get('expected_qnx'):
                round_cfg['verify_expected_qnx'] = package['expected_qnx']
            runner = PackageRound(round_cfg, package)
            record = {'round': index, 'package': (index - 1) % len(packages) + 1,
                      'original_source': package.get('original_source'),
                      'sha256': package['sha256'], 'expected_date': package['expected_date'],
                      'logs': str(runner.logs), 'status': 'running'}
            state['rounds'].append(record)
            save()
            started = time.monotonic()
            print(f'压测第 {index} 轮，包 {record["package"]}，预期日期 {package["expected_date"]}；Ctrl+C 停止', flush=True)
            require(runner.run(local=True), '升级被取消')
            smoke_result = getattr(runner, 'smoke_result', None)
            smoke_failed = isinstance(smoke_result, dict) and smoke_result.get('status') == 'failed'
            record.update(status='completed_with_smoke_failures' if smoke_failed else 'passed',
                          upgrade_status='passed', seconds=round(time.monotonic() - started, 2))
            if isinstance(smoke_result, dict):
                record['smoke'] = smoke_result
            state['completed_rounds'] = index
            state['smoke_failed_rounds'] = sum(r['status'] == 'completed_with_smoke_failures' for r in state['rounds'])
            state['fully_passed_rounds'] = sum(r['status'] == 'passed' for r in state['rounds'])
            print(f"第 {index} 轮升级校验通过；累计完成 {index} 轮，全部通过 {state['fully_passed_rounds']} 轮，冒烟未通过 {state['smoke_failed_rounds']} 轮", flush=True)
            save()
    except BaseException as exc:
        from error_evidence import capture
        capture(runner or controller, exc)
        status = 'cancelled' if isinstance(exc, KeyboardInterrupt) else 'failed'
        if record is not None and record['status'] == 'running':
            record.update(status=status, reason=str(exc) or '手动停止', seconds=round(time.monotonic() - started, 2))
        state.update(status=status, reason=str(exc) or '手动停止', finished=dt.datetime.now().isoformat())
        save()
        print(f'压测已停止；汇总：{report.resolve()}', flush=True)
        raise


def main():
    parser = argparse.ArgumentParser(description='独立 U 盘无限循环压测，支持 U 盘双版本与 ATS 冒烟')
    parser.add_argument('--config', default='usb_stress_config.json')
    parser.add_argument('--login', action='store_true', help='仅检查环境并登录云盘，不启动压测')
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    os.chdir(config_path.parent)
    cfg = json.loads(config_path.read_text(encoding='utf-8-sig'))
    try:
        if args.login:
            AutomaticUpgrade(cfg).check()
        else:
            run(cfg)
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print('压测错误：' + str(exc), flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Run the existing numbered smoke files serially without changing their fixtures."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

PATTERN = re.compile(r'test_smoke_test_(\d+)(?:\.(\d+))?(?:_row(\d+))?\.py$')
DEFAULT_PROJECT = str(Path(__file__).resolve().parent.parent)


def discover(cfg):
    root = Path(cfg.get('smoke', {}).get('project_root') or DEFAULT_PROJECT).resolve()
    directory = (root / cfg.get('smoke', {}).get('case_directory', 'tests_scripts')).resolve()
    if not directory.is_relative_to(root):
        raise RuntimeError('冒烟目录必须位于 ATS 工程内')
    if not directory.is_dir():
        raise RuntimeError('冒烟用例目录不存在：' + str(directory))
    requested = cfg.get('smoke', {}).get('case_files')
    selected = None
    if requested is not None:
        if not isinstance(requested, list) or not requested:
            raise RuntimeError('case_files 必须是非空用例路径数组')
        selected = {(root / name).resolve() for name in requested}
        if len(selected) != len(requested) or any(not p.is_file() or not p.is_relative_to(directory) or not PATTERN.fullmatch(p.name) for p in selected):
            raise RuntimeError('case_files 含重复、不存在或不属于冒烟目录的用例')
    numbered = []
    for path in directory.rglob('*.py'):
        match = PATTERN.fullmatch(path.name)
        if match and '__pycache__' not in path.parts and (selected is None or path.resolve() in selected):
            major, minor, row = (int(value or 0) for value in match.groups())
            numbered.append(((major, minor, row, path.relative_to(root).as_posix()), path))
    files = [path for _, path in sorted(numbered)]
    if not files:
        raise RuntimeError('未发现带编号的冒烟用例')
    return root, files


def run_smoke(cfg, logs, event):
    if not cfg.get('smoke', {}).get('enabled', True):
        event('SMOKE_SKIPPED', reason='disabled_by_configuration')
        return
    root, files = discover(cfg)
    from ats_client import run_ats
    return run_ats(cfg, root, files, logs, event)


def run_pytest(cfg, logs, event):
    if not cfg.get('smoke', {}).get('enabled', True):
        event('SMOKE_SKIPPED', reason='disabled_by_configuration')
        return
    root, files = discover(cfg)
    report = (Path(logs) / 'smoke').resolve()
    report.mkdir(parents=True, exist_ok=True)
    plan = [str(path.relative_to(root)) for path in files]
    (report / 'order.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    results = []
    environment = os.environ.copy()
    environment['PYTEST_ADDOPTS'] = ''  # No inherited parallelism, randomization or early exit.
    environment['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
    environment['PYTHONPATH'] = str(root) + os.pathsep + environment.get('PYTHONPATH', '')
    environment['PYTHONIOENCODING'] = 'utf-8'
    event('SMOKE_STARTED', count=len(files), report=str(report))
    for index, path in enumerate(files, 1):
        case_report = report / f'{index:03d}_{path.stem}'
        case_report.mkdir()
        environment['AUTOCAR_REPORT_DIR'] = str(case_report)
        junit = case_report / 'junit.xml'
        command = [sys.executable, '-m', 'pytest', '-p', 'allure_pytest', '-o', 'addopts=', '--import-mode=importlib',
                   str(path), '-v', '--tb=short', '--junitxml=' + str(junit),
                   '--alluredir=' + str(case_report / 'allure-results')]
        event('SMOKE_CASE_STARTED', index=index, file=str(path))
        print(f'冒烟 [{index}/{len(files)}] {path.name}', flush=True)
        with (case_report / 'output.log').open('w', encoding='utf-8') as output:
            try:
                completed = subprocess.run(command, cwd=root, env=environment, stdout=output,
                                           stderr=subprocess.STDOUT,
                                           timeout=cfg.get('smoke', {}).get('case_timeout', 1800))
                code = completed.returncode
            except subprocess.TimeoutExpired:
                code = -1
                output.write('\n用例执行超时\n')
        counts = {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
        if junit.is_file():
            try:
                tree = ET.parse(junit)
                for suite in tree.iter('testsuite'):
                    for key in counts:
                        counts[key] += int(suite.get(key, 0))
            except (ET.ParseError, ValueError):
                code = code or -2
        passed = (code == 0 and counts['tests'] > 0 and
                  not any(counts[key] for key in ('failures', 'errors', 'skipped')))
        result = {'index': index, 'file': str(path.relative_to(root)), 'exit_code': code,
                  'passed': passed, **counts, 'output': str(case_report / 'output.log')}
        results.append(result)
        (report / 'summary.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        event('SMOKE_CASE_COMPLETE', **result)
    failures = sum(not result['passed'] for result in results)
    event('SMOKE_COMPLETE', files=len(results), failed_files=failures, report=str(report))
    if failures:
        raise RuntimeError(f'冒烟执行完成，{failures}/{len(results)} 个文件未全部通过；报告：{report}')

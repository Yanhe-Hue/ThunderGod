"""Submit an ordered plan to ATS; mirror ATS's own run.log to this terminal."""
import codecs
import json
import os
from pathlib import Path
import time
from urllib.parse import urlencode


class SmokeResultFailure(RuntimeError):
    """ATS finished the run, but its cases did not all pass."""
    def __init__(self, response, report):
        self.response = response
        self.report = str(report)
        super().__init__('ATS 冒烟未全部通过：' + json.dumps(response, ensure_ascii=False))


def run_ats(cfg, root, files, logs, event):
    report = (Path(logs) / 'smoke').resolve()
    # Bridge only accepts requests in the ATS workspace's usbupdate/logs.
    if not report.is_relative_to(root / 'usbupdate' / 'logs'):
        report = root / 'usbupdate' / 'logs' / ('ats_' + time.strftime('%Y%m%d_%H%M%S')) / 'smoke'
    report.mkdir(parents=True, exist_ok=False)
    request = report / 'ats-request.json'
    request.write_text(json.dumps({'created': int(time.time() * 1000), 'files': [str(p) for p in files],
                                  'deviceId': cfg.get('usb_serial', '')}, ensure_ascii=False), encoding='utf-8')
    (report / 'order.json').write_text(json.dumps([str(p.relative_to(root)) for p in files], ensure_ascii=False, indent=2), encoding='utf-8')
    uri = 'vscode://local-usbupdate.usbupdate-ats-bridge/run?' + urlencode({'request': str(request)})
    print(f'正在调用 ATS 执行页面，共 {len(files)} 个冒烟文件。请保持 ATS 工程在 VS Code 中打开。', flush=True)
    os.startfile(uri)
    event('ATS_SUBMITTED', count=len(files), report=str(report))
    start_deadline = time.monotonic() + 120
    log_path = report / 'ats-report' / 'run.log'
    result_path = report / 'ats-result.json'
    offset = 0
    decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
    last_progress = 0
    try:
        while True:
            if log_path.is_file():
                with log_path.open('rb') as stream:
                    stream.seek(offset)
                    data = stream.read()
                    offset = stream.tell()
                if data:
                    print(decoder.decode(data), end='', flush=True)
            if result_path.is_file():
                response = json.loads(result_path.read_text(encoding='utf-8'))
                result = response.get('result') or {}
                event('ATS_COMPLETE', response=response, report=str(report))
                if (response.get('status') != 'complete' or not result.get('total') or
                        result.get('passed') != result.get('total') or
                        any(result.get(key) for key in ('failed', 'skipped', 'blocked', 'errorCount'))):
                    if response.get('status') == 'complete' and not result.get('aborted'):
                        raise SmokeResultFailure(response, report)
                    raise RuntimeError('ATS 未正常完成：' + json.dumps(response, ensure_ascii=False))
                print('\nATS 冒烟全部通过。', flush=True)
                return {'status': 'passed', 'response': response, 'report': str(report)}
            if not (report / 'ats-started.json').is_file() and time.monotonic() > start_deadline:
                raise RuntimeError('ATS 未接收任务，请确认连接扩展已安装、已打开 ATS 工程，并允许 VS Code 打开执行链接。')
            if time.monotonic() - last_progress > 15:
                print('\n[ATS] ' + ('执行中，详细进度见 ATS 页面。' if (report / 'ats-started.json').is_file() else '等待 ATS 接收任务…'), flush=True)
                last_progress = time.monotonic()
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n终端监看已中断；请在 ATS 执行页面点击停止，终止正在执行的用例。', flush=True)
        raise

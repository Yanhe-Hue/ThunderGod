"""Serial USB upgrade stress; stop at the first failed or cancelled round."""
import copy
import datetime as dt
import json
import itertools
from pathlib import Path
import time

from auto_update import AutomaticUpgrade
from usb_update import Upgrade, digest, require


class StressRound(AutomaticUpgrade):
    def __init__(self, cfg, reusable=None):
        super().__init__(cfg)
        self.reusable = reusable

    def local_package(self, root):
        if self.reusable is None:
            return super().local_package(root)
        entry = copy.deepcopy(self.reusable)
        target = root / 'USB_UPDATE' / 'Update.zip'
        require(target.is_file(), '复用安装包已不存在，停止压测')
        require(digest(target) == entry['sha256'], '复用安装包已改变，停止压测')
        entry['source'] = str(target)
        self.event('STRESS_PACKAGE_REUSED', target=str(target), sha256=entry['sha256'])
        return entry


def run_stress(cfg):
    controller = Upgrade(cfg)
    report = controller.logs / 'stress_summary.json'
    state = {'requested_rounds': None, 'mode': 'reuse', 'smoke': 'none',
             'started': dt.datetime.now().isoformat(), 'status': 'running', 'rounds': []}
    def save():
        temporary = report.with_suffix('.tmp')
        temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(report)
    save()
    controller.event('STRESS_STARTED', cycles='unlimited', mode='reuse', smoke='none', report=str(report))
    reusable = None
    frozen_date = dt.date.today().isoformat()
    try:
        for index in itertools.count(1):
            round_cfg = copy.deepcopy(cfg)
            round_cfg['_stress_round'] = index
            # Reusing a package across midnight must not change its expected date.
            round_cfg['_stress_expected_date'] = frozen_date
            round_cfg.pop('verify_expected_qnx', None)
            round_cfg.setdefault('smoke', {})['enabled'] = False
            runner = StressRound(round_cfg, reusable)
            record = {'round': index, 'status': 'running', 'logs': str(runner.logs),
                      'started': dt.datetime.now().isoformat()}
            state['rounds'].append(record)
            save()
            print(f'压测第 {index} 轮开始（持续运行，Ctrl+C 停止）；日志：{runner.logs}', flush=True)
            controller.event('STRESS_ROUND_STARTED', round=index, logs=str(runner.logs))
            started = time.monotonic()
            try:
                if not runner.run(local=True):
                    raise RuntimeError('用户取消安装包选择，压测已停止')
                reusable = copy.deepcopy(runner.entry)
                record.update(status='passed', seconds=round(time.monotonic() - started, 2),
                              sha256=runner.entry['sha256'])
                controller.event('STRESS_ROUND_PASSED', round=index)
            except BaseException as exc:
                record.update(status='cancelled' if isinstance(exc, KeyboardInterrupt) else 'failed',
                              reason=str(exc) or '用户中断', seconds=round(time.monotonic() - started, 2))
                state['status'] = 'cancelled' if isinstance(exc, KeyboardInterrupt) else 'stopped'
                state['finished'] = dt.datetime.now().isoformat()
                save()
                controller.event('STRESS_STOPPED', round=index, reason=record['reason'], report=str(report))
                raise
            save()
    except KeyboardInterrupt:
        state.update(status='cancelled', finished=dt.datetime.now().isoformat())
        save()
        print(f'压测已手动停止；汇总：{report}', flush=True)
        raise

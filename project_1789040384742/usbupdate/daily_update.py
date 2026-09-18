"""One successful full upgrade workflow per build date, then wait for midnight."""
import copy
import datetime as dt
import json
from pathlib import Path
import time

from auto_update import AutomaticUpgrade
from usb_update import require


def now():
    return dt.datetime.now()


def wait_next_day(completed_date, event):
    deadline = dt.datetime.combine(completed_date + dt.timedelta(days=1), dt.time())
    event('DAILY_WAITING_MIDNIGHT', until=deadline.isoformat())
    print(f'本日期流程已完成，等待 {deadline} 再检测云盘；Ctrl+C 停止。', flush=True)
    while now() < deadline:
        time.sleep(min(60, max(0.1, (deadline - now()).total_seconds())))


def run_daily(cfg, event, once=False):
    state_path = Path(cfg.get('daily_state_file', 'daily_state.json'))
    scope = json.dumps([cfg.get('usb_serial'), cfg['variant'], cfg['cloud']['url'], cfg['cloud']['path']], ensure_ascii=False)
    state = json.loads(state_path.read_text(encoding='utf-8-sig')) if state_path.exists() else {}
    require(isinstance(state, dict), '每日流程记录格式错误，请检查 daily_state.json')
    while True:
        previous = state.get(scope, {}).get('completed_build_date')
        if previous:
            completed_date = dt.date.fromisoformat(previous)
            if now().date() <= completed_date:
                if once:
                    event('CI_ALREADY_COMPLETE', build_date=previous)
                    print('该日期已完成，CI 不重复刷写。', flush=True)
                    return
                wait_next_day(completed_date, event)
        round_cfg = copy.deepcopy(cfg)
        round_cfg['_wait_today_cloud'] = True
        round_cfg['today_only'] = True
        if once:
            require(round_cfg.get('smoke', {}).get('enabled') is True, 'CI 完整流程要求 smoke.enabled=true，不能跳过冒烟')
            round_cfg['_cloud_wait_timeout_seconds'] = round_cfg.get('cloud', {}).get('ci_wait_timeout_seconds', 7200)
            round_cfg['_ci_target_date'] = now().date().isoformat()
        runner = AutomaticUpgrade(round_cfg)
        event('DAILY_STARTED', variant=cfg['variant'], logs=str(runner.logs))
        require(runner.run(local=False), '每日升级流程未完成')
        build_date = dt.date.fromisoformat(runner.entry['build_date']).isoformat()
        # Only persist after upgrade, version check and configured smoke all succeed.
        state[scope] = {'completed_build_date': build_date, 'finished': now().isoformat(),
                        'logs': str(runner.logs), 'sha256': runner.entry['sha256']}
        state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = state_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(state_path)
        event('DAILY_COMPLETE', build_date=build_date, logs=str(runner.logs))
        if once:
            return

"""Best-effort read-only failure evidence; never hide the original error."""
from pathlib import Path
import subprocess
import traceback


def capture(runner, exc):
    if not isinstance(getattr(runner, 'adb', None), str) or not isinstance(getattr(runner, 'serial', None), str) or not getattr(runner, 'logs', None):
        return
    if getattr(runner, '_smoke_started', False) or isinstance(exc, KeyboardInterrupt):
        return
    if getattr(exc, '_usb_evidence_saved', False):
        return
    try:
        folder = Path(runner.logs) / 'error'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'exception.txt').write_text(''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)), encoding='utf-8')
        failures = []
        for name, args in [('device.png', ['exec-out', 'screencap', '-p']),
                           ('logcat.txt', ['logcat', '-d', '-t', '2000']),
                           ('devices.txt', ['devices', '-l'])]:
            try:
                command = [runner.adb] + ([] if name == 'devices.txt' else ['-s', runner.serial]) + args
                result = subprocess.run(command, capture_output=True, timeout=15)
                if result.returncode or not result.stdout:
                    raise RuntimeError(result.stderr.decode('utf-8', errors='replace') or '未返回证据')
                if name.endswith('.png') and not result.stdout.startswith(b'\x89PNG\r\n\x1a\n'):
                    raise RuntimeError('截屏返回的不是 PNG')
                (folder / name).write_bytes(result.stdout)
            except Exception as error:
                failures.append(name + ': ' + str(error))
        (folder / 'capture_status.txt').write_text('\n'.join(failures) or '取证完成', encoding='utf-8')
        exc._usb_evidence_saved = True
        print('异常证据：' + str(folder.resolve()), flush=True)
    except Exception as error:
        print('异常取证未完成：' + str(error), flush=True)

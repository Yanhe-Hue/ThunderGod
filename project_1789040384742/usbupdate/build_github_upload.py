"""Create a clean repository-root upload bundle from an explicit allowlist."""
import datetime as dt
import json
from pathlib import Path
import shutil
import zipfile


ROOT = Path(__file__).resolve().parent
FILES = [
    'configure_stress.ps1', 'configure_stress.py',
    'deploy_all.ps1',
    'smoke_picker.py',
    'python_runtime.ps1', 'deploy.ps1', 'run_stress.ps1', 'check_environment.ps1',
    'check_environment.py', 'requirements-support.txt', '新电脑部署指南.md',
    '.gitignore', '.github/workflows/usb-upgrade.yml',
    'ats_client.py', 'auto_update.py', 'build_ats_bridge.py', 'ci_run.ps1',
    'cloud_download.py', 'config.example.json', 'daily_update.py', 'error_evidence.py',
    'format_usb.ps1', 'hardware.py', 'package_metadata.py', 'run.ps1', 'setup.ps1',
    'smoke_runner.py', 'stress_update.py', 'usb_stress.py', 'usb_update.py',
    'version_records.py', 'volume.py',
    'smoke_cases/README.md', 'ats_bridge/package.json', 'ats_bridge/extension.js',
    'ats_bridge/usbupdate-ats-bridge-1.0.2.vsix',
    '功能与使用说明.md', '环境依赖与配置说明.md', '独立压测使用说明.md',
    'GitHub_Actions部署与原理.md', 'build_github_upload.py',
]

README = '''# USB 升级与 ATS 冒烟自动化

Windows 台架工具，支持云盘每日升级、ATS 冒烟和独立 U 盘压测。

## 提交 GitHub

将本目录内的内容作为仓库根目录提交，保持 `.github/workflows/usb-upgrade.yml` 位于仓库根目录下。不要再套一层 `usbupdate` 或 `repository`，也不要只上传压缩包。

本包不包含真实配置、云盘登录会话、安装包、日志、设备知识库或旧扩展安装包。config.example.json 是必需配置模板；独立压测模板为 usb_stress_config.example.json。

## 部署

1. 将脚本部署到连接车机的 Windows ATS 工程 usbupdate 目录；GitHub 工作流直接调用台架已部署代码，不自动 checkout/覆盖台架工程。
2. 运行 setup.ps1 创建缺失的 config.json，按实际设备修改配置。运行 run.ps1 check 选择 GAS/no_gas 并登录云盘。
3. 需要独立压测时，将 usb_stress_config.example.json 复制为 usb_stress_config.json，填写设备、模式和本地安装包信息。
4. 使用 CI 时，注册带 renault-usb 标签的 Windows 自托管 Runner，在仓库变量中设置 USBUPDATE_DIR 和 AUTOCAR_PYTHON。保持 ATS 工程在同一交互桌面打开。
5. 首次从 GitHub Actions 手动运行验证；默认每天北京时间 00:07 调度。该任务会操作真实硬件并格式化配置 U 盘。

## 入口

| 命令 | 用途 |
|---|---|
| .\\run.ps1 check | 选择分类、保存配置、云盘登录 |
| .\\run.ps1 ci-once | 等待当天包，执行完整流程一次后退出 |
| .\\run.ps1 auto | 每天重复完整流程 |
| .\\run.ps1 local | 本地单次升级及冒烟 |
| .\\run.ps1 smoke | 仅 ATS 冒烟 |
| Python 执行 usb_stress.py | 独立云盘/单包/A-B 交替压测 |

详细说明：[GitHub 部署与原理](GitHub_Actions部署与原理.md)、[环境依赖](环境依赖与配置说明.md)、[使用说明](功能与使用说明.md)、[独立压测](独立压测使用说明.md)。

工作流必须提交到默认分支，定时任务才会生效。仅提交文件不会自动注册 Runner 或安装台架依赖。此包未完成 GitHub 实机验收。
'''


def build():
    output = ROOT / 'github_upload' / dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    repo = output / 'repository'
    repo.mkdir(parents=True)
    files = FILES + [p.relative_to(ROOT).as_posix() for p in (ROOT / 'tests').glob('test_*.py')]
    for name in files:
        source = ROOT / name
        target = repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (repo / 'README.md').write_text(README, encoding='utf-8')
    config = json.loads((ROOT / 'config.example.json').read_text(encoding='utf-8-sig'))
    config['smoke'] = {'enabled': True, 'project_root': '', 'case_directory': 'tests_scripts', 'select_before_stress': True}
    config['stress'] = {'mode': 'usb_pair_smoke', 'cache_dir': 'stress_cache', 'packages': [], 'cloud_expected_date': ''}
    (repo / 'usb_stress_config.example.json').write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    archive_path = output / 'usbupdate-github.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(repo.rglob('*')):
            if file.is_file():
                archive.write(file, file.relative_to(repo).as_posix())
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        assert '.github/workflows/usb-upgrade.yml' in names
        forbidden = {'config.json', 'usb_stress_config.json', 'packages.json', 'daily_state.json', 'prepared_package.json'}
        assert not any(Path(n).name in forbidden or n.startswith(('.auth/', 'logs/', 'knowledge/', 'downloads/')) for n in names)
        assert archive.testzip() is None
    print(f'UPLOAD_DIRECTORY={repo}\nZIP={archive_path}\nFILES={len(names)}')


if __name__ == '__main__':
    build()

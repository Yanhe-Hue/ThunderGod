"""
根级 conftest v8.0 (AT 统一 API + Allure)
文件: tests_scripts/conftest.py

放入 tests_scripts/conftest.py，为所有模块提供共享 fixtures。
若 tests_scripts/conftest.py 不存在，Agent Run 自动从此模板创建。

Fixtures:
    - config: 设备配置（session）
    - allure_environment: 自动写入环境信息 + 失败分类规则到 allure-results（session, autouse）

Hooks:
    - pytest_runtest_makereport: 失败时自动截图

Helper Functions (供模块 conftest 导入调用):
    - go_home_car(device): 回到桌面（兼容 AT / U2Manager）
    - go_home_phone(device): 手机回到桌面（兼容 AT / U2Manager）

授权由 guard.py 底层统一管理（网络验证：硬件指纹 + Cursor 账号 → 服务器）。
若未找到有效密钥则抛出 AuthenticationError 终止程序。
"""

import importlib.util
import json
import logging
import os
import sys
from pathlib import Path

import allure
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


def _phone_device_id(config, slot):
    """读取手机设备 ID；新变量优先，旧变量仅作为兼容回退。"""
    keys = {
        1: ("PHONE_DEVICE1_ID", "PHONE_DEVICE_ID"),
        2: ("PHONE_DEVICE2_ID", "PHONE2_DEVICE_ID"),
    }
    try:
        config_keys = keys[slot]
    except KeyError as exc:
        raise ValueError(f"unsupported phone slot: {slot}") from exc
    for config_key in config_keys:
        device_id = str(config.get(config_key) or "").strip()
        if device_id:
            return device_id
    return None


def _load_optional_session_extensions():
    """加载 tests_scripts/cli_session_*.py 的可选 pytest 集成。

    不 import CAN CLI Session 守护入口：该模块走 python -m，产线 .pyd 包
    即使保留源码也不应在 pytest 收集期拉起 CAN Session 栈。
    """
    tests_scripts = PROJECT_ROOT / "tests_scripts"
    extension_files = (
        sorted(tests_scripts.glob("cli_session_*.py"))
        if tests_scripts.is_dir()
        else []
    )
    for extension_file in extension_files:
        module_name = f"tests_scripts.{extension_file.stem}"
        module = sys.modules.get(module_name)
        if module is None:
            spec = importlib.util.spec_from_file_location(module_name, extension_file)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"无法加载 CLI Session Hook 文件: {extension_file}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)
            except Exception as exc:
                raise RuntimeError(
                    f"CLI Session Hook 文件加载失败: {extension_file}: {exc}"
                ) from exc

        install_pytest = getattr(module, "install_pytest", None)
        if callable(install_pytest):
            install_pytest()
            logger.info("已启用 Session 扩展的 pytest 集成: %s", extension_file)


_load_optional_session_extensions()


def _live_report_dir():
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                v, _ = winreg.QueryValueEx(k, "AUTOCAR_REPORT_DIR")
                if v:
                    return str(v)
        except (FileNotFoundError, OSError):
            pass
    return os.environ.get("AUTOCAR_REPORT_DIR")


_report_base = _live_report_dir() or str(PROJECT_ROOT / "temp")
ALLURE_RESULTS_DIR = Path(_report_base) / "allure-results"


def pytest_configure(config):
    """当 CLI 未显式指定 --alluredir 时，根据 AUTOCAR_REPORT_DIR 动态设置

    allure-pytest 注册 --alluredir 时 dest='allure_report_dir'。
    rootdir conftest 的 pytest_configure 在 allure-pytest 插件之前执行，
    因此此处设置 allure_report_dir 后，allure-pytest 会自动创建 listener。
    """
    report_dir = getattr(config.option, "allure_report_dir", None)
    if not report_dir:
        ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        config.option.allure_report_dir = str(ALLURE_RESULTS_DIR)


ALLURE_CATEGORIES = [
    {
        "name": "产品缺陷",
        "description": "测试用例因被测应用异常而失败",
        "matchedStatuses": ["failed"],
    },
    {
        "name": "测试缺陷",
        "description": "测试脚本自身错误（定位器过期、超时、环境问题等）",
        "matchedStatuses": ["broken"],
    },
    {
        "name": "已知问题",
        "description": "已标记为已知问题的失败用例",
        "matchedStatuses": ["failed"],
        "traceRegex": ".*known_issue.*",
    },
]


@pytest.fixture(scope="session")
def config():
    """加载设备配置（从 page_objects/configs/dev.py）"""
    config_path = PROJECT_ROOT / "page_objects" / "configs" / "dev.py"
    cfg = {}
    if config_path.exists():
        exec(config_path.read_text(encoding="utf-8"), cfg)
    return cfg


@pytest.fixture(scope="session", autouse=True)
def allure_environment(config):
    """写入 Allure 环境信息 + 失败分类规则；session 结束后去重历史结果"""
    yield
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    env_path = ALLURE_RESULTS_DIR / "environment.properties"
    lines = [
        f"Device.ID={config.get('DEVICE_ID', 'N/A')}",
        f"Operator.Mode={config.get('OPERATOR_MODE', 'u2')}",
        f"Project.Root={PROJECT_ROOT}",
    ]
    if config.get("CAN_INTERFACE"):
        lines.append(f"CAN.Interface={config.get('CAN_INTERFACE')}")
        lines.append(f"CAN.Channel={config.get('CAN_CHANNEL', '')}")
    phone_id = _phone_device_id(config, 1)
    phone2_id = _phone_device_id(config, 2)
    if phone_id:
        lines.append(f"Phone.ID={phone_id}")
    if phone2_id:
        lines.append(f"Phone2.ID={phone2_id}")
    env_path.write_text("\n".join(lines), encoding="utf-8")

    categories_path = ALLURE_RESULTS_DIR / "categories.json"
    categories_path.write_text(
        json.dumps(ALLURE_CATEGORIES, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图。"""
    outcome = yield
    report = outcome.get_result()

    # 1. 失败截图（Allure）
    if report.when == "call" and report.failed:
        screenshot_dir = ALLURE_RESULTS_DIR / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        safe_name = item.nodeid.replace("::", "_").replace("/", "_")
        for key, label in [
            ("car", "失败截图"),
            ("phone", "手机截图"),
            ("phone2", "第二手机截图"),
        ]:
            try:
                dev = item.funcargs.get(key)
            except (KeyError, AttributeError):
                dev = None
            if dev:
                try:
                    img_path = screenshot_dir / f"{safe_name}_{key}.png"
                    dev.screenshot(path=str(img_path))
                    allure.attach.file(
                        str(img_path),
                        name=label,
                        attachment_type=allure.attachment_type.PNG,
                    )
                except Exception as e:
                    logger.warning(f"Allure {label}采集异常: {e}")

def go_home_car(device):
    """关闭瞬态覆层并回到桌面（通用版，兼容 AT / U2Manager）

    issue #56: 用 adb keyevent HOME 代替 u2 press('home')，
               避免多屏显示器焦点丢失。

    Args:
        device: AT 实例或 U2Manager 实例均可
    """
    import subprocess
    import time

    device_id = ""
    if hasattr(device, "u2"):
        device_id = device.u2.device_id or ""
    elif hasattr(device, "device_id"):
        device_id = device.device_id or ""

    prefix = f"adb -s {device_id}" if device_id else "adb"
    try:
        subprocess.run(
            f"{prefix} shell input keyevent BACK",
            shell=True,
            timeout=5,
            capture_output=True,
        )
        time.sleep(0.2)
    except Exception as e:
        logger.warning(f"go_home_car dismiss overlay failed: {e}")
    try:
        subprocess.run(
            f"{prefix} shell input keyevent HOME",
            shell=True,
            timeout=5,
            capture_output=True,
        )
        time.sleep(2)
    except Exception as e:
        logger.warning(f"go_home_car failed: {e}")


def go_home_phone(device):
    """手机回到桌面（兼容 AT / U2Manager）

    Args:
        device: AT 实例或 U2Manager 实例均可
    """
    try:
        target = getattr(device, "u2", device)
        target.press("home")
    except Exception as e:
        logger.warning(f"go_home_phone failed: {e}")

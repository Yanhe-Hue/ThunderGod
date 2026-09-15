# -*- coding: utf-8 -*-
"""
多设备 conftest 模板 v8.1（POM 环境层 — fixture + reset）
文件: src/autocar/agent_cli/templates/conftest_template.py

本文件职责: 提供 at/car/硬件 fixture 与 reset_environment；不写用例步骤与断言。

AT 是认证入口 + 设备工厂，connect_device 返回独立 U2Manager 对象。
前提: tests_scripts/conftest.py 提供 config, go_home_car/go_home_phone, Allure 全局 hook。
授权由 AuthGuard 底层统一管理：默认网络验证，成功后写入 active_key 3 天缓存；仅显式 AUTOCAR_SKIP_AUTH=1 才跳过。
本模板仅包含模块特有的 fixture，放入 tests_scripts/媒体Page/conftest.py。

Fixtures:
    - at: AT 工厂实例（session）— OCR/TTS/Audio、project_path/report_path 等
    - car: U2Manager 设备对象（session）— UI 操作
    - configured_phone: PHONE_DEVICE1_ID 非空时尽力连接（兼容 PHONE_DEVICE_ID），用于统一 Home 清理
    - configured_phone2: PHONE_DEVICE2_ID 非空时尽力连接（兼容 PHONE2_DEVICE_ID），用于统一 Home 清理
    - reset_environment: 环境还原（function, autouse）

硬件 Fixture（按需启用，对应 page_objects/configs/dev.py）:
    car         车机 U2Manager        ← DEVICE_ID
    phone       手机（互联测试）        ← PHONE_DEVICE1_ID（兼容 PHONE_DEVICE_ID）
    phone2      第二手机（互联测试）    ← PHONE_DEVICE2_ID（兼容 PHONE2_DEVICE_ID）
    ps          程控电源 PowerSupply   ← POWER_RESOURCE
    can / can2  CAN 总线（双路）        ← CAN_INTERFACE / CAN2_INTERFACE + *_CHANNEL/*_FD/*_BITRATE/DBC_PATH
    uds / uds2  UDS 诊断（绑 can / can2）← UDS_* / UDS2_*
    ic          仪表 ClusterManager    ← CLUSTER_TYPE 选择内部来源；camera 时内部读取 CAMERA_*，调用仍为 ic.*
    cam         摄像头 CameraManager   ← CAMERA_NAME / CAMERA_TYPE / CAMERA_INDEX / CAMERA_RESOLUTION / CAMERA_FPS / CAMERA_CROP_REGION
    someip      以太网/SOME/IP         ← SOMEIP_BASE_URL / SIMULATOR_BASE_URL 或 ARXML_PATH / ETH_LOCAL_IP / SOMEIP_*
    （USB 切换器是 at 方法：at.usb_switch(config["USB_SWITCH_PORT"], usb_port=1)，无需 fixture）
    👉 CodeGen 仅启用当前用例需要的硬件 fixture，其余保持注释；后期持续扩充。

Allure: 失败截图由根 conftest pytest_runtest_makereport hook 统一处理。
"""

import logging
import subprocess
import sys

import pytest
from tests_scripts.conftest import go_home_car, go_home_phone

from autocar import AT

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


def _stop_can_cli_session():
    """关闭 AutoCar CLI CAN session，释放跨命令遗留的 CAN 总线占用。"""
    try:
        subprocess.run(
            [sys.executable, "-m", "autocar.cli", "can", "session", "stop"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
    except Exception as e:
        logger.warning(f"stop CAN CLI session failed: {e}")


def _stop_someip_cli_session():
    """关闭 AutoCar CLI SOME/IP session，释放跨命令遗留的连接资源。"""
    try:
        subprocess.run(
            [sys.executable, "-m", "autocar.cli", "someip", "close"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
    except Exception as e:
        logger.warning(f"stop SOME/IP CLI session failed: {e}")


@pytest.fixture(scope="module")
def at():
    """AT 工厂实例（module 级别）— 提供 OCR/TTS/Audio 等软件方法"""
    instance = AT()
    yield instance
    instance.disconnect()


@pytest.fixture(scope="module")
def car(at, config):
    """车机驱动 ← DEVICE_ID + OPERATOR_MODE"""
    # Match Explore's car connection mode; phones resolve independently below.
    mode = str(config.get("OPERATOR_MODE") or "u2").strip() or "u2"
    car_mgr = at.connect_device(config["DEVICE_ID"], mode=mode)
    yield car_mgr
    car_mgr.disconnect()


@pytest.fixture(scope="module")
def configured_phone(config):
    """按主手机配置可选连接，供统一 Home 清理；失败不阻塞车机用例。"""
    dev_id = _phone_device_id(config, 1)
    if not dev_id:
        yield None
        return
    phone_at = None
    connection_error = None
    try:
        phone_at = AT()
        dev = phone_at.connect_device(dev_id)
    except (Exception, SystemExit) as e:
        connection_error = e
        logger.warning(f"configured phone connection failed: {e}")
    if connection_error is not None:
        if phone_at is not None:
            try:
                phone_at.disconnect()
            except (Exception, SystemExit) as disconnect_error:
                logger.warning(f"configured phone cleanup failed: {disconnect_error}")
        yield None
        return
    try:
        yield dev
    finally:
        try:
            phone_at.disconnect()
        except (Exception, SystemExit) as e:
            logger.warning(f"configured phone disconnect failed: {e}")


@pytest.fixture(scope="module")
def configured_phone2(config):
    """按第二手机配置可选连接；失败不阻塞其他设备用例。"""
    dev_id = _phone_device_id(config, 2)
    if not dev_id:
        yield None
        return
    phone_at = None
    dev = None
    try:
        phone_at = AT()
        dev = phone_at.connect_device(dev_id)
    except (Exception, SystemExit) as e:
        logger.warning(f"configured phone2 connection failed: {e}")
        if phone_at is not None:
            try:
                phone_at.disconnect()
            except (Exception, SystemExit) as disconnect_error:
                logger.warning(f"configured phone2 cleanup failed: {disconnect_error}")
    if dev is None:
        yield None
        return
    try:
        yield dev
    finally:
        try:
            phone_at.disconnect()
        except (Exception, SystemExit) as e:
            logger.warning(f"configured phone2 disconnect failed: {e}")


# ==================== 硬件 Fixture（按需启用，取消注释） ====================
# 仅放开当前用例需要的硬件；config 取值见 page_objects/configs/dev.py。
# 约定: ① 当前用例声明的必需硬件缺配置或 open 失败 → pytest.fail，如实判定环境失败
#       ② teardown 只释放连接；Power 不关闭输出，避免下条用例/重跑时设备掉电
#       ③ 硬件 fixture 为 module 级；用例级状态恢复请写在 test 自身 teardown

# @pytest.fixture(scope="module")
# def phone(config, configured_phone):
#     """手机设备（蓝牙/WiFi 互联测试）← PHONE_DEVICE1_ID"""
#     dev_id = _phone_device_id(config, 1)
#     if not dev_id:
#         pytest.fail("PHONE_DEVICE1_ID 未配置")
#     if configured_phone is None:
#         pytest.fail("手机连接失败，详见 configured phone connection 日志")
#     return configured_phone

# @pytest.fixture(scope="module")
# def phone2(config, configured_phone2):
#     """第二手机设备（互联测试）← PHONE_DEVICE2_ID"""
#     dev_id = _phone_device_id(config, 2)
#     if not dev_id:
#         pytest.fail("PHONE_DEVICE2_ID 未配置")
#     if configured_phone2 is None:
#         pytest.fail("第二手机连接失败，详见 configured phone2 connection 日志")
#     return configured_phone2

# @pytest.fixture(scope="module")
# def ps(at, config):
#     """程控电源 ← POWER_RESOURCE"""
#     resource = config.get("POWER_RESOURCE")
#     if not resource:
#         pytest.fail("POWER_RESOURCE 未配置")
#     try:
#         supply = at.power_open(resource)
#     except Exception as e:
#         pytest.fail(f"程控电源连接失败: {e}")
#     yield supply
#     supply.ps_close()

# @pytest.fixture(scope="module")
# def can(at, config):
#     """CAN 总线第一路 ← CAN_INTERFACE / CAN_CHANNEL / CAN_FD / *_BITRATE / DBC_PATH"""
#     if not config.get("CAN_INTERFACE"):
#         pytest.fail("CAN_INTERFACE 未配置")
#     _stop_can_cli_session()
#     try:
#         bus = at.can_open(
#             config["CAN_INTERFACE"],
#             channel=config.get("CAN_CHANNEL", ""),
#             bitrate=config.get("CAN_ARB_BITRATE", 500000),
#             fd=config.get("CAN_FD", False),
#             data_bitrate=(config.get("CAN_BITRATE") or 5000000) if config.get("CAN_FD") else 0,
#             dbc_path=config.get("DBC_PATH"),
#             mac_dll_path=config.get("CAN_MAC_DLL_PATH") or None,
#             mac_mact_path=config.get("CAN_MAC_MACT_PATH") or None,
#         )
#     except Exception as e:
#         pytest.fail(f"CAN 总线连接失败: {e}")
#     yield bus
#     try:
#         bus.can_close()
#     finally:
#         _stop_can_cli_session()

# @pytest.fixture(scope="module")
# def uds(can, config):
#     """UDS 诊断会话 ← UDS_RXID / UDS_TXID / UDS_FUNC_*（复用 can fixture）"""
#     rxid = config.get("UDS_RXID")
#     txid = config.get("UDS_TXID")
#     if rxid in (None, "") or txid in (None, ""):
#         pytest.skip("UDS_RXID/UDS_TXID 未配置；非 UDS 用例无需填写诊断 ID")
#     try:
#         client = can.uds_open(
#             rxid=rxid,
#             txid=txid,
#             func_rxid=config.get("UDS_FUNC_RXID"),
#             func_txid=config.get("UDS_FUNC_TXID"),
#         )
#     except Exception as e:
#         pytest.fail(f"UDS 会话建立失败: {e}")
#     yield client
#     can.uds_close()

# @pytest.fixture(scope="module")
# def can2(at, config):
#     """CAN 总线第二路 ← CAN2_INTERFACE / CAN2_CHANNEL / ... / DBC2_PATH"""
#     if not config.get("CAN2_INTERFACE"):
#         pytest.fail("CAN2_INTERFACE 未配置")
#     _stop_can_cli_session()
#     try:
#         bus = at.can_open(
#             config["CAN2_INTERFACE"],
#             channel=config.get("CAN2_CHANNEL", ""),
#             bitrate=config.get("CAN2_ARB_BITRATE", 500000),
#             fd=config.get("CAN2_FD", False),
#             data_bitrate=(config.get("CAN2_BITRATE") or 5000000) if config.get("CAN2_FD") else 0,
#             dbc_path=config.get("DBC2_PATH"),
#             mac_dll_path=config.get("CAN2_MAC_DLL_PATH") or None,
#             mac_mact_path=config.get("CAN2_MAC_MACT_PATH") or None,
#         )
#     except Exception as e:
#         pytest.fail(f"CAN2 总线连接失败: {e}")
#     yield bus
#     try:
#         bus.can_close()
#     finally:
#         _stop_can_cli_session()

# @pytest.fixture(scope="module")
# def uds2(can2, config):
#     """UDS 诊断会话（第二路）← UDS2_RXID / UDS2_TXID / UDS2_FUNC_*（复用 can2 fixture）"""
#     rxid = config.get("UDS2_RXID")
#     txid = config.get("UDS2_TXID")
#     if rxid in (None, "") or txid in (None, ""):
#         pytest.skip("UDS2_RXID/UDS2_TXID 未配置；非 UDS 用例无需填写诊断 ID")
#     try:
#         client = can2.uds_open(
#             rxid=rxid,
#             txid=txid,
#             func_rxid=config.get("UDS2_FUNC_RXID"),
#             func_txid=config.get("UDS2_FUNC_TXID"),
#         )
#     except Exception as e:
#         pytest.fail(f"UDS2 会话建立失败: {e}")
#     yield client
#     can2.uds_close()

# @pytest.fixture(scope="module")
# def ic(at, config):
#     """仪表 ClusterManager；cluster_open 按 CLUSTER_TYPE 在内部选择来源，测试始终调用 ic.*。"""
#     try:
#         cluster = at.cluster_open()
#     except Exception as e:
#         pytest.fail(f"仪表连接失败: {e}")
#     yield cluster
#     try:
#         cluster.close()
#     except Exception:
#         pass

# @pytest.fixture(scope="module")
# def cam(at, config):
#     """摄像头 CameraManager ← CAMERA_NAME / CAMERA_TYPE / CAMERA_INDEX / CAMERA_FPS / CAMERA_CROP_REGION"""
#     if not (config.get("CAMERA_NAME") or config.get("CAMERA_TYPE")):
#         pytest.fail("CAMERA_NAME / CAMERA_TYPE 未配置")
#     try:
#         camera = at.camera_open(
#             camera_name=config.get("CAMERA_NAME"),
#             camera_type=config.get("CAMERA_TYPE"),
#             camera_index=config.get("CAMERA_INDEX", 1),
#             resolution=config.get("CAMERA_RESOLUTION"),
#             target_fps=config.get("CAMERA_FPS", 10),
#             crop_region=config.get("CAMERA_CROP_REGION"),
#         )
#     except Exception as e:
#         pytest.fail(f"摄像头连接失败: {e}")
#     yield camera
#     camera.close()

# @pytest.fixture(scope="module")
# def someip(at, config):
#     """以太网 / SOME/IP ← SOMEIP_BASE_URL / SIMULATOR_BASE_URL 或 ARXML_PATH / ETH_LOCAL_IP"""
#     base_url = config.get("SOMEIP_BASE_URL") or config.get("SIMULATOR_BASE_URL")
#     _stop_someip_cli_session()
#     try:
#         if base_url:
#             mgr = at.someip_open(base_url=base_url)
#         else:
#             if not (config.get("ARXML_PATH") and config.get("ETH_LOCAL_IP")):
#                 pytest.fail("SOMEIP_BASE_URL / SIMULATOR_BASE_URL 或 ARXML_PATH / ETH_LOCAL_IP 未配置")
#             mgr = at.someip_open(
#                 config["ARXML_PATH"],
#                 config["ETH_LOCAL_IP"],
#                 multicast_ip=config.get("SOMEIP_MULTICAST_IP", "239.48.52.1"),
#                 sd_port=config.get("SOMEIP_SD_PORT", 30490),
#                 ttl=config.get("SOMEIP_TTL", 30),
#             )
#     except Exception as e:
#         pytest.fail(f"SOME/IP 连接失败: {e}")
#     yield mgr
#     try:
#         mgr.disconnect()
#     finally:
#         _stop_someip_cli_session()


# 模块主应用包名 — 仅使用 case/profile 明确提供的值；空字符串表示不停止应用
MODULE_PACKAGE = ""


def _stop_module_app(car):
    """测试前按显式包名清理应用；未知包名时安全跳过。"""
    if not MODULE_PACKAGE:
        return
    serial = str(getattr(car, "device_id", "") or "").strip()
    mode = getattr(car, "mode", None)
    mode = getattr(mode, "value", mode)
    if (
        str(mode or "").strip().lower() == "robot"
        or (serial.isdigit() and len(serial) == 3)
        or serial.lower().startswith("robot-")
    ):
        return
    car.stop_app(MODULE_PACKAGE)
    car.sleep(0.5)


def _go_home_devices(car, phone=None, phone2=None):
    """车机和两台已配置手机分别回到 Home；任一端失败不影响其他设备。"""
    try:
        go_home_car(car)
    except (Exception, SystemExit) as e:
        logger.warning(f"go_home_car failed: {e}")
    if phone is not None:
        try:
            go_home_phone(phone)
        except (Exception, SystemExit) as e:
            logger.warning(f"go_home_phone failed: {e}")
    if phone2 is not None:
        try:
            go_home_phone(phone2)
        except (Exception, SystemExit) as e:
            logger.warning(f"go_home_phone2 failed: {e}")


@pytest.fixture(scope="function", autouse=True)
def reset_environment(car, configured_phone, configured_phone2):
    """每个测试前后让车机及两台已配置手机回桌面。

    前置清理: 有明确包名时停止模块 App，再让两端回桌面，隔离上个用例的页面状态。
    后置清理: 只让两端回桌面，避免停止应用打断异步保存/恢复；业务状态恢复写在 test 自身 teardown。
    """
    try:
        _stop_module_app(car)
    except Exception as e:
        logger.warning(f"pre-test stop_app failed: {e}")
    _go_home_devices(car, configured_phone, configured_phone2)
    yield
    _go_home_devices(car, configured_phone, configured_phone2)

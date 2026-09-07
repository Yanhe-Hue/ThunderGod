# ==================== 设备配置 ====================
# 受保护文件 — 仅由用户手动维护
# 此文件被 config_loader / conftest 自动加载

# --- 车机 ---
DEVICE_ID = ""
# 接口类型: tosun / pcan / vector / zlgcan
# 接口类型: tosun / pcan / vector / zlgcan；留空则不启用

# --- LIN 总线 ---
# 接口类型: plin / vectorlin；留空则不启用
# "qnx" / "linux" / "camera"；camera 模式读取下方 CAMERA_* 参数
# 提供 CAMERA_NAME 时自动识别类型；为空时使用 CAMERA_TYPE
# --- 蓝牙配对设备 ---
BT_DEVICE_NAME = ""

# --- WiFi 测试环境 ---
WIFI_SSID = ""
WIFI_PASSWORD = ""

# --- 以太网 / SOME/IP 基础配置（车载以太网订阅测试）---

# --- 操作模式 ---
OPERATOR_MODE = "u2"
# --- AutoCar 0817+ 默认字段（插件更新自动补齐，请按需修改）---
PERF_DB = None
LOGCAT_DIR = None

# --- CAN 总线（第一路）---
CAN_INTERFACE = ""
CAN_CHANNEL = ""
CAN_FD = False
CAN_ARB_BITRATE = ""
CAN_BITRATE = ""
DBC_PATH = r""
CAN_MAC_DLL_PATH = r""
CAN_MAC_MACT_PATH = r""
UDS_TXID = ""    # 诊断请求 ID（发送）
UDS_RXID = ""    # ECU 应答 ID（接收）
UDS_FUNC_TXID = ""   # 功能寻址请求 ID（广播，ISO 标准值）
UDS_FUNC_RXID = ""   # 功能寻址响应 ID（= ECU 物理应答 ID）
UDS_SEEDKEY_DLL = r""

# --- CAN 总线（第二路，可选）---
CAN2_INTERFACE = ""
CAN2_CHANNEL = ""
CAN2_FD = False
CAN2_ARB_BITRATE = ""
CAN2_BITRATE = ""
DBC2_PATH = r""
CAN2_MAC_DLL_PATH = r""
CAN2_MAC_MACT_PATH = r""
UDS2_TXID = ""    # 诊断请求 ID（发送）
UDS2_RXID = ""    # ECU 应答 ID（接收）
UDS2_FUNC_TXID = ""   # 功能寻址请求 ID（广播，ISO 标准值）
UDS2_FUNC_RXID = ""   # 功能寻址响应 ID（= ECU 物理应答 ID）
UDS2_SEEDKEY_DLL = r""

# --- LIN 总线 ---
LIN_INTERFACE = ""
LIN_CHANNEL = ""
LIN_BITRATE = 19200

# --- SOME/IP ---
SOMEIP_BASE_URL = ""
ETH_LOCAL_IP = ""
ARXML_PATH = r""
SOMEIP_MULTICAST_IP = "239.48.52.1"
SOMEIP_SD_PORT = 30490
SOMEIP_DATA_PORT = 30501
SOMEIP_TTL = 30

# --- 仪表 (Cluster) ---
CLUSTER_TYPE = ""
CLUSTER_IP = ""
CLUSTER_USER = ""
CLUSTER_PASSWORD = ""
CLUSTER_LINUX_PORT = ""
CLUSTER_LINUX_REMOTE_PORT = ""

# --- 摄像头 (Camera) ---
CAMERA_NAME = None
CAMERA_TYPE = ""
CAMERA_INDEX = ""
CAMERA_RESOLUTION = None
CAMERA_FPS = ""
CAMERA_CROP_REGION = None

# --- 程控电源 (VISA) ---
POWER_RESOURCE = ""

# --- 故障注入继电器板（串口）---
FAULT_INJECTION_PORT = ""

# --- USB 切换器（串口硬件开关）---
USB_SWITCH_PORT = ""
USB_SWITCH_BAUDRATE = ""

# --- 手机（蓝牙/WiFi 互联测试用，未连接时留空）---
# 手机类型: Android / iOS / HarmonyOS
PHONE_DEVICE1_ID = ""
PHONE_DEVICE1_TYPE = "Android"
PHONE_DEVICE2_ID = ""
PHONE_DEVICE2_TYPE = "Android"
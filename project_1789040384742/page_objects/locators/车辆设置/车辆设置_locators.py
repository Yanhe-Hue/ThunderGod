# -*- coding: utf-8 -*-
"""
定位器模板 v8.1（POM 定位器层 — 只放常量）
文件: src/autocar/agent_cli/templates/locators_template.py

变量占位符: 车辆设置 小写模块名；车辆设置Page 驼峰模块名。

本文件职责:
    - 只定义 class Loc 与 (value, by) 常量
    - 不写 car/at、不写点击/断言/导航逻辑
    - 操作与断言见 page_template / test_template

格式: (value, by)；by 白名单: text | id | desc | xpath | textContains
选择优先级: autocar-ref-locator 技能（-l-b ＞ --text ＞ --text-contains --nth ＞ --ref）
"""


class Loc:
    """车辆设置Page 模块定位器"""

    # ==================== 导航入口 ====================
    # 格式: (value, by) — 在 Page 中引用: self.car.ensure_click(Loc.BTN_XXX)

    # BTN_ENTRY = ("设置", "desc")           # 优先 desc
    # BTN_ENTRY2 = ("蓝牙", "text")           # 其次 text
    # BTN_ENTRY3 = ("com.xxx:id/entry", "id") # 最后 id

    # ==================== 页面元素 ====================

    # TITLE = ("页面标题", "text")
    # SWITCH_XXX = ("蓝牙", "desc")

    # ==================== 按钮 ====================

    # BTN_CONFIRM = ("确定", "text")
    # BTN_CANCEL = ("取消", "text")

    # ==================== 导航入口 ====================
    BTN_HOME_CLOSE = ("com.renault.car.launcher:id/close_button", "id")
    BTN_CLOSE = ("关闭", "desc")
    BTN_BACK = ("返回", "desc")
    ENTRY_SETTINGS = ("设置", "text")
    ENTRY_NETWORK_INTERNET = ("网络和互联网", "text")
    ENTRY_WLAN_PREFERENCES = ("WLAN 偏好设置", "text")

    # ==================== 页面元素 ====================
    TXT_WLAN_AUTO_ENABLE = ("自动开启 WLAN", "text")
    TXT_INSTALL_CERTIFICATES = ("Install certificates", "text")

    # ==================== Smoke_Test_44: 车辆 > 驾驶辅助 > 停车 ====================
    # 前置回主页面（车机正常启动，处于主页面）
    HOME_CAR_WORLD = ("com.android.systemui:id/car_world", "id")
    # 导航入口
    ENTRY_DRIVE_ASSIST = ("驾驶辅助", "text")
    ENTRY_PARKING = ("停车", "text")

    # 页面标题文本
    TXT_FRONT = ("前面", "text")
    TXT_SIDE = ("侧面", "text")
    TXT_RCTA = ("后交叉停车警报", "text")
    TXT_RAEB = ("后主动紧急制动", "text")
    # 原案文案"乘员安全出口"；UI 实测为"乘客安全出口"（Explore assert_text ok:true）
    TXT_OSE = ("乘客安全出口", "text")

    # 5 个选项开关
    TOGGLE_FRONT = ("com.renault.car.driveassist:id/front_toggle", "id")
    TOGGLE_SIDE = ("com.renault.car.driveassist:id/side_toggle", "id")
    TOGGLE_RCTA = ("com.renault.car.driveassist:id/rcta_toggle", "id")
    TOGGLE_RAEB = ("com.renault.car.driveassist:id/raeb_toggle", "id")
    TOGGLE_OSE = ("com.renault.car.driveassist:id/ose_toggle", "id")

    # 开关内部 switch_widget 状态（checked 属性）
    SWITCH_FRONT = ("//*[@resource-id='com.renault.car.driveassist:id/front_toggle']//*[@resource-id='android:id/switch_widget']", "xpath")
    SWITCH_SIDE = ("//*[@resource-id='com.renault.car.driveassist:id/side_toggle']//*[@resource-id='android:id/switch_widget']", "xpath")
    SWITCH_RCTA = ("//*[@resource-id='com.renault.car.driveassist:id/rcta_toggle']//*[@resource-id='android:id/switch_widget']", "xpath")
    SWITCH_RAEB = ("//*[@resource-id='com.renault.car.driveassist:id/raeb_toggle']//*[@resource-id='android:id/switch_widget']", "xpath")
    SWITCH_OSE = ("//*[@resource-id='com.renault.car.driveassist:id/ose_toggle']//*[@resource-id='android:id/switch_widget']", "xpath")

    # ==================== Smoke_Test_37: 设置 > 系统 > 语言和输入法 > 语言 ====================
    # 前置导航：打开 设置>系统（回放已验证入口：grid_nav→应用菜单→设置，滚动定位 系统）
    GRID_NAV = ("com.android.systemui:id/grid_nav", "id")
    ENTRY_SYSTEM = ("系统", "text")

    # 步骤0：打开语言和输入法 —— 系统设置页首屏项（explored[0].assert_text ok:true）
    ENTRY_LANGUAGE_INPUT = ("语言和输入法", "text")
    TXT_UNIT = ("单位", "text")
    TXT_STORAGE = ("存储空间", "text")
    TXT_ABOUT = ("关于", "text")
    TXT_LEGAL_INFO = ("法律信息", "text")
    # 步骤0 次屏项（第一次 swipe 之后可见）
    TXT_RESET_OPTIONS = ("重置选项", "text")
    TXT_ANDROID_AUTO = ("Android Auto", "text")

    # 步骤1：点击语言 —— 语言选择页
    ENTRY_LANGUAGE = ("语言", "text")
    TXT_SUGGESTED = ("建议", "text")
    TXT_SIMPLIFIED_CHINESE_CN = ("简体中文（中国）", "text")
    TXT_ALL_LANGUAGES = ("所有语言", "text")

    # 语言列表项（explored[1].assert_text ok:true）
    LANG_CS = ("Čeština", "text")
    LANG_DA = ("Dansk", "text")
    LANG_DE = ("Deutsch", "text")
    LANG_ET = ("Eesti", "text")
    LANG_EN = ("English", "text")
    LANG_ES = ("Español", "text")
    LANG_FR = ("Français", "text")
    LANG_HR = ("Hrvatski", "text")
    LANG_IT = ("Italiano", "text")
    LANG_LV = ("Latviešu", "text")
    LANG_LT = ("Lietuvių", "text")
    LANG_HU = ("Magyar", "text")
    LANG_MS = ("Melayu", "text")
    LANG_NL = ("Nederlands", "text")
    LANG_PL = ("Polski", "text")
    LANG_PT = ("Português", "text")
    LANG_RO = ("Română", "text")
    LANG_SQ = ("Shqip", "text")
    LANG_JA = ("日本語", "text")
    LANG_ZH_HANT = ("繁體中文", "text")

    # ==================== Smoke_Test_46: 车辆 > 座椅 ====================
    # 步骤2：点击座椅（UI 实测文案"座位"，回放 idx1）
    ENTRY_SEAT = ("座位", "text")

    # 座椅页面元素（explored final_assertions ok:true）
    TXT_DRIVING_POSITION = ("驾驶位置", "text")
    TXT_SEAT_DRIVING_DEVICE = ("座椅和驾驶设备", "text")
    BTN_SAVE = ("保存", "text")
    BTN_CALL = ("调用", "text")

    # --- END ---

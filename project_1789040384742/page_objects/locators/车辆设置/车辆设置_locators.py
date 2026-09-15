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
    # 导航入口（launcher apps_grid 与 driveassist UI 均为英文，
    # 层次树 dump 实测 apps_grid 节点 title="Driving assistance"，无中文文案）
    ENTRY_DRIVE_ASSIST = ("Driving assistance", "text")
    ENTRY_PARKING = ("Parking", "text")

    # 页面标题文本（case expected 文案为英文，与 UI 英文一致）
    TXT_FRONT = ("Front", "text")
    TXT_SIDE = ("Side", "text")
    TXT_RCTA = ("Rear Cross Parking Alert", "text")
    TXT_RAEB = ("Rear Active Emergency Braking", "text")
    TXT_OSE = ("Occupant Safe Exit", "text")

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
    # 开关处于开启状态时的匹配 XPath（exists 探测 @checked='true'，避免 get_element_info 返回键不可靠）
    SWITCH_FRONT_ON = ("//*[@resource-id='com.renault.car.driveassist:id/front_toggle']//*[@resource-id='android:id/switch_widget' and @checked='true']", "xpath")
    SWITCH_SIDE_ON = ("//*[@resource-id='com.renault.car.driveassist:id/side_toggle']//*[@resource-id='android:id/switch_widget' and @checked='true']", "xpath")
    SWITCH_RCTA_ON = ("//*[@resource-id='com.renault.car.driveassist:id/rcta_toggle']//*[@resource-id='android:id/switch_widget' and @checked='true']", "xpath")
    SWITCH_RAEB_ON = ("//*[@resource-id='com.renault.car.driveassist:id/raeb_toggle']//*[@resource-id='android:id/switch_widget' and @checked='true']", "xpath")
    SWITCH_OSE_ON = ("//*[@resource-id='com.renault.car.driveassist:id/ose_toggle']//*[@resource-id='android:id/switch_widget' and @checked='true']", "xpath")

    # ==================== Smoke_Test_37: 设置 > 系统 > 语言和输入法 > 语言 ====================
    # 前置导航：打开 Settings>System（回放已验证入口：grid_nav→应用菜单"Settings"，滚动定位 "System"；
    # 车机 launcher 菜单与 car settings 均为英文文案，pytest 实测 apps_grid 无中文"设置"）
    GRID_NAV = ("com.android.systemui:id/grid_nav", "id")
    ENTRY_SYSTEM = ("System", "text")

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

    # ==================== Smoke_Test_41: 能源/驾驶 - 我的驾驶 ====================
    # 步骤1：进入车辆页面后左侧栏项（explored assert_exists ok:true）
    TXT_DRIVE_MODE = ("Drive Mode", "text")
    ENTRY_MY_DRIVING = ("My Driving", "text")
    TXT_DRIVING_ASSISTANCE = ("Driving assistance", "text")
    TXT_VEHICLE = ("Vehicle", "text")
    TXT_SETTINGS = ("Settings", "text")

    # 步骤2：My Driving 页面（explored assert_text/assert_ocr ok:true；"Eco"为实测节点文案）
    TXT_ECO_SCORE = ("Eco", "text")
    ENTRY_ENERGY = ("Energy", "text")
    BTN_SINCE_START = ("Since start", "text")
    BTN_SINCE_RESET = ("Since reset", "text")

    # 步骤3：Energy Detail 页面（explored assert_text ok:true）
    TXT_ENERGY_CONSUMPTION = ("Energy consumption", "text")

    # 步骤4/5：Since reset 页面（explored assert_exists/assert_text ok:true）
    BTN_RESET = ("Reset", "text")
    TXT_CONSUMPTION = ("Consumption", "text")
    # MyDriving 页面工具栏返回按钮（explored step4 prereq ensure_click "Back" by=desc ok:true）
    BTN_BACK_MYDRIVING = ("Back", "desc")

    # ==================== Smoke_Test_46: 车辆 > 座椅 ====================
    # 步骤2：点击 Seats 进入座椅页（原用例步骤2原文"点击Seats"；当前设备 vehicle 菜单为英文，
    #        anchors=[Drive Mode, Electric, Seats]，Smoke_Test_7 explore assert_text("Seats") ok:true）
    ENTRY_SEAT = ("Seats", "text")

    # 座椅页面元素（当前设备 vehiclesettings 应用为英文界面；设备实际文案与 case 引号不完全一致，
    # pytest assert_text 'driver position' 实测树中不存在，故按 explore dump 2026-09-10 实测的
    # resource-id 断言业务元素存在性，语言无关）
    TXT_DRIVING_POSITION = ("driver position", "text")
    TXT_SEAT_DRIVING_DEVICE = ("Seats and driving equipment", "text")
    SEAT_DRIVER_POSITION_VIEW = ("com.renault.car.vehiclesettings:id/seatsDriverPositionTextView", "id")
    SEAT_DRIVER_DETAILS_VIEW = ("com.renault.car.vehiclesettings:id/seatsDriverPositionDetailsTextView", "id")
    # 保存/调用按钮（case"带有保存和调用按钮"）
    BTN_SAVE = ("com.renault.car.vehiclesettings:id/seatsPositionDriverSaveButton", "id")
    BTN_CALL = ("com.renault.car.vehiclesettings:id/seatsPositionDriverRecallButton", "id")

    # ==================== Smoke_Test_43: 能源/驾驶 - 驾驶辅助 - 舒适 ====================
    # 步骤1：点击左侧导航栏 Vehicle > Driving assistance > Comfort（回放 idx23-25）
    TXT_COMFORT = ("Comfort", "text")
    # 点击 launcher 网格 "Driving assistance" 后 driveassist 落到的中间页（回放 idx24 证据 My Safety）
    TXT_MY_SAFETY = ("My Safety", "text")

    # 步骤1 页面显示文案（explored final_assertions assert_text ok:true；"Eco predictive assistant *" 含实测节点星号）
    TXT_ECO_PREDICTIVE_ASSISTANT = ("Eco predictive assistant *", "text")
    TXT_FOLLOWING_DISTANCE = ("Following distance", "text")
    TXT_DISPLAY_RISKY_AREAS = ("Display risky areas", "text")
    TXT_ADAPTIVE_SPEED_LIMITER = ("Adaptive speed limiter and cruise control", "text")
    TXT_TO_ROAD_CONTEXT = ("To road context", "text")

    # 步骤2：3 个选项开关（回放 idx16-18 ensure_click ok:true）
    TOGGLE_FOLLOWING_DISTANCE = ("com.renault.car.driveassist:id/driving_following_distance", "id")
    TOGGLE_RISK_AREA_DISPLAY = ("com.renault.car.driveassist:id/driving_risk_area_display", "id")
    TOGGLE_AUTO_SPEED_SIGN = ("com.renault.car.driveassist:id/driving_automatic_speed_sign", "id")

    # 开关内部 switch_widget 状态（checked 属性，explored final_assertions assert_attr ok:true）
    SWITCH_FOLLOWING_DISTANCE = ("//*[@resource-id='com.renault.car.driveassist:id/driving_following_distance']//*[@resource-id='android:id/switch_widget']", "xpath")
    SWITCH_RISK_AREA_DISPLAY = ("//*[@resource-id='com.renault.car.driveassist:id/driving_risk_area_display']//*[@resource-id='android:id/switch_widget']", "xpath")
    SWITCH_AUTO_SPEED_SIGN = ("//*[@resource-id='com.renault.car.driveassist:id/driving_automatic_speed_sign']//*[@resource-id='android:id/switch_widget']", "xpath")
    # 开关处于开启状态时的匹配 XPath（通过 exists 探测 checked=true，避免依赖 get_element_info 返回键）
    SWITCH_FOLLOWING_DISTANCE_ON = ("//*[@resource-id='com.renault.car.driveassist:id/driving_following_distance']//*[@resource-id='android:id/switch_widget' and @checked='true']", "xpath")
    SWITCH_RISK_AREA_DISPLAY_ON = ("//*[@resource-id='com.renault.car.driveassist:id/driving_risk_area_display']//*[@resource-id='android:id/switch_widget' and @checked='true']", "xpath")
    SWITCH_AUTO_SPEED_SIGN_ON = ("//*[@resource-id='com.renault.car.driveassist:id/driving_automatic_speed_sign']//*[@resource-id='android:id/switch_widget' and @checked='true']", "xpath")

    # ==================== Smoke_Test_45: 能源/驾驶 - 驾驶ECO/MySense声音 ====================
    # 步骤3：My Driving 页面 Energy 入口（回放 idx13 ensure_click by=id ok:true）
    ENERGY_ENTRY = ("com.renault.car.mydriving:id/energyConsumptionTrip", "id")

    # ==================== Smoke_Test_17: 蓝牙 - 可发现性开关行为 ====================
    # 步骤0/1：Bluetooth 设置页配对模式开关（回放 idx18 关闭、idx20 开启 ensure_click by=desc ok:true；
    #         开启蓝牙会触发 GMS“Play Protect certified”弹层覆盖，idx21 第二次 ensure_click 在 pytest
    #         树中不可达，开启后改为回主界面重新导航进入设置页复核，不再连续点击同一 desc）
    TOGGLE_BLUETOOTH_PAIRING = ("Bluetooth toggle switch", "desc")
    # 开关内部 switch_widget 状态节点（final_assertions assert_attr checked by=id ok:true，
    #         用于断言配对模式关闭/激活后的可发现性状态）
    SWITCH_BLUETOOTH = ("android:id/switch_widget", "id")
    # 开关处于开启状态时的匹配 XPath（exists 探测 @checked='true'，供前置“启用Bluetooth”
    #         确保开启使用；初始开关状态随车机记忆可变，pytest 曾为 OFF）
    SWITCH_BLUETOOTH_ON = ("//*[@resource-id='android:id/switch_widget' and @checked='true']", "xpath")
    # 开关处于关闭状态时的匹配 XPath（wait 探测 @checked='false'，供步骤0“关闭配对模式”确认）
    SWITCH_BLUETOOTH_OFF = ("//*[@resource-id='android:id/switch_widget' and @checked='false']", "xpath")
    # Bluetooth 设置页入口（回放 idx28 ensure_click by=text ok:true；Settings 列表下滑 3 次后可见）
    ENTRY_BLUETOOTH = ("Bluetooth", "text")

    # ==================== Smoke_Test_18: 蓝牙 - 扫描、配对、配置文件与取消流程 ====================
    # 步骤0/3：Pair new device 入口（回放 idx3/21 ensure_click by=text ok:true）
    BTN_PAIR_NEW_DEVICE = ("Pair new device", "text")
    # 扫描结果中的可连接设备名（回放 idx22/23 ensure_click by=text ok:true；final_assertions assert_exists ok:true）
    TXT_DEVICE_F53G = ("F-53G", "text")
    TXT_DEVICE_REDMI_WATCH = ("REDMI Watch 6 C571", "text")
    # 已配对设备名（回放 idx6/15 ensure_click、idx13 返回后 final_assertions assert_exists 均 ok:true）
    TXT_DEVICE_62888B2B = ("62888b2b", "text")
    # 配对确认弹窗按钮（回放 idx7/8 ensure_click by=text ok:true；原 case 文案 "pair"，实测弹窗按钮为 Connect）
    BTN_CONNECT = ("Connect", "text")
    # 取消配对按钮（回放 idx24 ensure_click by=text ok:true）
    BTN_CANCEL = ("Cancel", "text")
    # 设备配置文件页按钮（final_assertions assert_exists by=text ok:true）
    TXT_DISCONNECT = ("Disconnect", "text")
    TXT_FORGET = ("Forget", "text")
    # 配置文件列表项（final_assertions assert_exists "Phone calls" ok:true；Media audio/Text Messages/
    # Contacts and call history sharing 来自原 case expected 文案，按同 by=text 模式断言）
    TXT_PHONE_CALLS = ("Phone calls", "text")
    TXT_MEDIA_AUDIO = ("Media audio", "text")
    TXT_TEXT_MESSAGES = ("Text Messages", "text")
    TXT_CONTACTS_SHARING = ("Contacts and call history sharing", "text")
    # 配对中状态文案（final_assertions assert_exists expected=false ok:true，用于确认配对已中止）
    TXT_PAIRING = ("Pairing", "text")

    # ==================== Smoke_Test_36: 设置 > Wi-Fi > Wi-Fi偏好设置 ====================
    # 步骤1：左侧导航栏 Vehicle > Settings > Network and internet（回放 idx0-2 ensure_click ok:true，UI 实测英文文案）
    #        car_world 入口复用 HOME_CAR_WORLD（回放 idx0 by=id）；Settings 复用 TXT_SETTINGS（回放 idx1 by=text）
    TXT_NETWORK_INTERNET = ("Network and internet", "text")
    # 步骤2：Network and internet 列表底部的 Wi-Fi preferences 入口（回放 idx6 ensure_click ok:true，含 U+2011 窄连字符）
    TXT_WIFI_PREFERENCES = ("Wi‑Fi preferences", "text")
    # 步骤2 终态页面文本（回放 idx6 后 final_assertions assert_text ok:true；Install certificates 复用 TXT_INSTALL_CERTIFICATES）
    TXT_TURN_ON_WIFI_AUTO = ("Turn on Wi‑Fi automatically", "text")

    # ==================== Smoke_Test_19: 蓝牙 - 断开与忘记流程 ====================
    # 步骤0：Disconnect 后返回 Bluetooth 界面显示的无连接状态文案
    # （回放 idx5 press back 后 final_assertions[0] assert_text "Disconnected" by=text ok:true）
    TXT_DISCONNECTED = ("Disconnected", "text")

    # --- END ---

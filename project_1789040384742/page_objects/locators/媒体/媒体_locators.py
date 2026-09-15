# -*- coding: utf-8 -*-
"""
定位器模板 v8.1（POM 定位器层 — 只放常量）
文件: src/autocar/agent_cli/templates/locators_template.py

变量占位符: 媒体 小写模块名；媒体Page 驼峰模块名。

本文件职责:
    - 只定义 class Loc 与 (value, by) 常量
    - 不写 car/at、不写点击/断言/导航逻辑
    - 操作与断言见 page_template / test_template

格式: (value, by)；by 白名单: text | id | desc | xpath | textContains
选择优先级: autocar-ref-locator 技能（-l-b ＞ --text ＞ --text-contains --nth ＞ --ref）
"""


class Loc:
    """媒体Page 模块定位器"""

    # ==================== 导航入口 ====================
    # 格式: (value, by) — 在 Page 中引用: self.car.ensure_click(Loc.BTN_XXX)

    # 底部导航栏 Phone 入口（replay_timeline ok:true）
    PHONE_NAV = ("com.android.systemui:id/phone_nav", "id")

    # ==================== 页面元素 ====================

    # 电话连接提示文案（error_string，final_assertions ok:true）
    DIALER_ERROR_STRING = ("com.renault.car.dialer:id/error_string", "id")
    # Connect to Bluetooth 按钮（final_assertions ok:true）
    CONNECT_TO_BLUETOOTH = ("Connect to Bluetooth", "text")
    # 可用设备列表标题（final_assertions ok:true）
    AVAILABLE_DEVICES = ("Available devices", "text")
    # 车辆名称（final_assertions ok:true）
    MY_CAR_TEXT = ("MY_CAR", "text")
    # 目标蓝牙设备 / 已配对设备（replay_timeline + final_assertions ok:true）
    BT_DEVICE_62888B2B = ("62888b2b", "text")

    # ==================== 按钮 ====================

    # Connect to Bluetooth 按钮（replay_timeline ok:true）
    CONNECT_BLUETOOTH_BUTTON = ("com.renault.car.dialer:id/connect_bluetooth_button", "id")
    # Pair new device 扫描新设备（replay_timeline ok:true）
    PAIR_NEW_DEVICE = ("Pair new device", "text")
    # 配对确认 Pair（replay_timeline ok:true）
    PAIR_BUTTON = ("Pair", "text")
    # 配对确认 配对 中文（replay_timeline ok:true）
    PAIR_BUTTON_CN = ("配对", "text")

    # ==================== 搜索与设备管理器（Smoke_Test_22） ====================

    # Phone 页右上角搜索图标（replay_timeline ok:true）
    SEARCH_ICON = ("Search", "desc")
    # 搜索输入框（replay_timeline ok:true）
    SEARCH_INPUT = ("com.renault.car.dialer:id/car_ui_toolbar_search_bar", "id")
    # 搜索关闭按钮（replay_timeline ok:true）
    SEARCH_CLOSE = ("com.renault.car.dialer:id/car_ui_toolbar_search_close", "id")
    # 返回按钮（replay_timeline ok:true）
    BACK_BUTTON = ("Back", "desc")
    # 设备管理入口（replay_timeline ok:true）
    DEVICE_MANAGER = ("com.renault.car.dialer:id/menu_item_device_manager", "id")
    # 设备管理页：电话按钮（final_assertions ok:true, checked=true）
    DEVICE_PHONE_BUTTON = ("com.renault.car.spcx:id/phoneButton", "id")
    # 设备管理页：媒体按钮（final_assertions ok:true, checked=true）
    DEVICE_MEDIA_BUTTON = ("com.renault.car.spcx:id/mediaButton", "id")
    # 设备管理页：删除设备按钮（final_assertions ok:true）
    DEVICE_DELETE_BUTTON = ("com.renault.car.spcx:id/deleteButton", "id")

    # ==================== 电话页标签页与同步断言（Smoke_Test_21） ====================

    # 电话页顶部标签页（replay_timeline ok:true，按 execution_index 顺序消费）
    RECENT_TAB = ("Recent", "text")
    CONTACTS_TAB = ("Contacts", "text")
    # 联系人标签的 desc 语义（replay_timeline ok:true）
    CONTACTS_TAB_CN = ("联系人", "desc")
    FAVOURITES_TAB = ("Favourites", "text")
    DIAL_PAD_TAB = ("Dial Pad", "text")

    # 最近通话列表中的通话记录（final_assertions ok:true，当前 Explore 实测记录）
    RECENT_CALL_ITEM = ("15649113591", "text")
    # 联系人标签页同步出的联系人（final_assertions ok:true）
    CONTACT_WANG = ("王", "text")
    # 收藏标签页本地收藏标题（final_assertions ok:true）
    LOCAL_FAVOURITES = ("Local favourites", "text")

    # --- END ---

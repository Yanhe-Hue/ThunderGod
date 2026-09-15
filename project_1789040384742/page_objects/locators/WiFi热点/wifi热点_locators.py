# -*- coding: utf-8 -*-
"""
定位器模板 v8.1（POM 定位器层 — 只放常量）
文件: src/autocar/agent_cli/templates/locators_template.py

变量占位符: wifi热点 小写模块名；Wifi热点Page 驼峰模块名。

本文件职责:
    - 只定义 class Loc 与 (value, by) 常量
    - 不写 car/at、不写点击/断言/导航逻辑
    - 操作与断言见 page_template / test_template

格式: (value, by)；by 白名单: text | id | desc | xpath | textContains
选择优先级: autocar-ref-locator 技能（-l-b ＞ --text ＞ --text-contains --nth ＞ --ref）
"""


class Loc:
    """Wifi热点Page 模块定位器"""

    # ==================== Smoke_Test_85: 设置 > Network and internet（WiFi 界面与默认状态） ====================
    # 前置/回放导航链（回放 exec16-18/22-24 已验证: grid_nav → Settings → Network and internet）
    GRID_NAV = ("com.android.systemui:id/grid_nav", "id")          # 底部导航栏应用图标
    ENTRY_SETTINGS = ("Settings", "text")
    ENTRY_NETWORK_INTERNET = ("Network and internet", "text")
    BTN_HOME = ("com.android.systemui:id/home", "id")              # 底部导航栏 Home
    BTN_BACK = ("Back", "desc")                                    # 设置页工具栏返回（回放 exec4）

    # ==================== 页面元素（Network and internet / Connectivity 区块） ====================
    # 文案含 U+2011 不间断连字符（Wi‑Fi），与页面实测节点一致
    TXT_CONNECTIVITY = ("Connectivity", "text")
    TXT_WIFI = ("Wi‑Fi", "text")
    TXT_JOIN_OTHER_NETWORK = ("Join other network", "text")
    TXT_WIFI_PREFERENCES = ("Wi‑Fi preferences", "text")
    TXT_HOTSPOT = ("Hotspot", "text")
    TXT_APP_DATA_USAGE = ("App data usage", "text")

    # ==================== WiFi 开关 ====================
    # Wi‑Fi 开关行（explored final_assertions assert_attr checked=false ok:true）
    WIFI_TOGGLE_SWITCH = ("Wi‑Fi toggle switch", "desc")
    # 开关控件本体（Smoke_Test_86 assert_attr checked 状态验证，replay final_assertions ok:true）
    SWITCH_WIDGET = ("android:id/switch_widget", "id")
    # 可用 WiFi 网络名（Smoke_Test_86 开启后列表填充验证，Explore assert_exists ok:true）
    TXT_WIFI_NETWORK_THUNDERSOFT = ("ThunderSoft-Global", "text")

    # --- END ---

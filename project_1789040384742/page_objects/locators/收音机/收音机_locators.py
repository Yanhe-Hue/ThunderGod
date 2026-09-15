# -*- coding: utf-8 -*-
"""
定位器模板 v8.1（POM 定位器层 — 只放常量）
文件: src/autocar/agent_cli/templates/locators_template.py

变量占位符: 收音机 小写模块名；收音机Page 驼峰模块名。

本文件职责:
    - 只定义 class Loc 与 (value, by) 常量
    - 不写 car/at、不写点击/断言/导航逻辑
    - 操作与断言见 page_template / test_template

格式: (value, by)；by 白名单: text | id | desc | xpath | textContains
选择优先级: autocar-ref-locator 技能（-l-b ＞ --text ＞ --text-contains --nth ＞ --ref）
"""


class Loc:
    """收音机Page 模块定位器"""

    # ==================== 导航入口 ====================
    # 格式: (value, by) — 在 Page 中引用: self.car.ensure_click(Loc.BTN_XXX)

    # 左侧导航栏“音乐”入口（Explored: car.ensure_click by=id）
    MUSIC_NAV = ("com.android.systemui:id/music_nav", "id")
    # 车机主页导航入口（Smoke_Test_56 postcondition: car.ensure_click by=id，后置恢复初始状态）
    HOME_NAV = ("com.android.systemui:id/home", "id")
    # “AM收音机”入口（Explored: car.ensure_click by=text）
    AM_RADIO = ("AM收音机", "text")
    # “AM Radio”英文入口文本（Smoke_Test_49 Explored: car.ensure_click by=text，界面实际显示英文 AM Radio）
    AM_RADIO_TEXT = ("AM Radio", "text")
    # FM 收音机“Radio”入口（Smoke_Test_53 precondition 回放: car.ensure_click by=text，点击进入 FM 收音机页面）
    RADIO_ENTRY = ("Radio", "text")
    # 返回键（Smoke_Test_54 回放: car.ensure_click by=desc）
    BACK = ("Back", "desc")

    # ==================== 页面元素 ====================

    # 标签页“列表”（Explored: car.assert_exists by=text）
    TAB_LIST = ("列表", "text")
    # 标签页“收藏”（Explored: car.assert_exists by=text）
    TAB_FAVORITE = ("收藏", "text")
    # 标签页“List”（Smoke_Test_51 回放: car.ensure_click by=text，界面英文）
    TAB_LIST_EN = ("List", "text")
    # 标签页“Favourites”（Smoke_Test_51 回放: car.ensure_click by=text，界面英文）
    TAB_FAVOURITES = ("Favourites", "text")
    # Favourites 列表空提示（Smoke_Test_51 Explored: car.assert_exists by=text，收藏移除后列表为空）
    FAVOURITES_EMPTY_HINT = ("Media isn't available for this list", "text")
    # 最小化控制栏标题 / 默认频率显示（Explored: car.assert_text by=id）
    MINIMIZED_CONTROL_BAR_TITLE = ("com.renault.car.media:id/minimized_control_bar_title", "id")
    # 最小化控制栏（Explored: car.assert_exists by=id）
    MINIMIZED_CONTROL_BAR = ("com.renault.car.media:id/minimized_control_bar", "id")
    # 播放/暂停/停止按钮（Explored: car.assert_exists by=id）
    PLAY_PAUSE_STOP = ("com.renault.car.media:id/play_pause_stop", "id")
    # 播放/暂停容器（Smoke_Test_54 final_assertions: car.assert_exists by=id）
    PLAY_PAUSE_CONTAINER = ("com.renault.car.media:id/play_pause_container", "id")
    # “正在播放”状态文案（本设备 UI 为英文：工具栏 car_ui_toolbar_title 显示 “Now Playing”，
    # Smoke_Test_50 AM Radio 页 anchors 实测 ["1239 kHz", "Now Playing"]；
    # “正在播放”仅出现在 xlsx 步骤文案，全部 hierarchy/截图证据无命中）
    PLAYING_STATUS_TEXT = ("Now Playing", "text")
    # 频率标题 / 531kHz频率按钮与调谐后频率显示（Explored: car.ensure_click / car.assert_text by=id）
    FREQUENCY_TITLE = ("com.renault.car.media:id/title", "id")
    # 切换到下一电台后的频率显示（Smoke_Test_50 Explored: car.assert_text by=text）
    FREQUENCY_1602KHZ = ("1602 kHz", "text")
    # FM 默认频率 87.5 MHz 显示（Smoke_Test_53 final_assertions: car.assert_text by=text，界面实际显示 MHz）
    FREQUENCY_875MHZ = ("87.5 MHz", "text")

    # ==================== 按钮 ====================

    # 频率列表项自定义动作（Explored: car.ensure_click by=id）
    BROWSE_ITEM_CUSTOM_ACTION = ("com.renault.car.media:id/browse_item_custom_action", "id")
    # 频率列表项容器（Smoke_Test_50 Explored: car.ensure_click by=id）
    ITEM_CONTAINER = ("com.renault.car.media:id/item_container", "id")
    # 最小化播放控制栏（Explored: car.ensure_click by=id）
    MINIMIZED_PLAYBACK_CONTROLS = ("com.renault.car.media:id/minimized_playback_controls", "id")
    # “下一曲”按钮（Explored: car.ensure_click by=id）
    SKIP_NEXT = ("com.renault.car.media:id/skip_next", "id")

    pass
    # --- END ---

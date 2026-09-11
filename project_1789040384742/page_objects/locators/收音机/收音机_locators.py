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
    # “AM收音机”入口（Explored: car.ensure_click by=text）
    AM_RADIO = ("AM收音机", "text")

    # ==================== 页面元素 ====================

    # 标签页“列表”（Explored: car.assert_exists by=text）
    TAB_LIST = ("列表", "text")
    # 标签页“收藏”（Explored: car.assert_exists by=text）
    TAB_FAVORITE = ("收藏", "text")
    # 最小化控制栏标题 / 默认频率显示（Explored: car.assert_text by=id）
    MINIMIZED_CONTROL_BAR_TITLE = ("com.renault.car.media:id/minimized_control_bar_title", "id")
    # 最小化控制栏（Explored: car.assert_exists by=id）
    MINIMIZED_CONTROL_BAR = ("com.renault.car.media:id/minimized_control_bar", "id")
    # 播放/暂停/停止按钮（Explored: car.assert_exists by=id）
    PLAY_PAUSE_STOP = ("com.renault.car.media:id/play_pause_stop", "id")
    # “正在播放”状态文案（Explored: car.assert_exists by=text）
    PLAYING_STATUS_TEXT = ("正在播放", "text")
    # 频率标题 / 531kHz频率按钮与调谐后频率显示（Explored: car.ensure_click / car.assert_text by=id）
    FREQUENCY_TITLE = ("com.renault.car.media:id/title", "id")

    # ==================== 按钮 ====================

    # 频率列表项自定义动作（Explored: car.ensure_click by=id）
    BROWSE_ITEM_CUSTOM_ACTION = ("com.renault.car.media:id/browse_item_custom_action", "id")
    # 最小化播放控制栏（Explored: car.ensure_click by=id）
    MINIMIZED_PLAYBACK_CONTROLS = ("com.renault.car.media:id/minimized_playback_controls", "id")
    # “下一曲”按钮（Explored: car.ensure_click by=id）
    SKIP_NEXT = ("com.renault.car.media:id/skip_next", "id")

    pass
    # --- END ---

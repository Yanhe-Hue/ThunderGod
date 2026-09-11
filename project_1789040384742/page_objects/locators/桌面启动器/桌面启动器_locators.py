# -*- coding: utf-8 -*-
"""
定位器模板 v8.1（POM 定位器层 — 只放常量）
文件: src/autocar/agent_cli/templates/locators_template.py

变量占位符: 桌面启动器 小写模块名；桌面启动器Page 驼峰模块名。

本文件职责:
    - 只定义 class Loc 与 (value, by) 常量
    - 不写 car/at、不写点击/断言/导航逻辑
    - 操作与断言见 page_template / test_template

格式: (value, by)；by 白名单: text | id | desc | xpath | textContains
选择优先级: autocar-ref-locator 技能（-l-b ＞ --text ＞ --text-contains --nth ＞ --ref）
"""


class Loc:
    """桌面启动器Page 模块定位器"""

    # ==================== 首页区域（原始 expected: 地图/音频/Google 助手） ====================
    # 格式: (value, by) — 在 Page 中引用: self.car.ensure_click(Loc.BTN_XXX)

    # Google 地图区域（final_assertions: by=id）
    MAPS_ZOOM_IN = ("com.google.android.apps.maps:id/map_buttons_view_zoom_in", "id")

    # 音频区域（final_assertions: by=text）
    AUDIO_AREA = ("音频", "text")

    # Google 助手区域（final_assertions: by=text）
    GOOGLE_ASSISTANT = ("Google 助理", "text")

    # Google 助手建议区（replay_timeline: car.ensure_click by=id，步骤1 第一击）
    GOOGLE_ASSISTANT_SUGGESTION = ("com.renault.car.launcher:id/google_assistant_suggestion_text", "id")

    # ==================== 地图搜索交互（Smoke_Test_4: 搜索下拉菜单 / 屏幕键盘） ====================

    # 谷歌地图搜索栏（replay_timeline: car.ensure_click by=id，步骤1 按序点击两次）
    MAPS_SEARCH_BOX = ("com.google.android.apps.maps:id/main_suggested_destinations_search_box", "id")

    # 键盘搜索输入框（replay_timeline: 步骤2 再次点击搜索栏 by=id）
    MAPS_KEYBOARD_SEARCH_EDIT = ("com.google.android.apps.maps:id/destination_input_keyboard_search_edit_text", "id")

    # 搜索下拉菜单（final_assertions: by=text，步骤1 预期）
    MAPS_DROPDOWN_RECENT = ("最近", "text")
    MAPS_DROPDOWN_CATEGORY = ("类别", "text")
    MAPS_DROPDOWN_SAVED = ("已保存", "text")

    # 屏幕键盘（final_assertions: by=desc，步骤2 预期）
    MAPS_KEYBOARD_SPACE = ("空格键", "desc")

    # ==================== 谷歌助手语音交互（Smoke_Test_6: 语音交互焦点） ====================

    # 语音交互焦点（final_assertions: by=id，步骤1 预期，位于屏幕底部）
    VOICEPLATE = ("com.google.android.carassistant:id/voiceplate", "id")

    # ==================== 左侧导航（Smoke_Test_7: 系统UI 左侧导航切换） ====================

    # 左侧导航栏应用图标（replay_timeline: car.ensure_click by=id，步骤0）
    NAV_APP = ("com.android.systemui:id/grid_nav", "id")

    # 左侧导航栏车辆图标（replay_timeline: car.ensure_click by=id，步骤1 / 步骤3 回切）
    NAV_VEHICLE = ("com.android.systemui:id/car_world", "id")

    # 左侧导航栏音乐图标（replay_timeline: car.ensure_click by=id，步骤2）
    NAV_MUSIC = ("com.android.systemui:id/music_nav", "id")

    # 左侧导航栏电话图标（replay_timeline: car.ensure_click by=id，步骤3）
    NAV_PHONE = ("com.android.systemui:id/phone_nav", "id")

    # ==================== 应用页面（Smoke_Test_7 步骤0 final_assertions: by=text） ====================
    APP_PLAY_STORE = ("Play 商店", "text")
    APP_ANDROID_AUTO = ("Android Auto", "text")
    APP_DEVICE_MANAGER = ("设备管理器", "text")
    APP_RADIO = ("收音机", "text")
    APP_AM_RADIO = ("AM收音机", "text")

    # ==================== 车辆页面（Smoke_Test_7 步骤1/3 final_assertions: by=text） ====================

    # 首页车辆小部件容器（Smoke_Test_36 final_assertions: by=id，车辆小部件添加后存在于主界面）
    VEHICLE_CONTAINER = ("com.renault.car.launcher:id/vehicle_container", "id")

    VEHICLE_LIVE_DATA = ("Live Data", "text")
    VEHICLE_COACHING = ("Coaching", "text")
    VEHICLE_CHALLENGES = ("Challenges", "text")
    VEHICLE_DRIVE_MODE = ("Drive Mode", "text")
    VEHICLE_POWER = ("电力", "text")
    VEHICLE_SEAT = ("座位", "text")
    VEHICLE_MY_DRIVING = ("My Driving", "text")
    VEHICLE_DRIVING_ASSIST = ("驾驶辅助", "text")
    VEHICLE_ITEM = ("车辆", "text")
    VEHICLE_RENO_ASSISTANT = ("Reno Assistant", "text")
    VEHICLE_SETTINGS = ("设置", "text")

    # ==================== 音乐源页面（Smoke_Test_7 步骤2 final_assertions: by=text） ====================
    MUSIC_BLUETOOTH_AUDIO = ("蓝牙音频", "text")
    MUSIC_GOOGLE_NEWS = ("Google 新闻", "text")
    MUSIC_USB = ("USB", "text")

    # ==================== 电话连接页面（Smoke_Test_7 步骤3 final_assertions） ====================
    PHONE_CONNECT_HINT = ("要完成通话，请先通过蓝牙将您的手机连接到汽车。", "text")
    PHONE_CONNECT_BLUETOOTH = ("连接到蓝牙", "text")

    # ==================== 窗口小部件编辑界面（Smoke_Test_7__row6: 右滑打开） ====================

    # 窗口小部件编辑窗口标题（final_assertions: by=text，右滑后右侧出现）
    WIDGET_EDIT_TITLE = ("编辑窗口部件", "text")

    # 下方小部件选项（final_assertions: by=text）
    WIDGET_EDIT_GOOGLE_ASSISTANT = ("Google 助理", "text")
    WIDGET_EDIT_DATE_TIME = ("日期和时间", "text")
    WIDGET_EDIT_GG_IMAGE = ("GG图", "text")
    WIDGET_EDIT_ECO_SCORE = ("Eco Score", "text")
    WIDGET_EDIT_PHONE = ("电话", "text")
    WIDGET_EDIT_AUDIO = ("音频", "text")

    # 编辑界面 overlay 层（replay_timeline: car.ensure_click by=id，步骤0 第二次右滑后先点击该层再选小部件）
    WIDGET_EDIT_OVERLAY = ("com.renault.car.launcher:id/overlay", "id")

    # ==================== 日期和时间小部件生命周期（Smoke_Test_10: 添加首页 / 移除） ====================

    # 日期和时间小部件容器（final_assertions: by=id，添加后存在于首页，更换小部件后移除）
    DATETIME_CONTAINER = ("com.renault.car.launcher:id/datetime_container", "id")

    # 窗口小部件编辑界面关闭按钮（replay_timeline: car.ensure_click by=id，退出编辑界面）
    WIDGET_EDIT_CLOSE_BUTTON = ("com.renault.car.launcher:id/close_button", "id")

    # 日期和时间小部件显示的日期文案（final_assertions: by=text，添加后首页显示数据；
    # 具体日期随车机当前日期变化，属可变内容，改用年份片段 textContains 验证稳定完成态）
    DATETIME_DATE_TEXT = ("2026", "textContains")

    # ==================== 电话小部件与电话设置页面（Smoke_Test_15: 点击电话小部件进入设置） ====================

    # 首页电话小部件容器（replay_timeline: car.ensure_click by=id，步骤1 点击进入电话设置页面）
    PHONE_CONTAINER = ("com.renault.car.launcher:id/phone_container", "id")

    # 电话设置页面蓝牙入口（final_assertions: by=text，进入电话设置页面后存在）
    PHONE_SETTINGS_BLUETOOTH = ("蓝牙", "text")

    # --- END ---

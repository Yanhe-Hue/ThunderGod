# -*- coding: utf-8 -*-
"""页面类模板 v8.4 — POM 页面层。"""

from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


class 桌面启动器Page:
    """桌面启动器Page 页面"""

    def __init__(self, car, at=None):
        self.car = car
        self.at = at

    def _exists(self, loc, timeout=0):
        """car.exists() 返回 MethodResult（透明化: 可直接 if 判断）。"""
        return self.car.exists(loc, timeout=timeout)

    def go_home(self):
        """回到主页面（replay_timeline: car.press key='home'）"""
        self.car.press("home")

    def add_google_assistant_widget(self):
        """步骤1：点击编辑界面 Google 助理小部件添加至主页面，点击关闭按钮退出编辑界面（replay_timeline: ensure_click Google 助理 → close_button）"""
        self.car.ensure_click(Loc.WIDGET_EDIT_GOOGLE_ASSISTANT, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_google_assistant(self):
        """步骤1：点击主界面谷歌助手区域（replay_timeline 按序：助手建议区 → 两次 Google 助理）"""
        
        self.car.ensure_click(Loc.GOOGLE_ASSISTANT, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        

    def replace_google_assistant_with_datetime(self):
        """步骤3：返回主页面，右滑打开编辑界面，点击日期和时间小部件替换 Google 助理，点击关闭按钮退出（replay_timeline: press back → swipe → ensure_click 日期和时间 → close_button）"""
        self.car.press("back")
        self.swipe_open_widget_editor()
        self.car.ensure_click(Loc.WIDGET_EDIT_DATE_TIME, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_maps_search_box(self):
        """步骤1：点击谷歌地图搜索栏（replay_timeline 按序两次点击同一搜索栏，触发搜索下拉菜单）"""
        self.car.ensure_click(Loc.MAPS_SEARCH_BOX, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        

    def click_keyboard_search_edit(self):
        """步骤2：再次点击搜索栏（键盘搜索输入框，唤起屏幕键盘）"""
        self.car.ensure_click(Loc.MAPS_KEYBOARD_SEARCH_EDIT, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_nav_app(self):
        """步骤0：点击左侧导航栏应用图标（replay_timeline: car.ensure_click by=id）"""
        self.car.ensure_click(Loc.NAV_APP, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_nav_vehicle(self):
        """步骤1/步骤3回切：点击左侧导航栏车辆图标（replay_timeline: car.ensure_click by=id）"""
        self.car.ensure_click(Loc.NAV_VEHICLE, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_nav_music(self):
        """步骤2：点击左侧导航栏音乐图标（replay_timeline: car.ensure_click by=id）"""
        self.car.ensure_click(Loc.NAV_MUSIC, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_nav_phone(self):
        """步骤3：点击左侧导航栏电话图标（replay_timeline: car.ensure_click by=id）"""
        self.car.ensure_click(Loc.NAV_PHONE, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def swipe_open_widget_editor(self):
        """步骤0/步骤2：从屏幕右侧向左滑动，打开窗口小部件编辑界面（replay_timeline: car.swipe 精确路径 [[1270,360],[300,360]]）"""
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, auto_wait=True)

    def add_datetime_widget(self):
        """步骤1：点击日期和时间小部件添加至首页，点击关闭按钮退出编辑界面（replay_timeline: ensure_click 日期和时间 → close_button）"""
        self.car.ensure_click(Loc.WIDGET_EDIT_DATE_TIME, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_datetime_widget(self):
        """步骤1：点击主界面上的日期和时间小部件进入设置页面（replay_timeline: car.click_position (1075, 479)）"""
        self.car.click_position(1075, 479)

    def click_audio_widget(self):
        """步骤1：点击主界面上的"音频"小部件进入设置页面（replay_timeline: car.ensure_click 音频 by=text）"""
        self.car.ensure_click(Loc.AUDIO_AREA, by="text", max_scrolls=10, scroll_direction="up", fingers=1)

    def replace_datetime_with_gg_image(self):
        """步骤2：点击 GG图 小部件替换日期和时间小部件，点击关闭按钮退出编辑界面（replay_timeline: ensure_click GG图 → close_button）"""
        self.car.ensure_click(Loc.WIDGET_EDIT_GG_IMAGE, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def remove_audio_widget(self):
        """步骤0：右滑打开编辑界面 → 点击 GG图 更换音频小部件 → 关闭；再次右滑 → 点击 overlay → 点击 日期和时间 更换 → 关闭（replay_timeline execution_index 0-6 顺序，音频小部件最终从首页移除）"""
        self.swipe_open_widget_editor()
        self.car.ensure_click(Loc.WIDGET_EDIT_GG_IMAGE, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        self.swipe_open_widget_editor()
        self.car.ensure_click(Loc.WIDGET_EDIT_OVERLAY, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_DATE_TIME, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def add_audio_widget(self):
        """步骤1：右滑打开编辑界面 → 点击 音频 小部件添加至主页面 → 点击关闭按钮退出编辑界面（replay_timeline execution_index 8-10 顺序）"""
        self.swipe_open_widget_editor()
        self.car.ensure_click(Loc.WIDGET_EDIT_AUDIO, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def add_phone_widget(self):
        """步骤1：点击编辑界面 电话 小部件添加至主页面，点击关闭按钮退出编辑界面（replay_timeline: ensure_click 电话 → close_button）"""
        self.car.ensure_click(Loc.WIDGET_EDIT_PHONE, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_phone_widget(self):
        """步骤1：点击主界面上的\"电话\"小部件进入电话设置页面（replay_timeline: car.ensure_click phone_container by=id）"""
        self.car.ensure_click(Loc.PHONE_CONTAINER, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def replace_phone_widget_with_others(self):
        """步骤2：右滑打开编辑界面 → 点击 日期和时间 更换 → 关闭；再次右滑 → 点击 GG图 更换 → 关闭（replay_timeline exec 4-9 顺序，电话 小部件最终从首页移除）"""
        self.swipe_open_widget_editor()
        self.car.ensure_click(Loc.WIDGET_EDIT_DATE_TIME, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        self.swipe_open_widget_editor()
        self.car.ensure_click(Loc.WIDGET_EDIT_GG_IMAGE, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def swipe_continue_widget_editor(self):
        """延续右向左滑动序列（replay_timeline 后续 ok:true swipe 动作，保持窗口小部件编辑界面时序）"""
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, auto_wait=True)
        self.car.swipe(direction=None, locator=((1230, 350), (900, 350)), duration=0.3, auto_wait=True)
        self.car.swipe(direction=None, locator=((1250, 300), (860, 300)), duration=0.3, auto_wait=True)

    def add_vehicle_widget(self):
        """步骤1：右滑打开编辑界面 → 上滑滚动 → 点击“车辆”小部件添加至主页面 → 点击关闭按钮退出编辑界面（replay_timeline exec 1-4 顺序）"""
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, auto_wait=True, fingers=1)
        self.car.swipe(direction=None, locator=((1100, 550), (1100, 300)), duration=0.3, auto_wait=True, fingers=1)
        self.car.ensure_click(Loc.VEHICLE_ITEM, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_vehicle_settings(self):
        """步骤2：点击主页面“车辆”进入车辆设置界面（replay_timeline exec 7：编辑界面已在步骤1退出，主页面无残留编辑器，无需再点 close_button）"""
        self.car.ensure_click(Loc.VEHICLE_ITEM, by="text", max_scrolls=10, scroll_direction="up", fingers=1)

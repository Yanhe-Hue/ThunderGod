# -*- coding: utf-8 -*-
"""页面类模板 v8.4 — POM 页面层。"""

from page_objects.locators.车辆设置.车辆设置_locators import Loc


class 车辆设置Page:
    """车辆设置Page 页面"""

    def __init__(self, car, at=None):
        self.car = car
        self.at = at

    def _exists(self, loc, timeout=0):
        """car.exists() 返回 MethodResult（透明化: 可直接 if 判断）。"""
        return self.car.exists(loc, timeout=timeout)

    def navigate_to_network_internet(self):
        """步骤1：进入左侧导航栏\"车辆\">\"设置\">\"网络互联网\""""
        self.car.click_position(159, 164)
        self.car.ensure_click(Loc.BTN_CLOSE, by="desc")
        self.car.click_position(56, 103)
        self.car.click_position(1242, 409)
        self.car.ensure_click(Loc.BTN_BACK, by="desc")
        self.car.click_position(56, 568)
        self.car.ensure_click(Loc.ENTRY_SETTINGS, by="text")
        self.car.ensure_click(Loc.ENTRY_NETWORK_INTERNET, by="text")

    def open_wlan_preferences(self):
        """步骤2：滑动到界面底部，点击\"Wi-Fi偏好设置\""""
        self.car.scroll_to_element(Loc.ENTRY_WLAN_PREFERENCES, by="text")
        self.car.ensure_click(Loc.ENTRY_WLAN_PREFERENCES, by="text")

    def navigate_to_parking_assist(self):
        """步骤1：导航到车辆 > 驾驶辅助 > 停车"""
        self.car.ensure_click(Loc.ENTRY_DRIVE_ASSIST, by="text")
        self.car.ensure_click(Loc.ENTRY_PARKING, by="text")

    def toggle_parking_options(self):
        """步骤2：切换"前面"、"侧面"、"后交叉停车警报"、"后主动紧急制动"和"乘员安全出"5个选项的开/关"""
        self.car.ensure_click(Loc.TOGGLE_FRONT, by="id")
        self.car.ensure_click(Loc.TOGGLE_SIDE, by="id")
        self.car.ensure_click(Loc.TOGGLE_RCTA, by="id")
        self.car.ensure_click(Loc.TOGGLE_RAEB, by="id")
        self.car.ensure_click(Loc.TOGGLE_OSE, by="id")

    def navigate_to_system_page(self):
        """Smoke_Test_37 前置：打开 设置>系统（回放已验证入口 grid_nav→应用菜单→设置，滚动定位 系统）"""
        self.car.press(key="home")
        self.car.ensure_click(Loc.GRID_NAV, by="id")
        self.car.ensure_click(Loc.ENTRY_SETTINGS, by="text")
        self.car.scroll_to_element(Loc.ENTRY_SYSTEM, by="text")
        self.car.ensure_click(Loc.ENTRY_SYSTEM, by="text")

    def swipe_up_system_page(self):
        """Smoke_Test_37 步骤0：系统设置页向上滑动（回放 idx19，首屏→次屏）"""
        self.car.swipe(direction="up", scale=0.8, fingers=1)

    def swipe_down_system_page(self):
        """Smoke_Test_37 步骤0：系统设置页向下滑动（回放 idx22，次屏→首屏）"""
        self.car.swipe(direction="down", scale=0.8, fingers=1)

    def open_language_and_input(self):
        """Smoke_Test_37 步骤0：点击\"语言和输入法\"进入语言和输入法设置（回放 idx23）"""
        self.car.ensure_click(Loc.ENTRY_LANGUAGE_INPUT, by="text")

    def open_language(self):
        """Smoke_Test_37 步骤1：点击\"语言\"（回放 idx24）"""
        self.car.ensure_click(Loc.ENTRY_LANGUAGE, by="text")

    def swipe_language_list(self):
        """Smoke_Test_37 步骤1：语言列表向上滑动（回放 idx30/34/37/40/44/47/52/55）"""
        self.car.swipe(direction="up", scale=0.8, fingers=1)

    def assert_language_item(self, loc, text):
        """Smoke_Test_37 步骤1：语言项滚动进可视区后断言（scroll_to_element 兜底，避免固定滑动距离的波动）"""
        self.car.scroll_to_element(loc, by="text")
        self.car.assert_text(loc, text)

    def enter_vehicle_page(self):
        """步骤1：点击左侧导航栏车辆图标进入车辆页面（回放 idx0）"""
        self.car.ensure_click(Loc.HOME_CAR_WORLD, by="id")

    def enter_seat_page(self):
        """步骤2：点击\"座位\"进入座椅页面（回放 idx1）"""
        self.car.ensure_click(Loc.ENTRY_SEAT, by="text")

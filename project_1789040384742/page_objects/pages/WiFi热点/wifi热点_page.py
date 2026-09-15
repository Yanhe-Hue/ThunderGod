# -*- coding: utf-8 -*-
"""页面类模板 v8.4 — POM 页面层。"""

from page_objects.locators.WiFi热点.wifi热点_locators import Loc


class Wifi热点Page:
    """Wifi热点Page 页面"""

    def __init__(self, car, at=None):
        self.car = car
        self.at = at

    def _exists(self, loc, timeout=0):
        """car.exists() 返回 MethodResult（透明化: 可直接 if 判断）。"""
        return self.car.exists(loc, timeout=timeout)

    def wifi_interface_visible(self):
        """步骤0：查看 WiFi 界面功能项（回放 exec5 swipe up → exec6 scroll_to_element "App data usage"）

        注：explored exec4 的 Back 是从更深页面弹回 WiFi 页；open_network_and_internet()
        已直接落在 WiFi 页（深度 1），此处再点 Back 会弹出 WiFi 页回到设置首页，
        导致 'App data usage' 不可见，故不执行 Back。
        """
        self.car.swipe(direction="up", scale=0.5, duration=0.5, auto_wait=False)
        self.car.scroll_to_element(Loc.TXT_APP_DATA_USAGE, by="text", max_scrolls=10, scroll_direction="up")

    def scroll_to_wifi(self):
        """步骤1：滚动回页面顶部 Wi‑Fi（回放 exec11 scroll_to_element "Wi‑Fi"）"""
        self.car.scroll_to_element(Loc.TXT_WIFI, by="text", max_scrolls=10, scroll_direction="up")

    def open_network_and_internet(self):
        """前置/步骤1复验（第1次）：应用图标(grid_nav) > Settings > Network and internet（回放 exec16-18 已验证）"""
        self.car.ensure_click(Loc.GRID_NAV, by="id", max_scrolls=10, scroll_direction="up")
        self.car.ensure_click(Loc.ENTRY_SETTINGS, by="text", max_scrolls=10, scroll_direction="up")
        self.car.ensure_click(Loc.ENTRY_NETWORK_INTERNET, by="text", max_scrolls=10, scroll_direction="up")

    def go_home(self):
        """步骤1：返回主页面（回放 exec21 home 点击）"""
        self.car.ensure_click(Loc.BTN_HOME, by="id", max_scrolls=10, scroll_direction="up")

    def open_network_and_internet_again(self):
        """步骤1复验（第2次）：再次进入 Network and internet（回放 exec22-24 已验证）"""
        self.car.ensure_click(Loc.GRID_NAV, by="id", max_scrolls=10, scroll_direction="up")
        self.car.ensure_click(Loc.ENTRY_SETTINGS, by="text", max_scrolls=10, scroll_direction="up")
        self.car.ensure_click(Loc.ENTRY_NETWORK_INTERNET, by="text", max_scrolls=10, scroll_direction="up")

    def restore_home(self):
        """后置/恢复：车机恢复初始状态（回放 exec26 home 点击，postconditions[0] 已验证）"""
        self.car.ensure_click(Loc.BTN_HOME, by="id", max_scrolls=10, scroll_direction="up")

    def toggle_wifi(self):
        """点击 Wi‑Fi 开关（每次点击切换开/关；回放 exec4/exec10/exec13 ensure_click ok:true）"""
        self.car.ensure_click(Loc.WIFI_TOGGLE_SWITCH, by="desc", max_scrolls=10, scroll_direction="up")

    def wifi_switch_is_on(self):
        """探测 WiFi 开关当前是否处于开启（checked=true）。

        设备初始 WiFi 开关状态会保留上一轮运行现场（后置仅 home 回主屏，不复位开关），
        故步骤需按实际开关状态决定是否再点。assert_attr 校验不符时抛 AssertionError，
        此处用于探测当前 checked 状态。
        """
        try:
            self.car.assert_attr(Loc.SWITCH_WIDGET, attr="checked", expected=True, by="id")
            return True
        except AssertionError:
            return False

    def restore_initial_state(self):
        """后置/恢复：杀死所有进程，车机恢复初始状态（postconditions[0]：连续 home 点击 3 次回主页面，均 ok:true）"""
        self.car.ensure_click(Loc.BTN_HOME, by="id", max_scrolls=10, scroll_direction="up")
        self.car.ensure_click(Loc.BTN_HOME, by="id", max_scrolls=10, scroll_direction="up")
        self.car.ensure_click(Loc.BTN_HOME, by="id", max_scrolls=10, scroll_direction="up")

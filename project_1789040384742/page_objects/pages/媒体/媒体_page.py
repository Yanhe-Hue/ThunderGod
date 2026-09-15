# -*- coding: utf-8 -*-
"""媒体Page 页面类 — Smoke_Test_20 蓝牙电话连接与配对。"""

from page_objects.locators.媒体.媒体_locators import Loc


class 媒体Page:
    """媒体Page 页面"""

    def __init__(self, car, at=None):
        self.car = car
        self.at = at

    def _exists(self, loc, timeout=0):
        """car.exists() 返回 MethodResult（透明化: 可直接 if 判断）。"""
        return self.car.exists(loc, timeout=timeout)

    def open_phone_page(self):
        """点击底部导航栏 Phone 入口，打开电话连接页面。"""
        self.car.ensure_click(
            Loc.PHONE_NAV,
            by="id",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def click_connect_bluetooth(self):
        """点击 Connect to Bluetooth，进入 Settings-Bluetooth 页面。"""
        self.car.ensure_click(
            Loc.CONNECT_BLUETOOTH_BUTTON,
            by="id",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def click_pair_new_device(self):
        """点击 Pair new device，扫描新设备并刷新可用设备列表。"""
        self.car.ensure_click(
            Loc.PAIR_NEW_DEVICE,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def pair_device(self):
        """点击目标设备 62888b2b 开始配对；弹窗再次出现后依次点击 Pair / 配对 完成配对。

        回放顺序（全部 ok:true，按 execution_index 严格保留，不按 locator 去重）:
        62888b2b → 62888b2b → Pair → 62888b2b → Pair → 配对
        """
        self.car.ensure_click(
            Loc.BT_DEVICE_62888B2B,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )
        self.car.ensure_click(
            Loc.BT_DEVICE_62888B2B,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )
        self.car.ensure_click(
            Loc.PAIR_BUTTON,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )
        self.car.ensure_click(
            Loc.BT_DEVICE_62888B2B,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )
        self.car.ensure_click(
            Loc.PAIR_BUTTON,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )
        self.car.ensure_click(
            Loc.PAIR_BUTTON_CN,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def back_to_phone_page(self):
        """点击底部导航栏 Phone 入口，回到电话页面验证连接。"""
        self.car.ensure_click(
            Loc.PHONE_NAV,
            by="id",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def click_search_icon(self):
        """点击 Phone 页右上角搜索图标，打开搜索框（Smoke_Test_22 exec1 ok:true）。"""
        self.car.ensure_click(
            Loc.SEARCH_ICON,
            by="desc",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def input_search(self, text):
        """在搜索输入框输入搜索值（Smoke_Test_22 exec2 ok:true）。

        点击 Search 图标后搜索工具栏需要时间渲染出搜索框；
        car.input 无等待能力，先 wait 搜索框出现再输入。
        """
        self.car.wait(Loc.SEARCH_INPUT, by="id", timeout=10.0)
        self.car.input(
            Loc.SEARCH_INPUT,
            text,
            by="id",
            clear=True,
        )

    def close_search(self):
        """点击搜索框关闭按钮（Smoke_Test_22 exec4 ok:true）。"""
        self.car.ensure_click(
            Loc.SEARCH_CLOSE,
            by="id",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def click_back(self):
        """点击 Phone 页返回按钮（Smoke_Test_22 exec5 ok:true）。"""
        self.car.ensure_click(
            Loc.BACK_BUTTON,
            by="desc",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def open_device_manager(self):
        """点击右上角设备管理图标，进入设备管理器界面（Smoke_Test_22 exec6 ok:true）。"""
        self.car.ensure_click(
            Loc.DEVICE_MANAGER,
            by="id",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    # ==================== 电话页标签页（Smoke_Test_21 机械投影） ====================

    def click_contacts_tab(self):
        """点击 Contacts 标签，切换联系人标签页（Smoke_Test_21 timeline exec5 ok:true）。"""
        self.car.ensure_click(
            Loc.CONTACTS_TAB,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def click_contacts_list(self):
        """点击联系人列表入口“联系人”（desc），停留在联系人同步列表（Smoke_Test_21 timeline exec7 ok:true）。"""
        self.car.ensure_click(
            Loc.CONTACTS_TAB_CN,
            by="desc",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def click_favourites_tab(self):
        """点击 Favourites 标签，切换收藏标签页（Smoke_Test_21 timeline exec9 ok:true）。"""
        self.car.ensure_click(
            Loc.FAVOURITES_TAB,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

    def click_dial_pad_tab(self):
        """点击 Dial Pad 标签，切换拨号盘标签页（Smoke_Test_21 timeline exec11 ok:true）。"""
        self.car.ensure_click(
            Loc.DIAL_PAD_TAB,
            by="text",
            max_scrolls=10,
            scroll_direction="up",
            fingers=1,
        )

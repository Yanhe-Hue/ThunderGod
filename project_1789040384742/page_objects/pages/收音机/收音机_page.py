# -*- coding: utf-8 -*-
"""页面类模板 v8.4 — POM 页面层。"""

from page_objects.locators.收音机.收音机_locators import Loc


class 收音机Page:
    """收音机Page 页面"""

    def __init__(self, car, at=None):
        self.car = car
        self.at = at

    def _exists(self, loc, timeout=0):
        """car.exists() 返回 MethodResult（透明化: 可直接 if 判断）。"""
        return self.car.exists(loc, timeout=timeout)

    def open_music_am_radio(self):
        """点击左侧导航栏进入“音乐”页面，再点击“AM收音机”进入 AM 收音机界面"""
        self.car.ensure_click(Loc.MUSIC_NAV)
        self.car.ensure_click(Loc.AM_RADIO)

    def click_frequency_531khz(self):
        """步骤1：点击531kHz频率按钮"""
        self.car.ensure_click(Loc.FREQUENCY_TITLE)

    def tune_next_frequency(self):
        """步骤3：进入播放控制区并点击“下一曲”按钮调谐到新频率"""
        self.car.click_position(1229, 261)
        self.car.swipe(direction=None, locator=((696, 479), (696, 189)), duration=0.3, auto_wait=True)
        self.car.swipe(direction=None, locator=((404, 334), (988, 334)), duration=0.3, auto_wait=True)
        self.car.swipe(direction=None, locator=((696, 189), (696, 479)), duration=0.3, auto_wait=True)
        self.car.ensure_click(Loc.BROWSE_ITEM_CUSTOM_ACTION)
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)
        self.car.ensure_click(Loc.SKIP_NEXT)

    def navigate_to_feature(self):
        """导航到 feature 功能页面"""
        # self.car.ensure_click(Loc.TAB_XXX)
        # self.car.sleep(1)
        pass

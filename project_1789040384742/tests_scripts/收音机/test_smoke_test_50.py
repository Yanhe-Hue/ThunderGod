# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"01e2ba44774dfdfba5aeb1ef18ee5ff73ca9ee0a938d89265f616149b03ad21e","combined":"04e465eab61f91a470da613d6e1256f66f4f65de4cca8770166cc420c9fc69e0","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"9b9cc976982c923e4e64d89b412953e23039ff6eb3fadd4f02fad53750c538ba","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_text","click_position","ensure_click","exists","screenshot","sleep","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.收音机.收音机_page import 收音机Page
from page_objects.locators.收音机.收音机_locators import Loc


@allure.epic("媒体 - AM收音机 - 下一电台")
@allure.feature("收音机")
class TestSmokeTest50:
    """媒体 - AM收音机 - 下一电台 / smoke_test_50 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 收音机Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_50", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：进入“Music”页面 → 点击“AM Radio” → 点击频率进入播放界面；步骤1：AM Radio 正在播放
        self.page.enter_am_radio_playback()
        yield
        # AUTOCAR-POSTCONDITIONS: 原始要求“杀死所有进程，车机恢复初始状态”（Explore 未提供恢复动作，保留外部还原）
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("媒体 - AM收音机 - 下一电台")
    @allure.title("媒体 - AM收音机 - 下一电台")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_50(self):
        """前置: 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“AM Radio”进入页面后点击右下角频率，进入播放界面; 步骤1：”AM Radio“正在播放 | 步骤: ['步骤1：点击播放页面上的下一个按钮'] | 预期: 步骤1：电台应切换到下一电台（这个验证需要等待一方分钟）"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 点击播放页面上的下一个按钮"):
            self.page.click_skip_next()

        # AUTOCAR-EXPECTED[0]: 步骤1：电台应切换到下一电台（这个验证需要等待一方分钟）
        with allure.step("验证[0]: 步骤1：电台应切换到下一电台（这个验证需要等待一方分钟）"):
            # 电台切换约需一分钟，等待切换完成后再验证新频率
            self.car.sleep(60)
            self.car.assert_text(Loc.FREQUENCY_1602KHZ, "1602 kHz")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

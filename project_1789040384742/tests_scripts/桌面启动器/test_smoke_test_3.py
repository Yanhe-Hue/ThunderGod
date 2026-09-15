# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"3f261992c793dfdae359b6898854eec5c803d29422de8eee9e7bf8228e23e6a5","combined":"a61c870bd6b43faa547d4e34409252797a26d1735ab34f21cc7ba3e82fe35981","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"60e21475c9316002dda706dccc687e4c9c56204e3229a5f54e53ed580e9b4451","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 燃油车首页")
@allure.feature("桌面启动器")
class TestSmokeTest3:
    """系统UI - 燃油车首页 / smoke_test_3 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_3", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：车机正常启动，处于主页面
        # 车机正常启动为外部硬件前置（设备在线，car 已连接），无可执行来源，保留外部前置注释；
        # 处于主页面由用例步骤 car.press('home')（replay_timeline ok:true）建立。
        pass
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无显式 postconditions
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 燃油车首页")
    @allure.title("系统UI - 燃油车首页")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_3(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤1：检查首页'] | 预期: 步骤1：显示Google地图、音频、Google助手三个区域"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 检查首页"):
            # replay_timeline: car.press key='home'（回到主页面，随后校验三个区域）
            self.page.go_home()

        # AUTOCAR-EXPECTED[0]: 步骤1：显示Google地图、音频、Google助手三个区域
        with allure.step("验证[0]: 步骤1：显示Google地图、音频、Google助手三个区域"):
            # final_assertions（ok:true，均在 press home 所在主页面校验）
            self.car.assert_exists(Loc.MAPS_ZOOM_IN, by="id", expected=True, msg="首页应显示 Google 地图区域")
            self.car.assert_exists(Loc.AUDIO_AREA, by="text", expected=True, msg="首页应显示音频区域")
            self.car.assert_exists(Loc.GOOGLE_ASSISTANT, by="text", expected=True, msg="首页应显示 Google 助手区域")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"253908d4375cfd364845cc508d2bec5e7805ea46d4ea6c531db7c9c2ef6d1363","combined":"0d2d553ee8c276c28d88a442460b58ba33e76e2ddeac7d18fa11f58f7afcefa1","dependencies":"074ab0997d9958f5a5a932089c2112dc8b86dfc07db5f14abaa6838c8249a3a2","sdk":"60e21475c9316002dda706dccc687e4c9c56204e3229a5f54e53ed580e9b4451","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 音频小部件显示与移除")
@allure.feature("桌面启动器")
class TestSmokeTest12:
    """系统UI - 音频小部件显示与移除 / smoke_test_12 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_12", create=True))
        # AUTOCAR-PRECONDITIONS: 前置“步骤0：车机正常启动，处于主页面”——模块 reset_environment（function 级 autouse）
        # 已在每个测试前 _go_home_devices（stop_app + go_home）回到桌面；car 已连接且处于主页面，无需额外动作，
        # 与同模块 Smoke_Test_10 对相同前置的处理一致。
        pass
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无显式 postconditions。
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 音频小部件显示与移除")
    @allure.title("系统UI - 音频小部件显示与移除")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_12(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤0：从屏幕右侧向左滑动，打开窗口小部件编辑界面，将“音频”小部件更换成其他小部件，退出编辑界面并检查', '步骤1：从屏幕右侧向左滑动，打开窗口小部件编辑界面，点击“音频”小部件将它添加在屏幕中，退出编辑界面并检查'] | 预期: 步骤0：“音频”小部件从主页面移除; 步骤1：“音频”小部件添加到主页面"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤0: 将“音频”小部件更换成其他小部件，退出编辑界面"):
            self.page.remove_audio_widget()

        # AUTOCAR-EXPECTED[0]: 步骤0：“音频”小部件从主页面移除
        with allure.step("验证[0]: 步骤0：“音频”小部件从主页面移除"):
            self.car.assert_exists(Loc.AUDIO_AREA, by="text", expected=False, timeout=5.0)

        with allure.step("步骤1: 点击“音频”小部件添加至屏幕，退出编辑界面"):
            self.page.add_audio_widget()

        # AUTOCAR-EXPECTED[1]: 步骤1：“音频”小部件添加到主页面
        with allure.step("验证[1]: 步骤1：“音频”小部件添加到主页面"):
            self.car.assert_exists(Loc.AUDIO_AREA, by="text", expected=True, timeout=5.0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

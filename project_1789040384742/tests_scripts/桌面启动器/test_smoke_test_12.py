# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"31721aaccfc35530b8533bdec739bd01df1d15550d77d3be628d93827ff83d04","combined":"36ddd51f5ec0c44c491d530ab17bb148a8f0678065b1a82f5c73371843756731","dependencies":"074ab0997d9958f5a5a932089c2112dc8b86dfc07db5f14abaa6838c8249a3a2","sdk":"fc1aa99236362117709299e948385dacfb72ba87273548530ccc00e92f076a88","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","click_position","ensure_click","exists","press","screenshot","swipe"]},"version":2}

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

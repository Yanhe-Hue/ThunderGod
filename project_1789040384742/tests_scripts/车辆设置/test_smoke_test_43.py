# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"6cdab13ef399a87c08188a3819dba68c3319ab0467595478ff2f7f09ee4e3d24","combined":"ae2ebdc8f4b8082b16a46e4c38f40bdc6aeb865ea0cfc71fe6e3859c01b4bc0e","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"dbd5e9d894015605d506d109c8d8a87ccf350abea99ae61885e44b137f89c647","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe","wait"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("能源/驾驶 - 驾驶辅助 - 舒适")
@allure.feature("车辆设置")
class TestSmokeTest43:
    """能源/驾驶 - 驾驶辅助 - 舒适 / smoke_test_43 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_43", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：开机，adb正常连接（设备在线，car 已连接）
        pass
        yield
        # AUTOCAR-POSTCONDITIONS: 步骤0：杀死所有进程，车机恢复初始状态
        self.car.press(key="home")

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("能源/驾驶 - 驾驶辅助 - 舒适")
    @allure.title("能源/驾驶 - 驾驶辅助 - 舒适")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_43(self):
        """前置: 步骤0：开机，adb正常连接 | 步骤: ['步骤1：点击左侧导航栏 \"Vehicle\" > Driving assistance > Comfort', '步骤2：开启/关闭\"Following distance\", \"Display risky areas\", \"Adaptive speed limiter and cruise control\"3个选项'] | 预期: 步骤1：页面显示\"Eco predictive assistant\", \"Following distance\", \"Display risky areas\", \"Adaptive speed limiter and cruise control\" 和 \"To road context\"; 步骤2：3个选项成功开启/关闭，动画成功显示"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 点击左侧导航栏 Vehicle > Driving assistance > Comfort"):
            self.page.navigate_to_comfort()

        # AUTOCAR-EXPECTED[0]: 步骤1：页面显示"Eco predictive assistant", "Following distance", "Display risky areas", "Adaptive speed limiter and cruise control" 和 "To road context"
        with allure.step("验证[0]: 页面显示 Following distance / Display risky areas / Adaptive speed limiter and cruise control / Eco predictive assistant"):
            self.car.assert_text(Loc.TXT_FOLLOWING_DISTANCE, "Following distance", by="text")
            self.car.assert_text(Loc.TXT_DISPLAY_RISKY_AREAS, "Display risky areas", by="text")
            self.car.assert_text(Loc.TXT_ADAPTIVE_SPEED_LIMITER, "Adaptive speed limiter and cruise control", by="text")
            self.car.assert_text(Loc.TXT_ECO_PREDICTIVE_ASSISTANT, "Eco predictive assistant *", by="text")

        with allure.step("步骤2: 滑动 Comfort 页面露出下方选项"):
            self.page.swipe_comfort_page()

        with allure.step("验证[0]: 页面显示 To road context"):
            self.car.assert_text(Loc.TXT_TO_ROAD_CONTEXT, "To road context", by="text")

        with allure.step("步骤2: 开启/关闭 Following distance / Display risky areas / Adaptive speed limiter and cruise control 3个选项"):
            before = self.page.toggle_comfort_options()

        # AUTOCAR-EXPECTED[1]: 步骤2：3个选项成功开启/关闭，动画成功显示
        with allure.step("验证[1]: 3 个选项开关状态断言（开启/关闭成功，动画由开关状态切换体现）"):
            self.page.assert_comfort_options_flipped(before)

        with allure.step("步骤2: 返回主页面"):
            self.car.press(key="home")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

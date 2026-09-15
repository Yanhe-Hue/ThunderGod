# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"e8f351e4f398d3188c4afc61c223ac8a1e1cefbf31d79c755c9de420afa0aa45","combined":"6a861644ef321a602d9ec3c67b1e931c913997d1acfc9eaae744ad5430e5bc55","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"36e17d77316a88df4bccfebcc8267241fc74792f12c0564c0ea9a721fc503b31","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_ocr","assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe","wait"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("能源/驾驶 - 我的驾驶")
@allure.feature("车辆设置")
class TestSmokeTest41:
    """能源/驾驶 - 我的驾驶 / smoke_test_41 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_41", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：开机，adb正常连接（设备在线/已连接，car 已连接；开机为环境硬件前置，无独立控制/读回证据）
        pass
        yield
        # AUTOCAR-POSTCONDITIONS: 杀死所有进程，车机恢复初始状态（回主页收尾还原）
        self.page.restore_initial_state()

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("能源/驾驶 - 我的驾驶")
    @allure.title("能源/驾驶 - 我的驾驶")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_41(self):
        """前置: 步骤0：开机，adb正常连接 | 步骤: ['步骤1：点击左侧栏的 \"Vehicle\"', '步骤2：点击\"My Driving\"', '步骤3：点击\"Energy\"', '步骤4：点击\"Since reset\"', '步骤5：点击“\"Reset\"出现弹窗后再次点击\"Reset\"'] | 预期: 步骤1：页面显示 \"Drive Mode\", \"My Driving\", \"Driving assistance\", \"Vehicle\", \"Settings\"; 步骤2：显示 \"Eco Score\", \"energy consumption value\", and \"Energy\", and \"Since start\", \"Since reset\"按钮; 步骤3：系统导航到 Energy Detail页面; 步骤4：右侧显示\"Reset\"按钮; 步骤5：重置功能生效"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 点击左侧栏的 \"Vehicle\""):
            self.page.enter_vehicle_page()

        # AUTOCAR-EXPECTED[0]: 步骤1：页面显示 "Drive Mode", "My Driving", "Driving assistance", "Vehicle", "Settings"
        with allure.step("验证[0]: 步骤1：页面显示 \"Drive Mode\", \"My Driving\", \"Driving assistance\", \"Vehicle\", \"Settings\""):
            self.car.assert_exists(Loc.TXT_DRIVE_MODE, by="text", expected=True)
            self.car.assert_exists(Loc.ENTRY_MY_DRIVING, by="text", expected=True)
            self.car.assert_exists(Loc.TXT_DRIVING_ASSISTANCE, by="text", expected=True)
            self.car.assert_exists(Loc.TXT_VEHICLE, by="text", expected=True)
            self.car.assert_exists(Loc.TXT_SETTINGS, by="text", expected=True)

        with allure.step("步骤2: 点击\"My Driving\""):
            self.page.enter_my_driving()

        # AUTOCAR-EXPECTED[1]: 步骤2：显示 "Eco Score", "energy consumption value", and "Energy", and "Since start", "Since reset"按钮
        with allure.step("验证[1]: 步骤2：显示 \"Eco Score\", \"energy consumption value\", and \"Energy\", and \"Since start\", \"Since reset\"按钮"):
            self.car.assert_text(Loc.TXT_ECO_SCORE, "Eco")
            self.car.assert_text(Loc.ENTRY_ENERGY, "Energy")
            self.car.assert_text(Loc.BTN_SINCE_START, "Since start")
            self.car.assert_text(Loc.BTN_SINCE_RESET, "Since reset")
            self.car.assert_ocr("km", match_mode="contains")

        with allure.step("步骤3: 点击\"Energy\""):
            self.page.open_energy_detail()

        # AUTOCAR-EXPECTED[2]: 步骤3：系统导航到 Energy Detail页面
        with allure.step("验证[2]: 步骤3：系统导航到 Energy Detail页面"):
            self.car.assert_text(Loc.TXT_ENERGY_CONSUMPTION, "Energy consumption")

        with allure.step("步骤4: 点击\"Since reset\""):
            self.page.select_since_reset()

        # AUTOCAR-EXPECTED[3]: 步骤4：右侧显示"Reset"按钮
        with allure.step("验证[3]: 步骤4：右侧显示\"Reset\"按钮"):
            self.car.assert_exists(Loc.BTN_RESET, by="text", expected=True)

        with allure.step("步骤5: 点击\"Reset\"出现弹窗后再次点击\"Reset\""):
            self.page.reset_consumption()

        # AUTOCAR-EXPECTED[4]: 步骤5：重置功能生效
        with allure.step("验证[4]: 步骤5：重置功能生效"):
            self.car.assert_text(Loc.TXT_CONSUMPTION, "Consumption")
            self.car.assert_ocr("km", match_mode="contains")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

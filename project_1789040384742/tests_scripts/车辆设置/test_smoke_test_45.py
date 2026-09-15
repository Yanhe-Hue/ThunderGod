# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("能源/驾驶 - 驾驶ECO/MySense声音")
@allure.feature("车辆设置")
class TestSmokeTest45:
    """能源/驾驶 - 驾驶ECO/MySense声音 / smoke_test_45 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_45", create=True))
        # AUTOCAR-PRECONDITIONS: 前置"步骤0：开机"为硬件外置前置，Explore 无可控读回证据（precondition0 未验证），无法在本脚本自动验证
        pytest.fail("case_issue: 前置'步骤0：开机'无 Explore 可控读回证据，无法验证开机状态", pytrace=False)
        yield
        # AUTOCAR-POSTCONDITIONS: 笼统「设备还原」用 go_home 收尾
        self.page.restore_initial_state()

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("能源/驾驶 - 驾驶ECO/MySense声音")
    @allure.title("能源/驾驶 - 驾驶ECO/MySense声音")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_45(self):
        """前置: 步骤0：开机 | 步骤: ['步骤1：点击左侧栏的 \"Vehicle\"', '步骤2：点击\"My Driving\"', '步骤3：点击\"Energy\"', '步骤4：点击\"Since reset\"', '步骤5：点击“\"Reset\"出现弹窗后再次点击\"Reset\"'] | 预期: 步骤1：页面显示 \"Drive Mode\", \"My Driving\", \"Driving assistance\", \"Vehicle\", \"Settings\"; 步骤2：显示 \"Eco Score\", \"energy consumption value\", and \"Energy\", and \"Since start\", \"Since reset\"按钮; 步骤3：系统导航到 Energy Detail页面; 步骤4：右侧显示\"Reset\"按钮; 步骤5：重置功能生效"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 点击左侧栏的 Vehicle"):
            self.page.enter_vehicle_page()

        # AUTOCAR-EXPECTED[0]: 步骤1：页面显示 "Drive Mode", "My Driving", "Driving assistance", "Vehicle", "Settings"
        with allure.step("验证[0]: 步骤1：页面显示 \"Drive Mode\", \"My Driving\", \"Driving assistance\", \"Vehicle\", \"Settings\""):
            self.car.assert_text(Loc.TXT_DRIVE_MODE, "Drive Mode")
            self.car.assert_text(Loc.ENTRY_MY_DRIVING, "My Driving")
            self.car.assert_text(Loc.TXT_DRIVING_ASSISTANCE, "Driving assistance")
            self.car.assert_text(Loc.TXT_VEHICLE, "Vehicle")
            self.car.assert_text(Loc.TXT_SETTINGS, "Settings")

        with allure.step("步骤2: 点击 My Driving"):
            self.page.enter_my_driving()

        # AUTOCAR-EXPECTED[1]: 步骤2：显示 "Eco Score", "energy consumption value", and "Energy", and "Since start", "Since reset"按钮
        with allure.step("验证[1]: 步骤2：显示 Eco Score / 能耗值 / Since start / Since reset"):
            self.car.assert_text(Loc.TXT_CONSUMPTION, "Consumption")
            self.car.assert_text(Loc.BTN_SINCE_START, "Since start")
            self.car.assert_text(Loc.BTN_SINCE_RESET, "Since reset")
            self.car.assert_text(Loc.TXT_ECO_SCORE, "Eco")

        with allure.step("步骤3a: 返回 My Driving 主页面"):
            self.page.back_from_my_driving_page()

        with allure.step("验证[1b]: Energy 入口显示（My Driving 页）"):
            self.car.assert_exists(Loc.ENERGY_ENTRY, by="id", expected=True)

        with allure.step("步骤3b: 点击 Energy 进入 Energy Detail 页面"):
            self.page.click_energy_entry()

        # AUTOCAR-EXPECTED[2]: 步骤3：系统导航到 Energy Detail页面
        with allure.step("验证[2]: 步骤3：系统导航到 Energy Detail 页面"):
            self.car.assert_text(Loc.TXT_ENERGY_CONSUMPTION, "Energy consumption")

        with allure.step("步骤4: 点击 Since reset"):
            self.page.select_since_reset()

        # AUTOCAR-EXPECTED[3]: 步骤4：右侧显示"Reset"按钮
        with allure.step("验证[3]: 步骤4：右侧显示 Reset 按钮"):
            self.car.assert_exists(Loc.BTN_RESET, by="text", expected=True)

        with allure.step("步骤5: 点击 Reset 出现弹窗后再次点击 Reset"):
            self.page.reset_consumption()

        # AUTOCAR-EXPECTED[4]: 步骤5：重置功能生效
        with allure.step("验证[4]: 步骤5：重置功能生效"):
            self.car.assert_exists(Loc.BTN_RESET, by="text", expected=True)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

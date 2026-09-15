# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("驾驶辅助 - 界面与开关验证")
@allure.feature("车辆设置")
class TestSmokeTest42:
    """驾驶辅助 - 界面与开关验证 / smoke_test_42 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_42", create=True))
        # AUTOCAR-PRECONDITIONS: Codegen 仅在 Explore 有具体前置动作时替换下一行。
        pass
        yield
        # AUTOCAR-POSTCONDITIONS: Codegen 仅在 Explore 有具体恢复动作时替换下一行。
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("驾驶辅助 - 界面与开关验证")
    @allure.title("驾驶辅助 - 界面与开关验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_42(self):
        """前置: 步骤0：开机，adb正常连接; 步骤1：点击左侧导航栏“Vehicle” 进入页面后选择“Driving Assistance” | 步骤: ['步骤0：检查Driving Assistance界面。', '步骤1：点击页面上方\"Safety\"，检查页面显示', '步骤2: 将“My Safety”下的按钮切换成“Perso”点击\"Configure My Safety Perso\"检查页面显示', '步骤3：点击\"Departure anticipation\"检查页面显示', '步骤4：返回上一级，点击\"Vibration\"检查页面显示', '步骤5：回到“Safety\"界面，点击\"Warning anticipation\"检查页面显示'] | 预期: 步骤0：页面上方显示\"Safety\", \"Comfort\", and \"Parking\" 页面; 步骤1：页面显示：\"My Safety\",\"Configure My Safety Perso\",\"Blind spot warning\",\"Active braking\"\"Warning anticipation\"; 步骤2: ：页面显示\"Departure anticipation\", \"Vibration\", \"Emergency lane departure prevention\", \"Driver monitoring alert\",; 步骤3：\"Early\", \"Standard\", \"Late\" are listed,选项，点击选项成功开启/关闭，动画正确显示; 步骤4：列出\"Low\", \"Medium\", \"High\"选项，点击选项成功开启/关闭，动画正确显示; 步骤5：列出\"Early\", \"Standard\", \"Late\" 选项，可选择3个按钮，点击选项成功开启/关闭，动画正确显示"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: xxx"):
            # self.page.navigate_to_xxx()
            pytest.fail("AUTOCAR_SCAFFOLD_UNFILLED: Codegen 未填充测试步骤", pytrace=False)

        # AUTOCAR-EXPECTED[0]: 步骤0：页面上方显示"Safety", "Comfort", and "Parking" 页面
        with allure.step("验证[0]: 步骤0：页面上方显示\"Safety\", \"Comfort\", and \"Parking\" 页面"):
            pytest.fail(
                "AUTOCAR_SCAFFOLD_UNFILLED: Codegen 未填充 expected[0] 最终业务断言",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[1]: 步骤1：页面显示："My Safety","Configure My Safety Perso","Blind spot warning","Active braking""Warning anticipation"
        with allure.step("验证[1]: 步骤1：页面显示：\"My Safety\",\"Configure My Safety Perso\",\"Blind spot warning\",\"Active braking\"\"Warning anticipation\""):
            pytest.fail(
                "AUTOCAR_SCAFFOLD_UNFILLED: Codegen 未填充 expected[1] 最终业务断言",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[2]: 步骤2: ：页面显示"Departure anticipation", "Vibration", "Emergency lane departure prevention", "Driver monitoring alert",
        with allure.step("验证[2]: 步骤2: ：页面显示\"Departure anticipation\", \"Vibration\", \"Emergency lane departure prevention\", \"Driver monitoring alert\","):
            pytest.fail(
                "AUTOCAR_SCAFFOLD_UNFILLED: Codegen 未填充 expected[2] 最终业务断言",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[3]: 步骤3："Early", "Standard", "Late" are listed,选项，点击选项成功开启/关闭，动画正确显示
        with allure.step("验证[3]: 步骤3：\"Early\", \"Standard\", \"Late\" are listed,选项，点击选项成功开启/关闭，动画正确显示"):
            pytest.fail(
                "AUTOCAR_SCAFFOLD_UNFILLED: Codegen 未填充 expected[3] 最终业务断言",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[4]: 步骤4：列出"Low", "Medium", "High"选项，点击选项成功开启/关闭，动画正确显示
        with allure.step("验证[4]: 步骤4：列出\"Low\", \"Medium\", \"High\"选项，点击选项成功开启/关闭，动画正确显示"):
            pytest.fail(
                "AUTOCAR_SCAFFOLD_UNFILLED: Codegen 未填充 expected[4] 最终业务断言",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[5]: 步骤5：列出"Early", "Standard", "Late" 选项，可选择3个按钮，点击选项成功开启/关闭，动画正确显示
        with allure.step("验证[5]: 步骤5：列出\"Early\", \"Standard\", \"Late\" 选项，可选择3个按钮，点击选项成功开启/关闭，动画正确显示"):
            pytest.fail(
                "AUTOCAR_SCAFFOLD_UNFILLED: Codegen 未填充 expected[5] 最终业务断言",
                pytrace=False,
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"c737283bac5183bf99aac840620e51d238d3323dc4a5e12ec9fe2f3b889671e9","combined":"8cb97fef619dde44065ff5a5d92bca9a03f096d2f44fee5859438751578c7555","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"dbd5e9d894015605d506d109c8d8a87ccf350abea99ae61885e44b137f89c647","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe","wait"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("车辆设置")
@allure.feature("车辆设置")
class TestSmokeTest44:
    """车辆设置 / smoke_test_44 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_44", create=True))
        # AUTOCAR-PRECONDITIONS
        # 前置：步骤0 车机正常启动，处于主页面 —— 回到主界面
        self.car.ensure_click(Loc.HOME_CAR_WORLD, by="id")
        yield
        # AUTOCAR-POSTCONDITIONS
        # 原始 case 无 postconditions，保持环境现状
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("车辆设置")
    @allure.title("车辆设置")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_44(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤1：导航到车辆 > 驾驶辅助 > 停车', '步骤2：切换\"前面\"、\"侧面\"、\"后交叉停车警报\"、\"后主动紧急制动\"和\"乘员安全出\"5个选项的开/关'] | 预期: 步骤1：页面显示\"前面\"、\"侧面\"、\"后交叉停车警报\"、\"后主动紧急制动\"和\"乘员安全出口\"; 步骤2：5个选项成功切换开/关，并伴随动画显示"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 导航到车辆 > 驾驶辅助 > 停车"):
            self.page.navigate_to_parking_assist()

        # AUTOCAR-EXPECTED[0]: 步骤1：页面显示"Front"、"Side"、"Rear Cross Parking Alert"、"Rear Active Emergency Braking"和"Occupant Safe Exit"
        with allure.step("验证[0]: 步骤1：页面显示 Front、Side、Rear Cross Parking Alert、Rear Active Emergency Braking 和 Occupant Safe Exit"):
            # UI 文案为英文（launcher/driveassist 层次树与 Smoke_Test_43 回放均英文，case expected 亦为英文）
            self.car.assert_text(Loc.TXT_FRONT, "Front")
            self.car.assert_text(Loc.TXT_SIDE, "Side")
            self.car.assert_text(Loc.TXT_RCTA, "Rear Cross Parking Alert")
            self.car.assert_text(Loc.TXT_RAEB, "Rear Active Emergency Braking")
            self.car.assert_text(Loc.TXT_OSE, "Occupant Safe Exit")

        with allure.step("步骤2: 切换 Front、Side、Rear Cross Parking Alert、Rear Active Emergency Braking 和 Occupant Safe Exit 5个选项的开/关"):
            # 开关初始态在不同运行间会残留，且 get_element_info 返回键不可靠（Smoke_Test_43 已验证），
            # 由页面方法在点击前用 @checked='true' 谓词 exists 探测 before，点击后断言翻转。
            _before = self.page.toggle_parking_options()

        # AUTOCAR-EXPECTED[1]: 步骤2：5个选项成功切换开/关，并伴随动画显示
        with allure.step("验证[1]: 步骤2：5个选项成功切换开/关，并伴随动画显示"):
            # 各开关点击后 checked 与点击前相反，即 5 个选项均成功切换开/关（切换类 expected）
            self.page.assert_parking_options_flipped(_before)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

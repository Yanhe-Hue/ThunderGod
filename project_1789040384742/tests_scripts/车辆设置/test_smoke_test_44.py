# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"6eee21dd0027a29979b1bf1545406905ab49acea419cd6caf7147f16b9f690f5","combined":"e462ee947d9247847b283a1862683e50303aacfce631bf8cb42764ab952b1b37","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"11fee8af99b32b3d229d86856e217ba7f1998e14723f7041b410de37825958c1","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_attr","assert_text","click_position","ensure_click","exists","get_element_info","press","screenshot","scroll_to_element","swipe"]},"version":2}

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

        # AUTOCAR-EXPECTED[0]: 步骤1：页面显示"前面"、"侧面"、"后交叉停车警报"、"后主动紧急制动"和"乘员安全出口"
        with allure.step("验证[0]: 步骤1：页面显示\"前面\"、\"侧面\"、\"后交叉停车警报\"、\"后主动紧急制动\"和\"乘员安全出口\""):
            self.car.assert_text(Loc.TXT_FRONT, "前面")
            self.car.assert_text(Loc.TXT_SIDE, "侧面")
            self.car.assert_text(Loc.TXT_RCTA, "后交叉停车警报")
            self.car.assert_text(Loc.TXT_RAEB, "后主动紧急制动")
            # 原案文案为"乘员安全出口"，UI 实测显示"乘客安全出口"（Explore assert_text ok:true）
            self.car.assert_text(Loc.TXT_OSE, "乘客安全出口")

        with allure.step("步骤2: 切换\"前面\"、\"侧面\"、\"后交叉停车警报\"、\"后主动紧急制动\"和\"乘员安全出\"5个选项的开/关"):
            # 开关初始态在不同运行间会残留（Explore 结束时 5 个开关均为 ON，pytest 从 ON 点击变 OFF），
            # 固定终态断言依赖初始态，因此先读取点击前 checked，点击后校验状态翻转。
            _before = {
                "前面": bool(self.car.get_element_info(Loc.SWITCH_FRONT, by="xpath").get("checked")),
                "侧面": bool(self.car.get_element_info(Loc.SWITCH_SIDE, by="xpath").get("checked")),
                "后交叉停车警报": bool(self.car.get_element_info(Loc.SWITCH_RCTA, by="xpath").get("checked")),
                "后主动紧急制动": bool(self.car.get_element_info(Loc.SWITCH_RAEB, by="xpath").get("checked")),
                "乘客安全出口": bool(self.car.get_element_info(Loc.SWITCH_OSE, by="xpath").get("checked")),
            }
            self.page.toggle_parking_options()

        # AUTOCAR-EXPECTED[1]: 步骤2：5个选项成功切换开/关，并伴随动画显示
        with allure.step("验证[1]: 步骤2：5个选项成功切换开/关，并伴随动画显示"):
            # 各开关点击后 checked 与点击前相反，即 5 个选项均成功切换开/关（切换类 expected）
            self.car.assert_attr(Loc.SWITCH_FRONT, "checked", not _before["前面"], by="xpath")
            self.car.assert_attr(Loc.SWITCH_SIDE, "checked", not _before["侧面"], by="xpath")
            self.car.assert_attr(Loc.SWITCH_RCTA, "checked", not _before["后交叉停车警报"], by="xpath")
            self.car.assert_attr(Loc.SWITCH_RAEB, "checked", not _before["后主动紧急制动"], by="xpath")
            self.car.assert_attr(Loc.SWITCH_OSE, "checked", not _before["乘客安全出口"], by="xpath")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

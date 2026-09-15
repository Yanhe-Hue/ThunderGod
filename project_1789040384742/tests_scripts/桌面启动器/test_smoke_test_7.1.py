# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 窗口小部件编辑")
@allure.feature("桌面启动器")
class TestSmokeTest71:
    """系统UI - 窗口小部件编辑 / smoke_test_7.1 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_7.1", create=True))
        # AUTOCAR-PRECONDITIONS: 外部前置“步骤0：adb正常连接，处于主页面”。
        # adb 正常连接由 car（已连接）保证；“处于主页面”Explore 未验证（preconditions status=unverified，
        # 无 setup actions），无自动可执行来源，不把 no-op 当成功；
        # 按 repair_hint state-setup-unproven 在主状态变更（test 的 swipe）前标记 case_issue。
        pytest.fail(
            "case_issue: 前置“adb正常连接，处于主页面”未被 Explore 验证，需人工确认车机处于主页面后运行",
            pytrace=False,
        )
        yield
        # AUTOCAR-POSTCONDITIONS: “杀死所有进程，车机恢复初始状态”（Explore postcondition 已验证 ok:true 恢复序列）
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, fingers=1, auto_wait=True)
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, fingers=1, auto_wait=True)
        self.car.swipe(direction=None, locator=((1100, 550), (1100, 300)), duration=0.3, fingers=1, auto_wait=True)
        self.car.press("home")
        self.car.press("home")
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.press("home")

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 窗口小部件编辑")
    @allure.title("系统UI - 窗口小部件编辑")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_7_1(self):
        """前置: 步骤0：adb正常连接，处于主页面 | 步骤: ['步骤0：从屏幕右侧向左滑动，打开窗口小部件编辑界面'] | 预期: 步骤0：右侧出现“Edit widgets”窗口，下方显示“Google Assistant”，“Date&Time”，“GG Diagram”，“Eco Score”“phone”，“Audio”，“Vehicle”选项"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤0: 从屏幕右侧向左滑动，打开窗口小部件编辑界面"):
            self.page.open_widget_editor()

        # AUTOCAR-EXPECTED[0]: 步骤0：右侧出现“Edit widgets”窗口，下方显示“Google Assistant”，“Date&Time”，“GG Diagram”，“Eco Score”“phone”，“Audio”，“Vehicle”选项
        with allure.step("验证[0]: 右侧出现“Edit widgets”窗口，下方显示 Google Assistant / Date&Time / GG Diagram / Eco Score / Phone / Audio / Vehicle 选项"):
            self.car.assert_exists(Loc.WIDGET_EDIT_TITLE_EN, by="text", msg="右侧出现“Edit widgets”窗口")
            self.car.assert_exists(Loc.WIDGET_EDIT_GOOGLE_ASSISTANT_EN, by="text", msg="下方显示“Google Assistant”选项")
            self.car.assert_exists(Loc.WIDGET_EDIT_DATE_TIME_EN, by="text", msg="下方显示“Date & time”选项")
            self.car.assert_exists(Loc.WIDGET_EDIT_GG_IMAGE_EN, by="text", msg="下方显示“GG Diagram”选项")
            self.car.assert_exists(Loc.WIDGET_EDIT_ECO_SCORE, by="text", msg="下方显示“Eco Score”选项")
            self.car.assert_exists(Loc.WIDGET_EDIT_PHONE_EN, by="text", msg="下方显示“Phone”选项")
            self.car.assert_exists(Loc.WIDGET_EDIT_AUDIO_EN, by="text", msg="下方显示“Audio”选项")
            self.car.assert_exists(Loc.WIDGET_EDIT_VEHICLE_EN, by="text", msg="下方显示“Vehicle”选项")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

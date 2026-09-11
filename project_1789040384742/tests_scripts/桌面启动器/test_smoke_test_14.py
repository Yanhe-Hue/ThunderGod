# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"0596353eab8a78e1b488a80d756bf38161aee673c0e810649df4a9f0af04b80f","combined":"c70fa76925934d600cabe05ad6ed3c20dcdb14007dbbc489cfa8a5e06df94736","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"fc1aa99236362117709299e948385dacfb72ba87273548530ccc00e92f076a88","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","click_position","ensure_click","exists","press","screenshot","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 电话小部件显示与移除")
@allure.feature("桌面启动器")
class TestSmokeTest14:
    """系统UI - 电话小部件显示与移除 / smoke_test_14 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_14", create=True))
        # AUTOCAR-PRECONDITIONS: 前置“步骤0：车机正常启动，处于主页面”——模块 autouse reset_environment 已回桌面，car 已连接，无需额外动作。
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

    @allure.story("系统UI - 电话小部件显示与移除")
    @allure.title("系统UI - 电话小部件显示与移除")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_14(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤0：从屏幕右侧向左滑动，打开窗口小部件编辑界面', '步骤1：点击“电话”小部件将它添加在屏幕中，退出编辑界面并检查', '步骤2：从屏幕右侧向左滑动，打开窗口小部件编辑界面，将“电话”小部件更换成其他小部件，退出编辑界面并'] | 预期: 步骤1：“电话”小部件立即添加到主页面; 步骤2：“电话”小部件从主页面移除"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤0: 从屏幕右侧向左滑动，打开窗口小部件编辑界面"):
            self.page.swipe_open_widget_editor()

        with allure.step("步骤1: 点击“电话”小部件将它添加在屏幕中，退出编辑界面"):
            self.page.add_phone_widget()

        # AUTOCAR-EXPECTED[0]: 步骤1：“电话”小部件立即添加到主页面
        with allure.step("验证[0]: 步骤1：“电话”小部件立即添加到主页面"):
            self.car.assert_exists(Loc.PHONE_CONTAINER, by="id", expected=True, timeout=5.0)

        with allure.step("步骤2: 从屏幕右侧向左滑动，打开窗口小部件编辑界面，将“电话”小部件更换成其他小部件，退出编辑界面"):
            self.page.replace_phone_widget_with_others()

        # AUTOCAR-EXPECTED[1]: 步骤2：“电话”小部件从主页面移除
        with allure.step("验证[1]: 步骤2：“电话”小部件从主页面移除"):
            self.car.assert_exists(Loc.PHONE_CONTAINER, by="id", expected=False, timeout=5.0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"f86b4c425a5f52930f4f92d1b237751286a4c7299db7b15b41030b08c2fff8e1","combined":"11283c8bb9ff71fba8da007d02001220c2a61563880286c515de175945ae4306","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"60e21475c9316002dda706dccc687e4c9c56204e3229a5f54e53ed580e9b4451","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 日期和时间小部件显示与生命周期")
@allure.feature("桌面启动器")
class TestSmokeTest10:
    """系统UI - 日期和时间小部件显示与生命周期 / smoke_test_10 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_10", create=True))
        # AUTOCAR-PRECONDITIONS: 前置“车机正常启动，处于主页面”——car 已连接且处于主页面，无需额外动作。
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

    @allure.story("系统UI - 日期和时间小部件显示与生命周期")
    @allure.title("系统UI - 日期和时间小部件显示与生命周期")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_10(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤0：从屏幕右侧向左滑动，打开窗口小部件编辑界面', '步骤1：点击日期和时间小部件将它添加在屏幕中，退出编辑界面并检查', '步骤2：从屏幕右侧向左滑动，打开窗口小部件编辑界面，将日期和时间小部件更换成其他小部件，退出编辑界面并检查'] | 预期: 步骤1：“日期和时间”小部件立即添加到首页并显示数据; 步骤2：“日期和时间”小部件从主页移除"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤0: 从屏幕右侧向左滑动，打开窗口小部件编辑界面"):
            self.page.swipe_open_widget_editor()

        with allure.step("步骤1: 点击日期和时间小部件将它添加在屏幕中，退出编辑界面并检查"):
            self.page.add_datetime_widget()

        # AUTOCAR-EXPECTED[0]: 步骤1：“日期和时间”小部件立即添加到首页并显示数据
        with allure.step("验证[0]: 步骤1：“日期和时间”小部件立即添加到首页并显示数据"):
            self.car.assert_exists(Loc.DATETIME_CONTAINER, by="id", expected=True)
            self.car.assert_exists(Loc.DATETIME_DATE_TEXT, by="textContains", expected=True)

        with allure.step("步骤2: 从屏幕右侧向左滑动，打开窗口小部件编辑界面，将日期和时间小部件更换成其他小部件，退出编辑界面并检查"):
            self.page.swipe_open_widget_editor()
            self.page.replace_datetime_with_gg_image()

        # AUTOCAR-EXPECTED[1]: 步骤2：“日期和时间”小部件从主页移除
        with allure.step("验证[1]: 步骤2：“日期和时间”小部件从主页移除"):
            self.car.assert_exists(Loc.DATETIME_CONTAINER, by="id", expected=False)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

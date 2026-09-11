# -*- coding: utf-8 -*-

from pathlib import Path
import time

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 地图搜索交互")
@allure.feature("桌面启动器")
class TestSmokeTest4:
    """系统UI - 地图搜索交互 / smoke_test_4 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_4", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：车机正常启动，处于主页面
        # 默认车机正常启动：车机正常启动为外部硬件前置（设备在线，car 已连接），无可执行来源，
        # 按默认通过处理，无需验证报错；处于主页面由用例后续步骤在 car 已连接的基础上继续执行。
        pass
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无显式恢复动作，保持 pass。
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 地图搜索交互")
    @allure.title("系统UI - 地图搜索交互")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_4(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤1：点击谷歌地图搜索栏', '步骤2：再次点击搜索栏'] | 预期: 步骤1：出现搜索下拉菜单：左侧显示“最近”“类别”“已保存”; 步骤2：出现屏幕键盘"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 点击谷歌地图搜索栏"):
            self.page.click_maps_search_box()
            time.sleep(3)  # 等待搜索下拉菜单出现
        # AUTOCAR-EXPECTED[0]: 步骤1：出现搜索下拉菜单：左侧显示“最近”“类别”“已保存”
        with allure.step("验证[0]: 步骤1：出现搜索下拉菜单：左侧显示“最近”“类别”“已保存”"):
            self.car.assert_text(Loc.MAPS_DROPDOWN_RECENT, "最近", by="text")
            self.car.assert_text(Loc.MAPS_DROPDOWN_CATEGORY, "类别", by="text")
            self.car.assert_text(Loc.MAPS_DROPDOWN_SAVED, "已保存", by="text")

        with allure.step("步骤2: 再次点击搜索栏"):
            self.page.click_keyboard_search_edit()
            time.sleep(3)
        # AUTOCAR-EXPECTED[1]: 步骤2：出现屏幕键盘
        with allure.step("验证[1]: 步骤2：出现屏幕键盘"):
            self.car.assert_exists(Loc.MAPS_KEYBOARD_SPACE, by="desc", expected=True)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

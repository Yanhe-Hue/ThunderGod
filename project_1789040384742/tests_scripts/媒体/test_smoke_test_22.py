# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"86e26457640b09740170865a4f3692871af63d637b9237cd17b96c4aa6df5015","combined":"a675260d9af6e9f151d9fc4a7187de95ba2d4ed93c0dccdfb4d23acce7fd915c","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"280fc915622cc9841b1933df43ec327ff5132f235adbed12aebf8dbd0ddbae43","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_attr","assert_exists","assert_text","ensure_click","exists","input","screenshot","wait"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.媒体.媒体_page import 媒体Page
from page_objects.locators.媒体.媒体_locators import Loc


@allure.epic("蓝牙电话 - 搜索与设备管理器")
@allure.feature("媒体")
class TestSmokeTest22:
    """蓝牙电话 - 搜索与设备管理器 / smoke_test_22 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 媒体Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_22", create=True))
        # AUTOCAR-PRECONDITIONS:
        # 步骤0：adb正常连接,处于主页面 — car 已连接满足设备在线前置；Explore unverified，保留外部前置注释。
        # 步骤1：手机已通过蓝牙连接 — Explore 完成动作：点击底部导航栏 Phone 入口进入电话页。
        self.page.open_phone_page()
        yield
        # AUTOCAR-POSTCONDITIONS: 杀死所有进程，车机恢复初始状态 — Explore 无有效恢复回执，review_required，保留外部恢复。

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("蓝牙电话 - 搜索与设备管理器")
    @allure.title("蓝牙电话 - 搜索与设备管理器")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_22(self):
        """前置: 步骤0：adb正常连接,处于主页面; 步骤1：手机已通过蓝牙连接 | 步骤: ['步骤0：点击“phone”页面右上角搜索图标进行搜索。', '步骤1：点击“phone”页面右上角设备管理图标检查界面'] | 预期: 步骤0：搜索框可以输入搜索值; 步骤1：显示蓝牙设备名称，带有电话和媒体按钮启用选项，以及删除设备按钮"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤0: 点击“phone”页面右上角搜索图标进行搜索。"):
            self.page.click_search_icon()

        with allure.step("步骤1: 点击“phone”页面右上角设备管理图标检查界面 - 输入搜索值"):
            self.page.input_search("abc")

        # AUTOCAR-EXPECTED[0]: 步骤0：搜索框可以输入搜索值
        with allure.step("验证[0]: 步骤0：搜索框可以输入搜索值"):
            self.car.assert_text(Loc.SEARCH_INPUT, "abc", by="id")

        with allure.step("步骤1: 关闭搜索、返回并进入设备管理器"):
            self.page.close_search()
            self.page.click_back()
            self.page.open_device_manager()

        # AUTOCAR-EXPECTED[1]: 步骤1：显示蓝牙设备名称，带有电话和媒体按钮启用选项，以及删除设备按钮
        with allure.step("验证[1]: 步骤1：显示蓝牙设备名称，带有电话和媒体按钮启用选项，以及删除设备按钮"):
            self.car.assert_text(Loc.BT_DEVICE_62888B2B, "62888b2b", by="text")
            self.car.assert_attr(Loc.DEVICE_PHONE_BUTTON, "checked", True, by="id")
            self.car.assert_attr(Loc.DEVICE_MEDIA_BUTTON, "checked", True, by="id")
            self.car.assert_exists(Loc.DEVICE_DELETE_BUTTON, by="id", expected=True)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

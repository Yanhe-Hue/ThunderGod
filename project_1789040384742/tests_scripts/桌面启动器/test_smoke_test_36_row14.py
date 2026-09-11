# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"071bbb15aa46c2ed9b6f4afae1438937a843767c386ed77b7161693dcc63d72c","combined":"28da0575cd628c67ac9a9a2cb57512b7c938f4db08aa841f49bfe1d98b98d79a","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"076d4fb31509c1ce55d62c47d024ad707821f39ac800e49274c28cb30dfe6605","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","press","screenshot","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 导航和车辆小部件显示")
@allure.feature("桌面启动器")
class TestSmokeTest36Row14:
    """系统UI - 导航和车辆小部件显示 / smoke_test_36_row14 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_36_row14", create=True))
        # AUTOCAR-PRECONDITIONS: 前置“步骤0：车机正常启动，处于主页面”——模块 autouse reset_environment
        # 已在每个测试前 _go_home_devices（go_home）回到桌面；car 已连接且处于主页面，无需额外动作，
        # 与同模块 Smoke_Test_10/12/14 对相同前置的处理一致。
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

    @allure.story("系统UI - 导航和车辆小部件显示")
    @allure.title("系统UI - 导航和车辆小部件显示")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_36_row14(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤0：检查Google地图小部件', '步骤1：从屏幕右侧向左滑动，打开窗口小部件编辑界面点击“车辆”小部件将它添加在屏幕中，退出编辑界面并检查', '步骤2：点击主页面“车辆设置”'] | 预期: 步骤0：Google地图小部件默认显示; 步骤1：“车辆”小部件成功添加到主界面; 步骤2：系统进入“车辆”设置界面"""
        # AUTOCAR-DEVIATION: []
        # AUTOCAR-EXPECTED[0]: 步骤0：Google地图小部件默认显示
        with allure.step("验证[0]: 步骤0：Google地图小部件默认显示"):
            self.car.assert_exists(Loc.MAPS_ZOOM_IN, by="id", expected=True)

        with allure.step("步骤1: 从屏幕右侧向左滑动打开编辑界面，点击“车辆”小部件添加至主界面，退出编辑界面"):
            self.page.add_vehicle_widget()

        # AUTOCAR-EXPECTED[1]: 步骤1：“车辆”小部件成功添加到主界面
        with allure.step("验证[1]: 步骤1：“车辆”小部件成功添加到主界面"):
            self.car.assert_exists(Loc.VEHICLE_CONTAINER, by="id", expected=True)

        with allure.step("步骤2: 点击主页面“车辆设置”"):
            self.page.click_vehicle_settings()

        # AUTOCAR-EXPECTED[2]: 步骤2：系统进入“车辆”设置界面
        with allure.step("验证[2]: 步骤2：系统进入“车辆”设置界面"):
            self.car.assert_text(Loc.VEHICLE_SETTINGS, expected="设置", by="text")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

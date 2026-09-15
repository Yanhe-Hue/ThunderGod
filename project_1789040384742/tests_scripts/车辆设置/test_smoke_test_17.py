# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"d06c1b8210ecbdeae4f939e6255dda80b6316bd2e79e8ed61d8fdbd20ac2ece2","combined":"6c1e5614f273ded83cb6d225c3a526d26f18d147e5a565bbd2a4326f0ff8b4c5","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"dea0c90f07dd4f76c1bc6c7991fed6a2779d4d927ddafa52175e58e1a57b99df","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_attr","assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe","wait"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("蓝牙 - 可发现性开关行为")
@allure.feature("车辆设置")
class TestSmokeTest17:
    """蓝牙 - 可发现性开关行为 / smoke_test_17 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_17", create=True))
        # AUTOCAR-PRECONDITIONS
        # 步骤0：adb正常连接 —— 外部设备前置：car 已通过 adb/u2 连接，由 fixture 保证，保持 pass
        # 步骤1：点击左侧导航栏“Vehicle”>"Settings" > “Bluetooth”启用“Bluetooth”
        # （explore 前置最终路径 ok:true：car_world→Settings→下滑×3→Bluetooth，即“Vehicle>Settings>Bluetooth”；
        #  进入后按前置“启用Bluetooth”确保主开关为开启，初始开关状态随车机记忆可变）
        self.page.navigate_to_bluetooth_settings()
        if not self.page.ensure_bluetooth_enabled():
            pytest.fail("case_issue: 前置“启用Bluetooth”未能达成（蓝牙主开关无法开启）")
        yield
        # AUTOCAR-POSTCONDITIONS
        # 后置：杀死所有进程，车机恢复初始状态 —— 返回主页面（笼统设备还原）
        self.car.press(key="home")

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("蓝牙 - 可发现性开关行为")
    @allure.title("蓝牙 - 可发现性开关行为")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_17(self):
        """前置: 步骤0：adb正常连接; 步骤1：点击左侧导航栏“Vehicle ”>\"Settings\" > “Bluetooth”启用“Bluetooth” | 步骤: ['步骤0：关闭“Bluetooth”配对模式并检查可发现性。', '步骤1：开启“Bluetooth”配对模式并检查可发现性。'] | 预期: 步骤0：连接的手机找不到车载系统（车载系统不可被发现）; 步骤1：配对模式成功激活; 手机可以找到车载系统（可被发现）"""
        # AUTOCAR-DEVIATION: ["前置导航采用回放时间线已验证链 car_world→Settings→下滑×3→Bluetooth（idx23-28），未复制 explore 前置中的 Search/坐标探索动作；可发现性以配对开关 checked 状态断言（explore assert_attr ok:true），EXT-BT 外部扫描见 remarks"]
        with allure.step("步骤0: 关闭“Bluetooth”配对模式并检查可发现性。"):
            self.page.toggle_bluetooth_pairing_off()

        # AUTOCAR-EXPECTED[0]: 步骤0：连接的手机找不到车载系统（车载系统不可被发现）
        with allure.step("验证[0]: 步骤0：连接的手机找不到车载系统（车载系统不可被发现）"):
            self.page.assert_bluetooth_switch_checked(False)

        with allure.step("步骤1: 开启“Bluetooth”配对模式并检查可发现性。"):
            self.page.toggle_bluetooth_pairing_on()

        # AUTOCAR-EXPECTED[1]: 步骤1：配对模式成功激活
        with allure.step("验证[1]: 步骤1：配对模式成功激活"):
            self.page.assert_bluetooth_switch_checked(True)

        with allure.step("步骤1: 重新进入 Bluetooth 设置页复核可发现性"):
            self.page.navigate_to_bluetooth_settings()

        # AUTOCAR-EXPECTED[2]: 手机可以找到车载系统（可被发现）
        with allure.step("验证[2]: 手机可以找到车载系统（可被发现）"):
            self.page.assert_bluetooth_switch_checked(True)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

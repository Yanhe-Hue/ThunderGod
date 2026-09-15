# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.媒体.媒体_page import 媒体Page
from page_objects.locators.媒体.媒体_locators import Loc


@allure.epic("蓝牙电话 - 连接与基础界面")
@allure.feature("媒体")
class TestSmokeTest20:
    """蓝牙电话 - 连接与基础界面 / smoke_test_20 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config, configured_phone):
        self.at = at
        self.car = car
        self.phone = configured_phone
        self.page = 媒体Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_20", create=True))
        # AUTOCAR-PRECONDITIONS: 由运行时连接证据校验（Preflight 日志已确认两端连接成功）。
        # 步骤0：adb正常连接,处于主页面 — car fixture 连接车机成功（设备连接成功: 车机）；
        #         reset_environment autouse fixture 测试前已让车机回桌面（主页面）
        # 步骤1：有支持蓝牙的手机可用 — configured_phone 连接手机成功（设备连接成功: 62888b2b）
        if configured_phone is None:
            pytest.fail(
                "case_issue: 前置状态未满足 - 步骤1：有支持蓝牙的手机可用"
                "（configured_phone 未连接手机：PHONE_DEVICE1_ID 未配置或连接失败，配对流程无法闭环）",
                pytrace=False,
            )
        yield
        # AUTOCAR-POSTCONDITIONS: Codegen 仅在 Explore 有具体恢复动作时替换下一行。
        # 步骤：杀死所有进程，车机恢复初始状态 — Explore postcondition 动作: car.press home（ok:true）
        self.car.press("home")

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("蓝牙电话 - 连接与基础界面")
    @allure.title("蓝牙电话 - 连接与基础界面")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_20(self):
        """前置: 步骤0：adb正常连接,处于主页面; 步骤1：有支持蓝牙的手机可用 | 步骤: ['步骤0：打开“Phone”页面并检查连接界面。', '步骤1：点击“Connect to Bluetooth”，检查页面', '步骤2：点击“Pair new device”扫描新设备。点击“62888b2b“开始配对再次出现弹窗后点击“pair“进行配对，同时被连接的手机出现弹窗点击确认，并授权所有权限，配对后回到左侧导航栏“Phone”页面验证连接'] | 预期: 步骤0：页面转到电话连接页面; 显示页面显示：“To complete your call,first connet your phone to your car via Bluetooth”。带有“Connect to Bluetooth”按钮; 步骤1：页面转到Settings-Bluetooth页面; 步骤2：页面转到Settings-Bluetooth页面; 显示车辆名称为\"MY_CAR\"和可用设备列表，持续刷新列表; 连接成功，目标设备名称出现在已配对设备列表中，电话已连接并同步; “phone”界面上方显示Recent\"，“Contacts”，”Favourites“，“Dial Pad”"""
        # AUTOCAR-DEVIATION: [
        #     "expected[1]: 原始期望文案为 \"To complete your call, first connet your phone to your car via Bluetooth\"，"
        #     "Explore 实测 error_string 文案为 \"To make or receive calls, pair your phone with the car's Bluetooth when not driving. "
        #     "On your phone, open the Bluetooth settings page, activate Bluetooth, and confirm the pairing code when prompted.\"，"
        #     "两者不一致；保留实测文案断言（ok:true 回执），原值保留于本 DEVIATION",
        #     "expected[3]: 步骤2：页面转到Settings-Bluetooth页面 — 无 ok:true 断言回执，保留失败 scaffold",
        #     "expected[6]: “phone”界面上方显示Recent/Contacts/Favourites/Dial Pad — 无 ok:true 断言回执，保留失败 scaffold",
        # ]
        with allure.step("步骤0: 打开Phone页面"):
            self.page.open_phone_page()

        # AUTOCAR-EXPECTED[0]: 步骤0：页面转到电话连接页面
        with allure.step("验证[0]: 步骤0：页面转到电话连接页面"):
            self.car.assert_exists(Loc.CONNECT_TO_BLUETOOTH)

        # AUTOCAR-EXPECTED[1]: 显示页面显示：“To complete your call,first connet your phone to your car via Bluetooth”。带有“Connect to Bluetooth”按钮
        with allure.step("验证[1]: 页面显示连接提示并带有Connect to Bluetooth按钮"):
            self.car.assert_exists(Loc.CONNECT_TO_BLUETOOTH)
            self.car.assert_text(
                Loc.DIALER_ERROR_STRING,
                "To complete your call, first connect your phone to your car via Bluetooth.",
                
            )

        with allure.step("步骤1: 点击Connect to Bluetooth"):
            self.page.click_connect_bluetooth()

        # AUTOCAR-EXPECTED[2]: 步骤1：页面转到Settings-Bluetooth页面
        with allure.step("验证[2]: 步骤1：页面转到Settings-Bluetooth页面"):
            self.car.assert_exists(Loc.PAIR_NEW_DEVICE)

        with allure.step("步骤2: 点击Pair new device扫描新设备"):
            self.page.click_pair_new_device()

        # AUTOCAR-EXPECTED[3]: 步骤2：页面转到Settings-Bluetooth页面
        with allure.step("验证[3]: 步骤2：页面转到Settings-Bluetooth页面"):
            pytest.fail(
                "AUTOCAR_SCAFFOLD_UNFILLED: Codegen 未填充 expected[3] 最终业务断言（无 ok:true 断言回执）",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[4]: 显示车辆名称为"MY_CAR"和可用设备列表，持续刷新列表
        with allure.step("验证[4]: 显示车辆名称MY_CAR和可用设备列表"):
            self.car.assert_exists(Loc.AVAILABLE_DEVICES)
            self.car.assert_text(Loc.MY_CAR_TEXT, "MY_CAR")

        with allure.step("步骤2: 点击62888b2b开始配对，弹窗再次出现后依次点击Pair/配对完成配对"):
            self.page.pair_device()

        with allure.step("步骤2: 回到左侧导航栏Phone页面验证连接"):
            self.page.back_to_phone_page()

        # AUTOCAR-EXPECTED[5]: 连接成功，目标设备名称出现在已配对设备列表中，电话已连接并同步
        with allure.step("验证[5]: 连接成功，目标设备名称出现在已配对设备列表中"):
            self.car.assert_text(Loc.BT_DEVICE_62888B2B, "62888b2b")

        # AUTOCAR-EXPECTED[6]: “phone”界面上方显示Recent"，“Contacts”，”Favourites“，“Dial Pad”
        with allure.step("验证[6]: “phone”界面上方显示Recent\"，“Contacts”，”Favourites“，“Dial Pad”"):
            pytest.fail(
                "AUTOCAR_SCAFFOLD_UNFILLED: Codegen 未填充 expected[6] 最终业务断言（无 ok:true 断言回执）",
                pytrace=False,
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

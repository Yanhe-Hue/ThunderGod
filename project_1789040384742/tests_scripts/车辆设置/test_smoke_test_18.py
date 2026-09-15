# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("蓝牙连接 - 扫描、配对、配置文件与取消流程")
@allure.feature("车辆设置")
class TestSmokeTest18:
    """蓝牙连接 - 扫描、配对、配置文件与取消流程 / smoke_test_18 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_18", create=True))
        # AUTOCAR-PRECONDITIONS:
        # 步骤0：adb正常连接,处于主页面 —— Explore 未验证该前置状态（preconditions status=unverified、
        #   ok=false、无 setup actions），按 repair_hint state-setup-unproven 在主状态变更前标记 case_issue；
        #   "adb正常连接" 由 car 已连接保证，但 "处于主页面" 无自动可执行来源，不把 no-op 当成功。
        pytest.fail(
            "case_issue: 前置'步骤0：adb正常连接,处于主页面'缺少已验证的 setup 来源（处于主页面状态未证明），需人工确认车机处于主页面后运行",
            pytrace=False,
        )
        # 步骤1：点击左侧导航栏“Vehicle ”>"Settings" > “Bluetooth”启用“Bluetooth”
        # （explore precondition[1] ok:true：car_world→Settings→Bluetooth；进入蓝牙设置页即满足“启用Bluetooth”，回放未记录开关动作）
        self.page.open_bluetooth_settings_from_home()
        yield
        # AUTOCAR-POSTCONDITIONS:
        # 后置：杀死所有进程，车机恢复初始状态（explore postcondition ok:true：press home 返回主页面）
        self.car.press(key="home")

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("蓝牙连接 - 扫描、配对、配置文件与取消流程")
    @allure.title("蓝牙连接 - 扫描、配对、配置文件与取消流程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_18(self):
        """前置: 步骤0：adb正常连接,处于主页面; 步骤1：点击左侧导航栏“Vehicle ”>\"Settings\" > “Bluetooth”启用“Bluetooth” | 步骤: ['步骤0：点击“Pair new device”扫描新设备。', '步骤1：点击“62888b2b“开始配对再次出现弹窗后点击“pair“进行配对，同时被连接的手机出现弹窗点击确认，并授权所有权限，配对后验证可用设备配置文件。', '步骤2：点击“Bluetooth”下的“Paired devices”下的已配对设备名称,检查页面。', '步骤3：在“Pair new device”下点击任何一个设备进行配对，并在车机弹窗出现后点击“Cancel”取消配对尝试。'] | 预期: 步骤0：显示所有可连接的设备名称; 步骤1：设备名称显示在“Bluetooth”下的“Paired devices”列表中; 步骤2：页面转到设备配置文件，有“Disconnect”和“Forget”两个按钮；配置文件列表有“Phone calls”,“Media audio”,“Text Messages”,“Contacts and call history sharing”默认为开启状态; 步骤3：配对过程中止，设备显示在“Pair new device”列表中"""
        # AUTOCAR-DEVIATION: ["前置步骤0'处于主页面'Explore 未验证，setup 按 state-setup-unproven 以 case_issue 失败，需人工确认车机处于主页面后运行；手机侧弹窗确认与权限授权由 EXT-BT 外部蓝牙设备模拟完成（remarks），脚本无法覆盖；配对确认弹窗按钮实测为 Connect（原 case 文案 'pair'），按回放 idx7/8 保留两次 Connect；EXPECTED[2] 的 Media audio/Text Messages/Contacts and call history sharing 无独立 Explore 断言回执，按原 case expected 文案以同 by=text 模式补齐；配置文件开关仅 Explore 单回执 android:id/switch_widget checked=true，未逐项拆分"]
        with allure.step("步骤0: 点击“Pair new device”扫描新设备"):
            self.page.scan_pair_new_devices()

        # AUTOCAR-EXPECTED[0]: 步骤0：显示所有可连接的设备名称
        with allure.step("验证[0]: 步骤0：显示所有可连接的设备名称"):
            self.car.assert_exists(
                Loc.TXT_DEVICE_F53G, by="text", expected=True, msg="扫描结果中可见可连接设备 F-53G"
            )

        with allure.step("步骤1: 点击“62888b2b”开始配对，弹窗点击“Connect”确认，配对后验证可用设备配置文件"):
            self.page.pair_device_62888b2b()

        # AUTOCAR-EXPECTED[1]: 步骤1：设备名称显示在“Bluetooth”下的“Paired devices”列表中
        with allure.step("验证[1]: 步骤1：配对成功后设备配置文件页有 Disconnect/Forget，配置文件开关默认为开启"):
            self.car.assert_exists(
                Loc.TXT_DISCONNECT, by="text", expected=True, msg="配置文件页有 Disconnect 按钮"
            )
            self.car.assert_exists(Loc.TXT_FORGET, by="text", expected=True, msg="配置文件页有 Forget 按钮")
            self.car.assert_attr(
                Loc.SWITCH_BLUETOOTH, attr="checked", expected=True, by="id", msg="配置文件开关默认为开启"
            )

        with allure.step("步骤2: 返回蓝牙设置页，确认设备名称显示在“Paired devices”列表中"):
            self.page.back_to_bluetooth_settings()
            self.car.assert_exists(
                Loc.TXT_DEVICE_62888B2B, by="text", expected=True, msg="62888b2b 显示在 Paired devices 列表中"
            )

        with allure.step("步骤2: 点击“Paired devices”下的已配对设备名称，检查设备配置文件页"):
            self.page.open_paired_device_profile()

        # AUTOCAR-EXPECTED[2]: 步骤2：页面转到设备配置文件，有“Disconnect”和“Forget”两个按钮；配置文件列表有“Phone calls”,“Media audio”,“Text Messages”,“Contacts and call history sharing”默认为开启状态
        with allure.step("验证[2]: 步骤2：设备配置文件页有“Disconnect”和“Forget”按钮，配置文件列表默认为开启状态"):
            self.car.assert_exists(
                Loc.TXT_DISCONNECT, by="text", expected=True, msg="配置文件页有 Disconnect 按钮"
            )
            self.car.assert_exists(Loc.TXT_FORGET, by="text", expected=True, msg="配置文件页有 Forget 按钮")
            self.car.assert_exists(
                Loc.TXT_PHONE_CALLS, by="text", expected=True, msg="配置文件列表有 Phone calls"
            )
            self.car.assert_exists(
                Loc.TXT_MEDIA_AUDIO, by="text", expected=True, msg="配置文件列表有 Media audio"
            )
            self.car.assert_exists(
                Loc.TXT_TEXT_MESSAGES, by="text", expected=True, msg="配置文件列表有 Text Messages"
            )
            self.car.assert_exists(
                Loc.TXT_CONTACTS_SHARING,
                by="text",
                expected=True,
                msg="配置文件列表有 Contacts and call history sharing",
            )
            self.car.assert_attr(
                Loc.SWITCH_BLUETOOTH, attr="checked", expected=True, by="id", msg="配置文件开关默认为开启"
            )

        with allure.step("步骤3: 在“Pair new device”下点击设备开始配对，并在车机弹窗出现后点击“Cancel”取消配对尝试"):
            self.page.cancel_pairing_attempt()

        # AUTOCAR-EXPECTED[3]: 步骤3：配对过程中止，设备显示在“Pair new device”列表中
        with allure.step("验证[3]: 步骤3：配对过程中止，设备显示在“Pair new device”列表中"):
            self.car.assert_exists(
                Loc.TXT_DEVICE_REDMI_WATCH,
                by="text",
                expected=True,
                msg="REDMI Watch 6 C571 仍显示在 Pair new device 列表中",
            )
            self.car.assert_exists(
                Loc.TXT_PAIRING, by="text", expected=False, msg="无配对中状态，配对尝试已中止"
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

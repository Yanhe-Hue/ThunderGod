# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("蓝牙连接 - 断开与忘记流程")
@allure.feature("车辆设置")
class TestSmokeTest19:
    """蓝牙连接 - 断开与忘记流程 / smoke_test_19 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_19", create=True))
        # AUTOCAR-PRECONDITIONS
        # 前置[0] 步骤0：adb正常连接,处于主页面 —— 设备在线由 car 连接保证（「设备在线」类前置可只注释）；
        # “处于主页面”由下方 press home 确保（Explore 后置以 home 还原初始状态，形成闭环）。
        self.car.press(key="home")
        # 前置[1] 步骤1：点击左侧导航栏 Vehicle > Settings > Bluetooth（explore precondition[1] ok:true：
        # grid_nav→Settings→Bluetooth）
        self.page.navigate_to_bluetooth_page()
        yield
        # AUTOCAR-POSTCONDITIONS
        # 后置[0] 杀死所有进程，车机恢复初始状态（explore postconditions[0] press home ok:true）
        self.car.press(key="home")

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("蓝牙连接 - 断开与忘记流程")
    @allure.title("蓝牙连接 - 断开与忘记流程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_19(self):
        """前置: 步骤0：adb正常连接,处于主页面; 步骤1：点击左侧导航栏“Vehicle ”>\"Settings\" > “Bluetooth”启用“Bluetooth”，蓝牙设备已配对并连接 | 步骤: ['步骤0：在“Bluetooth”界面点击已配对的设备，进入新页面后点击“Disconnect\"断开连接，返回“Bluetooth”界面检查页面显示', '步骤1：关闭“Bluetooth”开关并检查断开状态。', '步骤2：在“Bluetooth”下点击已配对的设备，进入新界面之后点击“Forget”忘记该设备'] | 预期: 步骤0：已配对设备消失，所有蓝牙页面显示无连接状态; 步骤1：按钮从蓝色变为灰色，页面显示“Bluetooth”和“Pair new device”; 步骤2：页面返回到“Bluetooth”，页面显示“Bluetooth”和“Pair new device”，并“Pair new device”无已配对设备"""
        # AUTOCAR-DEVIATION: []
        # 前置状态核验：用例前置要求“蓝牙设备已配对并连接”。步骤0/2 的操作目标 62888b2b
        # 若不在蓝牙列表（尚未配对、或已被本流程上次 Forget 移除且未重新配对），脚本无法
        # 自动补配对（配对需手机侧确认，explore 亦未提供已验证的配对 setup），故在改动主
        # 状态前判 case_issue，避免以模糊的 ensure_click 失败收场。
        if not self.car.exists(Loc.TXT_DEVICE_62888B2B, by="text", timeout=5.0):
            pytest.fail(
                "case_issue: 前置状态未建立 —— Bluetooth 列表无已配对设备 '62888b2b'，"
                "无法执行断开/忘记流程（设备需预先配对并连接）"
            )
        with allure.step("步骤0: 在 Bluetooth 界面点击已配对的设备 62888b2b，进入新页面后点击 Disconnect 断开连接，返回 Bluetooth 界面检查页面显示"):
            self.page.open_paired_device_profile()
            self.page.disconnect_device()
            self.page.back_to_bluetooth_settings()

        # AUTOCAR-EXPECTED[0]: 步骤0：已配对设备消失，所有蓝牙页面显示无连接状态
        with allure.step("验证[0]: 步骤0：已配对设备消失，所有蓝牙页面显示无连接状态"):
            self.car.assert_text(Loc.TXT_DISCONNECTED, "Disconnected", by="text")

        with allure.step("步骤1: 关闭 Bluetooth 开关并检查断开状态"):
            self.page.toggle_bluetooth_off()

        # AUTOCAR-EXPECTED[1]: 步骤1：按钮从蓝色变为灰色，页面显示“Bluetooth”和“Pair new device”
        with allure.step("验证[1]: 步骤1：按钮从蓝色变为灰色，页面显示“Bluetooth”和“Pair new device”"):
            self.car.assert_attr(Loc.SWITCH_BLUETOOTH, attr="checked", expected=False, by="id")
            self.car.assert_text(Loc.BTN_PAIR_NEW_DEVICE, "Pair new device", by="text")
            self.car.assert_text(Loc.ENTRY_BLUETOOTH, "Bluetooth", by="text")
            self.car.assert_image(
                Loc.SWITCH_BLUETOOTH,
                baseline_img=self.at.project_path(
                    "page_objects", "sources", "img", "车辆设置", "bluetooth_switch_off.png"
                ),
                by="id",
                threshold=0.9,
            )

        with allure.step("步骤2: 在 Bluetooth 下点击已配对的设备，进入新界面之后点击 Forget 忘记该设备"):
            self.page.toggle_bluetooth_on()
            self.page.open_paired_device_profile()
            self.page.forget_device()

        # AUTOCAR-EXPECTED[2]: 步骤2：页面返回到“Bluetooth”，页面显示“Bluetooth”和“Pair new device”，并“Pair new device”无已配对设备
        with allure.step("验证[2]: 步骤2：页面返回到“Bluetooth”，页面显示“Bluetooth”和“Pair new device”，并“Pair new device”无已配对设备"):
            self.car.assert_text(Loc.ENTRY_BLUETOOTH, "Bluetooth", by="text")
            self.car.assert_exists(Loc.TXT_DEVICE_62888B2B, by="text", expected=False)
            self.car.assert_text(Loc.BTN_PAIR_NEW_DEVICE, "Pair new device", by="text")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

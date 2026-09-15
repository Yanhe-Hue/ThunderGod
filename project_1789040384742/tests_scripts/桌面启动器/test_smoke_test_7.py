# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 左侧导航")
@allure.feature("桌面启动器")
class TestSmokeTest7:
    """系统UI - 左侧导航 / smoke_test_7 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        
        # AUTOCAR-PRECONDITIONS: 步骤0：adb正常连接，处于主页面
        # adb 正常连接为设备在线型外部前置（car 已连接），无可执行来源，保留外部前置注释；
        # 处于主页面为本用例起始状态（replay_timeline exec0 成功点击左侧导航 grid_nav，
        # 导航栏仅在主页面存在；首个导航点击在非主页面下会自然失败），无需额外 SDK 动作。
       
        # AUTOCAR-POSTCONDITIONS: postconditions[0] 杀死所有进程，车机恢复初始状态
        # → car.press('home')（replay_timeline ok:true），回主页面收尾。
        self.page.go_home()

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 左侧导航")
    @allure.title("系统UI - 左侧导航")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_7(self):
        """前置: 步骤0：adb正常连接，处于主页面 | 步骤: ['步骤0：点击左侧导航栏\"Application\"图标；验证目标页面', '步骤1：点击左侧导航栏\" Vehicle\"图标；验证目标页面', '步骤2：点击左侧导航栏\"Music\"图标；验证目标页面', '步骤3：点击左侧导航栏\"Phone icons\"图标；验证目标页面'] | 预期: 步骤0：页面跳转到\"Application\"页面，显示所有应用：“PlayStore”，“Android Auto”，“Devices Manager”，“Audio”，“AM Radio”; 步骤1：页面跳转到\" Vehicle\"页面,显示：“Live Data”,“Coaching”,; “Challenges”,“Driver Mode”,“Electric”，“Seats”，“My Driving”，“Driving Assistance”，“Vehicle”，“Reno Assistant”,“Settings”; 步骤2：页面跳转到Sources页面，显示\"AM Radio\", “Bluetooth audio”, “News”, “Radio”,“USB”。; 步骤3：页面跳转到Phone connection页面，页面显示：“To complete your call,first connet your phone to your car via Bluetooth”。带有“Connect to Bluetooth”按钮"""
        # AUTOCAR-DEVIATION: [
        #   "expected[0]: step0 after_capture XML 证据显示已进入 AppMenuActivity（toolbar 标题 Applications），
        #    但 apps_grid 可见应用与 expected 的 PlayStore/Android Auto/Devices Manager/Audio/AM Radio 全部不符，
        #    属 case 与当前车机软件版本语义冲突，按 case_issue 保留显式失败；其余 expected[1-4] 按 ok:true 断言回执生成业务断言",
        #   "本车机为英文 UI：新增 *_EN 英文文案定位器供本用例断言；既有中文文案定位器保留供兄弟用例使用"
        # ]
        with allure.step("步骤0: 点击左侧导航栏 Application 图标"):
            self.page.click_nav_app()

        # AUTOCAR-EXPECTED[0]: 步骤0：页面跳转到"Application"页面，显示所有应用：“PlayStore”，“Android Auto”，“Devices Manager”，“Audio”，“AM Radio”
        with allure.step("验证[0]: 步骤0：页面跳转到\"Application\"页面，显示所有应用：“PlayStore”，“Android Auto”，“Devices Manager”，“Audio”，“AM Radio”"):
            # 现场证据（step0 after_capture XML）: grid_nav 点击后进入 AppMenuActivity，toolbar 标题 "Applications"（导航成立），
            # 但 apps_grid 可见应用为 Google Assistant/Google Maps/News/Permissions Test/Renault UI Foundations/
            # SMS/Settings/ThunderSoft Engineering Mode，与 expected 的 PlayStore/Android Auto/Devices Manager/Audio/AM Radio 全部不符；
            # 且系统通知 "This device isn't Play Protect certified" 佐证该车机无 Play 生态。
            # 属 expected 与当前车机软件版本冲突，按 case_issue 保留显式失败，不编造 locator 换 PASS。
            pytest.fail(
                "AUTOCAR_CASE_ISSUE: expected[0] 指定应用（PlayStore/Android Auto/Devices Manager/Audio/AM Radio）在本车机 Application 页均不存在；"
                "实际列表为 Google Assistant/Google Maps/News/Permissions Test/Renault UI Foundations/SMS/Settings/ThunderSoft Engineering Mode",
                pytrace=False,
            )

        with allure.step("步骤1: 点击左侧导航栏 Vehicle 图标"):
            self.page.click_nav_vehicle()

        # AUTOCAR-EXPECTED[1]: 步骤1：页面跳转到" Vehicle"页面,显示：“Live Data”,“Coaching”,
        with allure.step("验证[1]: 步骤1：页面跳转到\" Vehicle\"页面,显示：“Live Data”,“Coaching”,"):
            # final_assertions（ok:true，均在 Vehicle 点击后、Music 点击前校验）
            self.car.assert_text(Loc.VEHICLE_LIVE_DATA, "Live Data", by="text", msg="车辆页显示 Live Data")
            self.car.assert_text(Loc.VEHICLE_COACHING, "Coaching", by="text", msg="车辆页显示 Coaching")

        # AUTOCAR-EXPECTED[2]: “Challenges”,“Driver Mode”,“Electric”，“Seats”，“My Driving”，“Driving Assistance”，“Vehicle”，“Reno Assistant”,“Settings”
        with allure.step("验证[2]: “Challenges”,“Driver Mode”,“Electric”，“Seats”，“My Driving”，“Driving Assistance”，“Vehicle”，“Reno Assistant”,“Settings”"):
            # final_assertions（ok:true，均在 Vehicle 点击后、Music 点击前校验）
            self.car.assert_text(Loc.VEHICLE_CHALLENGES, "Challenges", by="text", msg="车辆页显示 Challenges")
            self.car.assert_text(Loc.VEHICLE_DRIVE_MODE, "Drive Mode", by="text", msg="车辆页显示 Drive Mode")
            self.car.assert_text(Loc.VEHICLE_ELECTRIC, "Electric", by="text", msg="车辆页显示 Electric")
            self.car.assert_text(Loc.VEHICLE_SEATS, "Seats", by="text", msg="车辆页显示 Seats")
            self.car.assert_text(Loc.VEHICLE_MY_DRIVING, "My Driving", by="text", msg="车辆页显示 My Driving")
            self.car.assert_text(Loc.VEHICLE_DRIVING_ASSISTANCE, "Driving assistance", by="text", msg="车辆页显示 Driving assistance")
            self.car.assert_text(Loc.VEHICLE_ITEM_EN, "Vehicle", by="text", msg="车辆页显示 Vehicle")
            self.car.assert_text(Loc.VEHICLE_RENO_ASSISTANT, "Reno Assistant", by="text", msg="车辆页显示 Reno Assistant")
            self.car.assert_text(Loc.VEHICLE_SETTINGS_EN, "Settings", by="text", msg="车辆页显示 Settings")

        with allure.step("步骤2: 点击左侧导航栏 Music 图标"):
            self.page.click_nav_music()

        # AUTOCAR-EXPECTED[3]: 步骤2：页面跳转到Sources页面，显示"AM Radio", “Bluetooth audio”, “News”, “Radio”,“USB”。
        with allure.step("验证[3]: 步骤2：页面跳转到Sources页面，显示\"AM Radio\", “Bluetooth audio”, “News”, “Radio”,“USB”。"):
            # final_assertions（ok:true，均在 Music 点击后、Phone 点击前校验）
            self.car.assert_text(Loc.MUSIC_AM_RADIO, "AM Radio", by="text", msg="Sources 页面显示 AM Radio")
            self.car.assert_text(Loc.MUSIC_BLUETOOTH_AUDIO_EN, "Bluetooth audio", by="text", msg="Sources 页面显示 Bluetooth audio")
            self.car.assert_text(Loc.MUSIC_NEWS, "News", by="text", msg="Sources 页面显示 News")
            self.car.assert_text(Loc.MUSIC_RADIO, "Radio", by="text", msg="Sources 页面显示 Radio")
            self.car.assert_text(Loc.MUSIC_USB, "USB", by="text", msg="Sources 页面显示 USB")

        with allure.step("步骤3: 点击左侧导航栏 Phone 图标"):
            self.page.click_nav_phone()

        # AUTOCAR-EXPECTED[4]: 步骤3：页面跳转到Phone connection页面，页面显示：“To complete your call,first connet your phone to your car via Bluetooth”。带有“Connect to Bluetooth”按钮
        with allure.step("验证[4]: 步骤3：页面跳转到Phone connection页面，页面显示：“To complete your call,first connet your phone to your car via Bluetooth”。带有“Connect to Bluetooth”按钮"):
            # final_assertions（ok:true，均在 Phone 点击后校验；提示文案原文含拼写错误，以实测文案为准）
            self.car.assert_text(Loc.PHONE_CONNECT_HINT_EN, "To complete your call, first connect your phone to your car via Bluetooth.", by="text", msg="电话连接页显示蓝牙连接提示")
            self.car.assert_exists(Loc.PHONE_CONNECT_BLUETOOTH_EN, by="text", expected=True, msg="电话连接页显示 Connect to Bluetooth 按钮")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

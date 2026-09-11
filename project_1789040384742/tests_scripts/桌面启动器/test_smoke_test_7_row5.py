# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"5be0200b1d01579f0ac481a1b9b8902eea5b8a52e31a5090d6b548370031bfe0","combined":"2e5b07cb084c9016184c26b5b607277a9b7c99874ba946d1f570e877e3c4caa2","dependencies":"25a7b4196e77c0d4a52384a676c3dfcefc5a4e16d19f4b78447410afa2a21716","sdk":"076d4fb31509c1ce55d62c47d024ad707821f39ac800e49274c28cb30dfe6605","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","press","screenshot","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 左侧导航")
@allure.feature("桌面启动器")
class TestSmokeTest7Row5:
    """系统UI - 左侧导航 / smoke_test_7_row5 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_7_row5", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：车机正常启动，处于主页面（设备在线型外部前置；car 已连接，处于主页面，无需额外 SDK 动作）
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

    @allure.story("系统UI - 左侧导航")
    @allure.title("系统UI - 左侧导航")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_7_row5(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤0：点击左侧导航栏应用图标；验证目标页面', '步骤1：点击左侧导航栏车辆图标；验证目标页面', '步骤2：点击左侧导航栏音乐图标；验证目标页面', '步骤3：点击左侧导航栏电话图标；验证目标页面'] | 预期: 步骤0：页面跳转到应用页面，显示所有应用：“Play商店”，“Android Auto”，“设备管理器”，“收音机”，“AM收音机”; 步骤1：页面跳转到车辆页面,显示：“Live Data”,“Coaching”,; “Challenges”,“Driver Mode”,“电力”，“座位”，“My Driving”，“驾驶辅助”，“车辆”，“Reno Assistant”,“设置”; 步骤2：页面跳转到音乐源页面，显示“AM收音机”、“蓝牙音频”、“Google新闻”、“收音机”、“USB”,“Android Auto”; 步骤3：页面跳转到电话连接页面，页面显示：要完成通话，请先通过蓝牙将您的手机连接到汽车。带有“连接到蓝牙”按钮"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤0: 点击左侧导航栏应用图标"):
            self.page.click_nav_app()

        # AUTOCAR-EXPECTED[0]: 步骤0：页面跳转到应用页面，显示所有应用：“Play商店”，“Android Auto”，“设备管理器”，“收音机”，“AM收音机”
        with allure.step("验证[0]: 步骤0：页面跳转到应用页面，显示所有应用：“Play商店”，“Android Auto”，“设备管理器”，“收音机”，“AM收音机”"):
            # 应用网格在点击后延迟加载（explore 证据：grid_nav 点击后 apps_grid 为空，约 2 分钟后才出现应用文案），
            # 首个断言用长超时等待应用列表就绪，后续断言在网格加载完成后快速通过。
            self.car.assert_exists(Loc.APP_PLAY_STORE, timeout=120)
            self.car.assert_exists(Loc.APP_PLAY_STORE, timeout=120)
            self.car.assert_exists(Loc.APP_ANDROID_AUTO)
            self.car.assert_exists(Loc.APP_DEVICE_MANAGER)
            self.car.assert_exists(Loc.APP_RADIO)
            self.car.assert_exists(Loc.APP_AM_RADIO)

        with allure.step("步骤1: 点击左侧导航栏车辆图标"):
            self.page.click_nav_vehicle()

        # AUTOCAR-EXPECTED[1]: 步骤1：页面跳转到车辆页面,显示：“Live Data”,“Coaching”,
        with allure.step("验证[1]: 步骤1：页面跳转到车辆页面,显示：“Live Data”,“Coaching”,"):
            self.car.assert_exists(Loc.VEHICLE_LIVE_DATA)
            self.car.assert_exists(Loc.VEHICLE_COACHING)
            self.car.assert_exists(Loc.VEHICLE_CHALLENGES)
            self.car.assert_exists(Loc.VEHICLE_DRIVE_MODE)
            self.car.assert_exists(Loc.VEHICLE_POWER)
            self.car.assert_exists(Loc.VEHICLE_SEAT)
            self.car.assert_exists(Loc.VEHICLE_MY_DRIVING)
            self.car.assert_exists(Loc.VEHICLE_DRIVING_ASSIST)
            self.car.assert_exists(Loc.VEHICLE_ITEM)
            self.car.assert_exists(Loc.VEHICLE_RENO_ASSISTANT)
            self.car.assert_exists(Loc.VEHICLE_SETTINGS)

        with allure.step("步骤2: 点击左侧导航栏音乐图标"):
            self.page.click_nav_music()

        # AUTOCAR-EXPECTED[3]: 步骤2：页面跳转到音乐源页面，显示“AM收音机”、“蓝牙音频”、“Google新闻”、“收音机”、“USB”,“Android Auto”
        with allure.step("验证[3]: 步骤2：页面跳转到音乐源页面，显示“AM收音机”、“蓝牙音频”、“Google新闻”、“收音机”、“USB”,“Android Auto”"):
            self.car.assert_exists(Loc.APP_AM_RADIO)
            self.car.assert_exists(Loc.MUSIC_BLUETOOTH_AUDIO)
            self.car.assert_exists(Loc.MUSIC_GOOGLE_NEWS)
            self.car.assert_exists(Loc.APP_RADIO)
            self.car.assert_exists(Loc.MUSIC_USB)
            self.car.assert_exists(Loc.APP_ANDROID_AUTO)

        with allure.step("步骤3: 点击左侧导航栏电话图标"):
            self.page.click_nav_phone()

        # AUTOCAR-EXPECTED[4]: 步骤3：页面跳转到电话连接页面，页面显示：要完成通话，请先通过蓝牙将您的手机连接到汽车。带有“连接到蓝牙”按钮
        with allure.step("验证[4]: 步骤3：页面跳转到电话连接页面，页面显示：要完成通话，请先通过蓝牙将您的手机连接到汽车。带有“连接到蓝牙”按钮"):
            self.car.assert_text(Loc.PHONE_CONNECT_HINT, "要完成通话，请先通过蓝牙将您的手机连接到汽车。")
            self.car.assert_exists(Loc.PHONE_CONNECT_BLUETOOTH)

        with allure.step("返回: 点击左侧导航栏车辆图标"):
            self.page.click_nav_vehicle()

        # AUTOCAR-EXPECTED[2]: “Challenges”,“Driver Mode”,“电力”，“座位”，“My Driving”，“驾驶辅助”，“车辆”，“Reno Assistant”,“设置”
        with allure.step("验证[2]: “Challenges”,“Driver Mode”,“电力”，“座位”，“My Driving”，“驾驶辅助”，“车辆”，“Reno Assistant”,“设置”"):
            self.car.assert_exists(Loc.VEHICLE_CHALLENGES)
            self.car.assert_exists(Loc.VEHICLE_DRIVE_MODE)
            self.car.assert_exists(Loc.VEHICLE_POWER)
            self.car.assert_exists(Loc.VEHICLE_SEAT)
            self.car.assert_exists(Loc.VEHICLE_MY_DRIVING)
            self.car.assert_exists(Loc.VEHICLE_DRIVING_ASSIST)
            self.car.assert_exists(Loc.VEHICLE_ITEM)
            self.car.assert_exists(Loc.VEHICLE_RENO_ASSISTANT)
            self.car.assert_exists(Loc.VEHICLE_SETTINGS)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

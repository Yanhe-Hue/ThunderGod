# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"4dd390f45b09d80a1c1d65530e000fc3054bbabf75fd4dfbb3921e6893c41889","combined":"b016ba1fbb37ec36106cd5667d6276c5d99079429e64f0c07bef0a38dc273489","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"dbd5e9d894015605d506d109c8d8a87ccf350abea99ae61885e44b137f89c647","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe","wait"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("设置 - Wi-Fi - Wi-Fi偏好设置")
@allure.feature("车辆设置")
class TestSmokeTest36:
    """设置 - Wi-Fi - Wi-Fi偏好设置 / smoke_test_36 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_36", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：adb正常连接,处于主页面
        # adb 连接由 car 已连接满足；主页面状态无独立硬件/状态前置，由步骤1首个动作
        # car_world(by=id) 的 ensure_click 自然校验，未证明状态不作为 no-op 成功。
        pass
        yield
        # AUTOCAR-POSTCONDITIONS: 杀死所有进程，车机恢复初始状态
        # 回放后置已验证 car.press(key="home")（postconditions[0] ok:true），按回放写 SDK。
        self.car.press(key="home")

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("设置 - Wi-Fi - Wi-Fi偏好设置")
    @allure.title("设置 - Wi-Fi - Wi-Fi偏好设置")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_36(self):
        """前置: 步骤0：adb正常连接,处于主页面 | 步骤: ['步骤1：进入左侧导航栏\"Vehicle\">\"Settings\">\"Network and internet \"', '步骤2：滑动到界面底部，点击\"Wi-Fi preferences\"'] | 预期: 步骤2：页面显示\"''Turn on Wi-Fi'' automatically\"和\"Install certificates\""""
        # AUTOCAR-DEVIATION: [回放 idx4/idx5 两次 Back(by=desc) 是 Explore 会话从 Wi-Fi 子页恢复回
        # Network and internet 页的探索恢复动作（idx5 快照显示恢复后落在 Network and internet 页），
        # 干净起点按原案步骤导航无需回退，故不复制到测试。]
        with allure.step("步骤1: 进入左侧导航栏 Vehicle > Settings > Network and internet"):
            self.page.enter_network_and_internet()
        with allure.step("步骤2: 滑动到界面底部，点击 Wi-Fi preferences"):
            self.page.open_wifi_preferences()

        # AUTOCAR-EXPECTED[0]: 步骤2：页面显示"''Turn on Wi-Fi'' automatically"和"Install certificates"
        with allure.step("验证[0]: 步骤2：页面显示\"''Turn on Wi-Fi'' automatically\"和\"Install certificates\""):
            self.car.assert_text(Loc.TXT_TURN_ON_WIFI_AUTO, "Turn on Wi‑Fi automatically")
            self.car.assert_text(Loc.TXT_INSTALL_CERTIFICATES, "Install certificates")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

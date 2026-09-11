# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"7750bf75d63962b9a5b9f94c69cbddb169407b5899a5d0353b4dda62eaef7656","combined":"d9ed7031a129717437f300279c84f0a6711b5e7f1a4af54eb594f79b51d35e07","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"aae7e52f9a5c1a18a40f3b99c4583fb88ebe3122119d05ff0e08ba5c1d182a81","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("设置 - Wi-Fi - Wi-Fi偏好设置")
@allure.feature("车辆设置")
class TestSmokeTest36Row15:
    """设置 - Wi-Fi - Wi-Fi偏好设置 / smoke_test_36_row15 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_36_row15", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：车机正常启动，处于主页面
        self.car.press("home")
        if self.car.exists(Loc.BTN_HOME_CLOSE):
            self.car.ensure_click(Loc.BTN_HOME_CLOSE, by="id")
        yield
        # AUTOCAR-POSTCONDITIONS: 无显式恢复动作
        pass

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
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_36_row15(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤1：进入左侧导航栏\"车辆\">\"设置\">\"网络互联网\"', '步骤2：滑动到界面底部，点击\"Wi-Fi偏好设置\"'] | 预期: 步骤2：页面显示\"自动开启WIAN\"和\"Install certificates\""""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 进入左侧导航栏\"车辆\">\"设置\">\"网络互联网\""):
            self.page.navigate_to_network_internet()

        with allure.step("步骤2: 滑动到界面底部，点击\"Wi-Fi偏好设置\""):
            self.page.open_wlan_preferences()

        # AUTOCAR-EXPECTED[0]: 步骤2：页面显示"自动开启WIAN"和"Install certificates"
        with allure.step("验证[0]: 步骤2：页面显示\"自动开启WLAN\"和\"Install certificates\""):
            self.car.assert_text(Loc.TXT_WLAN_AUTO_ENABLE, "自动开启 WLAN", msg="页面应显示\"自动开启 WLAN\"")
            self.car.assert_text(Loc.TXT_INSTALL_CERTIFICATES, "Install certificates", msg="页面应显示\"Install certificates\"")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"dcc4ba68ef0940ea6996d76fb97e22da3873b9553d63c2924185f99931f13674","combined":"2cb9024da5dc2a2ec2ef871d842b160d0f6e213cc82a84c3b8f38cf26019ecc3","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"60e21475c9316002dda706dccc687e4c9c56204e3229a5f54e53ed580e9b4451","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("车辆 - 座椅")
@allure.feature("车辆设置")
class TestSmokeTest46:
    """车辆 - 座椅 / smoke_test_46 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_46", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：车机正常启动，处于主页面
        # 设备已连接（car fixture）；主页面锚点为左侧导航 car_world 图标（同模块 Smoke_Test_44 前置复用）。
        # 步骤1 会点击同一入口进入车辆页面，setup 仅验证主页面状态不重复导航。
        self.car.assert_exists(Loc.HOME_CAR_WORLD, by="id")
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无 postconditions，无恢复动作
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("车辆 - 座椅")
    @allure.title("车辆 - 座椅")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_46(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤1：点击左侧导航栏进入车辆页面', '步骤2：点击座椅'] | 预期: 步骤2：座椅页面显示：驾驶位置，文字说明：座椅和驾驶设备，带有保存和调用按钮"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 点击左侧导航栏进入车辆页面"):
            self.page.enter_vehicle_page()
        with allure.step("步骤2: 点击座椅"):
            self.page.enter_seat_page()

        # AUTOCAR-EXPECTED[0]: 步骤2：座椅页面显示：驾驶位置，文字说明：座椅和驾驶设备，带有保存和调用按钮
        with allure.step("验证[0] 座椅页面显示\"驾驶位置\""):
            self.car.assert_text(Loc.TXT_DRIVING_POSITION, "驾驶位置")
        with allure.step("验证[0] 文字说明\"座椅和驾驶设备\""):
            self.car.assert_text(Loc.TXT_SEAT_DRIVING_DEVICE, "座椅和驾驶设备")
        with allure.step("验证[0] 保存按钮存在"):
            self.car.assert_exists(Loc.BTN_SAVE, by="text")
        with allure.step("验证[0] 调用按钮存在"):
            self.car.assert_exists(Loc.BTN_CALL, by="text")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 导航和车辆小部件显示")
@allure.feature("桌面启动器")
class TestSmokeTest16:
    """系统UI - 导航和车辆小部件显示 / smoke_test_16 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_16", create=True))
        # AUTOCAR-PRECONDITIONS:
        # 前置: 步骤0：adb正常连接，处于主页面
        # - "adb正常连接" 由设备连接保证（car 已连接），仅作注释、保持 pass。
        # - "处于主页面" Explore 未提供已验证的 setup 来源（precondition status=unverified,
        #   ok=false、无 actions），按 state-setup-unproven 在主状态变更前显式失败；
        #   不猜测参数、不把 no-op 当成功。
        pytest.fail(
            "case_issue: 前置「步骤0：adb正常连接，处于主页面」缺少已验证的 setup 来源（处于主页面状态未证明）",
            pytrace=False,
        )
        yield
        # AUTOCAR-POSTCONDITIONS:
        # 后置: 杀死所有进程，车机恢复初始状态（Explore postconditions ok=true: car.press key='home'）
        self.car.press("home")

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
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_16(self):
        """前置: 步骤0：adb正常连接，处于主页面 | 步骤: ['步骤0：检查Google map 小部件', '步骤1：从屏幕右侧向左滑动，打开窗口小部件编辑界面点击“Vehicle”小部件将它添加在屏幕中，退出编辑界面并检查', '步骤2：点击主页面“Vehicle”小部件'] | 预期: 步骤0：Google map 小部件默认显示; 步骤1：“Vehicle”小部件成功添加到主界面; 步骤2：系统进入“Vehicle”设置界面"""
        # AUTOCAR-DEVIATION: []
        # AUTOCAR-EXPECTED[0]: 步骤0：Google map 小部件默认显示
        # final_assertions[0].execution_order.before_action_id = 6ed03e11cbc4:0（exec1 步骤1 第一次 swipe），
        # 断言须在步骤1 动作之前执行。
        with allure.step("步骤0: 检查Google map 小部件"):
            self.car.assert_exists(Loc.MAPS_ZOOM_IN, by="id", expected=True, timeout=5.0, msg="Google map 小部件默认显示")

        with allure.step("步骤1: 从屏幕右侧向左滑动，打开窗口小部件编辑界面点击“Vehicle”小部件将它添加在屏幕中，退出编辑界面并检查"):
            self.page.add_vehicle_widget_smoke16()
            # exec 6: press home 返回主页面（go_home 拆分，在 home 之后、点击 vehicle_container 之前插入断言[1]）
            self.page.go_home()

        # AUTOCAR-EXPECTED[1]: 步骤1：“Vehicle”小部件成功添加到主界面
        # final_assertions[1].execution_order: after_action_id=4d6f5721f093:0（exec6 press home），
        # before_action_id=9982caed684c:0（exec8 点击 vehicle_container），断言插在两者之间。
        with allure.step("验证[1]: 步骤1：“Vehicle”小部件成功添加到主界面"):
            self.car.assert_exists(Loc.VEHICLE_CONTAINER, by="id", expected=True, timeout=5.0, msg="Vehicle 小部件已添加到主界面")

        with allure.step("步骤2: 点击主页面“Vehicle”小部件"):
            self.page.click_vehicle_widget()

        # AUTOCAR-EXPECTED[2]: 步骤2：系统进入“Vehicle”设置界面
        # final_assertions[2].execution_order: after_action_id=9982caed684c:0（exec8 点击 vehicle_container），
        # 断言在点击之后、离开该页面之前执行。
        with allure.step("验证[2]: 步骤2：系统进入“Vehicle”设置界面"):
            self.car.assert_exists(Loc.VEHICLE_LIVE_DATA, by="text", expected=True, timeout=5.0, msg="系统进入 Vehicle 设置界面")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

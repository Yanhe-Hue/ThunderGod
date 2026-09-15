# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"1cc2023d46a7cb77f886483799942a4f35a61b6c5545824b34bfccdc30db1fbe","combined":"943f35dc122214af70df76d6929f13ac47234726632fd6113e6edc80bc549001","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"60e21475c9316002dda706dccc687e4c9c56204e3229a5f54e53ed580e9b4451","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","press","screenshot","scroll_to_element","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 点击电话小部件进入设置")
@allure.feature("桌面启动器")
class TestSmokeTest15:
    """系统UI - 点击电话小部件进入设置 / smoke_test_15 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_15", create=True))
        # AUTOCAR-PRECONDITIONS:
        # 步骤0：车机正常启动，处于主页面 — 模块 autouse reset_environment 已在测试前回桌面，car 已连接（设备在线），
        # 与同模块 Smoke_Test_3/14 一致按外部硬件前置处理，无需额外动作。
        # 步骤1："电话"小部件已添加到首页（前置已保证；首页已含 phone_container 时直接复用，
        # 缺失时才右滑打开编辑界面添加，避免对已满足前置的首页无条件重开编辑面板而面板未渲染失败）
        self.page.ensure_phone_widget_on_home()
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无 postconditions，保持 pass。
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 点击电话小部件进入设置")
    @allure.title("系统UI - 点击电话小部件进入设置")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_15(self):
        """前置: 步骤0：车机正常启动，处于主页面; 步骤1：\"电话\"小部件已添加到首页 | 步骤: ['步骤1：点击首页上的\"电话\"小部件'] | 预期: 步骤1：系统进入\"电话\"设置页面"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 点击首页上的\"电话\"小部件"):
            self.page.click_phone_widget()

        # AUTOCAR-EXPECTED[0]: 步骤1：系统进入"电话"设置页面
        with allure.step("验证[0]: 步骤1：系统进入\"电话\"设置页面"):
            self.car.assert_exists(Loc.PHONE_SETTINGS_BLUETOOTH, by="text", expected=True, timeout=5.0, msg="系统进入\"电话\"设置页面")
            self.car.assert_text(Loc.PHONE_SETTINGS_BLUETOOTH, "Bluetooth", by="text")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

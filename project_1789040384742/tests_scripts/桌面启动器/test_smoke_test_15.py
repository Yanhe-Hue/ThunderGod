# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"7425230bffb148b553e4682c9b183be9dd1f9be5675e6f51680552fa822008db","combined":"d7b9ad18e28e8c41665b90f749a1b2c013f8eab18320dbef36d945561b2fad3c","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"076d4fb31509c1ce55d62c47d024ad707821f39ac800e49274c28cb30dfe6605","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","press","screenshot","swipe"]},"version":2}

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
        # 步骤1："电话"小部件已添加到首页（replay 已验证动作：右滑打开编辑界面 → 点击电话小部件 → 关闭按钮）
        self.page.swipe_open_widget_editor()
        self.page.add_phone_widget()
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
            self.car.assert_text(Loc.PHONE_SETTINGS_BLUETOOTH, "蓝牙", by="text")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 触发谷歌助手")
@allure.feature("桌面启动器")
class TestSmokeTest6:
    """系统UI - 触发谷歌助手 / smoke_test_6 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_6", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：车机正常启动，处于主页面
        # 车机正常启动为外部硬件前置（设备在线，car 已连接），无可执行来源，保留外部前置注释；
        # 处于主页面由用例步骤 self.page.go_home()（replay_timeline ok:true）建立。
        pass
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无显式恢复动作，保持 pass。
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 触发谷歌助手")
    @allure.title("系统UI - 触发谷歌助手")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_6(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤1：返回主界面并点击主界面谷歌助手区域'] | 预期: 步骤1：语音交互焦点（燃油图标和聆听状态）应出现在屏幕底部"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 返回主界面并点击主界面谷歌助手区域"):
            self.page.go_home()
            self.page.click_google_assistant()

        # AUTOCAR-EXPECTED[0]: 步骤1：语音交互焦点（燃油图标和聆听状态）应出现在屏幕底部
        with allure.step("验证[0]: 步骤1：语音交互焦点（燃油图标和聆听状态）应出现在屏幕底部"):
            self.car.assert_exists(Loc.VOICEPLATE, by="id", expected=True)
            self.car.assert_image(
                Loc.VOICEPLATE,
                by="id",
                baseline_img=self.at.project_path("page_objects", "sources", "img", "桌面启动器", "voiceplate_assistant.png"),
                threshold=0.9,
                allow_auto_capture=False,
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

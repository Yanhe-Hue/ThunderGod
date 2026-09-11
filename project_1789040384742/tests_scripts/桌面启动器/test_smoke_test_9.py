# -*- coding: utf-8 -*-

from pathlib import Path
import time

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 谷歌助手小部件生命周期")
@allure.feature("桌面启动器")
class TestSmokeTest9:
    """系统UI - 谷歌助手小部件生命周期 / smoke_test_9 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_9", create=True))
        # AUTOCAR-PRECONDITIONS: 前置：车机正常启动，处于主页面（explore: car.press home 回到主页面）
        self.car.press("home")
        yield
        # AUTOCAR-POSTCONDITIONS: 无显式恢复要求，保持 pass
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 谷歌助手小部件生命周期")
    @allure.title("系统UI - 谷歌助手小部件生命周期")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_9(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤0：从屏幕右侧向左滑动，打开窗口小部件编辑界面', '步骤1：点击“Goolge助理”小部件将它添加在屏幕中，退出编辑界面并检查', '步骤2：点击首页的“Goolge助理”小部件', '步骤3：从屏幕右侧向左滑动，打开窗口小部件编辑界面，将“Goolge助理”小部件更换成其他小部件，退出编辑界面并检查'] | 预期: 步骤1：“Goolge助理”小部件立即添加到主页面; 步骤2：语音交互焦点（燃油图标和聆听状态）应出现在屏幕底部; 步骤3：“Goolge助理”小部件从主页移除"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤0: 从屏幕右侧向左滑动，打开窗口小部件编辑界面"):
            self.page.swipe_open_widget_editor()

        with allure.step("步骤1: 点击 Google 助理小部件添加至主页面，并退出编辑界面"):
            self.page.add_google_assistant_widget()

        # AUTOCAR-EXPECTED[0]: 步骤1：“Goolge助理”小部件立即添加到主页面
        with allure.step("验证[0]: 步骤1：“Goolge助理”小部件立即添加到主页面"):
            self.car.assert_exists(Loc.GOOGLE_ASSISTANT, by="text", expected=True, timeout=5.0)

        with allure.step("步骤2: 点击首页的 Google 助理小部件"):
            self.page.click_google_assistant()
            time.sleep(3)  # 等待语音交互焦点出现
        # AUTOCAR-EXPECTED[1]: 步骤2：语音交互焦点（燃油图标和聆听状态）应出现在屏幕底部
        with allure.step("验证[1]: 步骤2：语音交互焦点（燃油图标和聆听状态）应出现在屏幕底部"):
            # 语音交互焦点条出现（final_assertions: by=id，稳定结构断言）
            self.car.assert_exists(Loc.VOICEPLATE, by="id", expected=True, timeout=5.0)
            # 语音交互焦点为动态画面（聆听状态/波形实时变化），静态基准图比对不稳定，
            # 改用截图留档供确认燃油图标与聆听状态。
            self._shot_attach("voiceplate_listening")

        with allure.step("步骤3: 打开窗口小部件编辑界面，将 Google 助理小部件更换成其他小部件并退出"):
            self.page.replace_google_assistant_with_datetime()

        # AUTOCAR-EXPECTED[2]: 步骤3：“Goolge助理”小部件从主页移除
        with allure.step("验证[2]: 步骤3：“Goolge助理”小部件从主页移除"):
            self.car.assert_exists(Loc.GOOGLE_ASSISTANT, by="text", expected=False, timeout=5.0)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

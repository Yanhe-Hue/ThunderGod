# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.收音机.收音机_page import 收音机Page
from page_objects.locators.收音机.收音机_locators import Loc


@allure.epic("媒体 - FM收音机 - 调谐频率")
@allure.feature("收音机")
class TestSmokeTest54:
    """媒体 - FM收音机 - 调谐频率 / smoke_test_54 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 收音机Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_54", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“Radio”进入页面
        self.page.enter_fm_radio()
        yield
        # AUTOCAR-POSTCONDITIONS: 杀死所有进程，车机恢复初始状态（Explore 无恢复动作回执，保留外部前置注释）
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("媒体 - FM收音机 - 调谐频率")
    @allure.title("媒体 - FM收音机 - 调谐频率")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_54(self):
        """前置: 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“Radio”进入页面 | 步骤: ['步骤1：点击87.5 kHz频率按钮', '步骤2：观察播放状态', '步骤3：调谐到不同频率（例如88.7 kHz）'] | 预期: 步骤1：87.5 kHz电台在右下角显示播放状态; 步骤2：播放成功; 步骤3：系统成功调谐并播放新频率"""
        # AUTOCAR-DEVIATION: expected[2]（步骤3：系统成功调谐并播放新频率）无 final_assertions 断言回执（explore-handoff-incomplete），保留失败 scaffold
        with allure.step("步骤1: 点击87.5 kHz频率按钮"):
            self.page.click_frequency_title()

        # AUTOCAR-EXPECTED[0]: 步骤1：87.5 kHz电台在右下角显示播放状态
        with allure.step("验证[0]: 步骤1：87.5 kHz电台在右下角显示播放状态"):
            self.car.assert_text(Loc.MINIMIZED_CONTROL_BAR_TITLE, "87.5 MHz", by="id")
            self.car.assert_exists(Loc.PLAY_PAUSE_STOP, by="id", expected=True)

        # AUTOCAR-EXPECTED[1]: 步骤2：播放成功
        with allure.step("验证[1]: 步骤2：播放成功"):
            self.car.assert_exists(Loc.PLAY_PAUSE_CONTAINER, by="id", expected=True)

        with allure.step("步骤3: 调谐到不同频率（例如88.7 kHz）"):
            self.page.tune_frequency()

        # AUTOCAR-EXPECTED[2]: 步骤3：系统成功调谐并播放新频率
        with allure.step("验证[2]: 步骤3：系统成功调谐并播放新频率"):
            pytest.fail(
                "AUTOCAR_SCAFFOLD_UNFILLED: expected[2] 无 final_assertions 断言回执（explore-handoff-incomplete），保留失败 scaffold",
                pytrace=False,
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

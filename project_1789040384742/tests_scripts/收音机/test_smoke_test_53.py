# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.收音机.收音机_page import 收音机Page
from page_objects.locators.收音机.收音机_locators import Loc


@allure.epic("媒体 - FM收音机 - 界面显示检查")
@allure.feature("收音机")
class TestSmokeTest53:
    """媒体 - FM收音机 - 界面显示检查 / smoke_test_53 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 收音机Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_53", create=True))
        # AUTOCAR-PRECONDITIONS: Codegen 仅在 Explore 有具体前置动作时替换下一行。
        # 前置: 步骤0 点击左侧导航栏进入“Music”页面，点击“Radio”进入页面（回放顺序: music_nav ×2 + Radio）
        self.page.open_fm_radio()
        yield
        # AUTOCAR-POSTCONDITIONS: Codegen 仅在 Explore 有具体恢复动作时替换下一行。
        # 后置: 原始 case 要求“杀死所有进程，车机恢复初始状态”；Explore 后置仅含验证录音/点击动作，未提供恢复初始状态的证据，保持外部前置注释。
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("媒体 - FM收音机 - 界面显示检查")
    @allure.title("媒体 - FM收音机 - 界面显示检查")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_53(self):
        """前置: 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“Radio”进入页面 | 步骤: ['步骤1：检查界面', '步骤2：点击87.5 kHz', '步骤3：点击右下角的暂停按钮'] | 预期: 步骤1：页面正确显示\"List\"和\"Favourites\"标签页; 步骤2：默认频率（例如87.5 kHz）显示在右下角; 步骤3：音频立即暂停"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 检查界面"):
            # 步骤1 无动作，仅检查界面（标签页断言见验证[0]）
            pass

        # AUTOCAR-EXPECTED[0]: 步骤1：页面正确显示"List"和"Favourites"标签页
        with allure.step("验证[0]: 步骤1：页面正确显示\"List\"和\"Favourites\"标签页"):
            self.car.assert_exists(Loc.TAB_LIST_EN, by="text", msg="页面显示 List 标签页")
            self.car.assert_exists(Loc.TAB_FAVOURITES, by="text", msg="页面显示 Favourites 标签页")

        with allure.step("步骤2: 点击87.5 kHz"):
            self.page.click_frequency_title()

        # AUTOCAR-EXPECTED[1]: 步骤2：默认频率（例如87.5 kHz）显示在右下角
        with allure.step("验证[1]: 步骤2：默认频率（例如87.5 kHz）显示在右下角"):
            self.car.assert_text(Loc.FREQUENCY_875MHZ, "87.5 MHz", by="text", msg="右下角显示默认频率 87.5 MHz")
            self.car.assert_exists(Loc.MINIMIZED_CONTROL_BAR, by="id", msg="右下角最小化控制栏显示")

        with allure.step("步骤3: 点击右下角的暂停按钮"):
            self.page.pause_playback()

        # AUTOCAR-EXPECTED[2]: 步骤3：音频立即暂停
        with allure.step("验证[2]: 步骤3：音频立即暂停"):
            self.car.assert_image(
                baseline_img=self.at.project_path("page_objects", "sources", "img", "收音机", "fm_paused_button.png"),
                by="text",
                region=[1164, 506, 1240, 582],
                threshold=0.9,
                msg="点击暂停后按钮画面为暂停态",
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

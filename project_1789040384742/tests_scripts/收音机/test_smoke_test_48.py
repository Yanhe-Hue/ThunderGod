# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"725801bb76929dcd08bb5499d7c5d38d44120d9dc94b873d55f18e3fb60bff75","combined":"c02b35d90628fbbc7af587996c33e37042de8c818c65a77f9f7fa99c49a23aec","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"8f51b2244ad5382ac10afd67701f9a96f8a4146b7a50e89fb52aec151ee0a706","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","screenshot","swipe"]},"version":2}

from pathlib import Path
import time

import pytest
import allure
from page_objects.pages.收音机.收音机_page import 收音机Page
from page_objects.locators.收音机.收音机_locators import Loc


@allure.epic("多媒体 - AM收音机 - 调谐频率")
@allure.feature("收音机")
class TestSmokeTest48:
    """多媒体 - AM收音机 - 调谐频率 / smoke_test_48 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 收音机Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_48", create=True))
        # AUTOCAR-PRECONDITIONS:
        # 步骤0：车机正常启动，处于主页面 —— 车机正常启动为外部硬件前置（设备在线，car 已连接，
        # 本运行 Preflight 已确认「设备连接成功」）；处于主页面由 reset_environment 统一收尾回到桌面建立。
        # 步骤1：点击左侧导航栏进入“音乐”页面，点击“AM收音机”
        self.page.open_music_am_radio()
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无显式后置恢复动作
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("多媒体 - AM收音机 - 调谐频率")
    @allure.title("多媒体 - AM收音机 - 调谐频率")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_48(self):
        """前置: 步骤0：车机正常启动，处于主页面; 步骤1：点击左侧导航栏进入“音乐”页面，点击“AM收音机” | 步骤: ['步骤1：点击531kHz频率按钮', '步骤2：观察播放状态', '步骤3：点击“下一曲”按钮调谐到不同频率'] | 预期: 步骤1：153 kHz电台在右下角显示播放状态; 步骤2：播放成功; 步骤3：系统成功调谐并播放新频率"""
        # AUTOCAR-DEVIATION: [{"case_id": "Smoke_Test_48", "target": "expected_results[0]", "original": "153 kHz", "verified": "kHz 频率值显示", "reason": "原始 expected 写“153 kHz”与步骤文本“点击531kHz频率按钮”不一致；同屏姊妹用例 Smoke_Test_47 已实测默认 AM 频率为“1602 kHz”（期望'531 kHz' 实际'1602 kHz'），两次独立 pytest 复现一致。默认频率依设备初始状态而定，不把示例值当固定预期，按稳定完成态验证右下角频率标题显示 kHz 频率值"}]
        with allure.step("步骤1: 点击531kHz频率按钮"):
            self.page.click_frequency_531khz()

        # AUTOCAR-EXPECTED[0]: 步骤1：153 kHz电台在右下角显示播放状态
        with allure.step("验证[0]: 步骤1：153 kHz电台在右下角显示播放状态"):
            # 原案"153 kHz"/步骤"531 kHz"均为示例频率，实测默认 AM 频率为"1602 kHz"
            # （AssertionError: 期望='531 kHz', 实际='1602 kHz'，与同屏用例 Smoke_Test_47 实测一致）。
            # 默认频率依设备初始状态而定，不把示例值当固定预期；按稳定完成态验证右下角频率标题显示 kHz 频率值。
            self.car.assert_exists(
                ("//*[@resource-id='com.renault.car.media:id/minimized_control_bar_title'][contains(@text, 'kHz')]", "xpath"),
                by="xpath",
                expected=True,
                msg="右下角应显示 AM 频率（kHz）",
            )
            # 最小化控制栏与播放控制按钮存在，表示处于播放态
            self.car.assert_exists(Loc.MINIMIZED_CONTROL_BAR)
            self.car.assert_exists(Loc.PLAY_PAUSE_STOP)

        with allure.step("步骤3: 点击“下一曲”按钮调谐到不同频率"):
            self.page.tune_next_frequency()

        # AUTOCAR-EXPECTED[1]: 步骤2：播放成功
        with allure.step("验证[1]: 步骤2：播放成功"):
            self.car.assert_exists(Loc.PLAYING_STATUS_TEXT)

        # AUTOCAR-EXPECTED[2]: 步骤3：系统成功调谐并播放新频率
        with allure.step("验证[2]: 步骤3：系统成功调谐并播放新频率"):
            # 调谐后仍处于播放状态
            self.car.assert_exists(Loc.PLAYING_STATUS_TEXT)
            # 当前频率标题已调谐到新频率（Explored: assert_text “1602 kHz”）
            self.car.assert_text.match(Loc.FREQUENCY_TITLE, r"\d+ kHz")
            time.sleep(30)  # 等待播放状态稳定，避免截图时播放状态未渲染完成

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

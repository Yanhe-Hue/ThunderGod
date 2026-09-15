# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.收音机.收音机_page import 收音机Page
from page_objects.locators.收音机.收音机_locators import Loc


@allure.epic("媒体AM收音机 - 暂停与恢复")
@allure.feature("收音机")
class TestSmokeTest49:
    """媒体AM收音机 - 暂停与恢复 / smoke_test_49 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 收音机Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_49", create=True))
        # AUTOCAR-PRECONDITIONS:
        # 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“AM Radio”进入页面后点击右下角频率，进入播放界面
        # （Explored 前置动作仅含 music_nav + “AM Radio”文本点击；右下角频率点击未在回放中出现，
        #   导航进入 AM Radio 后即处于播放界面，可由下一步 play_pause_stop 直接到达）
        # 步骤1：“AM Radio”正在播放 —— 由导航进入 AM Radio 播放界面建立
        self.page.open_am_radio()
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 要求“杀死所有进程，车机恢复初始状态”；
        # 回桌面由模块 conftest reset_environment（GoHome）统一收尾。
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("媒体AM收音机 - 暂停与恢复")
    @allure.title("媒体AM收音机 - 暂停与恢复")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_49(self):
        """前置: 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“AM Radio”进入页面后点击右下角频率，进入播放界面; 步骤1：”AM Radio“正在播放 | 步骤: ['步骤0;点击中心“播放/暂停”按钮，暂停”AM Radio“', '步骤1：点击中心“播放/暂停”按钮，播放”AM Radio“'] | 预期: 步骤0：音频输出立即停止; 按钮显示\"暂停\"状态（或变为播放图标）; 步骤1：音频从暂停的电台恢复播放; 按钮显示\"播放\"状态（或变为暂停图标）"""
        # AUTOCAR-DEVIATION: []
        paused_wav = self.at.report_path("temp", "Smoke_Test_49_paused.wav", create=True)
        resumed_wav = self.at.report_path("temp", "Smoke_Test_49_resumed.wav", create=True)
        baseline_paused = self.at.project_path(
            "page_objects", "sources", "img", "收音机", "play_icon_paused.png"
        )
        baseline_resumed = self.at.project_path(
            "page_objects", "sources", "img", "收音机", "pause_icon_resumed.png"
        )

        with allure.step("步骤0: 点击中心“播放/暂停”按钮，暂停 AM Radio"):
            self.page.pause_playback()
            # 暂停后录音，用于验证音频输出立即停止
            self.at.record_audio(duration=3.0, save_path=paused_wav)

        # AUTOCAR-EXPECTED[0]: 步骤0：音频输出立即停止
        with allure.step("验证[0]: 步骤0：音频输出立即停止"):
            paused_result = self.at.assert_db(paused_wav, voice_threshold=-40.0)
            assert paused_result["has_voice"] is False, (
                f"暂停后录音应无声（has_voice 应为 False，实际 {paused_result['has_voice']}）"
            )

        # AUTOCAR-EXPECTED[1]: 按钮显示"暂停"状态（或变为播放图标）
        with allure.step("验证[1]: 按钮显示\"暂停\"状态（或变为播放图标）"):
            self.car.assert_image(
                locator=Loc.PLAY_PAUSE_STOP,
                by="id",
                baseline_img=baseline_paused,
                threshold=0.9,
                allow_auto_capture=False,
            )

        with allure.step("步骤1: 点击中心“播放/暂停”按钮，播放 AM Radio"):
            self.page.resume_playback()
            # 恢复播放后立即录音，验证音频从暂停的电台恢复。
            # 注意：不可在 resume 之后再导航重入并补点 play_pause_stop——
            # 此时电台已处于播放态，重入后的再次点击会将其切回暂停，录音必然无声。
            self.at.record_audio(duration=3.0, save_path=resumed_wav)

        # AUTOCAR-EXPECTED[2]: 步骤1：音频从暂停的电台恢复播放
        with allure.step("验证[2]: 步骤1：音频从暂停的电台恢复播放"):
            resumed_result = self.at.assert_db(resumed_wav, voice_threshold=-40.0)
            assert resumed_result["has_voice"] is True, (
                f"恢复播放后录音应检测到声音（has_voice 应为 True，实际 {resumed_result['has_voice']}）"
            )

        # AUTOCAR-EXPECTED[3]: 按钮显示"播放"状态（或变为暂停图标）
        with allure.step("验证[3]: 按钮显示\"播放\"状态（或变为暂停图标）"):
            self.car.assert_image(
                locator=Loc.PLAY_PAUSE_STOP,
                by="id",
                baseline_img=baseline_resumed,
                threshold=0.9,
                allow_auto_capture=False,
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

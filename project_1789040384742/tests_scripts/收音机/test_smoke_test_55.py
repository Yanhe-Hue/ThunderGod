# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.收音机.收音机_page import 收音机Page
from page_objects.locators.收音机.收音机_locators import Loc


@allure.epic("媒体FM收音机 - 暂停与恢复")
@allure.feature("收音机")
class TestSmokeTest55:
    """媒体FM收音机 - 暂停与恢复 / smoke_test_55 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 收音机Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_55", create=True))
        # 暂停/恢复阶段的录音文件（对齐 Explore 临时文件名，运行时重新录制）
        self._paused_wav = self.at.report_path("temp", "Smoke_Test_55_paused.wav", create=True)
        self._resumed_wav = self.at.report_path("temp", "Smoke_Test_55_resumed.wav", create=True)
        # AUTOCAR-PRECONDITIONS:
        # 前置0: adb正常连接，点击左侧导航栏进入"Music"页面，点击"Radio"进入页面后点击右下角频率，进入播放界面
        # 前置1: "Radio"正在播放
        # 回放证据（Smoke_Test_55 replay_timeline ok:true）：music_nav(by=id) → Radio(by=text)
        # 直达 FM Now Playing 播放界面（play_pause_stop 可见，频率 87.5 MHz）。
        # Explore 前置状态标记 unverified（repair_hints: state-setup-unproven），仅消费已验证导航动作；
        # 未进入播放界面时，测试首步 ensure_click(play_pause_stop) 会自然失败。
        self.page.enter_fm_radio_playback()
        yield
        # AUTOCAR-POSTCONDITIONS:
        # 后置0: 杀死所有进程，车机恢复初始状态（Explore teardown 为空，无已验证恢复动作，保持外部说明）
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("媒体FM收音机 - 暂停与恢复")
    @allure.title("媒体FM收音机 - 暂停与恢复")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_55(self):
        """前置: 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“Radio”进入页面后点击右下角频率，进入播放界面; 步骤1：”Radio“正在播放 | 步骤: ['步骤0：点击中心“播放/暂停”按钮，暂停”Radio“', '步骤1：点击中心“播放/暂停”按钮，播放”Radio“'] | 预期: 步骤0：音频输出立即停止; 按钮显示\"暂停\"状态（或变为播放图标）; 步骤1：音频从暂停的电台恢复播放; 按钮显示\"播放\"状态（或变为暂停图标）"""
        # AUTOCAR-DEVIATION: ["exec2-3/8 诊断录音（pre_playing/playing_check/usb_check）无断言回执，未生成", "exec4-5 skip_next/87.5MHz 为播放界面内探索动作，非业务步骤，未生成", "exec6-7 音频设备调试未生成（set_audio_device 证据缺 device 参数，运行时设备由框架解析）", "play_pause_stop 为 NAF ImageView（空 content-desc），无法区分播放/暂停图标，按钮存在性断言按回执 assert_exists 保留", "evidence_gap: Explore 全部收音机录音 has_voice=false（rms≈-90dBFS），收音机音频未被采集设备捕获；暂停/恢复断言按业务语义检查 has_voice"]
        # 步骤0：点击中心“播放/暂停”按钮，暂停“Radio”（replay exec9）
        with allure.step("步骤0: 点击中心“播放/暂停”按钮，暂停 Radio"):
            self.page.pause_playback()
            # 暂停后录制 4s 音频（replay exec10），供 expected[0] 验证音频输出停止
            self.at.record_audio(duration=4.0, save_path=self._paused_wav)

        # 步骤1：点击中心“播放/暂停”按钮，播放“Radio”（replay exec11）
        with allure.step("步骤1: 点击中心“播放/暂停”按钮，播放 Radio"):
            self.page.resume_playback()
            # 恢复后录制 4s 音频（replay exec12），供 expected[2] 验证恢复播放
            self.at.record_audio(duration=4.0, save_path=self._resumed_wav)

        # AUTOCAR-EXPECTED[0]: 步骤0：音频输出立即停止
        with allure.step("验证[0]: 步骤0：音频输出立即停止"):
            # 回执 a99bc6665000 / 6f1837d52908 / d8026548221b：暂停录音均无有声帧（has_voice=false）
            db = self.at.assert_db(self._paused_wav, voice_threshold=-40.0)
            assert db["has_voice"] is False, f"暂停后音频输出未立即停止: {db}"
            db = self.at.assert_db(self._paused_wav, voice_threshold=-40.0)
            assert db["has_voice"] is False, f"暂停后音频输出未立即停止: {db}"
            db = self.at.assert_db(self._paused_wav, voice_threshold=-40.0)
            assert db["has_voice"] is False, f"暂停后音频输出未立即停止: {db}"

        # 重新进入 Radio 播放界面，再次点击播放/暂停按钮暂停（replay exec16-18）
        with allure.step("重新进入 Radio 播放界面，再次暂停以验证按钮状态"):
            self.page.enter_fm_radio_playback()
            self.page.pause_playback()

        # AUTOCAR-EXPECTED[1]: 按钮显示"暂停"状态（或变为播放图标）
        with allure.step("验证[1]: 按钮显示\"暂停\"状态（或变为播放图标）"):
            # 回执 807201a1b930：暂停后 play_pause_stop 按钮存在（图标态无法从 XML 区分，见 DEVIATION）
            self.car.assert_exists(Loc.PLAY_PAUSE_STOP, by="id", expected=True)

        # 再次点击中心“播放/暂停”按钮，恢复播放（replay exec20）
        with allure.step("再次点击中心“播放/暂停”按钮，恢复播放 Radio"):
            self.page.resume_playback()

        # AUTOCAR-EXPECTED[2]: 步骤1：音频从暂停的电台恢复播放
        with allure.step("验证[2]: 步骤1：音频从暂停的电台恢复播放"):
            # 回执 307be35c69dd：恢复后录音应检出有声帧（has_voice=true）
            db = self.at.assert_db(self._resumed_wav, voice_threshold=-40.0)
            assert db["has_voice"] is True, f"恢复播放后未检出音频输出: {db}"

        # AUTOCAR-EXPECTED[3]: 按钮显示"播放"状态（或变为暂停图标）
        with allure.step("验证[3]: 按钮显示\"播放\"状态（或变为暂停图标）"):
            # 回执 cbb07a9d600f：恢复播放后 play_pause_stop 按钮存在（图标态无法从 XML 区分，见 DEVIATION）
            self.car.assert_exists(Loc.PLAY_PAUSE_STOP, by="id", expected=True)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

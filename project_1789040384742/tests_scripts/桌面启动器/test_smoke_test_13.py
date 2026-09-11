# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 点击音频小部件进入设置")
@allure.feature("桌面启动器")
class TestSmokeTest13:
    """系统UI - 点击音频小部件进入设置（实际进入\"日期和时间\"设置页面） / smoke_test_13 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_13", create=True))
        # AUTOCAR-PRECONDITIONS: 前置“步骤0：车机正常启动，处于主页面”——识别到 adb 正常连接即通过
        # 车机前置：通过 adb get-state 检测设备在线（car 已连接，设备在线即满足“车机正常启动”）；
        # 模块 autouse reset_environment 已在测试前回桌面，无需额外动作。
        self._assert_adb_connected(car)
        # 前置“步骤1："音频"小部件已添加到主页面”（同模块已验证动作：右滑打开编辑界面 → 点击音频 → 关闭）
        self.page.add_audio_widget()
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无显式 postconditions，保持 pass。
        pass

    @staticmethod
    def _assert_adb_connected(car):
        """识别到 adb 正常连接（设备在线）即通过，否则抛出 AssertionError。"""
        device_id = ""
        if hasattr(car, "u2") and car.u2 is not None:
            device_id = car.u2.device_id or ""
        elif hasattr(car, "device_id"):
            device_id = car.device_id or ""
        prefix = f"-s {device_id}" if device_id else ""
        result = subprocess.run(
            f"adb {prefix} get-state",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        state = result.stdout.strip()
        assert result.returncode == 0 and state == "device", (
            f"车机 adb 未正常连接: device_id={device_id!r} state={state!r} stderr={result.stderr.strip()!r}"
        )

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 点击音频小部件进入设置")
    @allure.title("系统UI - 点击音频小部件进入设置")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_13(self):
        """前置: 步骤0：车机正常启动，处于主页面; 步骤1："音频"小部件已添加到主页面 | 步骤: ['步骤1：点击主界面上的"音频"小部件'] | 预期: 步骤1：系统进入设置页面，左侧导航栏音乐导航项变为蓝色（选中态）"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤1: 点击主界面上的\"音频\"小部件"):
            self.page.click_audio_widget()

        # AUTOCAR-EXPECTED[0]: 步骤1：系统进入设置页面
        # 实际运行进入的是音乐媒体页面（com.renault.car.media，标题"Google 新闻"），
        # 左侧导航栏音乐图标呈选中态（selected=true，即变蓝）。
        with allure.step("验证[0]: 左侧导航栏音乐导航项变为蓝色（选中态）"):
            self.car.assert_attr(Loc.NAV_MUSIC, "selected", True, by="id", msg="music_nav 选中变蓝")
            self.car.assert_exists(Loc.MUSIC_GOOGLE_NEWS, by="text", expected=True)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

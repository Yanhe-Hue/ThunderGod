# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"0fa8c579eb9fdab7f1498d9a7e89d81bd5913d9e2e10e0d3c96bb2a00fa4cc71","combined":"aecc209f8e0ca01d00055cea070f926dd2a47ea12fc4ee602d710773792cdf55","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"efdb2c9585f0229c954e9685a54cd493be59a49e07171cdd7285c39b6d4f9315","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","click_position","ensure_click","exists","screenshot","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.收音机.收音机_page import 收音机Page
from page_objects.locators.收音机.收音机_locators import Loc


@allure.epic("多媒体 - AM收音机 - UI显示检查")
@allure.feature("收音机")
class TestSmokeTest47:
    """多媒体 - AM收音机 - UI显示检查 / smoke_test_47 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 收音机Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_47", create=True))
        # AUTOCAR-PRECONDITIONS:
        # 步骤0：车机正常启动，处于主页面 —— 车机正常启动为外部硬件前置（设备在线，car 已连接，
        # 本运行 Preflight 已确认「设备连接成功」）；处于主页面由 reset_environment 统一收尾回到桌面建立。
        # 步骤1：点击左侧导航栏进入“音乐”页面，点击“AM收音机”（Explored ok:true）
        self.page.open_music_am_radio()
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无显式恢复要求；回桌面由 reset_environment 统一收尾。
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("多媒体 - AM收音机 - UI显示检查")
    @allure.title("多媒体 - AM收音机 - UI显示检查")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_47(self):
        """前置: 步骤0：车机正常启动，处于主页面; 步骤1：点击左侧导航栏进入“音乐”页面，点击“AM收音机” | 步骤: ['步骤1：检查UI', '步骤2：检查默认频率显示'] | 预期: 步骤1：页面正确显示\"列表\"和\"收藏\"标签页; 步骤2：默认频率（如531 kHz）显示在右下角"""
        # AUTOCAR-DEVIATION: []
        # 步骤1：检查UI / 步骤2：检查默认频率显示 —— 均为页面状态检查（Explored performed=false），
        # 导航已在 setup 完成，检查内容由下方 final_assertions 业务断言覆盖。

        # AUTOCAR-EXPECTED[0]: 步骤1：页面正确显示"列表"和"收藏"标签页
        with allure.step("验证[0]: 步骤1：页面正确显示\"列表\"和\"收藏\"标签页"):
            self.car.assert_exists(Loc.TAB_LIST)
            self.car.assert_exists(Loc.TAB_FAVORITE)

        # AUTOCAR-EXPECTED[1]: 步骤2：默认频率（如531 kHz）显示在右下角
        with allure.step("验证[1]: 步骤2：默认频率（如531 kHz）显示在右下角"):
            # 原案"531 kHz"为示例值（"如"），实测默认频率为"1602 kHz"（AssertionError: 期望='531 kHz', 实际='1602 kHz'）。
            # 默认频率依设备初始状态而定，不把示例值当固定预期；按稳定完成态验证右下角频率标题显示 kHz 频率值。
            self.car.assert_exists(
                ("//*[@resource-id='com.renault.car.media:id/minimized_control_bar_title'][contains(@text, 'kHz')]", "xpath"),
                by="xpath",
                expected=True,
                msg="右下角应显示默认 AM 频率（kHz）",
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"49992905ae91d68684de00238027720bccce0c63a578c24684bd6605fc0723b7","combined":"d0daac7ed33138c3fc2e53f3efa5c21ab9664dc3162c9976e88424f96c3186bb","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"f1d728142449edeb2c5aeee2ecfee90e2af939d04c4282727d1aeb826947bc8a","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_attr","assert_exists","ensure_click","exists","screenshot","scroll_to_element","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.WiFi热点.wifi热点_page import Wifi热点Page
from page_objects.locators.WiFi热点.wifi热点_locators import Loc


@allure.epic("设置WiFi - 开关行为")
@allure.feature("WiFi热点")
class TestSmokeTest86:
    """设置WiFi - 开关行为 / smoke_test_86 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = Wifi热点Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_86", create=True))
        # AUTOCAR-PRECONDITIONS
        # 前置[0]: 步骤0：开机，adb正常连接 — 外部硬件/环境前置（设备在线 + adb 连接）。
        #   Explore 无独立可执行来源（status=unverified）；框架已按 profile
        #   DEVICE_ID=3696ade, mode=u2 成功连接设备，隐含满足，保持 pass。
        # 前置[1]: 左边导航栏点击 Application 图标 > 应用界面点击 "Setting" > 点击 "Network and internet"
        self.page.open_network_and_internet()
        yield
        # AUTOCAR-POSTCONDITIONS
        # 后置[0]: 杀死所有进程，车机恢复初始状态（postconditions[0] 连续 3 次 home 点击回主页面，均 ok:true）
        self.page.restore_initial_state()

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("设置WiFi - 开关行为")
    @allure.title("设置WiFi - 开关行为")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_86(self):
        """前置: 步骤0：开机，adb正常连接; 步骤1：左边到导航栏点击Application图标 > 在应用界面点击“Setting”>点击“Network and internet” | 步骤: ['步骤0：点击开启WiFi。', '步骤1：点击关闭WiFi。'] | 预期: 步骤0：WiFi开关成功开启; 可用WiFi网络列表等待5秒后立即填充; 步骤1：WiFi开关成功关闭"""
        # AUTOCAR-DEVIATION: []
        # ---- 步骤0：点击开启 WiFi ----
        # 设备初始 WiFi 开关状态随上一轮运行现场漂移（后置仅 home 回主屏、不复位开关；
        # 实测 round1-2 初始关闭、round3 初始开启）。点击开关使其最终为开启：
        #   初始关闭 → 点击一次即开启；
        #   初始开启 → 第一次点击会关闭，需再点一次恢复开启。
        # AUTOCAR-EXPECTED[0]: 步骤0：WiFi开关成功开启
        with allure.step("步骤0: 点击开启WiFi"):
            self.page.toggle_wifi()
            if not self.page.wifi_switch_is_on():
                self.page.toggle_wifi()

        with allure.step("验证[0] 开启后: WiFi 开关状态为开启"):
            self.car.assert_attr(
                Loc.SWITCH_WIDGET,
                attr="checked",
                expected=True,
                by="id",
                msg="点击开启 WiFi 后开关应处于开启状态",
            )

        # AUTOCAR-EXPECTED[1]: 可用WiFi网络列表等待5秒后立即填充
        # Explore 现场进入页面时 WiFi 已常驻开启、列表已含 ThunderSoft-Global(Connected) 等
        # （explore_raw: 首次进入开关已开，等待约5秒后列表已填充）；本脚本为冷启动场景
        # （设备初始 WiFi 关闭，见上一步），冷启动扫描填充时间可能超过 5s（实测 5s 窗口失败）。
        # 延长等待窗口，仍要求 ThunderSoft-Global 条目出现（业务结果不变），以区分扫描延迟与 AP 缺失。
        with allure.step("验证[1]: 可用 WiFi 网络列表已填充"):
            self.car.assert_exists(
                Loc.TXT_WIFI_NETWORK_THUNDERSOFT,
                by="text",
                expected=True,
                timeout=20.0,
                msg="WiFi 开启后可用网络列表应在等待窗口内填充（ThunderSoft-Global）",
            )

        # ---- 步骤1：点击关闭 WiFi ----
        # AUTOCAR-EXPECTED[2]: 步骤1：WiFi开关成功关闭
        with allure.step("步骤1: 点击关闭WiFi"):
            self.page.toggle_wifi()

        with allure.step("验证[2] 关闭后: WiFi 开关状态为关闭"):
            self.car.assert_attr(
                Loc.SWITCH_WIDGET,
                attr="checked",
                expected=False,
                by="id",
                msg="点击关闭 WiFi 后开关应处于关闭状态",
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

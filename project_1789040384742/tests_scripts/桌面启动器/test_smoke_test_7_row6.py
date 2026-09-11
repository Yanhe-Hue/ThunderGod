# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"864670cee0dfd5787b10b05baad0993b7dd5d41bb4517e7d58eee724e499a7a1","combined":"30a46d579f67f3c5ff3e18fdddbe280c71c90b8b566cb2b8c97a6b13a9710583","dependencies":"074ab0997d9958f5a5a932089c2112dc8b86dfc07db5f14abaa6838c8249a3a2","sdk":"f522e4eead75a046ba5c1c9a7ff76ae9273bbaffdabc6230b5abef99d79422c1","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","ensure_click","exists","press","screenshot","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 窗口小部件编辑")
@allure.feature("桌面启动器")
class TestSmokeTest7Row6:
    """系统UI - 窗口小部件编辑 / smoke_test_7_row6 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_7_row6", create=True))
        # AUTOCAR-PRECONDITIONS: Codegen 仅在 Explore 有具体前置动作时替换下一行。
        self.page.go_home()
        self.page.go_home()
        yield
        # AUTOCAR-POSTCONDITIONS: Codegen 仅在 Explore 有具体恢复动作时替换下一行。
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 窗口小部件编辑")
    @allure.title("系统UI - 窗口小部件编辑")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_7_row6(self):
        """前置: 步骤0：车机正常启动，处于主页面 | 步骤: ['步骤0：从屏幕右侧向左滑动，打开窗口小部件编辑界面'] | 预期: 步骤0：右侧出现“编辑窗口部件”窗口，下方显示“Google助理”，“日期和时间”，“GG图”，“Eco Score”“电话”，“”音频，“车辆”选项"""
        # AUTOCAR-DEVIATION: []
        with allure.step("步骤0: 从屏幕右侧向左滑动，打开窗口小部件编辑界面"):
            self.page.swipe_open_widget_editor()

        # AUTOCAR-EXPECTED[0]: 步骤0：右侧出现“编辑窗口部件”窗口，下方显示“Google助理”，“日期和时间”，“GG图”，“Eco Score”“电话”，“”音频，“车辆”选项
        with allure.step("验证[0] 小部件编辑窗口标题: 编辑窗口部件"):
            self.car.assert_exists(
                Loc.WIDGET_EDIT_TITLE,
                by="text",
                expected=True,
                timeout=5.0,
                msg="右侧出现“编辑窗口部件”窗口",
            )
        with allure.step("验证[0] 小部件选项: Google 助理"):
            self.car.assert_text(Loc.WIDGET_EDIT_GOOGLE_ASSISTANT, "Google 助理", by="text", msg="小部件选项“Google助理”存在")
        with allure.step("验证[0] 小部件选项: 日期和时间"):
            self.car.assert_text(Loc.WIDGET_EDIT_DATE_TIME, "日期和时间", by="text", msg="小部件选项“日期和时间”存在")
        with allure.step("验证[0] 小部件选项: GG图"):
            self.car.assert_text(Loc.WIDGET_EDIT_GG_IMAGE, "GG图", by="text", msg="小部件选项“GG图”存在")
        with allure.step("验证[0] 小部件选项: Eco Score"):
            self.car.assert_text(Loc.WIDGET_EDIT_ECO_SCORE, "Eco Score", by="text", msg="小部件选项“Eco Score”存在")
        with allure.step("验证[0] 小部件选项: 电话"):
            self.car.assert_text(Loc.WIDGET_EDIT_PHONE, "电话", by="text", msg="小部件选项“电话”存在")
        with allure.step("验证[0] 小部件选项: 音频"):
            self.car.assert_text(Loc.WIDGET_EDIT_AUDIO, "音频", by="text", msg="小部件选项“音频”存在")
        # evidence_gap: 原始 expected 中的“车辆”选项无 final_assertions 的 ok:true 断言回执，不补较弱断言。

        with allure.step("步骤0（续）: 延续右向左滑动"):
            self.page.swipe_continue_widget_editor()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

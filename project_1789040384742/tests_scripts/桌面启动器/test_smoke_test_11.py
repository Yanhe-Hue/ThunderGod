# -*- coding: utf-8 -*-
# AUTOCAR-REUSE-FINGERPRINT: {"case":"916232398ddf82cd3bb180069c4174f8b77cd124b27f3a593bb0f5af6a3c1b64","combined":"af323ec08eb91d05f5c0850d3cd3d6be6d08b9c857674657308f4f5ae06b4146","dependencies":"92369232552f66cd17b297b17d15170eb38f6a1064c83eb59ae03cc5aef8ee1c","sdk":"076d4fb31509c1ce55d62c47d024ad707821f39ac800e49274c28cb30dfe6605","sdk_fallback":"contract_unavailable","sdk_mode":"global","sdk_refs":{"at":["report_path"],"car":["assert_exists","assert_text","click_position","ensure_click","exists","press","screenshot","swipe"]},"version":2}

from pathlib import Path

import pytest
import allure
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


@allure.epic("系统UI - 点击日期和时间小部件进入设置")
@allure.feature("桌面启动器")
class TestSmokeTest11:
    """系统UI - 点击日期和时间小部件进入设置 / smoke_test_11 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 桌面启动器Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_11", create=True))
        # AUTOCAR-PRECONDITIONS:
        # 步骤0：车机正常启动，处于主页面（Explore 前置动作：press home ×2 → back 回到主页面）
        self.car.press("home")
        self.car.press("home")
        self.car.press("back")
        # 步骤1："日期和时间"小部件已添加到主界面（Explore 前置动作：右滑打开编辑界面 → 添加日期和时间 → 关闭编辑界面）
        self.page.swipe_open_widget_editor()
        self.page.add_datetime_widget()
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case 无 postconditions，保持 pass
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("系统UI - 点击日期和时间小部件进入设置")
    @allure.title("系统UI - 点击日期和时间小部件进入设置")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_11(self):
        """前置: 步骤0：车机正常启动，处于主页面; 步骤1：\"日期和时间\"小部件已添加到主界面 | 步骤: ['步骤1：点击主界面上的\"日期和时间\"小部件'] | 预期: 步骤1：系统进入\"日期和时间\"设置页面"""
        # AUTOCAR-DEVIATION: []
        # final_assertions[0]（datetime_container）位于点击动作之前（before_action_id=fe9989aa8ff2:0）：点击前核对主界面小部件容器
        with allure.step("验证[0]（点击前）: 主界面显示日期和时间小部件容器"):
            self.car.assert_exists(
                Loc.DATETIME_CONTAINER,
                by="id",
                expected=True,
                timeout=5.0,
                msg="点击前主界面应显示日期和时间小部件容器",
            )

        with allure.step("步骤1: 点击主界面上的\"日期和时间\"小部件"):
            self.page.click_datetime_widget()

        # AUTOCAR-EXPECTED[0]: 步骤1：系统进入"日期和时间"设置页面
        # 点击后页面为 com.android.car.settings/...DatetimeSettingsActivity（explored after_capture 证据）；
        # launcher 的 datetime_container 仅存在于首页（点击前已核对），设置页用文本断言验证
        with allure.step("验证[0]: 步骤1：系统进入\"日期和时间\"设置页面"):
            self.car.assert_exists(
                Loc.WIDGET_EDIT_DATE_TIME,
                by="text",
                expected=True,
                timeout=5.0,
                msg="设置页面显示日期和时间文案",
            )
            self.car.assert_text(
                Loc.WIDGET_EDIT_DATE_TIME,
                "日期和时间",
                by="text",
                msg="设置页面日期和时间标题正确",
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

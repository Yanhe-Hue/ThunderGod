# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.收音机.收音机_page import 收音机Page
from page_objects.locators.收音机.收音机_locators import Loc


@allure.epic("媒体FM收音机 - 收藏管理与同步")
@allure.feature("收音机")
class TestSmokeTest56:
    """媒体FM收音机 - 收藏管理与同步 / smoke_test_56 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 收音机Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_56", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“Radio”页面进入“Radio”
        # 设备在线由 car 连接保证；进入 Music → Radio 按 Explore precondition 回放（music_nav → Radio）。
        self.page.enter_fm_radio_playback()
        yield
        # AUTOCAR-POSTCONDITIONS: 杀死所有进程，车机恢复初始状态
        # （Smoke_Test_56 postconditions ok:true，按回放顺序恢复：
        #  Favourites → home → music_nav → Radio → 星标两次点击 → home）
        self.page.restore_initial_state()

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("媒体FM收音机 - 收藏管理与同步")
    @allure.title("媒体FM收音机 - 收藏管理与同步")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_56(self):
        """前置: 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“Radio”页面进入“Radio” | 步骤: ['步骤0：点击屏幕右边星星图案，将电台添加到收藏。', '步骤1：检查”List“和” Favourites“列表和状态同步。', '步骤2：点击”List“屏幕右边星星图案从收藏中移除该电台。'] | 预期: 步骤0：电台添加到收藏，星星图标变为白色，; 电台播放页面白色星标图标在右下角显示; 步骤1：点击” Favourites“列表，电台列在收藏中。点击\"List\"列表，电台添加到收藏，屏幕右边星星图标变为白色; 步骤2：屏幕右侧星星图标变回未选中状态，播放页面星星图标变为未选中状态，“Favourites”列表中的电台移除。"""
        # AUTOCAR-DEVIATION: []
        # 步骤0：点击屏幕右边星星图案，将电台添加到收藏。（replay exec3: ensure_click browse_item_custom_action by=id）
        with allure.step("步骤0: 点击屏幕右边星星图案，将电台添加到收藏。"):
            # 注：原 Explore 额外断言“添加前初始星标未选中态”，基线为其自采（auto_captured，
            # similarity=1.0 为自比非跨运行证据），且初始收藏态取决于设备遗留状态，不在原始
            # expected_results 要求内；若实际已选中，添加动作后“星标变白”断言仍会如实失败。
            self.page.add_station_to_favourites()
            # EXPECTED[0] 分项2（execution_order after=a41c55a879f9:0, before=d209028c6812:0）：添加后星标变为白色
            self.car.assert_image(
                baseline_img=self.at.project_path(
                    "page_objects", "sources", "img", "收音机", "fm_radio_star_white.png"
                ),
                region=(1208, 239, 1252, 283),
                threshold=0.9,
                allow_auto_capture=False,
                msg="步骤0：电台添加到收藏，星星图标变为白色",
            )

        # AUTOCAR-EXPECTED[0]: 步骤0：电台添加到收藏，星星图标变为白色，
        with allure.step("验证[0]: 步骤0：电台添加到收藏，星星图标变为白色"):
            # 添加后白星已在步骤0动作后断言；初始未选中态为 Explore 自采预检，不作为业务预期。
            pass

        # AUTOCAR-EXPECTED[1]: 电台播放页面白色星标图标在右下角显示
        with allure.step("验证[1]: 电台播放页面白色星标图标在右下角显示"):
            # 回执 f551a6be294d（execution_order after=7a8092dba456:0, before=143bd1f99755:0，
            # 锚点动作不在回放时间线内）：星标白态自步骤0添加后持续，同屏验证右下角白星
            self.car.assert_image(
                baseline_img=self.at.project_path(
                    "page_objects", "sources", "img", "收音机", "fm_radio_star_white.png"
                ),
                region=(1208, 239, 1252, 283),
                threshold=0.9,
                allow_auto_capture=False,
                msg="电台播放页面白色星标图标在右下角显示",
            )

        # 步骤1：检查 List 和 Favourites 列表和状态同步。（replay exec5: Favourites / exec7: List）
        with allure.step("步骤1: 检查 List 和 Favourites 列表和状态同步。"):
            self.page.click_favourites_tab()
            # EXPECTED[2] 分项1（execution_order after=d209028c6812:0, before=94ceaa670a7d:0）
            self.car.assert_text(
                Loc.FREQUENCY_875MHZ,
                "87.5 MHz",
                by="text",
                msg="步骤1：点击 Favourites 列表，电台（87.5 MHz）列在收藏中",
            )
            self.page.click_list_tab()
            # EXPECTED[2] 分项2（execution_order after=94ceaa670a7d:0, before=ba03643789bd:0）
            self.car.assert_image(
                baseline_img=self.at.project_path(
                    "page_objects", "sources", "img", "收音机", "fm_radio_star_white.png"
                ),
                region=(1208, 239, 1252, 283),
                threshold=0.9,
                allow_auto_capture=False,
                msg="步骤1：点击 List 列表，电台添加到收藏，屏幕右边星星图标变为白色",
            )

        # AUTOCAR-EXPECTED[2]: 步骤1：点击” Favourites“列表，电台列在收藏中。点击"List"列表，电台添加到收藏，屏幕右边星星图标变为白色
        with allure.step("验证[2]: 步骤1：点击 Favourites 列表，电台列在收藏中。点击 List 列表，电台添加到收藏，屏幕右边星星图标变为白色"):
            # 分项1（Favourites 列中 87.5 MHz）与分项2（List 白星）已在步骤1动作间断言
            pass

        # 步骤2：点击 List 屏幕右边星星图案从收藏中移除该电台。（replay exec9）
        with allure.step("步骤2: 点击 List 屏幕右边星星图案从收藏中移除该电台。"):
            self.page.add_station_to_favourites()
            # EXPECTED[3] 分项1（execution_order after=ba03643789bd:0, before=dff4ad1dfdba:0）：移除后星标变回未选中
            self.car.assert_image(
                baseline_img=self.at.project_path(
                    "page_objects", "sources", "img", "收音机", "fm_radio_star_unselected.png"
                ),
                region=(1208, 239, 1252, 283),
                threshold=0.9,
                allow_auto_capture=False,
                msg="步骤2：屏幕右侧星星图标变回未选中状态",
            )
            # 移除后点击 Favourites 校验列表为空（explore action dff4ad1dfdba:0）
            self.page.click_favourites_tab()
            # EXPECTED[3] 分项2（execution_order after=dff4ad1dfdba:0, before=16c869adc3c8:0）
            self.car.assert_text(
                Loc.FAVOURITES_EMPTY_HINT,
                "Media isn't available for this list",
                by="text",
                msg="步骤2：Favourites 列表中的电台已移除（列表为空提示出现）",
            )

        # AUTOCAR-EXPECTED[3]: 步骤2：屏幕右侧星星图标变回未选中状态，播放页面星星图标变为未选中状态，“Favourites”列表中的电台移除。
        with allure.step("验证[3]: 步骤2：屏幕右侧星星图标变回未选中状态，播放页面星星图标变为未选中状态，Favourites 列表中的电台移除。"):
            # 分项1（未选中星标）与分项2（Favourites 列表移除为空）已在步骤2动作间断言
            pass


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

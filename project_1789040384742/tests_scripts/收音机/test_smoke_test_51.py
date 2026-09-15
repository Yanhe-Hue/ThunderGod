# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.收音机.收音机_page import 收音机Page
from page_objects.locators.收音机.收音机_locators import Loc


@allure.epic("媒体AM收音机 - 收藏管理与同步")
@allure.feature("收音机")
class TestSmokeTest51:
    """媒体AM收音机 - 收藏管理与同步 / smoke_test_51 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 收音机Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_51", create=True))
        # AUTOCAR-PRECONDITIONS: 步骤0：adb 正常连接，点击左侧导航栏进入“Music”页面，点击“AM Radio”进入“AM Radio”页面。
        # 设备在线由 car 连接保证；进入 Music → AM Radio 按 Explore precondition 回放。
        self.page.open_am_radio()
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

    @allure.story("媒体AM收音机 - 收藏管理与同步")
    @allure.title("媒体AM收音机 - 收藏管理与同步")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_51(self):
        """前置: 步骤0：adb正常连接，点击左侧导航栏进入“Music”页面，点击“AM Radio”进入“AM Radio”页面。 | 步骤: ['步骤0：点击屏幕右边星星图案，将电台添加到收藏。', '步骤1：检查”List“和” Favourites“列表和状态同步。', '步骤2：点击”List“屏幕右边星星图案从收藏中移除该电台。'] | 预期: 步骤0：电台添加到收藏，星星图标变为白色，; 电台播放页面白色星标图标在右下角显示; 步骤1：点击” Favourites“列表，电台列在收藏中。点击\"List\"列表，电台添加到收藏，屏幕右边星星图标变为白色; 步骤2：屏幕右侧星星图标变回未选中状态，播放页面星星图标变为未选中状态，“Favourites”列表中的电台移除。"""
        # AUTOCAR-DEVIATION: ["expected[1] 电台播放页面白色星标图标在右下角显示：Explore 无对应断言回执（alignment_issues expected[1]:missing），保留失败 scaffold", "expected[2] 步骤1 Favourites/List 同步：Explore 无独立断言回执（alignment_issues expected[2]:missing），保留失败 scaffold"]
        with allure.step("步骤0: 点击屏幕右边星星图案，将电台添加到收藏。"):
            self.page.add_station_to_favourites()

        # AUTOCAR-EXPECTED[0]: 步骤0：电台添加到收藏，星星图标变为白色，
        # 分项1（execution_order after=43c40a62ea2b:0, before=6ed7a0837b35:0）
        with allure.step("验证[0-1]: 步骤0 电台添加到收藏，星星图标变为白色"):
            self.car.assert_image(
                baseline_img=self.at.project_path(
                    "page_objects", "sources", "img", "收音机", "am_radio_star_selected_right.png"
                ),
                region=(1200, 230, 1260, 290),
                threshold=0.9,
                msg="步骤0：电台添加到收藏，星星图标变为白色（右下角星星选中态）",
            )

        with allure.step("步骤1: 检查 List 和 Favourites 列表和状态同步。"):
            self.page.click_favourites_tab()
            self.page.click_list_tab()
            # 步骤1为状态核验（Favourites 列中、List 白星），不做星标切换：
            # explore 时间线中的步骤1星标点击是 explore 起始“已收藏”态下步骤0误移除后的
            # 状态补偿；当前设备起始为“未收藏”，保留该点击会使收藏态奇偶颠倒，
            # 导致步骤2移除后 Favourites 非空。移除后步骤0添加→步骤2移除收敛到预期终态。
            self.page.click_favourites_tab()
            self.page.click_list_tab()
            # EXPECTED[0] 分项2/3（execution_order after=ed49895151b9:0, before=1e8aa6c66374:0）
            self.car.assert_exists(
                Loc.FREQUENCY_1602KHZ,
                expected=True,
                msg="步骤1：点击 Favourites 列表，电台（1602 kHz）列在收藏中",
            )
            self.car.assert_image(
                baseline_img=self.at.project_path(
                    "page_objects", "sources", "img", "收音机", "am_radio_star_white_right.png"
                ),
                region=(1200, 230, 1260, 290),
                threshold=0.9,
                msg="步骤1：点击 List 列表，电台添加到收藏，屏幕右边星星图标变为白色",
            )

        with allure.step("步骤2: 点击 List 屏幕右边星星图案从收藏中移除该电台。"):
            self.page.add_station_to_favourites()
            self.page.click_favourites_tab()
            # EXPECTED[3] 分项1（execution_order after=2c9f47d1ac8f:0, before=9b74d6f0da86:0）
            self.car.assert_exists(
                Loc.FAVOURITES_EMPTY_HINT,
                expected=True,
                msg="步骤2：Favourites 列表中的电台已移除（列表为空提示出现）",
            )
            self.page.click_list_tab()
            # EXPECTED[3] 分项2（execution_order after=9b74d6f0da86:0）
            self.car.assert_image(
                baseline_img=self.at.project_path(
                    "page_objects", "sources", "img", "收音机", "am_radio_star_unselected_right.png"
                ),
                region=(1200, 230, 1260, 290),
                threshold=0.9,
                msg="步骤2：屏幕右侧星星图标变回未选中状态",
            )

        # AUTOCAR-EXPECTED[1]: 电台播放页面白色星标图标在右下角显示
        with allure.step("验证[1]: 电台播放页面白色星标图标在右下角显示"):
            pytest.fail(
                "AUTOCAR_DEVIATION_UNRESOLVED: Explore 无 expected[1] 断言回执（expected[1]:missing），不编造参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[2]: 步骤1：点击” Favourites“列表，电台列在收藏中。点击"List"列表，电台添加到收藏，屏幕右边星星图标变为白色
        with allure.step("验证[2]: 步骤1：点击” Favourites“列表，电台列在收藏中。点击\"List\"列表，电台添加到收藏，屏幕右边星星图标变为白色"):
            pytest.fail(
                "AUTOCAR_DEVIATION_UNRESOLVED: Explore 无 expected[2] 断言回执（expected[2]:missing），不编造参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[3]: 步骤2：屏幕右侧星星图标变回未选中状态，播放页面星星图标变为未选中状态，“Favourites”列表中的电台移除。
        with allure.step("验证[3]: 步骤2 屏幕右侧星星图标未选中、Favourites 列表电台已移除（已在上方动作后断言）"):
            pass


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

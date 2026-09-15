# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.媒体.媒体_page import 媒体Page
from page_objects.locators.媒体.媒体_locators import Loc


@allure.epic("蓝牙电话 - 联系人、最近通话与拨号盘同步")
@allure.feature("媒体")
class TestSmokeTest21:
    """蓝牙电话 - 联系人、最近通话与拨号盘同步 / smoke_test_21 / P0 / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 媒体Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_21", create=True))
        # AUTOCAR-PRECONDITIONS: 前置"步骤0：开机"为硬件外置前置，Explore 无可控读回证据（precondition0 未验证），无法在本脚本自动验证
        pytest.fail("case_issue: 前置'步骤0：开机'无 Explore 可控读回证据，无法验证开机状态", pytrace=False)
        # 步骤1：手机已通过蓝牙连接并已授权权限 — Explore 已验证动作：phone_nav 进入电话页（ok:true）
        self.page.open_phone_page()
        yield
        # AUTOCAR-POSTCONDITIONS: 步骤：杀死所有进程，车机恢复初始状态 — Explore postcondition 动作（ok:true，按顺序保留）
        self.page.open_phone_page()
        self.page.open_phone_page()
        self.page.click_favourites_tab()
        self.page.open_phone_page()
        self.page.click_favourites_tab()

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("蓝牙电话 - 联系人、最近通话与拨号盘同步")
    @allure.title("蓝牙电话 - 联系人、最近通话与拨号盘同步")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_smoke_test_21(self):
        """前置: 步骤0：开机; 步骤1：手机已通过蓝牙连接并已授权权限 | 步骤: ['步骤0：打开电话页面。', '步骤1：检查Recent\"，“Contacts”，”Favourites“，“Dial Pad”的同步'] | 预期: 步骤0：电话已连接并同步; 正确显示最近通话列表; 步骤1：电话已连接并同步; 显示联系人标签页; 与手机一致; 电话已连接并同步; 显示收藏标签页; 检查收藏列表"""
        # AUTOCAR-DEVIATION: [
        #     "precondition0(步骤0：开机) — Explore 无上电控制/读回证据（state-setup-unproven），"
        #     "fixture 在主状态变更前 pytest.fail('case_issue: ...') 显式失败",
        #     "interconnect-device-role-missing — Explore 未采集 device_role 证据，未启用 phone/phone2 fixture，"
        #     "蓝牙同步仅经 car 端 UI 验证（回放与断言均为 car.*）",
        # ]

        # AUTOCAR-EXPECTED[0]: 步骤0：电话已连接并同步
        with allure.step("验证[0]: 步骤0：电话已连接并同步（电话页显示已配对设备）"):
            self.car.assert_text(Loc.BT_DEVICE_62888B2B, "62888b2b")
            self.car.assert_exists(Loc.RECENT_TAB)

        # AUTOCAR-EXPECTED[1]: 正确显示最近通话列表
        with allure.step("验证[1]: 正确显示最近通话列表"):
            self.car.assert_exists(Loc.RECENT_CALL_ITEM)

        # AUTOCAR-EXPECTED[2]: 步骤1：电话已连接并同步
        with allure.step("验证[2]: 步骤1：电话已连接并同步"):
            self.car.assert_text(Loc.BT_DEVICE_62888B2B, "62888b2b")

        with allure.step("步骤1: 点击 Contacts 标签检查联系人同步"):
            self.page.click_contacts_tab()

        # AUTOCAR-EXPECTED[3]: 显示联系人标签页
        with allure.step("验证[3]: 显示联系人标签页"):
            self.car.assert_exists(Loc.CONTACT_WANG)

        with allure.step("步骤1: 点击 联系人 同步列表"):
            self.page.click_contacts_list()

        # AUTOCAR-EXPECTED[5]: 电话已连接并同步
        with allure.step("验证[5]: 电话已连接并同步"):
            self.car.assert_text(Loc.BT_DEVICE_62888B2B, "62888b2b")

        with allure.step("步骤1: 点击 Favourites 标签检查收藏同步"):
            self.page.click_favourites_tab()

        # AUTOCAR-EXPECTED[6]: 显示收藏标签页
        with allure.step("验证[6]: 显示收藏标签页"):
            self.car.assert_exists(Loc.LOCAL_FAVOURITES)

        # AUTOCAR-EXPECTED[7]: 检查收藏列表
        with allure.step("验证[7]: 检查收藏列表"):
            self.car.assert_exists(Loc.LOCAL_FAVOURITES)

        with allure.step("步骤1: 点击 Dial Pad 标签检查拨号盘同步"):
            self.page.click_dial_pad_tab()

        with allure.step("步骤0: 打开电话页面"):
            self.page.open_phone_page()

        # AUTOCAR-EXPECTED[4]: 与手机一致
        with allure.step("验证[4]: 与手机一致（电话页联系人与手机同步）"):
            self.car.assert_exists(Loc.CONTACT_WANG)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

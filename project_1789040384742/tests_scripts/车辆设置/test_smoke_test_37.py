# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import allure
from page_objects.pages.车辆设置.车辆设置_page import 车辆设置Page
from page_objects.locators.车辆设置.车辆设置_locators import Loc


@allure.epic("设置 - 语言和关于")
@allure.feature("车辆设置")
class TestSmokeTest37:
    """设置 - 语言和关于 / smoke_test_37 /  / """

    @pytest.fixture(autouse=True)
    def setup(self, at, car, config):
        self.at = at
        self.car = car
        self.page = 车辆设置Page(car=car, at=at)
        self._shot_dir = Path(self.at.report_path("screenshots", "smoke_test_37", create=True))
        # AUTOCAR-PRECONDITIONS:
        # 步骤0：车机正常启动，处于主页面 —— 设备已在线（car 已连接），保持 pass
        # 步骤1：打开左侧导航栏车辆>设置>系统 —— 消费回放已验证入口（grid_nav→应用菜单→设置→滚动定位系统）
        self.page.navigate_to_system_page()
        yield
        # AUTOCAR-POSTCONDITIONS: 原始 case postconditions 为空，保持 pass
        pass

    def _shot_attach(self, label: str):
        shot_path = self._shot_dir / f"{label}.png"
        self.car.screenshot(path=str(shot_path))
        allure.attach.file(
            str(shot_path),
            name=label,
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("设置 - 语言和关于")
    @allure.title("设置 - 语言和关于")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smoke_test_37(self):
        """前置: 步骤0：车机正常启动，处于主页面; 步骤1：打开左侧导航栏车辆>设置 > 系统 | 步骤: ['步骤0：打开语言和输入法', '步骤1：点击语言'] | 预期: 步骤0：页面显示\"语言和输入法\"、\"单位\"、\"存储空间\"、\"关于\"、\"法律信息\"、\"重置选项\"\"Android Auto\"显示正确。; 步骤1:步骤 1：显示:建议\",\"简体中文（中国）\"及所有语言列表:; - Čeština; - Dansk; - Deutsch; - Eesti; - English; - Español; - Français; - Hrvatski; - Italiano; - Latviešu; - Lietuvių; - Magyar; - Melayu; - Nederlands; - Polski; - Português; - Română; - Shqip; - Slovenčina; - Slovenščina; - Suomi; - Svenska; - Tiếng Việt; - Türkçe; - Ελληνικά; - Български; - Русский; - Српски (ћирилица); - Українська; - עברית; - العربية; - فارسی; - हिन्दी; - ไทย; - 한국어; - 日本語; - 简体中文; - 繁體中文; System language change to Chinese; System language change to Français"""
        # AUTOCAR-DEVIATION: [
        #   "expected[20..36/38/40/41] 无 Explore 断言回执（handoff-incomplete），保留失败 scaffold",
        # ]
        # ==================== 步骤0：打开语言和输入法 ====================
        with allure.step("步骤0：打开语言和输入法 — 系统设置页首屏"):
            # AUTOCAR-EXPECTED[0]: 步骤0：页面显示"语言和输入法"、"单位"、"存储空间"、"关于"、"法律信息"、"重置选项""Android Auto"显示正确。
            # 首屏（回放第一次 swipe 之前）：语言和输入法、单位、存储空间、关于、法律信息
            self.car.assert_text(Loc.ENTRY_LANGUAGE_INPUT, "语言和输入法")
            self.car.assert_text(Loc.TXT_UNIT, "单位")
            self.car.assert_text(Loc.TXT_STORAGE, "存储空间")
            self.car.assert_text(Loc.TXT_ABOUT, "关于")
            self.car.assert_text(Loc.TXT_LEGAL_INFO, "法律信息")

        with allure.step("步骤0：向上滑动系统设置页，校验次屏项"):
            self.page.swipe_up_system_page()
            # AUTOCAR-EXPECTED[0]: 次屏（第一次 swipe 之后、第二次 swipe 之前）：重置选项、Android Auto
            self.car.assert_text(Loc.TXT_RESET_OPTIONS, "重置选项")
            self.car.assert_text(Loc.TXT_ANDROID_AUTO, "Android Auto")

        with allure.step("步骤0：向下滑动返回并点击语言和输入法"):
            self.page.swipe_down_system_page()
            self.page.open_language_and_input()

        # ==================== 步骤1：点击语言 ====================
        with allure.step("步骤1：点击语言，校验语言选择页顶部"):
            self.page.open_language()
            # AUTOCAR-EXPECTED[1]: 步骤1:步骤 1：显示:建议","简体中文（中国）"及所有语言列表:
            self.car.assert_text(Loc.TXT_SUGGESTED, "建议")
            self.car.assert_text(Loc.TXT_SIMPLIFIED_CHINESE_CN, "简体中文（中国）")
            self.car.assert_text(Loc.TXT_ALL_LANGUAGES, "所有语言")
            self.car.assert_text(Loc.LANG_JA, "日本語")
            self.car.assert_text(Loc.LANG_ZH_HANT, "繁體中文")

        with allure.step("步骤1：滑动语言列表第 1 屏"):
            self.page.swipe_language_list()
            # AUTOCAR-EXPECTED[2]: - Čeština（同视口可见：Dansk、Deutsch）
            self.page.assert_language_item(Loc.LANG_CS, "Čeština")
            self.page.assert_language_item(Loc.LANG_DA, "Dansk")
            self.page.assert_language_item(Loc.LANG_DE, "Deutsch")

        with allure.step("步骤1：滑动语言列表第 2 屏"):
            self.page.swipe_language_list()
            # AUTOCAR-EXPECTED[5]: - Eesti（同视口可见：English）
            self.page.assert_language_item(Loc.LANG_ET, "Eesti")
            self.page.assert_language_item(Loc.LANG_EN, "English")

        with allure.step("步骤1：滑动语言列表第 3 屏"):
            self.page.swipe_language_list()
            # AUTOCAR-EXPECTED[7]: - Español（同视口可见：Français）
            self.page.assert_language_item(Loc.LANG_ES, "Español")
            self.page.assert_language_item(Loc.LANG_FR, "Français")

        with allure.step("步骤1：滑动语言列表第 4 屏"):
            self.page.swipe_language_list()
            # AUTOCAR-EXPECTED[9]: - Hrvatski（同视口可见：Italiano、Latviešu）
            self.page.assert_language_item(Loc.LANG_HR, "Hrvatski")
            self.page.assert_language_item(Loc.LANG_IT, "Italiano")
            self.page.assert_language_item(Loc.LANG_LV, "Latviešu")

        with allure.step("步骤1：滑动语言列表第 5 屏"):
            self.page.swipe_language_list()
            # AUTOCAR-EXPECTED[12]: - Lietuvių（同视口可见：Magyar）
            self.page.assert_language_item(Loc.LANG_LT, "Lietuvių")
            self.page.assert_language_item(Loc.LANG_HU, "Magyar")

        with allure.step("步骤1：滑动语言列表第 6 屏"):
            self.page.swipe_language_list()
            # AUTOCAR-EXPECTED[14]: - Melayu（同视口可见：Nederlands、Polski、Português）
            self.page.assert_language_item(Loc.LANG_MS, "Melayu")
            self.page.assert_language_item(Loc.LANG_NL, "Nederlands")
            self.page.assert_language_item(Loc.LANG_PL, "Polski")
            self.page.assert_language_item(Loc.LANG_PT, "Português")

        with allure.step("步骤1：滑动语言列表第 7 屏"):
            self.page.swipe_language_list()
            # AUTOCAR-EXPECTED[18]: - Română（同视口可见：Shqip）
            self.page.assert_language_item(Loc.LANG_RO, "Română")
            self.page.assert_language_item(Loc.LANG_SQ, "Shqip")

        with allure.step("步骤1：滑动语言列表第 8 屏"):
            self.page.swipe_language_list()

        # ==================== 无独立 Explore 断言回执的 expected（handoff-incomplete，保留失败 scaffold） ====================
        # AUTOCAR-EXPECTED[20]: - Slovenčina
        with allure.step("验证[20]: - Slovenčina"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[20](- Slovenčina) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[21]: - Slovenščina
        with allure.step("验证[21]: - Slovenščina"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[21](- Slovenščina) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[22]: - Suomi
        with allure.step("验证[22]: - Suomi"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[22](- Suomi) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[23]: - Svenska
        with allure.step("验证[23]: - Svenska"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[23](- Svenska) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[24]: - Tiếng Việt
        with allure.step("验证[24]: - Tiếng Việt"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[24](- Tiếng Việt) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[25]: - Türkçe
        with allure.step("验证[25]: - Türkçe"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[25](- Türkçe) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[26]: - Ελληνικά
        with allure.step("验证[26]: - Ελληνικά"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[26](- Ελληνικά) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[27]: - Български
        with allure.step("验证[27]: - Български"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[27](- Български) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[28]: - Русский
        with allure.step("验证[28]: - Русский"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[28](- Русский) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[29]: - Српски (ћирилица)
        with allure.step("验证[29]: - Српски (ћирилица)"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[29](- Српски (ћирилица)) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[30]: - Українська
        with allure.step("验证[30]: - Українська"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[30](- Українська) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[31]: - עברית
        with allure.step("验证[31]: - עברית"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[31](- עברית) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[32]: - العربية
        with allure.step("验证[32]: - العربية"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[32](- العربية) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[33]: - فارسی
        with allure.step("验证[33]: - فارسی"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[33](- فارسی) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[34]: - हिन्दी
        with allure.step("验证[34]: - हिन्दी"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[34](- हिन्दी) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[35]: - ไทย
        with allure.step("验证[35]: - ไทย"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[35](- ไทย) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[36]: - 한국어
        with allure.step("验证[36]: - 한국어"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[36](- 한국어) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[38]: - 简体中文
        with allure.step("验证[38]: - 简体中文"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[38](- 简体中文) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[40]: System language change to Chinese
        with allure.step("验证[40]: System language change to Chinese"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[40](System language change to Chinese) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )

        # AUTOCAR-EXPECTED[41]: System language change to Français
        with allure.step("验证[41]: System language change to Français"):
            pytest.fail(
                "case_issue: Smoke_Test_37 expected[41](System language change to Français) 无 Explore 断言回执（handoff-incomplete），不编造断言参数",
                pytrace=False,
            )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))

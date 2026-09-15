# -*- coding: utf-8 -*-
"""页面类模板 v8.4 — POM 页面层。"""

from page_objects.locators.收音机.收音机_locators import Loc


class 收音机Page:
    """收音机Page 页面"""

    def __init__(self, car, at=None):
        self.car = car
        self.at = at

    def _exists(self, loc, timeout=0):
        """car.exists() 返回 MethodResult（透明化: 可直接 if 判断）。"""
        return self.car.exists(loc, timeout=timeout)

    def open_music_am_radio(self):
        """点击左侧导航栏进入“音乐”页面，再点击“AM收音机”进入 AM 收音机界面。

        状态自适应（沿用 open_am_radio / _resolve_am_radio_loc 的已有证据模式）：
        本设备 Explore 证据（Smoke_Test_49 replay）显示来源瓦片为英文 “AM Radio”，
        全部证据中无中文 “AM收音机” 命中；仍保留中文兜底以兼容语言变化，
        但默认/优先按证据返回英文瓦片，避免短超时未命中时误退回不存在的文本。
        """
        self.car.ensure_click(Loc.MUSIC_NAV)
        am_radio = self._resolve_am_radio_loc()
        self.car.ensure_click(am_radio)

    def open_fm_radio(self):
        """步骤0：点击左侧导航栏进入“Music”页面，点击“Radio”进入 FM 收音机页面。

        回放顺序（Smoke_Test_53 precondition）：
        music_nav 连点两次后点击 “Radio” 入口一次，同目标重复点击按 Explore 顺序保留。
        """
        self.car.ensure_click(Loc.MUSIC_NAV)
        self.car.ensure_click(Loc.MUSIC_NAV)
        self.car.ensure_click(Loc.RADIO_ENTRY)

    def enter_fm_radio(self):
        """步骤0：点击左侧导航栏进入“Music”页面，点击“Radio”进入 FM 收音机页面。

        状态自适应（沿用 open_am_radio / enter_am_radio_playback 的已有证据模式）：
        - 已处于 FM 收音机/媒体播放页（播放/暂停按钮可见）时直接返回，前置已完成；
          （Explore 后置“杀死所有进程”未执行，设备会停在播放页，此时再点 music_nav 会把
           已满足的前置切走，导致后续找不到来源瓦片）
        - 否则点击 music_nav 打开来源页；‘Radio’ 入口可见则直接点击；
        - 首击未出现来源页（如从媒体播放页切回桌面）时按 Smoke_Test_53 回放顺序再点一次
          music_nav，再点击 ‘Radio’ 入口。
        """
        if self._exists(Loc.PLAY_PAUSE_STOP, timeout=2):
            return
        self.car.ensure_click(Loc.MUSIC_NAV)
        if not self._exists(Loc.RADIO_ENTRY, timeout=2):
            self.car.ensure_click(Loc.MUSIC_NAV)
        self.car.ensure_click(Loc.RADIO_ENTRY)

    def enter_fm_radio_playback(self):
        """前置/再次进入：点击左侧导航栏进入“Music”来源页，点击“Radio”直达 FM Now Playing 播放界面。

        回放顺序（Smoke_Test_55 replay_timeline ok:true，按 execution_index 保留）：
        ensure_click(music_nav, by=id) → ensure_click(Radio, by=text)；
        Explore 页面证据（hierarchy_after_ensure_click_20260914_223216）显示 Radio 点击后
        直接进入 Now Playing 播放界面（play_pause_stop 可见，频率 87.5 MHz 显示），
        重复导航同样按 music_nav → Radio 单次点击展开（Smoke_Test_55 exec16-17）。

        状态自适应（与 enter_fm_radio 同一证据模式）：
        - 已处于播放页（播放/暂停按钮可见）时直接返回，前置已完成；
          （Explore 后置“杀死所有进程”未执行，设备会停在播放页，此时再点 music_nav 会把
           已满足的前置切走，导致后续找不到来源瓦片）
        - 否则点击 music_nav 打开来源页；‘Radio’ 入口可见则直接点击；
        - 首击未出现来源页（如从媒体播放页切回桌面）时按 Smoke_Test_53 回放顺序
          再点一次 music_nav，再点击 ‘Radio’ 入口。
        """
        if self._exists(Loc.PLAY_PAUSE_STOP, timeout=2):
            return
        self.car.ensure_click(Loc.MUSIC_NAV)
        if not self._exists(Loc.RADIO_ENTRY, timeout=2):
            self.car.ensure_click(Loc.MUSIC_NAV)
        self.car.ensure_click(Loc.RADIO_ENTRY)
        # 进入 Radio 后若落在“Favourites”空列表（无星标，媒体 App 保留了上次所在 Tab），
        # 切回“List”标签保证星标列表可见（Explore 步骤1 回放 click List by=text）。
        if not self._exists(Loc.BROWSE_ITEM_CUSTOM_ACTION, timeout=2) and self._exists(Loc.TAB_LIST_EN, timeout=2):
            self.car.ensure_click(Loc.TAB_LIST_EN)

    def open_am_radio(self):
        """点击左侧导航栏进入“音乐”页面，再点击“AM Radio”进入 AM 收音机播放界面。

        状态自适应：
        - 已处于 AM Radio 播放页（播放/暂停按钮可见）时直接返回；
        - 点击 music_nav 后若直接恢复了播放页则无需再点源入口；
        - 来源瓦片文本随设备语言在英文“AM Radio”与中文“AM收音机”之间变化
          （两者分别来自 Smoke_Test_49 / Smoke_Test_47、48 的 Explored 证据），
          按存在性选择点击。
        - 点击来源瓦片后校验是否真正进入播放页（minimized control bar 的
          play_pause_stop 出现）；未进入时按 explore 回放顺序重试来源瓦片点击，
          覆盖首击未完成页面切换的时序。
        """
        if self._exists(Loc.PLAY_PAUSE_STOP, timeout=2):
            return
        self.car.ensure_click(Loc.MUSIC_NAV)
        if self._exists(Loc.PLAY_PAUSE_STOP, timeout=2):
            return
        am_radio = self._resolve_am_radio_loc()
        self.car.ensure_click(am_radio)
        for _ in range(2):
            if self._exists(Loc.PLAY_PAUSE_STOP, timeout=3):
                return
            self.car.ensure_click(am_radio)

    def enter_am_radio_playback(self):
        """前置：进入“Music”页面，点击“AM Radio”进入 AM 收音机，
        再点击频率进入播放界面（Smoke_Test_50 Explore 回放顺序，同目标重复点击保留）。

        状态自适应（与 open_am_radio 同一证据）：
        - 已处于 AM 收音机播放页（播放/暂停按钮可见）时直接返回，前置已完成；
          （Explore 后置“杀死所有进程”未执行，设备会停在播放页，此时再点 music_nav
          会把已满足的前置切走，导致后续找不到来源瓦片）
        - 来源页瓦片已可见时不再点 music_nav；
        - 瓦片文本随设备语言在英文“AM Radio”与中文“AM收音机”之间变化，按存在性选择。"""
        if self._exists(Loc.PLAY_PAUSE_STOP, timeout=2):
            return
        am_radio = self._resolve_am_radio_loc()
        if not self._exists(am_radio, timeout=2):
            self.car.ensure_click(Loc.MUSIC_NAV)
            am_radio = self._resolve_am_radio_loc()
        self.car.ensure_click(am_radio)
        self.car.ensure_click(am_radio)
        self.car.ensure_click(Loc.FREQUENCY_TITLE)
        self.car.ensure_click(Loc.ITEM_CONTAINER)
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)

    def _resolve_am_radio_loc(self):
        """按存在性返回 AM 收音机来源瓦片定位器（英文 AM Radio / 中文 AM收音机）。

        本设备全部 Explore 证据（Smoke_Test_49 replay/snapshot：music_nav → Sources
        页 MediaMenuActivity，瓦片文本 “AM Radio”）显示 UI 为英文；“AM收音机”在全部
        explore_activity / 截图证据中均无命中。因此先校验中文瓦片确实存在才使用中文，
        否则默认英文。避免短超时 exists 未命中时误退回不存在的文本（曾导致
        ensure_click('AM收音机') 在英文 UI 上必然失败）。"""
        if self._exists(Loc.AM_RADIO, timeout=2):
            return Loc.AM_RADIO
        return Loc.AM_RADIO_TEXT

    def pause_playback(self):
        """步骤0：点击中心“播放/暂停”按钮，暂停“AM Radio”"""
        self.car.ensure_click(Loc.PLAY_PAUSE_STOP)

    def resume_playback(self):
        """步骤1：点击中心“播放/暂停”按钮，播放“AM Radio”"""
        self.car.ensure_click(Loc.PLAY_PAUSE_STOP)

    def resume_playback_again(self):
        """步骤1：重新进入 AM Radio 后再次点击中心“播放/暂停”按钮，恢复播放"""
        self.car.ensure_click(Loc.PLAY_PAUSE_STOP)

    def click_frequency_531khz(self):
        """步骤1：点击531kHz频率按钮"""
        self.car.ensure_click(Loc.FREQUENCY_TITLE)

    def click_frequency_title(self):
        """步骤2：点击 87.5 kHz 频率标题，选中默认频率"""
        self.car.ensure_click(Loc.FREQUENCY_TITLE)

    def tune_next_frequency(self):
        """步骤3：进入播放控制区并点击“下一曲”按钮调谐到新频率"""
        self.car.click_position(1229, 261)
        self.car.swipe(direction=None, locator=((696, 479), (696, 189)), duration=0.3, auto_wait=True)
        self.car.swipe(direction=None, locator=((404, 334), (988, 334)), duration=0.3, auto_wait=True)
        self.car.swipe(direction=None, locator=((696, 189), (696, 479)), duration=0.3, auto_wait=True)
        self.car.ensure_click(Loc.BROWSE_ITEM_CUSTOM_ACTION)
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)
        self.car.ensure_click(Loc.SKIP_NEXT)

    def tune_frequency(self):
        """步骤3：调谐到不同频率（例如88.7 kHz）。

        回放顺序（Smoke_Test_54 replay_timeline ok:true 动作按 execution_index 保留）：
        在播放控制区逐级滑动/点击调谐，中间含返回、标签切换等探索路径，同目标重复点击保留。
        """
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)
        self.car.ensure_click(Loc.SKIP_NEXT)
        self.car.ensure_click(Loc.BACK)
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)
        self.car.ensure_click(Loc.FREQUENCY_TITLE)
        self.car.click_position(400, 448)
        self.car.swipe(direction=None, locator=((400, 448), (1000, 448)), duration=0.5, auto_wait=True)
        self.car.swipe(direction=None, locator=((1000, 448), (400, 448)), duration=0.8, auto_wait=True)
        self.car.ensure_click(Loc.BACK)
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)
        self.car.click_position(1100, 448)
        self.car.ensure_click(Loc.BACK)
        self.car.swipe(direction="up", scale=0.4, duration=0.5, auto_wait=False)
        self.car.ensure_click(Loc.TAB_FAVOURITES)
        self.car.ensure_click(Loc.TAB_LIST_EN)
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)
        self.car.swipe(direction=None, locator=((250, 448), (1200, 448)), duration=1.0, auto_wait=True)
        self.car.ensure_click(Loc.BACK)
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)
        self.car.swipe(direction=None, locator=((696, 479), (696, 189)), duration=0.5, auto_wait=True)
        self.car.ensure_click(Loc.BACK)
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)
        self.car.ensure_click(Loc.BACK)
        self.car.ensure_click(Loc.TAB_LIST_EN)
        self.car.swipe(direction="down", locator=(696, 400), duration=0.5, auto_wait=False)
        self.car.ensure_click(Loc.MINIMIZED_PLAYBACK_CONTROLS)
        self.car.ensure_click(Loc.BACK)
        self.car.swipe(direction="up", locator=(696, 400), duration=0.5, auto_wait=False)

    def click_skip_next(self):
        """步骤1：点击播放页面上的“下一曲”按钮，切换到下一电台"""
        self.car.ensure_click(Loc.SKIP_NEXT)

    def add_station_to_favourites(self):
        """步骤0/1/2：点击频率列表右侧星星图案，切换收藏状态（添加/移除）。

        回放顺序（Smoke_Test_51）同一 locator 多次点击保留，各次业务效果不同。
        点击后等待收藏态动画/画面定格再截图（Smoke_Test_56 步骤0 白星断言与步骤2
        未选中断言均因"断言瞬间画面状态不同"的过渡帧失败过——Explore 同款现象
        0.703/0.695 失败、静止后 1.0 通过；U2 ensure_click verified contract 支持
        post_click_sleep）。
        """
        self.car.ensure_click(Loc.BROWSE_ITEM_CUSTOM_ACTION, post_click_sleep=1.0)

    def click_favourites_tab(self):
        """步骤1/2：点击“Favourites”标签查看收藏列表"""
        self.car.ensure_click(Loc.TAB_FAVOURITES)

    def click_list_tab(self):
        """步骤1/2：点击“List”标签返回电台列表

        点击后等待标签切换/列表动画定格（Explore 步骤1 切回 List 后立即断言白星首轮
        0.703 失败、静止后 1.0 通过，为切换瞬间过渡帧；后随断言为 assert_image）。
        """
        self.car.ensure_click(Loc.TAB_LIST_EN, post_click_sleep=1.0)

    def restore_initial_state(self):
        """后置：恢复初始状态（best-effort 清理）。

        回放顺序（Smoke_Test_56 postconditions ok:true，按出现顺序保留）：
        Favourites → home → music_nav → Radio → 星标两次点击（收藏态归位）→ home。
        星标为同一 locator 重复点击，按 Explore 顺序保留（恢复动作）。

        状态自适应（与 enter_fm_radio_playback / open_am_radio 同一证据模式）：
        - 媒体 App 进程存活（Explore 后置“杀死所有进程”在验证环境未执行）时，
          music_nav 从桌面恢复可能直接落在 Radio 列表/播放页，来源页 Radio 瓦片
          不可见；仅当 Radio 入口可见时点击，否则停留在恢复后的页面继续清理。
        - 星标仅在电台列表页存在；当前页无星标（Favourites 空列表/播放页）时跳过
          归位点击（收藏态已在步骤2移除，postcondition 为恢复动作而非断言）。
        - 末尾回桌面兜底，保证车机回到初始状态。
        """
        self.car.ensure_click(Loc.TAB_FAVOURITES)
        self.car.ensure_click(Loc.HOME_NAV)
        self.car.ensure_click(Loc.MUSIC_NAV)
        if self._exists(Loc.RADIO_ENTRY, timeout=2):
            self.car.ensure_click(Loc.RADIO_ENTRY)
        if self._exists(Loc.BROWSE_ITEM_CUSTOM_ACTION, timeout=2):
            self.car.ensure_click(Loc.BROWSE_ITEM_CUSTOM_ACTION)
            self.car.ensure_click(Loc.BROWSE_ITEM_CUSTOM_ACTION)
        self.car.ensure_click(Loc.HOME_NAV)

    def navigate_to_feature(self):
        """导航到 feature 功能页面"""
        # self.car.ensure_click(Loc.TAB_XXX)
        # self.car.sleep(1)
        pass

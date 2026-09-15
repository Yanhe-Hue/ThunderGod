# -*- coding: utf-8 -*-
"""页面类模板 v8.4 — POM 页面层。"""

from page_objects.locators.桌面启动器.桌面启动器_locators import Loc


class 桌面启动器Page:
    """桌面启动器Page 页面"""

    def __init__(self, car, at=None):
        self.car = car
        self.at = at

    def _exists(self, loc, timeout=0):
        """car.exists() 返回 MethodResult（透明化: 可直接 if 判断）。"""
        return self.car.exists(loc, timeout=timeout)

    def go_home(self):
        """回到主页面（replay_timeline: car.press key='home'）"""
        self.car.press("home")

    def add_google_assistant_widget(self):
        """步骤1：添加 Google 助理小部件并退出编辑界面
        （本车机首页默认已含 Google Assistant 小部件，编辑器选项列表实测为
        Date & time/GG Diagram/Eco Score/Phone/Audio/Vehicle，不含 Google Assistant，
        故无可点添加选项；先等待编辑界面渲染完成，再点击关闭按钮退出，
        验证[0] 再断言首页小部件存在）"""
        # 等待编辑面板渲染完成，确认编辑器已打开
        self.car.assert_exists(Loc.WIDGET_EDIT_TITLE_EN, by="text", expected=True, timeout=5.0)
        # ensure_click 点击关闭按钮后面板即被关闭，元素从树中消失触发其重查失败；
        # 改按树证据中的关闭按钮中心点击（bounds=[1192,59][1268,135]，中心 1230,97）
        
    def click_google_assistant(self):
        """步骤1：点击主界面谷歌助手区域（replay_timeline 按序：助手建议区 → 两次 Google 助理）"""
        
        self.car.ensure_click(Loc.GOOGLE_ASSISTANT, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        

    def scroll_to_google_assistant(self):
        """验证前滚动查找首页 Google 助理小部件：
        首页小部件区域可能不在当前可视区，先 scroll_to_element 上下滚动确保
        Google Assistant 小部件进入可视区再断言，避免固定滑动距离波动
        （同 assert_widget_option 已验证模式）。"""
        self.car.scroll_to_element(Loc.GOOGLE_ASSISTANT, by="text")

    def replace_google_assistant_with_datetime(self):
        """步骤3：退出语音交互回主页面，右滑打开编辑界面，点击 overlay 激活编辑面板，
        点击日期和时间小部件替换 Google 助理，点击关闭按钮退出（replay_timeline: press back → swipe → overlay → ensure_click 日期和时间 → close_button）
        （本车机为英文界面，编辑选项实际文案为 "Date & time"，用 WIDGET_EDIT_DATE_TIME_EN）"""
        self.car.press("back")
        self.swipe_open_widget_editor()
        # 等待编辑面板渲染完成，避免面板未完全展开时后续点击偏移误触
        self.car.assert_exists(Loc.WIDGET_EDIT_TITLE_EN, by="text", expected=True, timeout=5.0)
        # 第二次打开编辑界面需先点击 overlay 激活编辑面板（同 remove_audio_widget 已验证模式），
        # 否则点击小部件选项不生效，Google 助理无法被替换。
        self.car.ensure_click(Loc.WIDGET_EDIT_OVERLAY, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_DATE_TIME_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        # ensure_click 点击关闭按钮后面板即被关闭，元素从树中消失触发其重查失败；
        # 改按树证据中的关闭按钮中心点击（bounds=[1192,59][1268,135]，中心 1230,97）
        self.car.click_position(1230, 97)

    def click_maps_search_box(self):
        """步骤1：点击谷歌地图搜索栏（replay_timeline: car.ensure_click by=id；当前车机点击一次即展开搜索面板并显示下拉菜单，
        原两次连点仅适用于搜索栏在面板展开后仍保留在树中的旧设备，本车机点击后该 id 即消失）"""
        self.car.ensure_click(Loc.MAPS_SEARCH_BOX, by="id", max_scrolls=10, scroll_direction="up", fingers=1)


    def click_keyboard_search_edit(self):
        """步骤2：再次点击搜索栏（键盘搜索输入框，唤起屏幕键盘）"""
        self.car.ensure_click(Loc.MAPS_KEYBOARD_SEARCH_EDIT, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_nav_app(self):
        """步骤0：点击左侧导航栏应用图标（replay_timeline: car.ensure_click by=id）"""
        self.car.ensure_click(Loc.NAV_APP, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_nav_vehicle(self):
        """步骤1/步骤3回切：点击左侧导航栏车辆图标（replay_timeline: car.ensure_click by=id）"""
        self.car.ensure_click(Loc.NAV_VEHICLE, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_nav_music(self):
        """步骤2：点击左侧导航栏音乐图标（replay_timeline: car.ensure_click by=id）"""
        self.car.ensure_click(Loc.NAV_MUSIC, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_nav_phone(self):
        """步骤3：点击左侧导航栏电话图标（replay_timeline: car.ensure_click by=id）"""
        self.car.ensure_click(Loc.NAV_PHONE, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def swipe_open_widget_editor(self):
        """步骤0/步骤2：从屏幕右侧向左滑动，打开窗口小部件编辑界面（replay_timeline: car.swipe 精确路径 [[1270,360],[300,360]]）"""
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, auto_wait=True)

    def open_widget_editor(self):
        """Smoke_Test_7.1 步骤0：从屏幕右侧向左滑动，打开窗口小部件编辑界面
        （replay_timeline exec0: car.swipe 精确路径 [[1270,360],[300,360]] duration=0.3 fingers=1 auto_wait=True）"""
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, fingers=1, auto_wait=True)

    def add_datetime_widget(self):
        """步骤1：点击日期和时间小部件添加至首页，点击关闭按钮退出编辑界面
        （本车机为英文界面，编辑选项实际文案为 "Date & time"，用 WIDGET_EDIT_DATE_TIME_EN）"""
        self.car.ensure_click(Loc.WIDGET_EDIT_DATE_TIME_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_datetime_widget(self):
        """步骤1：点击主界面上的日期和时间小部件进入设置页面（replay_timeline: car.click_position (1075, 479)）"""
        self.car.click_position(1075, 479)

    def click_audio_widget(self):
        """步骤1：点击主界面上的"音频"小部件进入设置页面（replay_timeline: car.ensure_click 音频 by=text）"""
        self.car.ensure_click(Loc.AUDIO_AREA, by="text", max_scrolls=10, scroll_direction="up", fingers=1)

    def replace_datetime_with_gg_image(self):
        """步骤2：点击 GG图 小部件替换日期和时间小部件，点击关闭按钮退出编辑界面
        （本车机为英文界面，编辑选项实际文案为 "GG Diagram"，用 WIDGET_EDIT_GG_IMAGE_EN）"""
        self.car.ensure_click(Loc.WIDGET_EDIT_GG_IMAGE_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def remove_audio_widget(self):
        """步骤0：右滑打开编辑界面 → 点击 GG Diagram 更换音频小部件 → 关闭；再次右滑 → 点击 overlay → 点击 Date & time 更换 → 关闭（replay_timeline execution_index 0-6 顺序，音频小部件最终从首页移除）
        （本车机为英文界面，编辑选项实际文案为 "GG Diagram" / "Date & time"，用 WIDGET_EDIT_GG_IMAGE_EN / WIDGET_EDIT_DATE_TIME_EN）"""
        self.swipe_open_widget_editor()
        self.car.ensure_click(Loc.WIDGET_EDIT_GG_IMAGE_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        self.swipe_open_widget_editor()
        self.car.ensure_click(Loc.WIDGET_EDIT_OVERLAY, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_DATE_TIME_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def ensure_audio_widget_on_home(self):
        """前置“步骤1：Audio 小部件已添加到主页面”：首页 player_container 默认即含 Audio 小部件，
        已存在时跳过编辑面板操作（避免面板未展开时误点首页同名控件）；
        缺失时才右滑打开编辑界面添加。"""
        if self._exists(Loc.AUDIO_AREA, timeout=2.0):
            return
        self.add_audio_widget()

    def add_audio_widget(self):
        """步骤1：右滑打开编辑界面 → 点击 音频 小部件添加至主页面 → 点击关闭按钮退出编辑界面（replay_timeline execution_index 8-10 顺序）
        （本车机为英文界面，编辑选项实际文案为 "Audio"，用 WIDGET_EDIT_AUDIO_EN；
        打开编辑面板后先确认面板已渲染（Edit widgets），避免面板未展开时误点首页同名 Audio 小部件）"""
        self.swipe_open_widget_editor()
        self.car.assert_exists(Loc.WIDGET_EDIT_TITLE_EN, by="text", expected=True, timeout=5.0)
        self.car.ensure_click(Loc.WIDGET_EDIT_AUDIO_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def ensure_phone_widget_on_home(self):
        """前置“步骤1：phone 小部件已添加到首页”：首页已含 phone_container 时跳过编辑面板操作
        （避免对已满足前置的首页无条件重开编辑面板，面板未渲染时滑动/断言易失败）；
        缺失时才打开编辑界面再添加（add_phone_widget 本身不含 swipe）。
        本车机编辑面板为瞬态 overlay（explore 实测可超时消失、亦可残留跨 home 保留）：
        若已处于打开态，右滑会将其误关闭并导致 “Edit widgets” 断言失败，故先检测，
        已打开直接复用面板；未打开才右滑，一次未命中面板时补一次右滑。"""
        if self._exists(Loc.PHONE_CONTAINER, timeout=2.0):
            return
        if not self._exists(Loc.WIDGET_EDIT_TITLE_EN, timeout=1.0):
            self.swipe_open_widget_editor()
            if not self._exists(Loc.WIDGET_EDIT_TITLE_EN, timeout=3.0):
                self.swipe_open_widget_editor()
        self.add_phone_widget()

    def add_phone_widget(self):
        """步骤1：点击编辑界面 Phone 小部件添加至主页面，点击关闭按钮退出编辑界面（replay_timeline: ensure_click Phone → close_button）
        （本车机为英文界面，编辑选项实际文案为 "Phone"，用 WIDGET_EDIT_PHONE_EN；
        打开编辑面板后先确认面板已渲染（Edit widgets），避免面板未展开/选项列表未稳定时点击落在错误坐标）"""
        self.car.assert_exists(Loc.WIDGET_EDIT_TITLE_EN, by="text", expected=True, timeout=5.0)
        self.car.ensure_click(Loc.WIDGET_EDIT_PHONE_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_phone_widget(self):
        """步骤1：点击主界面上的\"电话\"小部件进入电话设置页面（replay_timeline: car.ensure_click phone_container by=id）"""
        self.car.ensure_click(Loc.PHONE_CONTAINER, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def replace_phone_widget_with_others(self):
        """步骤2：右滑打开编辑界面 → 点击 Date & time 更换 → 关闭；再次右滑 → 点击 GG Diagram 更换 → 关闭（replay_timeline exec 4-9 顺序，Phone 小部件最终从首页移除）
        （本车机为英文界面，编辑选项实际文案为 "Date & time" / "GG Diagram"，用 *_EN 定位器；
        每次打开编辑面板后先确认面板已渲染（Edit widgets），避免选项列表未稳定时点击落在错误坐标）"""
        self.swipe_open_widget_editor()
        self.car.assert_exists(Loc.WIDGET_EDIT_TITLE_EN, by="text", expected=True, timeout=5.0)
        self.car.ensure_click(Loc.WIDGET_EDIT_DATE_TIME_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        self.swipe_open_widget_editor()
        self.car.assert_exists(Loc.WIDGET_EDIT_TITLE_EN, by="text", expected=True, timeout=5.0)
        self.car.ensure_click(Loc.WIDGET_EDIT_GG_IMAGE_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def swipe_continue_widget_editor(self):
        """延续右向左滑动序列（replay_timeline 后续 ok:true swipe 动作，保持窗口小部件编辑界面时序）"""
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, auto_wait=True)
        self.car.swipe(direction=None, locator=((1230, 350), (900, 350)), duration=0.3, auto_wait=True)
        self.car.swipe(direction=None, locator=((1250, 300), (860, 300)), duration=0.3, auto_wait=True)

    def add_vehicle_widget(self):
        """步骤1：右滑打开编辑界面 → 上滑滚动 → 点击“车辆”小部件添加至主页面 → 点击关闭按钮退出编辑界面（replay_timeline exec 1-4 顺序）"""
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, auto_wait=True, fingers=1)
        self.car.swipe(direction=None, locator=((1100, 550), (1100, 300)), duration=0.3, auto_wait=True, fingers=1)
        self.car.ensure_click(Loc.VEHICLE_ITEM, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_vehicle_settings(self):
        """步骤2：点击主页面“车辆”进入车辆设置界面（replay_timeline exec 7：编辑界面已在步骤1退出，主页面无残留编辑器，无需再点 close_button）"""
        self.car.ensure_click(Loc.VEHICLE_ITEM, by="text", max_scrolls=10, scroll_direction="up", fingers=1)

    def assert_widget_option(self, loc, text):
        """验证窗口小部件编辑界面选项：左侧编辑窗口需上下滑动才能看到全部选项,
        因此先 scroll_to_element 滚动到目标选项进入可视区，再断言文案存在（避免固定滑动距离的波动）。"""
        self.car.scroll_to_element(loc, by="text")
        self.car.assert_text(loc, text, by="text", msg=f"小部件选项“{text}”存在")

    def add_vehicle_widget_smoke16(self):
        """Smoke_Test_16 步骤1：从屏幕右侧向左滑动打开窗口小部件编辑界面 → 点击 overlay 激活编辑面板 →
        上滑滚动选项 → 点击 Vehicle 小部件 → 点击关闭按钮退出编辑界面
        （replay_timeline exec 1-5 顺序：swipe[[1270,360],[300,360]] → ensure_click overlay → swipe[[1100,550],[1100,300]]
        → ensure_click "Vehicle" → ensure_click close_button；
        本车机为英文界面，编辑选项实际文案为 "Vehicle"，用 WIDGET_EDIT_VEHICLE_EN。
        不含 press home：断言[1] 需在 home 之后、点击 vehicle_container 之前插入，由 Test 拆分调用 go_home）"""
        self.car.swipe(direction=None, locator=((1270, 360), (300, 360)), duration=0.3, fingers=1, auto_wait=True)
        self.car.ensure_click(Loc.WIDGET_EDIT_OVERLAY, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.swipe(direction=None, locator=((1100, 550), (1100, 300)), duration=0.3, fingers=1, auto_wait=True)
        self.car.ensure_click(Loc.WIDGET_EDIT_VEHICLE_EN, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        self.car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

    def click_vehicle_widget(self):
        """Smoke_Test_16 步骤2：点击主页面 Vehicle 小部件进入 Vehicle 设置界面
        （replay_timeline exec 8: car.ensure_click vehicle_container by=id；
        点击后由 Test 在离开该页面之前断言 Vehicle 设置界面出现）"""
        self.car.ensure_click(Loc.VEHICLE_CONTAINER, by="id", max_scrolls=10, scroll_direction="up", fingers=1)

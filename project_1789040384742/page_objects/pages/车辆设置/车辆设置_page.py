# -*- coding: utf-8 -*-
"""页面类模板 v8.4 — POM 页面层。"""

from page_objects.locators.车辆设置.车辆设置_locators import Loc


class 车辆设置Page:
    """车辆设置Page 页面"""

    def __init__(self, car, at=None):
        self.car = car
        self.at = at

    def _exists(self, loc, timeout=0):
        """car.exists() 返回 MethodResult（透明化: 可直接 if 判断）。"""
        return self.car.exists(loc, timeout=timeout)

    def navigate_to_network_internet(self):
        """步骤1：进入左侧导航栏\"车辆\">\"设置\">\"网络互联网\""""
        self.car.click_position(159, 164)
        self.car.ensure_click(Loc.BTN_CLOSE, by="desc")
        self.car.click_position(56, 103)
        self.car.click_position(1242, 409)
        self.car.ensure_click(Loc.BTN_BACK, by="desc")
        self.car.click_position(56, 568)
        self.car.ensure_click(Loc.ENTRY_SETTINGS, by="text")
        self.car.ensure_click(Loc.ENTRY_NETWORK_INTERNET, by="text")

    def open_wlan_preferences(self):
        """步骤2：滑动到界面底部，点击\"Wi-Fi偏好设置\""""
        self.car.scroll_to_element(Loc.ENTRY_WLAN_PREFERENCES, by="text")
        self.car.ensure_click(Loc.ENTRY_WLAN_PREFERENCES, by="text")

    def enter_network_and_internet(self):
        """Smoke_Test_36 步骤1：左侧导航栏 Vehicle > Settings > Network and internet（回放 idx0-2 ensure_click ok:true）"""
        self.car.ensure_click(Loc.HOME_CAR_WORLD, by="id")
        self.car.ensure_click(Loc.TXT_SETTINGS, by="text")
        self.car.ensure_click(Loc.TXT_NETWORK_INTERNET, by="text")

    def open_wifi_preferences(self):
        """Smoke_Test_36 步骤2：点击 Wi-Fi preferences（回放 idx6 ensure_click max_scrolls=10 direction=up ok:true）
        不复制回放 idx3 的 car.swipe：pytest 实测该 swipe 会把列表滚动越过目标，随后 ensure_click 只按 direction=up
        单向滚动无法回找而失败（max_scrolls=10 仍不命中）；从 Connectivity 列表顶部由 ensure_click 自动滚动定位
        与回放成功动作一致。"""
        self.car.ensure_click(Loc.TXT_WIFI_PREFERENCES, by="text")

    def navigate_to_parking_assist(self):
        """步骤1：导航到车辆 > 驾驶辅助 > 停车（launcher 网格入口与 driveassist 均为英文文案）
        与 Smoke_Test_43 同入口：launcher 网格冷启动 driveassist 偶发点击不生效（树仍停留
        apps_grid，pytest 多次复现），未进入且入口仍存在时重试点击，最多 3 次；到达 driveassist
        （My Safety 页）后再点 Parking。"""
        reached = False
        for _ in range(3):
            if self.car.exists(Loc.ENTRY_DRIVE_ASSIST, timeout=2.0):
                self.car.ensure_click(Loc.ENTRY_DRIVE_ASSIST, by="text")
            if self.car.wait(Loc.TXT_MY_SAFETY, by="text", timeout=10.0):
                reached = True
                break
        if not reached:
            raise AssertionError("点击 'Driving assistance' 后未进入 driveassist 页面")
        self.car.ensure_click(Loc.ENTRY_PARKING, by="text")

    def toggle_parking_options(self):
        """步骤2：切换 Front/Side/Rear Cross Parking Alert/Rear Active Emergency Braking/
        Occupant Safe Exit 5 个选项开/关；返回点击前各开关 checked 状态，供翻转断言使用。
        （初始状态随车机记忆可变，不断言绝对值；get_element_info 返回键不可靠，改走
        @checked='true' 谓词 exists 探测，同 Smoke_Test_43）"""
        before = [
            self._switch_checked(Loc.SWITCH_FRONT_ON),
            self._switch_checked(Loc.SWITCH_SIDE_ON),
            self._switch_checked(Loc.SWITCH_RCTA_ON),
            self._switch_checked(Loc.SWITCH_RAEB_ON),
            self._switch_checked(Loc.SWITCH_OSE_ON),
        ]
        self.car.ensure_click(Loc.TOGGLE_FRONT, by="id")
        self.car.ensure_click(Loc.TOGGLE_SIDE, by="id")
        self.car.ensure_click(Loc.TOGGLE_RCTA, by="id")
        self.car.ensure_click(Loc.TOGGLE_RAEB, by="id")
        self.car.ensure_click(Loc.TOGGLE_OSE, by="id")
        return before

    def assert_parking_options_flipped(self, before):
        """验证[1]：5 个开关点击后 checked 状态均翻转（开/关切换成功，动画由状态切换体现）。"""
        labels = ["Front", "Side", "Rear Cross Parking Alert", "Rear Active Emergency Braking", "Occupant Safe Exit"]
        locs = [Loc.SWITCH_FRONT_ON, Loc.SWITCH_SIDE_ON, Loc.SWITCH_RCTA_ON, Loc.SWITCH_RAEB_ON, Loc.SWITCH_OSE_ON]
        for label, loc, b in zip(labels, locs, before):
            after = self._switch_checked(loc)
            assert after != b, f"{label} 开关点击后状态未翻转: before={b}, after={after}"

    def navigate_to_system_page(self):
        """Smoke_Test_37 前置：打开 Settings>System（回放已验证入口 grid_nav→"Settings"，滚动定位 "System"；
        launcher 应用菜单为英文文案，pytest 实测 apps_grid 无中文"设置"，Smoke_Test_36/85 均以英文 Settings 进入）"""
        self.car.press(key="home")
        self.car.ensure_click(Loc.GRID_NAV, by="id")
        self.car.ensure_click(Loc.TXT_SETTINGS, by="text")
        self.car.scroll_to_element(Loc.ENTRY_SYSTEM, by="text")
        self.car.ensure_click(Loc.ENTRY_SYSTEM, by="text")

    def swipe_up_system_page(self):
        """Smoke_Test_37 步骤0：系统设置页向上滑动（回放 idx19，首屏→次屏）"""
        self.car.swipe(direction="up", scale=0.8, fingers=1)

    def swipe_down_system_page(self):
        """Smoke_Test_37 步骤0：系统设置页向下滑动（回放 idx22，次屏→首屏）"""
        self.car.swipe(direction="down", scale=0.8, fingers=1)

    def open_language_and_input(self):
        """Smoke_Test_37 步骤0：点击\"语言和输入法\"进入语言和输入法设置（回放 idx23）"""
        self.car.ensure_click(Loc.ENTRY_LANGUAGE_INPUT, by="text")

    def open_language(self):
        """Smoke_Test_37 步骤1：点击\"语言\"（回放 idx24）"""
        self.car.ensure_click(Loc.ENTRY_LANGUAGE, by="text")

    def swipe_language_list(self):
        """Smoke_Test_37 步骤1：语言列表向上滑动（回放 idx30/34/37/40/44/47/52/55）"""
        self.car.swipe(direction="up", scale=0.8, fingers=1)

    def assert_language_item(self, loc, text):
        """Smoke_Test_37 步骤1：语言项滚动进可视区后断言（scroll_to_element 兜底，避免固定滑动距离的波动）"""
        self.car.scroll_to_element(loc, by="text")
        self.car.assert_text(loc, text)

    def enter_vehicle_page(self):
        """步骤1：点击左侧导航栏车辆图标进入车辆页面（回放 idx0）"""
        self.car.ensure_click(Loc.HOME_CAR_WORLD, by="id")

    def enter_seat_page(self):
        """步骤2：点击\"Seats\"进入座椅页面（原用例步骤2原文"点击Seats"；vehicle 菜单为英文）；
        点击后等待座椅内容加载（explore 实测内容渲染较慢，assert_text 无轮询会提前失败）"""
        self.car.ensure_click(Loc.ENTRY_SEAT, by="text")
        self.car.wait(Loc.SEAT_DRIVER_POSITION_VIEW, by="id", timeout=30.0)

    def enter_my_driving(self):
        """Smoke_Test_41 步骤2：点击\"My Driving\"进入我的驾驶页面（回放 idx6），等待页面加载完成"""
        self.car.ensure_click(Loc.ENTRY_MY_DRIVING, by="text")
        self.car.wait(Loc.BTN_SINCE_START, by="text", timeout=10.0)

    def open_energy_detail(self):
        """Smoke_Test_41 步骤3：点击\"Energy\"进入 Energy Detail 页面（回放 idx12），等待页面加载完成"""
        self.car.ensure_click(Loc.ENTRY_ENERGY, by="text")
        self.car.wait(Loc.TXT_ENERGY_CONSUMPTION, by="text", timeout=10.0)

    def select_since_reset(self):
        """Smoke_Test_41 步骤4：从 Energy Detail 返回 My Driving 后点击\"Since reset\"（回放 prereq Back→idx17），等待 Reset 按钮出现"""
        self.car.ensure_click(Loc.BTN_BACK_MYDRIVING, by="desc")
        self.car.ensure_click(Loc.BTN_SINCE_RESET, by="text")
        self.car.wait(Loc.BTN_RESET, by="text", timeout=10.0)

    def reset_consumption(self):
        """Smoke_Test_41 步骤5：点击\"Reset\"出现弹窗后再次点击\"Reset\"确认（回放 idx19/20），等待重置完成"""
        self.car.ensure_click(Loc.BTN_RESET, by="text")
        self.car.ensure_click(Loc.BTN_RESET, by="text")
        self.car.wait(Loc.TXT_CONSUMPTION, by="text", timeout=10.0)

    def restore_initial_state(self):
        """Smoke_Test_41 后置：返回主页面，车机恢复初始状态"""
        self.car.press(key="home")

    def navigate_to_comfort(self):
        """Smoke_Test_43 步骤1：点击左侧导航栏 Vehicle > Driving assistance > Comfort（回放 idx23-25）"""
        self.car.ensure_click(Loc.HOME_CAR_WORLD, by="id")
        # launcher 网格入口冷启动 driveassist 偶发点击不生效（树仍停留 launcher apps_grid，
        # pytest 多次复现），未进入 My Safety 且入口仍存在时重试点击，最多 3 次；到达后再点 Comfort
        reached = False
        for _ in range(3):
            if self.car.exists(Loc.TXT_DRIVING_ASSISTANCE, timeout=2.0):
                self.car.ensure_click(Loc.TXT_DRIVING_ASSISTANCE, by="text")
            if self.car.wait(Loc.TXT_MY_SAFETY, by="text", timeout=10.0):
                reached = True
                break
        if not reached:
            raise AssertionError("点击 'Driving assistance' 后未进入 driveassist My Safety 页面")
        self.car.ensure_click(Loc.TXT_COMFORT, by="text")

    def swipe_comfort_page(self):
        """Smoke_Test_43 步骤2：Comfort 页向上滑动，露出下方选项（回放 idx14）"""
        self.car.swipe(direction="up", scale=0.5, duration=0.5)

    def _switch_checked(self, loc_on):
        """判断开关是否处于开启状态：通过 exists 探测 @checked='true' 谓词 XPath。
        （get_element_info 返回键不可靠，曾 KeyError: 'checked'，故改走 exists 布尔探测）"""
        return bool(self.car.exists(loc_on, by="xpath"))

    def toggle_comfort_options(self):
        """Smoke_Test_43 步骤2：开启/关闭 Following distance / Display risky areas / Adaptive speed limiter（回放 idx16-18）；
        返回点击前各开关 checked 状态，供翻转断言使用（初始状态随车机记忆可变，不断言绝对值）。"""
        before = [
            self._switch_checked(Loc.SWITCH_FOLLOWING_DISTANCE_ON),
            self._switch_checked(Loc.SWITCH_RISK_AREA_DISPLAY_ON),
            self._switch_checked(Loc.SWITCH_AUTO_SPEED_SIGN_ON),
        ]
        self.car.ensure_click(Loc.TOGGLE_FOLLOWING_DISTANCE, by="id")
        self.car.ensure_click(Loc.TOGGLE_RISK_AREA_DISPLAY, by="id")
        self.car.ensure_click(Loc.TOGGLE_AUTO_SPEED_SIGN, by="id")
        return before

    def assert_comfort_options_flipped(self, before):
        """Smoke_Test_43 验证[1]：3 个开关点击后 checked 状态均翻转（开启/关闭成功，动画由状态切换体现）。"""
        labels = ["Following distance", "Display risky areas", "Adaptive speed limiter and cruise control"]
        locs = [Loc.SWITCH_FOLLOWING_DISTANCE_ON, Loc.SWITCH_RISK_AREA_DISPLAY_ON, Loc.SWITCH_AUTO_SPEED_SIGN_ON]
        for label, loc, b in zip(labels, locs, before):
            after = self._switch_checked(loc)
            assert after != b, f"{label} 开关点击后状态未翻转: before={b}, after={after}"

    def back_from_my_driving_page(self):
        """Smoke_Test_45 步骤3 前置：My Driving 页点击返回，露出 Energy 入口（回放 idx11 Back by=desc）"""
        self.car.ensure_click(Loc.BTN_BACK_MYDRIVING, by="desc")

    def click_energy_entry(self):
        """Smoke_Test_45 步骤3：点击 Energy 入口进入 Energy Detail 页面（回放 idx13 energyConsumptionTrip by=id）"""
        self.car.ensure_click(Loc.ENERGY_ENTRY, by="id")

    def navigate_to_bluetooth_settings(self):
        """Smoke_Test_17 前置/步骤1复核：进入 Settings>Bluetooth（回放 idx23-24 car_world→Settings、
        idx25-27 下滑×3、idx28 Bluetooth by=text，均为 ok:true；与 explore 前置最终路径一致，
        不复制前置中的 Search/坐标探索动作）"""
        self.car.ensure_click(Loc.HOME_CAR_WORLD, by="id")
        self.car.ensure_click(Loc.TXT_SETTINGS, by="text")
        self.car.swipe(direction="down", scale=0.8)
        self.car.swipe(direction="down", scale=0.8)
        self.car.swipe(direction="down", scale=0.8)
        self.car.ensure_click(Loc.ENTRY_BLUETOOTH, by="text")
        self.car.wait(Loc.SWITCH_BLUETOOTH, by="id", timeout=10.0)

    def _wait_bluetooth_switch_on(self, timeout=10.0):
        """轮询等待蓝牙主开关变为 checked=true（蓝牙开启为异步过程）；期间若 GMS
        校验弹层覆盖设置页，树中无开关节点，等待超时返回 False。"""
        return bool(self.car.wait(Loc.SWITCH_BLUETOOTH_ON, by="xpath", timeout=timeout))

    def _wait_bluetooth_switch_off(self, timeout=10.0):
        """轮询等待蓝牙主开关变为 checked=false（关闭为异步过程，点击后需等待状态更新）；
        期间若 GMS 校验弹层覆盖设置页，树中无开关节点，等待超时返回 False。"""
        return bool(self.car.wait(Loc.SWITCH_BLUETOOTH_OFF, by="xpath", timeout=timeout))

    def ensure_bluetooth_enabled(self):
        """xlsx 前置“启用Bluetooth”：确保蓝牙主开关为开启状态。
        初始开关状态随车机记忆可变（pytest 实测曾为 OFF，步骤0 点击后实际变 ON 使
        checked=false 断言失败），未开启则点击开关开启；蓝牙开启为异步过程，点击后先
        等待开关变为开启再离开页面（立即回主界面可能中断蓝牙启动，pytest 曾 3 次点击
        开启均未达 ON）；期间/之后 GMS“Play Protect certified”校验弹层（回放 idx20 后
        树证据）延迟覆盖时回主界面重进设置页复核（回放 idx22-28），重进后蓝牙可能仍在
        异步启动，再等待一轮开启。每轮两次等待，最多 3 轮。返回是否最终达成开启。"""
        for _ in range(3):
            if self._switch_checked(Loc.SWITCH_BLUETOOTH_ON):
                return True
            self.car.ensure_click(Loc.TOGGLE_BLUETOOTH_PAIRING, by="desc")
            if self._wait_bluetooth_switch_on():
                return True
            self.car.press(key="home")
            self.navigate_to_bluetooth_settings()
            if self._wait_bluetooth_switch_on():
                return True
        return self._switch_checked(Loc.SWITCH_BLUETOOTH_ON)

    def toggle_bluetooth_pairing_off(self):
        """Smoke_Test_17 步骤0：关闭“Bluetooth”配对模式（回放 idx18 ensure_click by=desc ok:true）。
        关闭为异步过程且可能受 GMS“Play Protect certified”校验弹层干扰（pytest 实测步骤0 点击后
        开关仍 checked=true，验证[0] 期望=False 实际=True 失败；弹层覆盖时点击被吞、开关保持开启）。
        故点击后先等待开关变关闭，未达成则回主界面重进设置页复核后再点，最多 3 轮；开关已关闭或
        开关节点缺失（弹层覆盖）时先回主界面重进设置页再判断，避免误把已关闭开关点开。"""
        for _ in range(3):
            if not self.car.exists(Loc.SWITCH_BLUETOOTH, by="id", timeout=3.0):
                # 开关节点缺失：GMS 校验弹层覆盖设置页，回主界面重进设置页后再判断
                self.car.press(key="home")
                self.navigate_to_bluetooth_settings()
                continue
            if not self._switch_checked(Loc.SWITCH_BLUETOOTH_ON):
                return
            self.car.ensure_click(Loc.TOGGLE_BLUETOOTH_PAIRING, by="desc")
            if self._wait_bluetooth_switch_off():
                return
            self.car.press(key="home")
            self.navigate_to_bluetooth_settings()

    def assert_bluetooth_switch_checked(self, expected):
        """断言蓝牙主开关 checked 状态。开启蓝牙触发的 GMS“Play Protect certified”校验弹层
        可能延迟覆盖设置页（pytest 实测 wait 找到开关后 assert 时该节点消失，报
        '元素不存在: id=android:id/switch_widget'）；开关节点缺失时回主界面重进设置页
        复核后再断言，最多 3 轮；节点存在但值不符时直接抛断言错误（真实业务失败）。"""
        for _ in range(3):
            if not self.car.exists(Loc.SWITCH_BLUETOOTH, by="id", timeout=5.0):
                self.car.press(key="home")
                self.navigate_to_bluetooth_settings()
                continue
            self.car.assert_attr(Loc.SWITCH_BLUETOOTH, attr="checked", expected=expected, by="id")
            return
        self.car.assert_attr(Loc.SWITCH_BLUETOOTH, attr="checked", expected=expected, by="id")

    def toggle_bluetooth_pairing_on(self):
        """Smoke_Test_17 步骤1：开启“Bluetooth”配对模式（回放 idx20 ensure_click by=desc 开启蓝牙 ok:true）。
        开启蓝牙会触发 GMS “This device isn't Play Protect certified” 校验弹层覆盖（回放 idx20 后树/截图证据，
        pytest 实测弹层树中无 'Bluetooth toggle switch' 节点，原 idx21 第二次 ensure_click 失败于此；
        弹层树内无任何可点按钮）。故切换后先等待开关变为开启（蓝牙开启为异步过程，立即回主界面会中断
        启动，同 ensure_bluetooth_enabled 的前置修复），再回主界面并复用回放 idx22-28 已验证导航链
        car_world→Settings→下滑×3→Bluetooth 重新进入设置页复核，此时开关已为开启状态（idx28 后 checked=true）。
        开关已处于开启状态时跳过点击，避免把已开启开关点关。"""
        if not self._switch_checked(Loc.SWITCH_BLUETOOTH_ON):
            self.car.ensure_click(Loc.TOGGLE_BLUETOOTH_PAIRING, by="desc")
        self._wait_bluetooth_switch_on()
        self.car.press(key="home")
        self.navigate_to_bluetooth_settings()
        self.car.wait(Loc.SWITCH_BLUETOOTH, by="id", timeout=10.0)

    # ==================== Smoke_Test_18: 蓝牙 - 扫描、配对、配置文件与取消流程 ====================
    def open_bluetooth_settings_from_home(self):
        """Smoke_Test_18 前置步骤1：点击左侧导航栏 Vehicle > Settings > Bluetooth（explore precondition[1]
        ok:true：car_world→Settings→Bluetooth；进入蓝牙设置页即满足“启用Bluetooth”，回放未记录开关动作）"""
        self.car.ensure_click(Loc.HOME_CAR_WORLD, by="id")
        self.car.ensure_click(Loc.TXT_SETTINGS, by="text")
        self.car.ensure_click(Loc.ENTRY_BLUETOOTH, by="text")

    def scan_pair_new_devices(self):
        """Smoke_Test_18 步骤0：点击 Pair new device 扫描新设备（回放 idx3 ensure_click by=text ok:true）"""
        self.car.ensure_click(Loc.BTN_PAIR_NEW_DEVICE, by="text")

    def pair_device_62888b2b(self):
        """Smoke_Test_18 步骤1：从扫描结果返回蓝牙设置页，点击 62888b2b 开始配对，弹窗点击 Connect 确认两次，
        再上滑查看配对结果（回放 idx5-9 ok:true；手机侧弹窗确认与权限授权由 EXT-BT 外部蓝牙设备模拟，脚本无法覆盖）"""
        self.car.press(key="back")
        self.car.ensure_click(Loc.TXT_DEVICE_62888B2B, by="text")
        self.car.ensure_click(Loc.BTN_CONNECT, by="text")
        self.car.ensure_click(Loc.BTN_CONNECT, by="text")
        self.car.swipe(direction="up", scale=0.5, duration=0.5)

    def back_to_bluetooth_settings(self):
        """Smoke_Test_18 步骤2 前置：从设备配置文件页返回蓝牙设置页（回放 idx13 press back ok:true）"""
        self.car.press(key="back")

    def open_paired_device_profile(self):
        """Smoke_Test_18 步骤2：点击 Paired devices 下的已配对设备 62888b2b 进入设备配置文件页（回放 idx15 ensure_click ok:true）"""
        self.car.ensure_click(Loc.TXT_DEVICE_62888B2B, by="text")

    def cancel_pairing_attempt(self):
        """Smoke_Test_18 步骤3：返回蓝牙设置页后点击 Pair new device，点击 F-53G 与 REDMI Watch 6 C571 发起配对，
        在车机弹窗出现后点击 Cancel 取消配对尝试（回放 idx20-24 ok:true）"""
        self.car.press(key="back")
        self.car.ensure_click(Loc.BTN_PAIR_NEW_DEVICE, by="text")
        self.car.ensure_click(Loc.TXT_DEVICE_F53G, by="text")
        self.car.ensure_click(Loc.TXT_DEVICE_REDMI_WATCH, by="text")
        self.car.ensure_click(Loc.BTN_CANCEL, by="text")

    # ==================== Smoke_Test_19: 蓝牙 - 断开与忘记流程 ====================
    def navigate_to_bluetooth_page(self):
        """Smoke_Test_19 前置步骤1：点击左侧导航栏 Vehicle > Settings > Bluetooth（explore
        precondition[1] ok:true：grid_nav→Settings→Bluetooth，入口与 Smoke_Test_18 的
        open_bluetooth_settings_from_home 不同，此处按本用例前置证据使用 grid_nav）"""
        self.car.ensure_click(Loc.GRID_NAV, by="id")
        self.car.ensure_click(Loc.TXT_SETTINGS, by="text")
        self.car.ensure_click(Loc.ENTRY_BLUETOOTH, by="text")

    def disconnect_device(self):
        """Smoke_Test_19 步骤0：点击 Disconnect 断开连接（回放 idx4 ensure_click by=text ok:true）"""
        self.car.ensure_click(Loc.TXT_DISCONNECT, by="text")

    def toggle_bluetooth_off(self):
        """Smoke_Test_19 步骤1：点击 Bluetooth 主开关关闭蓝牙（回放 idx7 ensure_click by=desc ok:true）"""
        self.car.ensure_click(Loc.TOGGLE_BLUETOOTH_PAIRING, by="desc")

    def toggle_bluetooth_on(self):
        """Smoke_Test_19 步骤2：再次点击 Bluetooth 主开关重新开启蓝牙（回放 idx12 ensure_click by=desc
        ok:true；步骤1 关闭后此处点击即为重新开启，步骤2 需蓝牙开启才能管理已配对设备）"""
        self.car.ensure_click(Loc.TOGGLE_BLUETOOTH_PAIRING, by="desc")

    def forget_device(self):
        """Smoke_Test_19 步骤2：点击 Forget 忘记该设备（回放 idx14 ensure_click by=text ok:true；
        Forget 后自动返回 Bluetooth 界面）"""
        self.car.ensure_click(Loc.TXT_FORGET, by="text")

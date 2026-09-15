# -*- coding: utf-8 -*-
"""临时诊断脚本：复现 smoke_test_9 步骤3 小部件替换失败的根因。"""
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from autocar import AT  # noqa: E402
from page_objects.pages.桌面启动器.桌面启动器_page import 桌面启动器Page  # noqa: E402
from page_objects.locators.桌面启动器.桌面启动器_locators import Loc  # noqa: E402

DEVICE_ID = "3696ade"


def dump(label, car, locs):
    print(f"\n===== {label} =====")
    for name, loc in locs.items():
        try:
            ok = car.exists(loc, timeout=0.5)
            print(f"  {name:24s} exists={bool(ok)}")
        except Exception as e:
            print(f"  {name:24s} ERR {e}")


def main():
    at = AT()
    car = at.connect_device(DEVICE_ID, mode="u2")
    page = 桌面启动器Page(car=car, at=at)

    locs = {
        "编辑窗口标题": Loc.WIDGET_EDIT_TITLE,
        "Google助理(编辑/主页)": Loc.WIDGET_EDIT_GOOGLE_ASSISTANT,
        "日期和时间": Loc.WIDGET_EDIT_DATE_TIME,
        "GG图": Loc.WIDGET_EDIT_GG_IMAGE,
        "电话": Loc.WIDGET_EDIT_PHONE,
        "音频": Loc.WIDGET_EDIT_AUDIO,
        "voiceplate": Loc.VOICEPLATE,
        "overlay": Loc.WIDGET_EDIT_OVERLAY,
        "close_button": Loc.WIDGET_EDIT_CLOSE_BUTTON,
        "地图zoom_in": Loc.MAPS_ZOOM_IN,
    }
    try:
        car.press("home")
        time.sleep(1)
        dump("初始(回主页后)", car, locs)

        # 步骤0-1：打开编辑界面，添加 Google 助理
        page.swipe_open_widget_editor()
        time.sleep(1)
        dump("步骤0 打开编辑界面后", car, locs)
        page.add_google_assistant_widget()
        time.sleep(1)
        dump("步骤1 添加Google助理+关闭后", car, locs)

        # 步骤2：点击 Google 助理进入语音交互
        page.click_google_assistant()
        time.sleep(3)
        dump("步骤2 点击Google助理后(语音交互)", car, locs)

        # 步骤3 分步执行
        car.press("back")
        time.sleep(1)
        dump("步骤3 back后", car, locs)

        page.swipe_open_widget_editor()
        time.sleep(1)
        dump("步骤3 swipe打开编辑界面后", car, locs)

        # ===== 分析编辑界面完整 UI 层级 =====
        print("\n===== 编辑界面 UI 层级（launcher 相关节点） =====")
        try:
            xml = car.dump_hierarchy() if hasattr(car, "dump_hierarchy") else None
            if xml is None:
                # 尝试通过 adb uiautomator dump 获取
                import subprocess
                subprocess.run(["adb", "-s", DEVICE_ID, "shell", "uiautomator", "dump", "/sdcard/ui_x.xml"], check=True)
                xml = subprocess.run(
                    ["adb", "-s", DEVICE_ID, "shell", "cat", "/sdcard/ui_x.xml"],
                    capture_output=True, text=True, timeout=30,
                ).stdout
            import re
            # 提取所有 launcher 节点（含 id/文本/边界/可点击）
            nodes = re.findall(
                r'<node[^>]*package="com\.renault\.car\.launcher"[^>]*/?>',
                xml,
            )
            for n in nodes:
                tid = re.search(r'resource-id="([^"]*)"', n)
                txt = re.search(r'text="([^"]*)"', n)
                clk = re.search(r'clickable="([^"]*)"', n)
                bnd = re.search(r'bounds="([^"]*)"', n)
                cdesc = re.search(r'content-desc="([^"]*)"', n)
                print(
                    f"  id={tid.group(1) if tid else '':40s} "
                    f"text={txt.group(1) if txt else '':18s} "
                    f"desc={cdesc.group(1) if cdesc else '':15s} "
                    f"click={clk.group(1) if clk else '?':5s} "
                    f"bounds={bnd.group(1) if bnd else '?'}"
                )
        except Exception as e:
            print(f"  UI dump ERR {e}")

        # ===== 实验A：点击主页 Google 助理（选中）→ 再点日期和时间 → 关闭 =====
        print("\n===== 实验A：先点主页Google助理(选中) → 点日期和时间 → 关闭 =====")
        car.ensure_click(Loc.GOOGLE_ASSISTANT, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        time.sleep(1)
        dump("点击主页Google助理后", car, locs)
        car.ensure_click(Loc.WIDGET_EDIT_DATE_TIME, by="text", max_scrolls=10, scroll_direction="up", fingers=1)
        time.sleep(1)
        dump("点击日期和时间后", car, locs)
        car.ensure_click(Loc.WIDGET_EDIT_CLOSE_BUTTON, by="id", max_scrolls=10, scroll_direction="up", fingers=1)
        time.sleep(2)
        dump("关闭后主页状态", car, locs)

    finally:
        car.press("home")
        at.disconnect()


if __name__ == "__main__":
    main()

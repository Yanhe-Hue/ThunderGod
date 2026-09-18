# U 盘升级脚本（有线 ADB + AutoCar）

当前冒烟由 ATS 的 `AutoTest.RunScripts` 正式入口执行，自动显示 ATS 执行页面；终端同步输出 ATS run.log。需在 VS Code 中打开 ATS 工程根目录，启用本机已安装的 USB Upgrade ATS Bridge。停止测试使用 ATS 页面停止按钮。

完整功能和当前运行方式见 [功能与使用说明](功能与使用说明.md)。新增：auto/local/resume/verify-adb/verify-version 在版本校验成功后自动串行执行 ATS 冒烟；使用 `-SkipSmoke` 可只校验不跑冒烟，`smoke-plan` 查看数字排序。auto/local/resume 默认也核对当天日期，显式指定 -ExpectedQnx 时核对完整版本。下面的早期联调记录保留供排查，日常操作以新说明为准。

## 自动入口（新增）

**直接核对日期：**运行 `.\run.ps1 verify-adb`，直接连接 ADB、进入工程模式，读取 QNX system version 后缀中的日期，与电脑当天日期比较。不输入完整目标版本，不读取云盘、发布信息或包记录。支持 `-YYMMDD_HHMMSS` 和 `-YYYYMMDD_HHMMSS` 后缀；例如 `1.01.05.61-260914_023700` 的日期为 2026-09-14。日期相同显示 VERSION_DATE_VERIFIED，不同或无法解析则报错。这里只证明日期一致，不代表完整版本一致。

`.\run.ps1 verify-version` 执行同样的日期核对，但先等待 120 秒再连接 ADB。这两个指令不使用 -ExpectedQnx；升级指令 auto/local/resume 仍可通过该参数进行完整版本核对。

升级流程在程控电源重新上电后固定等待 **120 秒**，之后才开始通过 ADB 检测新的 boot_id 和启动完成状态。

**直接从车机升级继续：**运行 `.\run.ps1 resume`。请保持 U 盘接在车机端。此入口不登录云盘、不选择安装包、不格式化、不切换 USB，也不做电脑 ZIP/哈希或车机文件哈希检查；只检查配置和有线 ADB，然后进入升级页按当前状态继续。车机自身的校验步骤仍按页面状态执行；已校验则进入安装，已安装则进入激活。激活后核对重启提示、通过电源重启并记录实际 QNX，不使用旧包记录判定版本一致。

自动阶段支持按当前页面继续：检测到本阶段或更后阶段的完成标记时，记录 PHASE_ALREADY_COMPLETE 并跳过已完成动作。校验完成进入安装，安装完成进入激活，激活完成核对重启提示后重启。不单凭历史日志跳过操作；页面出现失败状态仍停止。

导航同时检查 USB Upgrade 标题与升级状态控件。已经位于升级页，或启动 Activity 后直接恢复升级页时，跳过 System Update 菜单等待，直接进入阶段判断，避免导航超时。

按用户确认，`auto` 每次在下载前将配置的 U 盘格式化为 exFAT，清除全盘文件，然后下载并校验，最终文件固定为 `USB_UPDATE/Update.zip`。此操作需要 Windows 管理员权限。格式化前核对可移动卷、USB 总线、非系统/启动盘及单分区；检查或格式化失败即停止。实现使用 [Microsoft Format-Volume](https://learn.microsoft.com/powershell/module/storage/format-volume)。`local` 不格式化；`cloud` 单独下载到电脑也不格式化。

已有安装包时运行 `.\run.ps1 local`。脚本将 U 盘切到电脑，再弹出文件选择框，默认打开 U 盘 USB_UPDATE 目录。可选择电脑或 U 盘上的 ZIP，以及下载完成但尚未改名的 `.part`。此入口无需云盘登录或 GAS/no_gas 选择，不重新下载。校验 ZIP CRC 和 SHA256 后准备为 USB_UPDATE/Update.zip，再自动升级、激活及重启。若选择的就是目标 Update.zip，则直接使用；其他文件复制校验成功后保留旧 Update.zip 备份。关闭选择框取消升级。

2026-09-14 按用户要求，自动升级不再因包内缺少明确 QNX 目标版本而停止。没有目标值时，重启后记录实际 QNX，并输出 VERSION_RECORDED_NOT_VERIFIED；这不表示目标版本比对通过。有目标值时仍严格比对，版本不符仍报错。ZIP 损坏、车机校验/安装/激活失败等错误仍停止。

完成一次性配置后，日常只需两条命令：

```powershell
.\run.ps1 check
.\run.ps1 auto
```

运行 `auto` 或 `cloud` 时会弹出版本选择窗口：GAS 对应 `full_userdebug`，no_gas 对应不含 full 的 `userdebug`。选择后按该分类查找最新构建，只下载其中唯一的 Renault 升级包。关闭窗口会取消运行，不开始下载或升级。`check` 不弹出版本选择。选择仅对本次运行生效，不修改配置文件。

需要跳过选择窗口时，可显式传入 `-Variant gas` 或 `-Variant no_gas`，例如 `.\run.ps1 auto -Variant no_gas`。直接运行 Python 时使用 `--variant no_gas`；不传时仍采用配置中的默认分类。

auto 串行执行有线连接、切换 USB3、格式化 U 盘为 exFAT、下载最新 Renault ZIP、包校验、定名 USB_UPDATE/Update.zip、安全弹出、USB2 挂载及哈希核验、页面校验/刷写/激活、电源重启及 QNX 读取。auto 格式化会清除旧包。下载期间使用临时文件，校验完成后自动改名为 Update.zip，无需手动复制或改名。旧的分阶段命令保留用于排查。

2026-09-14 已在设备 3696ade 实跑自动页面导航与 QNX 文本读取；三个升级完成状态来自该设备 APK 的默认资源，尚未执行真实刷写验证。40 项本地测试通过不等于端到端升级通过。usb_root 仍需与实际 U 盘盘符一致（目前 F:/）；运行期间不会让用户逐步确认。

**云盘登录已并入 check。** check 检查依赖后验证已有登录；未登录或登录失效时自动打开扫码页面，扫码后继续，并用新的浏览器会话验证登录能否复用。只有登录验证和状态保存都成功，才显示 `CLOUD_LOGIN_READY`、`ENVIRONMENT_CHECK_PASSED`。超时或失败时不会显示检查通过。

登录状态保存在 `.auth/cloud.json`，不要上传或分享该文件。之后直接运行 auto，不再单独执行 login，也不会在自动流程中要求扫码。如果会话在运行前或运行中失效，auto 报错停止，重新执行 check 即可。login 仅保留为兼容排查入口。

云盘自动模式优先使用 expected_qnx_by_build 中与完整构建目录绑定的预期 QNX；没有配置时从下载 ZIP 的小型 JSON/XML/属性文件里读取明确的版本字段。本地模式尝试读取包内字段。无法取得唯一明确值时记录原因并继续升级，重启后只记录实际版本，不将包名日期或刷写后读到的值充当预期。无需在运行中输入版本。

导航配置为步骤数组，每项包含 selector 或已核实的 component，以及 arrived 页面锚点。因原文 USBUpdating Btn 未能在列表匹配，脚本改用已实测的 Activity 启动入口 com.alliance.engineering.fota/.UsbUpdateBtnActivity，再点击 USB Upgrade；工程模式入口为 com.ts.engineermode/.MainActivity，其 Overview 直接显示 QNX，无需假设存在 Version Date Information 子页。此处使用 ADB 启动作为导航降级，仍以实际 UI 锚点验证到达。

本机资源定义显示，校验后的第二个按钮是 **Start Upgrade**，不是 Start Update。自动状态为 Upgrade package verified → Installation complete → Activation complete，最后还核对“Please reboot the vehicle to finish the upgrade”完整描述才下电。失败提示 Upgrade failed 会立即停止。

自动弹出使用 Windows 锁卷、刷新、卸载和弹出接口，锁卷失败不强行卸载，且不会切到车机。可能需要管理员权限；脚本不自动提升权限。实现依据：[Microsoft 卷卸载说明](https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-fsctl_dismount_volume)。硬件切换与安全弹出尚未实机验证。

默认 GAS（full_userdebug）。详见 [设计大纲](设计大纲.md)。已接入 AutoCar 电源和 USB 切换调用；尚未真机验证。

## 环境与配置

使用已安装公司 AutoCar SDK 的 Python。PowerShell 示例路径需要替换：

```powershell
$env:AUTOCAR_PYTHON = 'C:/Users/TS/AppData/Roaming/iatset/venv/Scripts/python.exe'
./setup.ps1
# 仅缺少 ADB 时：
./setup.ps1 -InstallAdb
# 缺少网页自动化依赖时：
./setup.ps1 -InstallCloud
```

setup 检测 Python、AutoCar、ADB，首次复制示例配置；已有配置不会覆盖。旧版配置请对照 config.example.json 更新，移除无线 ADB 和外部电源命令字段。不要自动安装来源不明的同名 AutoCar 包。

| 配置 | 值/含义 |
|---|---|
| adb | ADB 路径或 PATH 中的 adb |
| usb_serial | 已检测并填入 3696ade；更换设备后需更新 |
| wired_adb_independent | 用户已确认独立有线连接，已设 true |
| usb_root | 电脑 U 盘盘符根目录，例如 F:/ |
| power.resource | 已设置 ASRL13::INSTR |
| power.off_seconds | 已设置 5 秒 |
| usb_switch.port | 已设置 COM14 |
| usb_switch.pc_usb_port | 用户确认电脑端 USB3，已设 3 |
| usb_switch.car_usb_port | 用户确认车机端 USB2，已设 2 |

USB 切换器为互斥 MUX，0 表示全关。截图右侧被截断的通道号已由用户补充：3=电脑，2=车机。用户确认 ADB 独立连接，脚本仍在切换后检查连接状态。usb_root 目前示例为 F:/，运行前必须改成实际 U 盘盘符。

Wi-Fi 仍用于时间同步，但不用于 ADB。脚本不会执行 adb connect 或 adb tcpip；车机时间与电脑偏差超限时停止，联网同步后再试。

## 云盘与包清单

```powershell
& $env:AUTOCAR_PYTHON usb_update.py cloud
```

cloud 使用独立 Microsoft Edge 会话打开 [创达云盘](https://pan.thundersoft.com/web/index.html)，扫码登录后自动进入 **群组文件 → ThunderGod → 01-DailyBuild → ThunderGod-a-14.0-qcom_r14.1-main-Asample**，遍历目录，选择最新时间戳的 GAS 构建，从右键菜单下载 Renault 包到 downloads/，验证大小与 ZIP CRC 后生成 packages.json。不会导出或复用当前 Codex 浏览器的登录凭据，因此脚本的新会话仍需扫码。

网页目录与菜单已在已登录页面核对；完整 2.54 GB 下载尚未实跑验证。运行时从 cloud.expected_qnx 读取目标 QNX，未填写则要求输入发布信息中的完整值。当前目录的 .tar.gz.sha256 对应 tar 包，不能拿来校验 Renault ZIP。脚本计算下载文件 SHA256 用于后续复制一致性校验，记录来源为 local_download_for_copy_integrity。

也可以手动下载并填写 packages.json：

- folder：真实目录。GAS 后缀 full_userdebug；NO_GAS 后缀 userdebug 且不含 full。
- name：文件原名，支持 update_all_renault 或现场实际的 update_all_renault.zip 结尾。
- build_date：YYYY-MM-DD。当前配置 today_only=true，只选择当天所选 GAS/no_gas 分类，同日取 YYYYMMDD_HHMMSS 最大时间戳；没有当天对应分类则停止，不回退旧包。先确认选包再格式化 U 盘。日志记录目录列表和最终完整路径。
- source：本地包绝对路径，或实际 HTTPS 下载直链，不是分享或登录页面。
- sha256：可信包的 SHA256。可用 Get-FileHash -Algorithm SHA256 -LiteralPath '包路径' 计算本地文件哈希用于复制校验；自行计算不证明发布来源。
- expected_qnx：该构建对应的完整 QNX 版本值。

云盘自动流程先选最新构建再找包，最新目录没有 Renault 包就停止，不回退旧目录。手工清单须真实反映目标目录。手工 HTTPS 直链下载的令牌可通过 download_token_env 指定环境变量。

## 分阶段执行

```powershell
& $env:AUTOCAR_PYTHON usb_update.py check
& $env:AUTOCAR_PYTHON usb_update.py connect
& $env:AUTOCAR_PYTHON usb_update.py cloud
& $env:AUTOCAR_PYTHON usb_update.py plan
& $env:AUTOCAR_PYTHON usb_update.py prepare
& $env:AUTOCAR_PYTHON usb_update.py upgrade
```

每条成功后再执行下一条：

旧分阶段模式需先执行 cloud 生成真实 packages.json，再执行 plan；setup 仅创建空清单，不包含示例包。手工下载的包建议使用 local 或 stress 选择，无需手填清单。每个 Python 入口命令都需要子命令；仅运行 usb_update.py 会提示缺少 action。hardware.py 和 cloud_download.py 是被主入口调用的模块，不需要单独运行。

也可使用 ./run.ps1 cloud、./run.ps1 plan、./run.ps1 check 等快捷命令，默认使用已提供的 AutoCar 环境。

1. check 检查 ADB、序列号和 AutoCar 可导入性，不打开电源。
2. connect 检查有线 ADB 与车机时钟。
3. cloud 下载目标包并生成真实清单，需要扫码登录与目标 QNX 值。
4. plan 校验清单并打印目标，不操作硬件。
5. prepare 调用 at.usb_switch(port="COM14", usb_port=电脑通道)，等待盘符出现，写 USB_UPDATE/Update.zip。执行 flush/fsync、SHA256 与 ZIP CRC 校验；记录 prepared_package.json。旧包不覆盖，失败保留 .part。
6. upgrade 匹配准备记录。人工完成 Windows 安全弹出后，调用 at.usb_switch(port="COM14", usb_port=车机通道)，检查电脑盘符消失与 ADB 在线，再人工确认车机识别包。关闭文件窗口不等于安全弹出。
7. 进入 USBUpdating Btn → USB Upgrade，第一次 Start Update 校验；确认成功后第二次开始刷写。刷写完成后 Activate。
8. 明确激活完成且要求重启后，执行下电、等待 5 秒、上电。不会改变电压或限流。

实际调用结构：

```python
from autocar import AT
import time
at = AT()
ps = at.power_open("ASRL13::INSTR")
ps.set_output(on=False)
time.sleep(5)
ps.set_output(on=True)
```

脚本还检查 SDK 返回结果并记录日志。用 time.sleep 实现截图中 at.sleep 的等待。比较重启前后 boot_id 并等待 sys.boot_completed=1，防止将旧系统误判成已重启。失败或中断后不自动补发上下电，先检查现场状态。

9. ThunderSoft 工程模式 → Version Date Information → QNX system version，与预期完整值比较。

重启后连接失败时，修复有线连接后单独核验，不要再次刷写：

```powershell
& $env:AUTOCAR_PYTHON usb_update.py verify
```

## UI 联调与测试

ui 的 validation_done、flash_done、activation_done 默认为 null，需要人工确认。现场取证后填写精确 text/resource-id/content-desc；不要用常驻 Start Update 按钮作为校验成功标记。failure_selectors 配置错误提示。qnx_value 定位版本值控件，其 text 必须恰好等于预期版本。

旧分阶段排查模式保留 Windows 安全弹出、车机挂载确认和页面操作提示；日常使用 check → auto，扫码只发生在 check 阶段，其余按本文顶部的自动流程执行。已使用用户提供的 AutoCar 环境核对以下接口；set_output 的原始返回值为 None，但公开调用返回含 success/method 的 MethodResult，脚本检查该包装的成功状态。硬件动作尚未实跑。

```powershell
& $env:AUTOCAR_PYTHON -m autocar.cli at search usb
& $env:AUTOCAR_PYTHON -m autocar.cli at info at.usb_switch
& $env:AUTOCAR_PYTHON -m autocar.cli at info at.power_open
& $env:AUTOCAR_PYTHON -m autocar.cli at info ps.set_output
& $env:AUTOCAR_PYTHON -m unittest discover -s tests -v
```

单元测试使用硬件替身，不会切换 USB 或上下电。日志位于 logs/，记录人工或界面核验来源。保留本次清单和准备记录，避免跨天变更构建后继续执行。


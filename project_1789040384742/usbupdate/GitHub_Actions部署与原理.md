# GitHub Actions：U 盘升级与 ATS 冒烟的 CI/CD

## 1. 是什么，谁在执行

GitHub 的 CI/CD 服务叫 **GitHub Actions**。本工程主要用它做每天的设备升级与回归验证：CI 是持续集成/验证，CD 是持续交付或部署；当前工作流不发布生产软件，只升级测试车机并运行冒烟。

执行链路：GitHub 定时或人工触发 → 创建 workflow run → 任务进入队列 → 匹配 Windows 台架 Runner → 本机执行 ci-once → 返回退出码 → 上传报告 → GitHub 显示成功/失败。

GitHub 负责调度和展示；接着电源、USB 切换器、车机的 Windows 电脑负责实际操作。不能用 GitHub 公共云 Windows 虚拟机替代这台电脑，因为云端不能直接访问台架串口、U 盘和车机。

官方概念与语法：[GitHub Actions 工作流语法](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)。

## 2. 本次已提供的文件

| 文件/入口 | 用途 |
|---|---|
| run.ps1 ci-once | 等待当天包，升级、版本核验、冒烟，成功后退出 |
| daily_update.py | auto 和 ci-once 共用每日完成记录逻辑 |
| ci_run.ps1 | CI 包装：本机互斥锁、终端记录、收集本次日志、返回退出码 |
| .github/workflows/usb-upgrade.yml | GitHub Actions 调度定义，支持人工运行和每日定时 |
| daily_state.json | 本机每日成功记录，不上传 Git；相同设备/分类/目录当天已成功则返回 0 并记录 CI_ALREADY_COMPLETE，不重新刷写 |

`auto` 仍是无限每日循环，适合终端常驻；`ci-once` 只执行一次，适合让 CI 调度下一天。**不能同时运行 auto、stress、ci-once 或另一工具操作同一台架。** Workflow 并发组只能约束同仓库使用相同组的任务；本机 CI 互斥锁仅约束 ci_run.ps1，不锁住手动入口或其他软件。

当前 YAML **直接调用台架已部署的 D 盘脚本，不 checkout 或自动覆盖 ATS 工程**。所以 GitHub workflow commit 不代表台架脚本版本；更新 Python 脚本后先在台架部署验证，不能仅把修改 push 到 GitHub 就认为已生效。这是为了复用现有 ATS 根工程、界面、配置和登录会话。若以后要求每次严格执行指定提交，需要额外设计受控部署步骤。

## 3. 首次部署步骤

### 第一步：准备台架

沿用《环境依赖与配置说明.md》的 Windows、AutoCar Python、ADB、驱动、电源和 USB 接线。保持电脑时区 Asia/Shanghai、时钟正确、不开启自动睡眠。以日常使用 ATS 的用户登录 Windows，打开并信任 ATS 根工程，启用 AI Test Studio 和 1.0.1 连接扩展。

本工程默认目录：

```text
D:\renult\project_1788164131875\project_1788434794119\project_1788434802235\project_1789040384742\usbupdate
```

关闭仍在运行的 auto/stress。以管理员 PowerShell 进入上面目录（格式化 U 盘需要权限），先运行：

```powershell
.\run.ps1 check
```

选择 GAS/no_gas，扫码登录。config.json 保持 smoke.enabled=true；确认 cloud.auth_state 的会话可用，ATS 工程已打开。CI 不弹窗选择分类或等待扫码；登录过期需要人工重新 check。

### 第二步：建立 GitHub 私有仓库

使用公司允许的 GitHub 私有仓库。仓库中至少放工作流文件，路径必须为**仓库根目录** `.github/workflows/usb-upgrade.yml`，并合入默认分支。如果上传的是整个 ATS 工程，需把 usbupdate/.github 下的工作流复制到 ATS 仓库根的 .github/workflows，不能保持嵌套路径。

脚本源码可一并纳入版本控制，但 config.json、.auth/cloud.json、daily_state.json、安装包和本机缓存不要提交。日志/截图会随 artifact 上传到该仓库，先确认公司允许上传这些测试证据。本次没有创建仓库、提交代码或注册 Runner。

### 第三步：注册 Windows self-hosted Runner

在仓库中依次打开 **Settings → Actions → Runners → New self-hosted runner**，选择 Windows、x64。按网页即时生成的命令，在台架电脑 `C:\actions-runner` 下载、解压和注册 Runner。使用页面给出的真实仓库 URL 和临时注册 token，不使用文档中的伪 token。

注册时为 Runner 增加自定义标签 `renault-usb`，名称可用 `renault-bench-01`。默认标签还应包含 self-hosted、Windows、X64，与 YAML 的 runs-on 全部匹配。安装和注册命令以 GitHub 页面为准，避免硬编码过期下载版本。[官方 Runner 添加步骤](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners)

**针对本工程，不安装为 Windows 后台服务**：当前 Edge 和 ATS 依赖已登录用户的交互桌面，服务账户/会话不能等同于这个桌面。注册时拒绝安装服务，然后在同一用户的管理员终端执行：

```powershell
cd C:\actions-runner
.\run.cmd
```

终端显示 Listening for Jobs，GitHub Runner 列表显示 Idle，表示可接任务。保持该终端、Windows 用户会话和 ATS 窗口运行。需要开机自动启动时，可另行配置“仅用户登录时运行”的任务计划，而不是改成无交互服务。不要同时注册多个 Runner 争用同一台架。

### 第四步：设置仓库变量

打开 **Settings → Secrets and variables → Actions → Variables → New repository variable**：

| 名称 | 值 |
|---|---|
| USBUPDATE_DIR | 上述 D 盘 usbupdate 完整路径 |
| AUTOCAR_PYTHON | C:/Users/TS/AppData/Roaming/iatset/venv/Scripts/python.exe |

这两个是路径变量，不是登录密钥。云盘会话保留在台架本地，不复制到仓库变量。工作流中的脚本参数通过环境变量读取，不把路径字符串拼成任意 PowerShell 代码。

仓库 Actions 策略需允许运行工作流及 actions/upload-artifact。Runner 电脑需能访问 GitHub Actions、artifact 服务和创达云盘，公司代理/防火墙规则按本地网络条件配置。

### 第五步：首次手动验证

推荐先在台架终端验证一次（此命令会真正格式化 U 盘、刷写并测试）：

```powershell
.\run.ps1 ci-once
```

成功后 GitHub 中打开 **Actions → USB upgrade and ATS smoke → Run workflow → 选择默认分支 → Run workflow**。

若当天已在终端成功执行，GitHub 任务会显示 CI_ALREADY_COMPLETE 并正常退出，这只验证调度与跳过逻辑，不代表它再次刷写。首次完整端到端验证可直接在尚未完成当天流程时使用 GitHub 人工触发。不要为了看绿色状态而忽略失败或删除未知运行记录。

任务执行时查看 Actions 实时日志，同时本机 ATS 显示测试页面。结束后在该 run 的 Artifacts 下载 `usb-upgrade-运行ID-尝试次数`，包含 console.txt、ci-result.json、升级日志、异常证据及本次日志目录内的 ATS 报告。

## 4. 定时、并发、失败规则

工作流中：

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: '7 16 * * *'
```

这里未设置时区，因此 cron 使用 UTC：UTC 16:07 对应北京时间次日 00:07。选择过零点 7 分钟避开整点拥堵。若希望零点触发可改为 `0 16 * * *`，但 GitHub 定时可能延迟，不能保证精确到秒。schedule 使用默认分支上的定义；高负载可能延迟或丢弃部分排队任务，不能把它当严格实时调度器。[定时事件规则](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

规则如下：

| 规则 | 当前实现 |
|---|---|
| 触发 | 每日定时或 Run workflow 手动触发；不配置 push/PR 自动刷写 |
| 执行位置 | 仅匹配 renault-usb 等全部标签的自托管 Windows Runner |
| 同一台架互斥 | 固定 concurrency group，不按分支或 GAS 分类分组；cancel-in-progress=false，不为了新任务取消正在刷写的任务 |
| 排队 | 同一并发组限制运行；默认待运行任务不是无限 FIFO 队列，新待运行任务可能替换旧待运行任务 |
| 等包 | 默认每 60 秒检测，CI 默认等包 7200 秒；无包直到超时则失败 |
| 跨日 | 等包尚未选中且跨日则失败退出，下一天由新任务触发；已选中下载/刷写的包继续完成，以该包日期校验 |
| 完成判定 | 升级、日期校验、ATS 全部通过，才写每日完成记录并返回 0；当天此前成功则返回 0 并明确记录跳过 |
| 失败 | 非零退出码使 job 失败；不设置 continue-on-error，不在失败后假定成功继续刷写 |
| 总任务上限 | YAML timeout-minutes=360，即示例最多 6 小时，需根据真实等包、刷写、冒烟耗时评估 |
| 报告归档 | if: always() 尝试在失败后也上传；保留 14 天；强制终止、电脑掉线等情况不保证最终归档完成 |

官方并发说明：[控制工作流并发](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)。报告上传工具：[actions/upload-artifact](https://github.com/actions/upload-artifact)。示例 v4 用于 GitHub.com；GitHub Enterprise Server 的兼容版本需按其部署版本另行核对。

CI 的等包上限可在 config.json 的 cloud 中增加：

```json
"ci_wait_timeout_seconds": 7200
```

保留足够的任务剩余时间用于下载、刷写、重启和全部冒烟；上限过短可能在刷写中途杀掉控制进程。超时或人工取消不等于车机停止刷写，也不保证 ATS 测试停止。需要停止 ATS 时使用 ATS 页面停止按钮，并现场确认车机、电源状态后再重跑。

Runner 在线只是能够接任务，不能保证云盘登录、串口、电源、车机或 ATS 正常。CI 执行失败后查看具体步骤与证据，不应仅通过“重新运行”掩盖故障。当前失败后不会整夜自动重试；可按公司流程人工修复后手动重跑。

## 5. 入口实现原理

`run.ps1 ci-once` → `usb_update.py` → `run_daily(..., once=True)`：

1. 读取本机已保存分类和当日成功记录；已完成则明确跳过。
2. 要求 smoke.enabled=true，禁止 CI 完整流程跳过冒烟。
3. 给云盘轮询设置本次日期及等包截止时间。
4. 调用现有 AutomaticUpgrade.run：选包 → 格式化/下载 → 升级/激活 → 程控重启 → 等待 120 秒 → ADB/日期校验 → ATS。
5. 全部成功才保存记录；once=True 立即 return。普通 auto 则继续等待次日。
6. ci_run.ps1 保存终端和本次日志，传递真实退出码给 Actions；后续归档 step 即使前一步失败也尝试运行。

本实现复用现有升级流程，不维护第二套刷写代码。当前工作流未在真实 GitHub Runner 上运行；本地测试通过不能替代首次 CI 台架验证。

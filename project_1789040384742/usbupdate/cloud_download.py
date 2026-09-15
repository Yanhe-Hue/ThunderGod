"""ThunderSoft web download adapter. Selectors grounded against the logged-in UI.

Uses a separate, ephemeral Edge browser session; scan with Feishu when prompted.
Does not export cookies from the user's existing browser or invent private APIs.
"""
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import time
import zipfile
import tempfile

from usb_update import build_timestamp, digest, is_renault_package, require


def select_build(names, variant, today_only=False):
    require(variant in ('gas', 'no_gas'), '未知升级版本分类')
    choices = []
    for name in names:
        gas = name.endswith('full_userdebug')
        matches = gas if variant == 'gas' else name.endswith('userdebug') and 'full' not in name
        if not matches:
            continue
        stamp = build_timestamp(name)
        require(stamp is not None, '候选构建目录缺少完整时间戳，不能确定最新版本: ' + name)
        if stamp.date() <= dt.date.today():
            choices.append((stamp, name))
    require(choices, '云盘没有对应分类的构建目录')
    latest = max(stamp for stamp, _ in choices)
    require(not today_only or latest.date() == dt.date.today(),
            f'云盘没有今天 {dt.date.today()} 的 {variant} 构建；该分类最新日期为 {latest.date()}，停止下载，不使用旧包或其他分类')
    names = {name for stamp, name in choices if stamp == latest}
    require(len(names) == 1, '相同时间戳存在不同构建，无法唯一选择')
    return names.pop()


def select_file(files):
    matches = [item for item in files if is_renault_package(item['name'])]
    require(len(matches) == 1, '最新构建尚无唯一 Renault 升级包；可能仍在上传，禁止回退旧构建或替换为 CDC 包')
    require(matches[0]['size'] > 0, '升级包大小无效')
    return matches[0]


def wait_list(page):
    page.locator('.filename').first.wait_for(state='visible', timeout=60000)
    page.get_by_text('正在加载...', exact=True).wait_for(state='hidden', timeout=60000)


def open_folder(page, name):
    locator = page.locator('.filename.folderview').filter(has_text=re.compile('^' + re.escape(name) + '$'))
    require(locator.count() == 1, '目录没有唯一匹配: ' + name)
    old_url = page.url
    locator.dblclick()
    page.wait_for_url(lambda url: str(url) != old_url, timeout=30000)
    wait_list(page)


def list_entries(page, kind):
    """Scroll the observed list container to load subsequent pages, if any."""
    selector = '.filename.' + kind
    found = {}
    stable = 0
    wrap = page.locator('.xtable-listwrap')
    require(wrap.count() == 1, '云盘列表容器不唯一，需更新适配')
    wrap.evaluate('el => { el.scrollTop = 0; }')
    time.sleep(1)
    for _ in range(300):
        batch = page.locator(selector).evaluate_all('els => els.map(el => ({name: el.textContent.trim(), size: Number(el.getAttribute("size")), path: el.getAttribute("title")}))')
        previous_count = len(found)
        found.update((item['name'], item) for item in batch)
        wrap.evaluate('el => { el.scrollTop += Math.max(1, el.clientHeight * 0.8); }')
        time.sleep(1)
        page.get_by_text('正在加载...', exact=True).wait_for(state='hidden', timeout=60000)
        at_bottom = wrap.evaluate('el => el.scrollTop + el.clientHeight >= el.scrollHeight - 2')
        stable = stable + 1 if len(found) == previous_count and at_bottom else 0
        if stable >= 3:
            return list(found.values())
    raise RuntimeError('目录分页未能在上限内遍历完成，禁止从不完整结果选最新包')


def ensure_cloud_login(cfg, event=None):
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
    cloud = cfg['cloud']
    path = Path(cloud.get('auth_state', '.auth/cloud.json'))
    path.parent.mkdir(parents=True, exist_ok=True)
    emit = event or (lambda state: print(state, flush=True))
    state = None
    if path.is_file():
        try:
            candidate = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(candidate, dict) and isinstance(candidate.get('cookies'), list) and isinstance(candidate.get('origins'), list):
                state = candidate
        except (ValueError, UnicodeError):
            pass
    emit('CLOUD_LOGIN_CHECK')
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=cloud.get('browser_channel', 'msedge'), headless=False)
        try:
            context = browser.new_context(**({'storage_state': state} if state is not None else {}))
            page = context.new_page()
            page.goto(cloud['url'], wait_until='domcontentloaded')
            ready = page.get_by_text('群组文件', exact=True).first
            try:
                ready.wait_for(state='visible', timeout=15000)
            except BrowserTimeout:
                emit('CLOUD_LOGIN_REQUIRED')
                print('环境检查需要云盘登录：请在打开的窗口扫码；登录完成后检查会自动继续。', flush=True)
                try:
                    ready.wait_for(state='visible', timeout=cloud.get('login_timeout', 300)*1000)
                except BrowserTimeout as exc:
                    raise RuntimeError('云盘登录超时，环境检查未通过；请重新运行 check') from exc
            saved = context.storage_state()
            # Prove that auto can reuse this state in a fresh context, not just this tab.
            probe = browser.new_context(storage_state=saved)
            try:
                probe_page = probe.new_page()
                probe_page.goto(cloud['url'], wait_until='domcontentloaded')
                try:
                    probe_page.get_by_text('群组文件', exact=True).first.wait_for(state='visible', timeout=30000)
                except BrowserTimeout as exc:
                    raise RuntimeError('登录状态无法在新会话中复用，环境检查未通过') from exc
            finally:
                probe.close()
            temporary = path.with_name(path.name + '.tmp')
            temporary.write_text(json.dumps(saved, ensure_ascii=False), encoding='utf-8')
            temporary.replace(path)
            emit('CLOUD_LOGIN_READY')
        finally:
            browser.close()


def login(cfg):
    # Backward-compatible troubleshooting entry; normal usage is check -> auto.
    ensure_cloud_login(cfg)


def release_version_on_page(page, event):
    from version_records import explicit_versions, unique_version
    notes = [item for item in list_entries(page, 'fileview')
             if Path(item['name']).suffix.lower() in ('.txt', '.json', '.md', '.ini', '.prop', '.properties')
             and 0 < item['size'] <= 1024 * 1024]
    require(len(notes) <= 32 and sum(item['size'] for item in notes) <= 4 * 1024 * 1024,
            '发布信息文件超出扫描上限，无法确认目标版本')
    values = set()
    with tempfile.TemporaryDirectory(prefix='usb_release_') as directory:
        for index, item in enumerate(notes):
            locator = page.locator('.filename.fileview').filter(has_text=re.compile('^' + re.escape(item['name']) + '$'))
            require(locator.count() == 1, '发布信息文件未唯一定位：' + item['name'])
            locator.click(button='right')
            with page.expect_download(timeout=60000) as pending:
                page.get_by_role('listitem').filter(has_text=re.compile('^下载$')).click()
            download = pending.value
            path = Path(directory) / str(index)
            download.save_as(str(path))
            require(not download.failure() and path.stat().st_size == item['size'], '发布信息下载不完整')
            content = path.read_bytes()
            try:
                text = content.decode('utf-8-sig')
            except UnicodeError:
                text = content.decode('gb18030', errors='replace')
            found = explicit_versions(text)
            values.update(found)
            event('RELEASE_NOTE_READ', name=item['name'], versions=sorted(found))
    return unique_version(values)


def fetch_release_version(cfg, folder, event):
    """Open the receipt's exact build, never today's or the latest build."""
    from playwright.sync_api import sync_playwright
    cloud = cfg['cloud']
    segments = folder.strip('/').split('/')
    require(segments[:-1] == cloud['path'], '升级记录的云盘分支与当前配置不一致')
    state = cloud.get('auth_state', '.auth/cloud.json')
    require(Path(state).is_file(), '自动读取发布信息需要云盘登录，请先运行 check')
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=cloud.get('browser_channel', 'msedge'), headless=False)
        try:
            context = browser.new_context(storage_state=state, accept_downloads=True)
            page = context.new_page()
            page.goto(cloud['url'], wait_until='domcontentloaded')
            group = page.get_by_text('群组文件', exact=True).first
            group.wait_for(state='visible', timeout=30000)
            group.click()
            wait_list(page)
            for segment in segments[1:]:
                list_entries(page, 'folderview')
                open_folder(page, segment)
            event('RELEASE_BUILD_OPENED', folder=folder)
            return release_version_on_page(page, event)
        finally:
            browser.close()


def download_latest(cfg, event, automatic=False, destination=None, target_name=None, prepare_destination=None):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError('缺少 Playwright，请执行 setup.ps1 -InstallCloud') from exc
    cloud = cfg['cloud']
    destination = Path(destination or 'downloads').resolve()
    # Version is supplied from release information, never guessed from filename.
    expected_qnx = cloud.get('expected_qnx', '').strip()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=cloud.get('browser_channel', 'msedge'), headless=False)
        state = cloud.get('auth_state', '.auth/cloud.json')
        context = browser.new_context(accept_downloads=True, **({'storage_state': state} if automatic else {}))
        page = context.new_page()
        page.set_default_timeout(30000)
        try:
            page.goto(cloud['url'], wait_until='domcontentloaded')
            if not automatic:
                print('请在新打开的云盘窗口扫码登录；登录完成后脚本会继续。', flush=True)
            try:
                page.get_by_text('群组文件', exact=True).first.wait_for(state='visible', timeout=(30 if automatic else cloud.get('login_timeout', 300)) * 1000)
            except Exception as exc:
                raise RuntimeError('云盘登录不可用；请重新运行 check 完成登录，auto 不会停留等待扫码') from exc
            page.get_by_text('群组文件', exact=True).first.click()
            wait_list(page)
            for segment in cloud['path'][1:]:
                list_entries(page, 'folderview')
                open_folder(page, segment)
            folders = list_entries(page, 'folderview')
            folder_names = [item['name'] for item in folders]
            event('CLOUD_BUILD_CANDIDATES', variant=cfg['variant'], folders=folder_names)
            build = select_build(folder_names, cfg['variant'], cfg.get('today_only', False))
            selected_path = '/' + '/'.join(cloud['path'] + [build])
            print(f"云盘选择：{cfg['variant']} | 构建时间 {build_timestamp(build)} | {selected_path}", flush=True)
            event('CLOUD_BUILD_SELECTED', variant=cfg['variant'], folder=selected_path,
                  build_time=build_timestamp(build).isoformat())
            if automatic:
                expected_qnx = cloud.get('expected_qnx_by_build', {}).get(build, '').strip()
                require(not expected_qnx.startswith('REPLACE'), '目标 QNX 仍为占位值：' + build)
            open_folder(page, build)
            package = select_file(list_entries(page, 'fileview'))
            event('CLOUD_PACKAGE_SELECTED', folder=build, name=package['name'], size=package['size'])
            require(Path(package['name']).name == package['name'] and not re.search(r'[<>:"/\\|?*]', package['name']), '云盘文件名包含不安全路径字符')
            # Only initialize the USB after a matching build and package are confirmed.
            if prepare_destination:
                prepare_destination()
            destination.mkdir(parents=True, exist_ok=True)
            target = destination / (target_name or package['name'])
            require(Path(target.name).name == target.name, '下载目标名称无效')
            require(automatic or not target.exists(), '下载目标已存在，请先检查已有包')
            require(not target.with_suffix('.part').exists(), '发现未完成下载，停止以保留现场文件')
            require(shutil.disk_usage(destination).free > package['size'] * 2 + 100 * 1024 * 1024, '电脑下载空间不足（需容纳浏览器临时文件和最终包）')
            if not expected_qnx and not automatic:
                expected_qnx = input('请输入该构建发布信息中的完整预期 QNX 版本值（不能用日期猜测）: ').strip()
            require(automatic or expected_qnx, '缺少目标 QNX 版本，停止下载')
            file_locator = page.locator('.filename.fileview').filter(has_text=re.compile('^' + re.escape(package['name']) + '$'))
            require(file_locator.count() == 1, '下载文件未唯一定位')
            file_locator.click(button='right')
            with page.expect_download(timeout=cloud.get('download_timeout', 7200) * 1000) as pending:
                page.get_by_role('listitem').filter(has_text=re.compile('^下载$')).click()
            download = pending.value
            # A native browser download preserves the authenticated download flow.
            partial = target.with_suffix('.part')
            download.save_as(str(partial))
            require(not download.failure(), '浏览器下载失败')
            require(partial.stat().st_size == package['size'], '下载大小与云盘文件大小不匹配')
            require(zipfile.is_zipfile(partial), '下载内容不是 ZIP')
            with zipfile.ZipFile(partial) as archive:
                require(archive.testzip() is None, '下载 ZIP CRC 错误')
            if automatic and not expected_qnx:
                from package_metadata import qnx_version
                try:
                    expected_qnx = qnx_version(partial)
                except RuntimeError as exc:
                    event('TARGET_VERSION_UNAVAILABLE', reason=str(exc))
            sha256 = digest(partial)
            if target.exists():
                target.rename(target.with_name(target.name + '.' + dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak'))
            partial.rename(target)
            print('升级包已就绪：' + str(target), flush=True)
            stamp = build_timestamp(build)
            entry = {'folder': '/' + '/'.join(cloud['path'] + [build]),
                     'name': package['name'], 'build_date': stamp.date().isoformat(),
                     'source': str(target), 'sha256': sha256,
                     'sha256_origin': 'local_download_for_copy_integrity',
                     'expected_qnx': expected_qnx}
            manifest = Path(cfg['package_manifest'])
            if manifest.exists():
                backup = manifest.with_name(manifest.name + '.' + dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
                shutil.copy2(manifest, backup)
            manifest.write_text(json.dumps([entry], ensure_ascii=False, indent=2), encoding='utf-8')
            event('CLOUD_DOWNLOAD_COMPLETE', target=str(target), manifest=str(manifest), sha256=sha256)
            return entry
        finally:
            context.close()
            browser.close()

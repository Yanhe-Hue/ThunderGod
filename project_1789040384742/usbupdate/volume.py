"""Lock, flush, dismount and eject a configured removable Windows volume."""
import ctypes
from ctypes import wintypes as w
import os
import re
import subprocess
from pathlib import Path


def format_exfat(root):
    value = str(root)
    if os.name != 'nt' or not re.fullmatch(r'[D-Zd-z]:[/\\]', value):
        raise RuntimeError('格式化目标必须是明确的可移动盘根目录（D: 至 Z:）')
    result = subprocess.run(
        ['powershell.exe', '-NoProfile', '-NonInteractive', '-File',
         str(Path(__file__).with_name('format_usb.ps1')), '-DriveLetter', value[0].upper()],
        capture_output=True, text=True, errors='replace', timeout=300)
    if result.returncode or 'USB_FORMAT_EXFAT_COMPLETE' not in result.stdout:
        raise RuntimeError('U 盘格式化失败，停止下载；请检查盘符及管理员权限：' +
                           (result.stderr or result.stdout).strip())


def removable_roots():
    if os.name != 'nt':
        return []
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetLogicalDrives.restype = w.DWORD
    kernel.GetDriveTypeW.argtypes = [w.LPCWSTR]
    mask = kernel.GetLogicalDrives()
    return [chr(65+i) + ':/' for i in range(26)
            if mask & (1 << i) and kernel.GetDriveTypeW(chr(65+i) + ':\\') == 2]


def eject(root):
    path = Path(root).resolve()
    if os.name != 'nt' or path != Path(path.anchor):
        raise RuntimeError('自动弹出仅支持 Windows 盘符根目录')
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.GetDriveTypeW.argtypes = [w.LPCWSTR]
    if k.GetDriveTypeW(str(path)) != 2:
        raise RuntimeError('拒绝弹出非可移动磁盘')
    k.CreateFileW.argtypes = [w.LPCWSTR,w.DWORD,w.DWORD,w.LPVOID,w.DWORD,w.DWORD,w.HANDLE]
    k.CreateFileW.restype = w.HANDLE
    k.DeviceIoControl.argtypes = [w.HANDLE,w.DWORD,w.LPVOID,w.DWORD,w.LPVOID,w.DWORD,ctypes.POINTER(w.DWORD),w.LPVOID]
    k.FlushFileBuffers.argtypes = [w.HANDLE]
    k.CloseHandle.argtypes = [w.HANDLE]
    handle = k.CreateFileW('\\\\.\\' + path.drive, 0xC0000000, 3, None, 3, 0, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    count = w.DWORD()
    try:
        # Lock must succeed before dismount; never force removal of busy volumes.
        for code in (0x90018,):
            if not k.DeviceIoControl(handle, code, None, 0, None, 0, ctypes.byref(count), None):
                raise ctypes.WinError(ctypes.get_last_error())
        if not k.FlushFileBuffers(handle):
            raise ctypes.WinError(ctypes.get_last_error())
        for code in (0x90020, 0x2D4808):
            if not k.DeviceIoControl(handle, code, None, 0, None, 0, ctypes.byref(count), None):
                raise ctypes.WinError(ctypes.get_last_error())
    finally:
        k.CloseHandle(handle)

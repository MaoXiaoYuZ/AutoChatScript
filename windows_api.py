import win32gui


def enum_windows_proc(hwnd, windows):
    """
    枚举窗口的回调函数，用于检查窗口是否可见并获取其标题。
    """
    if win32gui.IsWindowVisible(hwnd):
        window_text = win32gui.GetWindowText(hwnd)
        if window_text:  # 排除没有标题的窗口
            print(f"Handle: {hwnd}, Title: {window_text}")
            windows.append((hwnd, window_text))
    return True

def get_all_window_titles():
    """
    获取当前所有可见窗口的标题。
    """
    print("Enumerating windows...")
    windows = []
    win32gui.EnumWindows(enum_windows_proc, windows)
    return windows

import win32gui

def get_window_position(hwnd):
    """
    获取具有特定标题的窗口的屏幕位置和大小。
    """

    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    width = right - left  # 计算窗口宽度
    height = bottom - top  # 计算窗口高度
    print(f"Window '{hwnd}' is located at ({left}, {top}), with width {width}px and height {height}px.")

    return left, top, right, bottom


import pygetwindow as gw
import pyautogui

def get_mouse_window_rect():
    x, y = pyautogui.position()
    win = gw.getWindowsAt(x, y)
    if win:
        win = win[0]  # 获取鼠标下的第一个窗口
        return (win.left, win.top, win.left + win.width, win.top + win.height)
    else:
        return None



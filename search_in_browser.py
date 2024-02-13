from collections import Counter
import pyautogui
import pyperclip



def locate_text(keyword):
    from frog_eye import find_all_highlight_rect

    pyautogui.hotkey('ctrl', 'f')

    pyperclip.copy(keyword)
    pyautogui.hotkey('ctrl', 'a', 'v')
    pyautogui.press('enter')
    img_before = pyautogui.screenshot()

    pyautogui.hotkey('ctrl', 'a', 'backspace')
    img_after = pyautogui.screenshot()

    pyautogui.press('esc')

    rects = find_all_highlight_rect(img_before, img_after, vis=False, width_height_ratio=len(keyword))
    line_height = Counter([rect[:, 1].max() - rect[:, 1].min() for rect in rects]).most_common(1)[0][0]

    rects.sort(key=lambda e: (e[:, 1].min(axis=0) // line_height) * 10000 + e[:, 0].min(axis=0))

    return rects, line_height

if __name__ == '__main__':
    import time
    time.sleep(2)
    keyword = "要使用pyautogui库在浏览器中实现滑动到页面底端的功能，通常涉及模拟按键操作，如使用Page Down键或End键。但是，需要注意的是，pyautogui主要用于模拟鼠标和键盘操作，其作用与直接使用浏览器提供的快捷键或JavaScript代码执行滑动操作略有不同。以下是一个简单的步骤指南，展示如何使用pyautogui实现这一功能"
    rects, line_height = locate_text(keyword)
    print(len(rects))


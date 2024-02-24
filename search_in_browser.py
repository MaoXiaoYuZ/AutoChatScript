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
    
    if rects:
        line_height = Counter([rect[:, 1].max() - rect[:, 1].min() for rect in rects]).most_common(1)[0][0]

        rects.sort(key=lambda e: (e[:, 1].min(axis=0) // line_height) * 10000 + e[:, 0].min(axis=0))
    else:
        line_height = None

    return rects, line_height

if __name__ == '__main__':
    import time
    time.sleep(2)
    keyword = "7tAYlnGUJYRw"
    rects, line_height = locate_text(keyword)
    pyautogui.moveTo(rects[0].mean(axis=0).tolist())
    print(len(rects))


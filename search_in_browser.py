import pyautogui
import pyperclip



def locate_text(keyword):
    from frog_eye import find_optimal_highlight_rect

    pyautogui.hotkey('ctrl', 'f')

    pyperclip.copy(keyword)
    pyautogui.hotkey('ctrl', 'a', 'v')
    img_before = pyautogui.screenshot()

    pyautogui.hotkey('ctrl', 'a', 'backspace')
    img_after = pyautogui.screenshot()

    rect = find_optimal_highlight_rect(img_before, img_after, vis=False, width_height_ratio=len(keyword))

    return rect

if __name__ == '__main__':
    import time
    time.sleep(2)
    keyword = "Message ChatGPT"
    rect = locate_text(keyword)
    print(rect)


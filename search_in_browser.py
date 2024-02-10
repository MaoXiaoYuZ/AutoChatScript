import pyautogui
import pyperclip

def search(keword):
    pyautogui.hotkey('ctrl', 'f')
    pyperclip.copy(keword)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')

def close():
    pyautogui.press('esc')

def locate_text(keyword):
    from frog_eye import find_optimal_highlight_rect
    search(keyword)
    img_before = pyautogui.screenshot()
    close()
    img_after = pyautogui.screenshot()
    
    rect = find_optimal_highlight_rect(img_before, img_after, vis=False, width_height_ratio=len(keyword))

    if rect is None or True:    # 暂时直接采用失去焦点后的判断结果
        img_before = img_after
        pyautogui.click()
        img_after = pyautogui.screenshot()

        rect = find_optimal_highlight_rect(img_before, img_after, vis=False, width_height_ratio=len(keyword))
    else:
        pyautogui.click()

    return rect

if __name__ == '__main__':
    import time
    time.sleep(2)
    keyword = "后一个三引号对只有前面那个"
    rect = locate_text(keyword)
    print(rect)


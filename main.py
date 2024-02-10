import pyautogui
import pyperclip
import time
from PIL import Image

import frog_eye
import search_in_browser


#keyword = input("请输入您要搜索的关键词: ")
keyword = "请在一个三引号"
time.sleep(2)
img_before = pyautogui.screenshot()
search_in_browser.search(keyword)
img_after = pyautogui.screenshot()
rect = frog_eye.find_optimal_highlight_rect(img_before, img_after)
line_height = rect[:, 1].max() - rect[:, 1].min()
line_left_top = rect.min(axis=0)
next_line_left_top = (line_left_top[0], line_left_top[1] + line_height)
pyautogui.moveTo(next_line_left_top[0], next_line_left_top[1])
exit(0)


# 加载图片
submit_button_png = Image.open('submit_button.png')
input_box_png = Image.open('input_box.png')
copy_retry_feedback_png = Image.open('copy_retry_feedback.png')

# 定位输入框和提交按钮的位置
submit_button_pos = pyautogui.locateCenterOnScreen(submit_button_png, confidence=0.9)
input_box_pos = pyautogui.locateCenterOnScreen(input_box_png, confidence=0.9)

# 获取用户输入的内容
while user_input := input("请输入您的内容: "):
    # 将光标移动到输入框并点击，准备输入内容
    pyautogui.click(*input_box_pos)
    pyperclip.copy(user_input)
    pyautogui.hotkey('ctrl', 'v')

    # 移动到提交按钮并点击
    pyautogui.click(*submit_button_pos)

    # 定位复制/重试/反馈按钮的位置
    region = (input_box_pos[0]-100, input_box_pos[1]-300, submit_button_pos[0], submit_button_pos[1])
    while True:
        try:
            copy_retry_feedback_pos = pyautogui.locateCenterOnScreen(copy_retry_feedback_png, region=region, confidence=0.9)
        except Exception:
            time.sleep(0.1)
        else:
            break

    # 如果找到了复制/重试/反馈按钮，定位复制按钮并点击
    if copy_retry_feedback_pos:
        copy_pos = copy_retry_feedback_pos[0]-40, copy_retry_feedback_pos[1]
        pyautogui.click(*copy_pos)

        # 假设响应已复制到剪贴板，您可以使用其他库如pyperclip来获取剪贴板内容
        try:
            response = pyperclip.paste()
            print("响应内容：", response)
        except Exception as e:
            print("获取剪贴板内容失败：", e)
    else:
        print("未能定位到复制/重试/反馈按钮的位置。")

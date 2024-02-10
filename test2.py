import pyautogui
import pyperclip
import time
import re
from PIL import Image
import numpy as np

import frog_eye
import search_in_browser


def focus_chat_input():
    pyautogui.hotkey("shift", "esc")

def new_chat():
    pyautogui.hotkey("ctrl", "shift", "o")

def copy_last_response():
    pyautogui.hotkey("ctrl", "shift", "c")
    return pyperclip.paste()

def submit(prompt):
    focus_chat_input()
    pyperclip.copy(prompt)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("tab")
    pyautogui.press("tab")
    pyautogui.press("enter")

def match_code_block(response):
    pattern = r"(?<=[\r\n])```.*?```(?=[\r\n])"
    matches = re.findall(pattern, '\n' + response + '```\n', re.DOTALL)
    return matches

def resubmit(prompt):
    focus_chat_input()
    pyperclip.copy(prompt)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.keyDown('shift')

    pyautogui.press("tab")  # Bad response
    pyautogui.press("tab")  # Regenerate
    pyautogui.press("tab")  # Copy

    matches = match_code_block(copy_last_response())

    pyautogui.keyUp('shift')
    #pyautogui.press("enter")

def regenerate():
    focus_chat_input()
    pyautogui.hotkey("shift", "tab", "tab")
    pyautogui.press("enter")



time.sleep(1)
last_response = copy_last_response()

a = match_code_block(last_response)

last_response = "你的pattern有问题，没有匹配三引号，而是单引号，另外没有考虑到消息被截断的情况，也就是最后一个三引号对只有前面那个"


def find_buttom():
    last_para = [e for e in last_response.split("\n") if e.strip()][-1]
    left_top_text = last_para[:5]
    right_bottom_text = last_response[-5:]

    left_top_rect = search_in_browser.locate_text(left_top_text)
    right_bottom_rect = search_in_browser.locate_text(right_bottom_text)
    line_height = right_bottom_rect[:, 1].max() - left_top_rect[:, 1].max()

    next_line_left_top = (left_top_rect[:, 0].min(axis=0), right_bottom_rect[:, 1].max())
    first_char_center = next_line_left_top + line_height // 2

    pyautogui.moveTo(first_char_center[0], first_char_center[1])


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

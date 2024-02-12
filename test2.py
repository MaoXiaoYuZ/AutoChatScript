import os
import pyautogui
import pyperclip
import time
import re
from PIL import Image
import numpy as np

import frog_eye
import cursor
import search_in_browser
import windows_api




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
    pyautogui.hotkey("ctrl", "a")
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


def wait_image(image, region=None, timeout=10):
    t0 = time.time()
    while True:
        try:
            left, top, right, bottom = region        
            pos = pyautogui.locateCenterOnScreen(image, region=(left, top, right - left, bottom - top), confidence=0.9)
        except Exception:
            if time.time() - t0 > timeout:
                pyautogui.alert(text='未能定位到图片！(Failed to locate the image!) ', title='程序终止(Program Abort)', button='OK')
                return None
            time.sleep(0.1)
        else:
            break

    return pos

def locate_image(image):
    try:
        location = pyautogui.locateOnScreen(image, confidence=0.9)
    except Exception:
        pyautogui.alert(text='未能定位到图片！(Failed to locate the image!) ', title='程序终止(Program Abort)', button='OK')
        return None
    
    return location.left, location.top, location.left + location.width, location.top + location.height


retry_button_path = "detected_images/retry_button.png"
submit_button_path = "detected_images/submit_button.png"

def location_retry_button():
    last_response = copy_last_response()
    last_para = [e for e in last_response.split("\n") if e.strip()][-1]
    left_top_text = last_para[:5]
    right_bottom_text = last_response[-5:]

    left_top_rect = search_in_browser.locate_text(left_top_text)
    right_bottom_rect = search_in_browser.locate_text(right_bottom_text)
    line_height = right_bottom_rect[:, 1].max() - right_bottom_rect[:, 1].min()
    next_line_left_top = (left_top_rect[:, 0].min(axis=0), right_bottom_rect[:, 1].max())

    button_right_bottom = next_line_left_top[0] + line_height * 10, next_line_left_top[1] + line_height * 2

    button_boundary_list = cursor.detect_button_boundary(
        next_line_left_top, 
        button_right_bottom, 
        step=line_height // 2, 
        sub_step=line_height // 8, 
        only_first=True)
    
    if len(button_boundary_list) == 1:
        left, top, right, bottom = button_boundary_list[0]
        image = pyautogui.screenshot(retry_button_path, region=(left, top, right - left, bottom - top))
    else:
        pyautogui.alert(text='未能定位到重试按钮！(Failed to locate the retry button!) ', title='程序终止(Program Abort)', button='OK')

    return button_boundary_list[0], image

def location_submit_button():
    focus_chat_input()
    pyperclip.copy("Message ChatGPT")
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")

    text_rect = search_in_browser.locate_text("Message ChatGPT")
    line_height = int(text_rect[:, 1].max() - text_rect[:, 1].min())

    button_left_top = int(text_rect[:, 0].max()), int(text_rect[:, 1].min())
    #button_right_bottom = windows_api.get_mouse_window_rect()[2] - line_height // 4, int(text_rect[:, 1].max())
    button_right_bottom = windows_api.get_mouse_window_rect()[2:]

    button_boundary_list = cursor.detect_button_boundary(
        button_left_top, 
        button_right_bottom, 
        step=line_height // 2, 
        sub_step=line_height // 8, 
        only_first=True)
    
    if len(button_boundary_list) == 1:
        left, top, right, bottom = button_boundary_list[0]
        image = pyautogui.screenshot(submit_button_path, region=(left, top, right - left, bottom - top))
    else:
        pyautogui.alert(text='未能定位到重试按钮！(Failed to locate the submit button!) ', title='程序终止(Program Abort)', button='OK')

    return button_boundary_list[0], image

if os.path.exists(submit_button_path):
    submit_button_image = Image.open(submit_button_path)
    submit_button_region = locate_image(submit_button_image)
else:
    submit_button_region, submit_button_image = location_submit_button()
    

if os.path.exists(retry_button_path):
    retry_button_image = Image.open(retry_button_path)
    retry_button_region = locate_image(retry_button_image)
else:
    retry_button_region, retry_button_image = location_retry_button()

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

import functools
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


def focus_window(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 假设第一个参数是调用该方法的类实例
        self = args[0]
        cursor_pos = pyautogui.position()
        flag = False
        if not self._on_focus:
            pyautogui.click(self.window_rect[0] + 10, self.window_rect[1] + 10)
            self._on_focus = True
            flag = True
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            if flag:
                pyautogui.moveTo(cursor_pos)
                self._on_focus = False
            
    return wrapper


class ChatGPT_Auto_Script:
    def __init__(self):
        self.retry_button_path = "detected_images/retry_button.png"
        self.submit_button_path = "detected_images/submit_button.png"
        self.resubmit_button_path = "detected_images/resubmit_button.png"
        self._on_focus = False

    
    def init(self):
        # 执行这段代码前要保证鼠标焦点在chatgpt网页上
        cursor_pos = pyautogui.position()

        self.scroll_to_bottom()

        self.window_rect = windows_api.get_mouse_window_rect()

        if os.path.exists(self.submit_button_path):
            self.submit_button_image = Image.open(self.submit_button_path)
            self.submit_button_region = self.locate_image(self.submit_button_image, confidence=0.9)
        else:
            self.submit_button_region, self.submit_button_image = self.locate_submit_button()

        if os.path.exists(self.retry_button_path):
            self.retry_button_image = Image.open(self.retry_button_path)
        else:
            _, self.retry_button_image = self.locate_retry_button()
        
        if os.path.exists(self.resubmit_button_path):
            self.resubmit_button_image = Image.open(self.resubmit_button_path)
        else:
            _, self.resubmit_button_image = self.locate_resubmit_button()

        pyautogui.moveTo(cursor_pos)
    
    def screenshot(self):
        return pyautogui.screenshot(region=self.window_rect)
    
    @focus_window
    def _focus_chat_input(self):
        pyautogui.hotkey("shift", "esc")

    @focus_window
    def new_chat(self):
        pyautogui.hotkey("ctrl", "shift", "o")

    def _wait_last_response(self):
        wait_start = self.wait_stationary(delay=1, timeout=10, reverse=True)
        if wait_start:
            wait_finish = self.wait_stationary(delay=1, timeout=10, reverse=False)
        else:
            raise Exception("ChatGPT未能返回响应！(ChatGPT failed to return a response!)")

        return self.copy_last_response()
    
    @focus_window
    def copy_last_response(self):
        pyautogui.hotkey("ctrl", "shift", "c")
        return pyperclip.paste()

    @focus_window
    def submit(self, prompt):
        self._focus_chat_input()
        pyperclip.copy(prompt)
        pyautogui.hotkey("ctrl", "a", "v")

        pos = self.wait_image(self.submit_button_image, region=self.submit_button_region, confidence=0.9, timeout=0)
        if pos is None:
            self.submit_button_region, self.submit_button_image = self.locate_submit_button()
            return
        else:
            pyautogui.click(pos)
        
        try:
            response = self._wait_last_response()
        except Exception as e:
            print(e)
        
        return response

    def match_code_block(self, response):
        pattern = r"(?<=[\r\n])```.*?```(?=[\r\n])"
        matches = re.findall(pattern, '\n' + response + '```\n', re.DOTALL)
        return matches
    
    def scroll_to_bottom(self):
        pyautogui.scroll(-1000)

    @focus_window
    def resubmit(self, prompt):
        button_left_top, button_right_bottom, line_height = self.estimate_resubmit_button_reigon()

        pyautogui.moveTo(button_left_top[0], button_left_top[1])

        pos = self.wait_image(self.resubmit_button_image, region=(*button_left_top, *button_right_bottom), confidence=0.9, timeout=0)
        
        if pos is None:
            #self.resubmit_button_region, self.resubmit_button_image = self.locate_resubmit_button()
            raise Exception("未能定位到resubmit按钮！(Failed to locate the resubmit button!)")
            return
        else:
            pyautogui.click(pos)
        
        pyperclip.copy(prompt)
        pyautogui.hotkey("ctrl", "a", "v")
        pyautogui.hotkey("tab", "enter")

        try:
            response = self._wait_last_response()
        except Exception as e:
            print(e)
        
        return response

    @focus_window
    def regenerate(self):
        self._focus_chat_input()
        pyautogui.hotkey("shift", "tab", "tab")
        pyautogui.press("enter")

    def wait_image(self, image, region=None, confidence=1, timeout=10):
        t0 = time.time()
        while True:
            try:
                if region is not None:
                    left, top, right, bottom = region        
                    region = (left, top, right - left, bottom - top)
                pos = pyautogui.locateCenterOnScreen(image, region=region, confidence=confidence)
                return pos
            except Exception:
                if time.time() - t0 > timeout:
                    return None
                time.sleep(0.1)
    
    def wait_stationary(self, delay=2, timeout=10, reverse=False):
        t0 = time.time()
        img_before = self.screenshot()
        cur_delay = delay
        while True:
            time.sleep(0.5)
            img_after = self.screenshot()
            is_stationary = frog_eye.is_stationary(img_before, img_after)
            if not is_stationary if reverse else is_stationary:
                cur_delay -= 0.5
                if cur_delay <= 0:
                    return True
            else:
                cur_delay = delay
            if time.time() - t0 > timeout:
                return False        
            img_before = img_after

    def locate_image(self, image, region=None, confidence=1):
        try:
            location = pyautogui.locateOnScreen(image, region=region, confidence=confidence)
        except Exception:
            return None
        
        return location.left, location.top, location.left + location.width, location.top + location.height

    def manual_locate_image(self, image_file):
        while not input("移动鼠标，悬停到按钮上后，按下回车键"):
            if cursor.get_cursor_state() != 'HAND':
                print("请将鼠标移动到按钮上！")
            else:
                cursor_pos = np.asarray(pyautogui.position())
                ((left, top), (right, bottom)) = cursor.detect_cur_button_boundary(cursor_pos, cursor_pos - 200, cursor_pos + 200, step=5)
                image = pyautogui.screenshot(image_file, region=(left, top, right - left, bottom - top))
                pyautogui.moveTo(cursor_pos[0], cursor_pos[1])
                return (left, top, right, bottom), image

    @focus_window
    def locate_retry_button(self):
        last_response = self.copy_last_response()
        last_para = [e for e in last_response.split("\n") if e.strip()][-1]
        last_para = last_para.replace('`', '')

        text_rects, line_height = search_in_browser.locate_text(last_para)
        left_top_rect = text_rects[0]
        right_bottom_rect = text_rects[-1]
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
            image = pyautogui.screenshot(self.retry_button_path, region=(left, top, right - left, bottom - top))
        else:
            assert False, "未能定位到重试按钮！(Failed to locate the retry button!)"

        return button_boundary_list[0], image
    
    @focus_window
    def estimate_resubmit_button_reigon(self):
        last_response = self.copy_last_response()
        left_top_text = [e for e in last_response.split("\n") if e.strip()][0]
        left_top_text = left_top_text.replace('`', '')

        text_rects, line_height = search_in_browser.locate_text(left_top_text)
        left_top_rect = text_rects[0]
        
        button_left_top = left_top_rect.min(axis=0) + np.array([-line_height, -line_height * 5])

        button_right_bottom = left_top_rect.max(axis=0)

        return button_left_top, button_right_bottom, line_height

    @focus_window
    def locate_resubmit_button(self):
        button_left_top, button_right_bottom, line_height = self.estimate_resubmit_button_reigon()

        button_boundary_list = cursor.detect_button_boundary(
            button_left_top, 
            button_right_bottom, 
            step=line_height // 2, 
            sub_step=line_height // 8, 
            only_first=True)
        
        if len(button_boundary_list) == 1:
            left, top, right, bottom = button_boundary_list[0]
            pyautogui.moveTo(left, top - line_height)
            image = pyautogui.screenshot(self.resubmit_button_path, region=(left, top, right - left, bottom - top))
        else:
            assert False, "未能定位到resubmit按钮！(Failed to locate the resubmit button!)"

        return button_boundary_list[0], image

    @focus_window    
    def locate_submit_button(self):
        self._focus_chat_input()
        
        pyperclip.copy("u_hZ26nN:JC.3Dj")
        pyautogui.hotkey("ctrl", "a", "v")

        text_rects, line_height = search_in_browser.locate_text("u_hZ26nN:JC.3Dj")
        text_rect = text_rects[0]

        button_left_top = int(text_rect[:, 0].max()), int(text_rect[:, 1].min())
        #button_right_bottom = windows_api.get_mouse_window_rect()[2] - line_height // 4, int(text_rect[:, 1].max())
        button_right_bottom = self.window_rect[2:]

        button_boundary_list = cursor.detect_button_boundary(
            button_left_top, 
            button_right_bottom, 
            step=line_height // 2, 
            sub_step=line_height // 8, 
            only_first=True)
        
        if len(button_boundary_list) == 1:
            left, top, right, bottom = button_boundary_list[0]
            image = pyautogui.screenshot(self.submit_button_path, region=(left, top, right - left, bottom - top))
        else:
            assert False, "未能定位到submit按钮！(Failed to locate the submit button!)"

        return button_boundary_list[0], image
    
    def demo(self):
        print("请在三秒后将鼠标移动到chatgpt网页上...")
        # print("3...")
        # time.sleep(1)
        # print("2...")
        # time.sleep(1)
        print("1...")
        time.sleep(1)
        print("开始初始化...")
        self.init()
        while prompt := input("User: "):
            self.submit(prompt)
            print("ChatGPT:", self.wait_last_response())

#remove all file in detected_images
# for file in os.listdir("detected_images"):
#     os.remove(os.path.join("detected_images", file))
chatgpt = ChatGPT_Auto_Script()
# time.sleep(1)
# chatgpt.init()
# #chatgpt.new_chat()
# chatgpt.resubmit("翻译为一个英文函数名：手动定位图片")

while True:
    chatgpt.manual_locate_image('test.png')
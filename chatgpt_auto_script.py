# ChatGPT网页的自动化脚本，只实现自动化操作，不存储任何数据

import functools
import os
import pyautogui
import pyperclip
import time
import re
import random
import string
from PIL import Image
import numpy as np

import frog_eye
import cursor
import search_in_browser
import windows_api

from pynput.mouse import Listener


class ChatGPTAutoScript:
    def __init__(self):
        self.retry_button_path = "detected_images/retry_button.png"
        self.submit_button_path = "detected_images/submit_button.png"
        self.resubmit_button_path = "detected_images/resubmit_button.png"
        self._on_focus = False

    def focus_window(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 假设第一个参数是调用该方法的类实例
            self = args[0]
            cursor_pos = pyautogui.position()
            flag = False
            if not self._on_focus:
                self._focus_chat_input()
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

    def init_window_rect(self):
        self.window_rect = windows_api.get_mouse_window_rect()

    def test(self):
        self.new_chat()

        prompt = "Translate to Chinese: This is a test."
        print("User:", prompt)
        response = self.submit(prompt)
        print("ChatGPT:", response)

        prompt = "Translate to Chinese: This is the second test."
        print("User:", prompt)
        response = self.resubmit(prompt)
        print("ChatGPT:", response)

    def init_submit_button(self):
        cursor_pos = pyautogui.position()

        init_submit_button_flag = True
        if os.path.exists(self.submit_button_path):
            self.submit_button_image = Image.open(self.submit_button_path)
            if (region := self.locate_image(self.submit_button_image, confidence=0.9)):
                self.submit_button_region = self.pad_image_region(region)
                cursor_pos = pyautogui.position()
                pyautogui.moveTo(region[0], region[1])
                self.init_window_rect()
                pyautogui.moveTo(cursor_pos)
                init_submit_button_flag = False

        if init_submit_button_flag:
            pyautogui.alert(text='程序将监听鼠标点击，请将鼠标移动到ChatGPT网页空白处，并点击一次。\nThe program will listen for mouse clicks, please move the mouse to a blank area of the ChatGPT webpage and click once.', title='初始化自动脚本 (Initialize AutoChatScript)', button='ok')
            
            # 定义点击事件处理函数
            def on_click(x, y, button, pressed):
                if pressed:
                    print(f"Mouse clicked at ({x}, {y})")
                    return False  # 返回False以停止监听

            # 启动监听
            with Listener(on_click=on_click) as listener:
                listener.join()

            print("开始初始化...")
            self.init_window_rect()
            self.submit_button_region, self.submit_button_image = self.locate_submit_button()

     
        # if os.path.exists(self.retry_button_path):
        #     self.retry_button_image = Image.open(self.retry_button_path)
        # else:
        #     _, self.retry_button_image = self.locate_retry_button()
        
        # if os.path.exists(self.resubmit_button_path):
        #     self.resubmit_button_image = Image.open(self.resubmit_button_path)
        # else:
        #     _, self.resubmit_button_image = self.locate_resubmit_button()

        pyautogui.moveTo(cursor_pos)
    
    def wait_submit_image(self, timeout=0):
        pos = self.wait_image(self.submit_button_image, region=self.submit_button_region, confidence=0.9, timeout=0)
        if pos is None:
            self.init_submit_button()
            pos = self.wait_image(self.submit_button_image, region=self.submit_button_region, confidence=0.9, timeout=timeout)
            if pos is None:
                raise Exception("未能定位到submit按钮！(Failed to locate the submit button!)")
        return pos
    
    def init_resubmit_button(self):
        if os.path.exists(self.resubmit_button_path):
            self.resubmit_button_image = Image.open(self.resubmit_button_path)
        else:
            pyautogui.alert(text='点击ok后，程序将自动检测修改按钮图片。\nAfter clicking ok, the program will automatically detect the resubmit button image.', title='初始化自动脚本 (Initialize AutoChatScript)', button='ok')
            
            while (response := self.copy_last_response()) is None:
                pyautogui.alert(text='请展示有对话内容的网页，以便程序检测修改按钮位置。\nPlease display a webpage with dialogue content so the program can detect the position of the resubmit button.', title='初始化自动脚本 (Initialize AutoChatScript)', button='ok')

            _, self.resubmit_button_image = self.locate_resubmit_button(response)
    
    def screenshot(self, filepath=None, region=None):
        if region is None:
            left, top, right, bottom = self.window_rect
        else:
            left, top, right, bottom = region        
        region = (int(left), int(top), int(right - left), int(bottom - top))
        if filepath is not None:
            return pyautogui.screenshot(filepath, region=region)
        else:
            return pyautogui.screenshot(region=region)
    
    def locateCenterOnScreen(self, image, region=None, confidence=1):
        if region is None:
            left, top, right, bottom = self.window_rect
        else:
            left, top, right, bottom = region        
        region = (int(left), int(top), int(right - left), int(bottom - top))

        return pyautogui.locateCenterOnScreen(image, region=region, confidence=confidence)
    
    def _focus_chat_input(self):
        pos = self.wait_submit_image()
        left, top, right, bottom = self.submit_button_region
        pyautogui.click(left, (top + bottom) // 2)
        return pos
    
    def _focus_chat_input_by_keyboard(self):
        pyautogui.hotkey("shift", "esc")

    @focus_window
    def new_chat(self):
        pyautogui.hotkey("ctrl", "shift", "o")

    def _wait_last_response(self):
        # self.scroll_to_bottom()
        # wait_start = self.wait_stationary(delay=1, timeout=10, reverse=True)
        # wait_finish = self.wait_stationary(delay=1, timeout=10, reverse=False)
        time.sleep(0.5)     # 等待浏览器响应点击submit事件
        
        wait_start = self.wait_image_disappear(self.submit_button_image, region=self.submit_button_region, confidence=0.9, timeout=30)
        
        if wait_start:
            wait_finish = self.wait_image(self.submit_button_image, region=self.submit_button_region, confidence=0.9, timeout=120)
            if wait_finish:
                response = self.copy_last_response()
                if response is None:
                    pyautogui.alert(text='请手动复制，程序将监听下一次的复制内容。\nPlease copy manually, the program will listen for the next copy action.', title='复制快捷键未起效！(Copy shortcut key is not effective!)', button='OK')
                else:
                    if len(response) > 500:
                        continue_generating_button, _ = search_in_browser.locate_text("Continue generating")
                        if continue_generating_button:
                            cursor_pos = pyautogui.position()
                            pyautogui.click(continue_generating_button[0].mean(axis=0).tolist())
                            pyautogui.moveTo(cursor_pos)
                            return self._wait_last_response()
                    else:
                        return response
            else:
                pyautogui.alert(text='请手动复制，程序将监听下一次的复制内容。\nPlease copy manually, the program will listen for the next copy action.', title='ChatGPT回复超时！(ChatGPT response timeout!)', button='OK')
        else:
            pyautogui.alert(text='请手动复制，程序将监听下一次的复制内容。\nPlease copy manually, the program will listen for the next copy action.', title='ChatGPT未响应！(ChatGPT is not responding!)', button='OK')

        return self.wait_for_clip_copy()
    
    def wait_for_clip_copy(self):
        clip_state = pyperclip.paste()
        initial_clipboard_content = self.generate_password()
        pyperclip.copy(initial_clipboard_content)
        while pyperclip.paste() == initial_clipboard_content:
            time.sleep(0.1)
        new_clipboard_content = pyperclip.paste()
        pyperclip.copy(clip_state)
        return new_clipboard_content
    
    def generate_password(self, length=12):
        # 定义密码字符池
        characters = string.ascii_letters + string.digits + "!@#$%^&*()"
        # 随机选择字符生成密码
        password = ''.join(random.choice(characters) for i in range(length))
        return password
    
    @focus_window
    def copy_last_response(self):
        clip_state = pyperclip.paste()
        initial_clipboard_content = self.generate_password()
        pyperclip.copy(initial_clipboard_content)
        
        pyautogui.hotkey("ctrl", "shift", "c")

        if pyperclip.paste() == initial_clipboard_content:
            return None

        new_clipboard_content = pyperclip.paste()
        pyperclip.copy(clip_state)
        return new_clipboard_content

    def submit(self, prompt):
        debug = False
        if debug:
            return debug

        cursor_pos = pyautogui.position()
        pos = self._focus_chat_input()
        pyperclip.copy(prompt)
        pyautogui.hotkey("ctrl", "a", "v")
        pyautogui.scroll(-1_000_000)

        pos = self.wait_submit_image(timeout=0.5)   # 浏览器需要时间响应粘贴和滚动事件
        pyautogui.click(pos)
        pyautogui.moveTo(cursor_pos)
        
        try:
            response = self._wait_last_response()
        except Exception as e:
            print(e)
        
        return response

    def match_code_block(self, response):
        pattern = r"(?<=[\r\n])```.*?```(?=[\r\n])"
        matches = re.findall(pattern, '\n' + response + '```\n', re.DOTALL)
        return matches
    
    def scroll_to_bottom(self, clicks=-1_000_000):
        pos = (self.window_rect[0] + self.window_rect[2]) // 2, (self.window_rect[1] + self.window_rect[3]) // 2
        pyautogui.moveTo(pos)
        pyautogui.scroll(clicks)

    def resubmit(self, prompt, response=None):
        if not hasattr(self, "resubmit_button_image"):
            self.init_resubmit_button()

        if response is None:
            response = self.copy_last_response()
        
        button_left_top, button_right_bottom, line_height = self.estimate_resubmit_button_reigon(response)

        cursor_pos = pyautogui.position()
        pyautogui.moveTo(button_left_top[0] + line_height, button_left_top[1] + line_height)
        pos = self.wait_image(self.resubmit_button_image, region=(*button_left_top, self.window_rect[2], button_right_bottom[1]), confidence=0.9, timeout=0)
        
        if pos is None:
            if os.path.exists(self.resubmit_button_path):
                os.remove(self.resubmit_button_path)
            if hasattr(self, "resubmit_button_image"):
                del self.resubmit_button_image
            return self.resubmit(prompt, response)
        else:
            pyautogui.click(pos)
        
            pyperclip.copy(prompt)
            pyautogui.hotkey("ctrl", "a", "v")
            pyautogui.hotkey("tab", "enter")
            pyautogui.moveTo(cursor_pos)

        try:
            response = self._wait_last_response()
        except Exception as e:
            print(e)
        
        return response

    def wait_image(self, image, region=None, confidence=1, timeout=10, debug=False):
        t0 = time.time()
        while True:
            try:
                if debug:self.screenshot(f"debug/wait_image/{t0:.0f}-{time.time()-t0:.3f}.png", region=region)
                pos = self.locateCenterOnScreen(image, region=region, confidence=confidence)
                return pos
            except Exception:
                if time.time() - t0 > timeout:
                    return None
                time.sleep(0.5 if debug else 0.1)
    
    def wait_image_disappear(self, image, region=None, confidence=1, timeout=10, debug=False):
        t0 = time.time()
        pos = True
        while pos:
            try:
                if debug:self.screenshot(f"debug/wait_image_disappear/{t0:.0f}-{time.time()-t0:.3f}.png", region=region)
                pos = self.locateCenterOnScreen(image, region=region, confidence=confidence)
            except Exception:
                return True
            if time.time() - t0 > timeout:
                return False
            time.sleep(0.5 if debug else 0.1)
     
    def wait_stationary(self, delay=2, timeout=10, reverse=False, debug=False):
        t0 = time.time()
        img_before = self.screenshot()
        cur_delay = delay
        if debug:os.makedirs(f"debug/wait_stationary/{t0}")
        while True:
            time.sleep(0.5)
            img_after = self.screenshot()
            ret_change_ratio = []
            is_stationary = frog_eye.is_stationary(img_before, img_after, ret_change_ratio=ret_change_ratio)
            if reverse: is_stationary = not is_stationary
            if is_stationary:
                cur_delay -= 0.5
                if debug:img_after.save(f"debug/wait_stationary/{t0}/{time.time()}-{ret_change_ratio[0]}-{cur_delay}.png")
                if cur_delay <= 0:
                    return True
            else:
                if debug:img_after.save(f"debug/wait_stationary/{t0}/{time.time()}-{ret_change_ratio[0]}-{cur_delay}.png")
                cur_delay = delay
            if time.time() - t0 > timeout:
                return False        
            img_before = img_after

    def locate_image(self, image, confidence=1):
        try:
            location = pyautogui.locateOnScreen(image, confidence=confidence)
        except Exception:
            return None
        
        return location.left, location.top, location.left + location.width, location.top + location.height

    def pad_image_region(self, region, pad = 50):
        left, top, right, bottom = region
        return (left - pad, top - pad, right + pad, bottom + pad)

    def manual_locate_image_region(self, image_file):
        while not input("移动鼠标，悬停到按钮上后，按下回车键"):
            if cursor.get_cursor_state() != 'HAND':
                print("请将鼠标移动到按钮上！")
            else:
                cursor_pos = np.asarray(pyautogui.position())
                region = cursor.detect_cur_button_boundary(cursor_pos, cursor_pos - 200, cursor_pos + 200, step=5)
                image = self.screenshot(image_file, region=region)
                pyautogui.moveTo(cursor_pos[0], cursor_pos[1])
                return self.pad_image_region(region), image

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
            image = self.screenshot(self.retry_button_path, region=button_boundary_list[0])
        else:
            assert False, "未能定位到重试按钮！(Failed to locate the retry button!)"

        return self.pad_image_region(button_boundary_list[0]), image
    
    @focus_window
    def estimate_resubmit_button_reigon(self, response):
        for left_top_text in response.split("\r\n"):
            if left_top_text.startswith('```'):
                continue
            left_top_text = left_top_text.replace("`", "")
            if len(left_top_text) < 7:
                continue
            break
        left_top_text = left_top_text.replace('`', '')

        text_rects, line_height = search_in_browser.locate_text(left_top_text)
        left_top_rect = text_rects[0]
        
        button_left_top = left_top_rect.min(axis=0) + np.array([-line_height, -line_height * 5])
        button_right_bottom = left_top_rect.max(axis=0)

        # if button_left_top is on the top of the window, scroll to the bottom
        if (button_left_top[1] - self.window_rect[1]) / (self.window_rect[3] - self.window_rect[1]) < 0.25:
            self.scroll_to_bottom(clicks=(self.window_rect[3] - self.window_rect[1]) // 4)
            
            text_rects, line_height = search_in_browser.locate_text(left_top_text)
            left_top_rect = text_rects[0]
            
            button_left_top = left_top_rect.min(axis=0) + np.array([-line_height * 2, -line_height * 7])
            button_right_bottom = left_top_rect.max(axis=0)

        return button_left_top.tolist(), button_right_bottom.tolist(), int(line_height)

    @focus_window
    def locate_resubmit_button(self, response):
        button_left_top, button_right_bottom, line_height = self.estimate_resubmit_button_reigon(response)

        button_boundary_list = cursor.detect_button_boundary(
            button_left_top, 
            button_right_bottom, 
            step=line_height // 2, 
            sub_step=line_height // 8, 
            only_first=True)
        
        if len(button_boundary_list) == 1:
            left, top, right, bottom = button_boundary_list[0]
            pyautogui.moveTo(left, top - line_height)
            image = self.screenshot(self.resubmit_button_path, region=button_boundary_list[0])
        else:
            assert False, "未能定位到resubmit按钮！(Failed to locate the resubmit button!)"

        return self.pad_image_region(button_boundary_list[0]), image

    def locate_submit_button(self):
        self._focus_chat_input_by_keyboard()
        
        #random_string = self.generate_password()
        random_string = "This Say a is Test!"
        pyperclip.copy(random_string)
        pyautogui.hotkey("ctrl", "a", "v")

        text_rects, line_height = search_in_browser.locate_text(random_string)
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
            image = self.screenshot(self.submit_button_path, region=button_boundary_list[0])
        else:
            assert False, "未能定位到submit按钮！(Failed to locate the submit button!)"

        return self.pad_image_region(button_boundary_list[0]), image
    
    def demo(self):
        self.init_submit_button()
        while prompt := input("User(q to quit, r to resubmit): "):
            if prompt == 'q':
                break
            elif prompt == 'r':
                prompt = input("\t resubmit:")
                response = self.resubmit(prompt)
                print("ChatGPT:", response)
            elif len(prompt) == 0:
                print("Input cannot be empty!")
            else:
                response = self.submit(prompt)
                print("ChatGPT:", response)

#remove all file in detected_images
# for file in os.listdir("detected_images"):
#     os.remove(os.path.join("detected_images", file))
if __name__ == "__main__":
    chatgpt = ChatGPTAutoScript()
    #response = chatgpt.submit("你好")
    #print(response)
    chatgpt.demo()
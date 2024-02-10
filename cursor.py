import os
import time

import win32gui
import win32con

import pyautogui

from sklearn.cluster import DBSCAN
import numpy as np

pyautogui.PAUSE = 0
pyautogui.DARWIN_CATCH_UP_TIME = 0.01
pyautogui.FAILSAFE = False

class Cursor:
    def get_state(self, ):
        """
        获取当前鼠标光标的状态。
        """

        # 获取光标的图标ID，这个ID可以用来判断光标的类型
        cursor_id = win32gui.GetCursorInfo()[1]
        
        # 例如，可以通过比较cursor_id与系统预定义的光标类型来判断光标状态
        if cursor_id == win32gui.LoadCursor(0, win32con.IDC_ARROW):
            return "ARROW"
        elif cursor_id == win32gui.LoadCursor(0, win32con.IDC_IBEAM):
            return "IBEAM"
        elif cursor_id == win32gui.LoadCursor(0, win32con.IDC_HAND):
            return "HAND"
        else:
            print("Unknown cursor.")
            return None
    
    def set_pos(self, x, y):
        """
        设置鼠标光标的位置。
        """
        pyautogui.moveTo(x, y)


    def detect_hand_location(self, left_top, right_bottom, step=20):
        import frog_eye
        t0 = time.time()
        i = 0
        left, top = left_top
        right, bottom = right_bottom

        left = 0
        top = 0

        self.set_pos(-1, -1)
        
        bg_img = pyautogui.screenshot(region=(left, top, right - left, bottom - top))

        frog_eye.vis_contours(bg_img, [], delay=0)
        
        hand_positions = []

        for x in range(left + step, right, step):  # 以50像素的步长在屏幕上移动鼠标
            for y in range(top + step, bottom, step):
                self.set_pos(x, y)
                i += 1
                time.sleep(0.05)
                state = self.get_state()
                if state == "HAND":
                    hand_positions.append((x, y))
                    # file_path = os.path.join("cursor_area", f"HAND-{i:06d}.png")
                    img = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
                    contours = frog_eye.find_contours(bg_img, img, thresh=1)
                    if contours:
                        frog_eye.vis_contours(img, contours, delay=1)
                        pass
                
                if time.time() - t0 > 60:
                    print("Timeout.")
                    return
                
        print(f"Time: {time.time() - t0:.2f} seconds")
        return self.merge_positions_using_dbscan(hand_positions, eps=step+1, min_samples=2)
    
    def merge_positions_using_dbscan(self, positions, eps=10, min_samples=2):
        """
        使用DBSCAN算法合并手形光标位置。
        
        :param positions: 手形光标的位置列表，格式为[(x1, y1), (x2, y2), ...]
        :param eps: DBSCAN的邻域半径参数
        :param min_samples: 形成簇所需的最小样本数
        :return: 按簇合并后的手形光标位置的列表，格式为[[(x11, y11), (x12, y12), ...], ...]
        """
        if not positions:
            return []

        # 将位置转换为NumPy数组以供DBSCAN使用
        X = np.array(positions)
        
        # 应用DBSCAN算法
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
        labels = db.labels_
        
        # 将位置按照所属簇组织起来
        clusters = {}
        for label, position in zip(labels, positions):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(position)
        
        # 忽略噪声点，仅返回有效簇
        clusters = [np.array(clusters[label]) for label in clusters if label != -1]
        return clusters

if __name__ == '__main__':
    cursor = Cursor()
    result = cursor.detect_hand_location((0, 0), (400, 500))
    for hand in result:
        left_top = hand.min(axis=0)
        right_bottom = hand.max(axis=0)
        left, top, right, bottom = left_top[0].item(), left_top[1].item(), right_bottom[0].item(), right_bottom[1].item()
        pyautogui.screenshot(os.path.join("cursor_area", f"HAND-{left}-{top}-{right}-{bottom}.png"), region=(left, top, right - left, bottom - top))
        print(hand.min(axis=0), hand.max(axis=0))
        print()

import os
import time

import win32gui
import win32con
import functools
import pyautogui


from sklearn.cluster import DBSCAN
import numpy as np


def modify_pyautogui_settings(func):
    @functools.wraps(func)  # 保持被修饰函数的元数据
    def wrapper(*args, **kwargs):
        # 保存当前pyautogui设置
        pyautogui_values = (pyautogui.PAUSE, pyautogui.DARWIN_CATCH_UP_TIME, pyautogui.FAILSAFE)
        
        # 临时修改设置
        pyautogui.PAUSE, pyautogui.DARWIN_CATCH_UP_TIME, pyautogui.FAILSAFE = 0.01, 0.01, False
        
        try:
            # 执行被修饰的函数
            return func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            # 恢复原来的pyautogui设置
            pyautogui.PAUSE, pyautogui.DARWIN_CATCH_UP_TIME, pyautogui.FAILSAFE = pyautogui_values
            
    return wrapper


def get_cursor_state():
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


def _detect_button_boundary(start_pos, left_top, right_bottom, step=20):
    directions = ['left', 'right', 'up', 'down']
    bounds = {}

    # 定义搜索边界
    search_boundaries = {
        'left': left_top[0],
        'right': right_bottom[0],
        'up': left_top[1],
        'down': right_bottom[1]
    }

    cursor_pos = pyautogui.position()

    for direction in directions:
        x, y = start_pos
        while True:
            if direction == 'left':
                x -= step
            elif direction == 'right':
                x += step
            elif direction == 'up':
                y -= step
            elif direction == 'down':
                y += step
            else:
                break

            if  x < search_boundaries['left'] or x > search_boundaries['right'] or y < search_boundaries['up'] or y > search_boundaries['down']:
                # 如果到达了搜索区域的边界，结束搜索
                bounds[direction] = (x, y)
                break

            if pyautogui.position() == cursor_pos:
                pyautogui.moveTo(x, y)
                cursor_pos = (x, y)
            else:
                pyautogui.alert(text='检测到人为鼠标移动！(Detected artificial mouse movement!) ', title='程序终止(Program Abort)', button='OK')
                return

            if get_cursor_state() != "HAND":
                # 一旦光标状态不是手形，记录边界点并跳出循环
                bounds[direction] = (x, y)
                break

    # 计算矩形左上角和右下角的坐标
    left = bounds.get('left', start_pos)[0]
    right = bounds.get('right', start_pos)[0]
    top = bounds.get('up', start_pos)[1]
    bottom = bounds.get('down', start_pos)[1]

    return (int(left), int(top)), (int(right), int(bottom))

@modify_pyautogui_settings
def detect_button_boundary(left_top, right_bottom, step=20, sub_step=5, only_first=False):
    width = right_bottom[0] - left_top[0]
    height = right_bottom[1] - left_top[1]
    # 创建一个二维数组，初始化为False
    visited = np.full((height // step + 1, width // step + 1), False, dtype=bool)
    
    all_boundaries = []

    for idx_y, y in enumerate(range(left_top[1], right_bottom[1], step)):
        for idx_x, x in enumerate(range(left_top[0], right_bottom[0], step)):
            if visited[idx_y, idx_x]:
                continue  # 如果当前点已经被检查过，跳过

            pyautogui.moveTo(x, y)

            if get_cursor_state() == "HAND":
                rect_start, rect_end = _detect_button_boundary((x, y), left_top, right_bottom, step=sub_step)
                boundary = (*rect_start, *rect_end)
                if only_first:
                    return [boundary, ]

                assert boundary not in all_boundaries
                all_boundaries.append(boundary)

                for by in range(rect_start[1], rect_end[1] + 1, step):
                    for bx in range(rect_start[0], rect_end[0] + 1, step):
                        idx_visited_x = (bx - left_top[0]) // step
                        idx_visited_y = (by - left_top[1]) // step
                        visited[idx_visited_y, idx_visited_x] = True
    return all_boundaries

def merge_positions_using_dbscan(positions, eps=10, min_samples=2):
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

@modify_pyautogui_settings
def detect_hand_location(left_top, right_bottom, step=20):
    t0 = time.time()
    i = 0
    left, top = left_top
    right, bottom = right_bottom
    
    hand_positions = []

    cursor_pos = pyautogui.position()

    for y in range(top, bottom, step):
        for x in range(left, right, step):  # 以50像素的步长在屏幕上移动鼠标
            if pyautogui.position() == cursor_pos:
                pyautogui.moveTo(x, y)
                cursor_pos = (x, y)
            else:
                pyautogui.alert(text='检测到人为鼠标s移动！(Detected artificial mouse movement!) ', title='程序终止(Program Abort)', button='OK')
                return
            i += 1
            state = get_cursor_state()
            if state == "HAND":
                hand_positions.append((x, y))

            if time.time() - t0 > 60:
                print("Timeout.")
                return
   
    print(f"Time: {time.time() - t0:.2f} seconds")

    return merge_positions_using_dbscan(hand_positions, eps=step+1, min_samples=2)

if __name__ == '__main__':
    button_boundary_list = detect_button_boundary((0, 0), (100, 500))
    if len(button_boundary_list) == 1:
        left, top, right, bottom = button_boundary_list[0]
        pyautogui.screenshot(os.path.join("detected_images", f"Button.png"), region=(left, top, right - left, bottom - top))
    exit(0)
    result = detect_hand_location((0, 0), (100, 500))
    for hand in result:
        left_top = hand.min(axis=0)
        right_bottom = hand.max(axis=0)
        left, top, right, bottom = left_top[0].item(), left_top[1].item(), right_bottom[0].item(), right_bottom[1].item()
        pyautogui.screenshot(os.path.join("cursor_area", f"HAND-{left}-{top}-{right}-{bottom}.png"), region=(left, top, right - left, bottom - top))
        print(hand.min(axis=0), hand.max(axis=0))
        print()

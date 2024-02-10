import cv2
import pyautogui

import numpy as np

def find_contours(img_before, img_after, thresh=30):
    img_before, img_after = np.asarray(img_before), np.asarray(img_after)
    
    # 转换为灰度图以加快处理速度
    gray_before = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(img_after, cv2.COLOR_BGR2GRAY)
    
    # 计算两个图像之间的差异
    diff = cv2.absdiff(gray_before, gray_after)
    _, thresh = cv2.threshold(diff, thresh, 255, cv2.THRESH_BINARY)
    
    # 寻找差异区域的轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

def point_in_contour(point, contour):
    dist = cv2.pointPolygonTest(contour, point, False)

    return dist >= 0

def vis_contours(img, contours, delay=0):
    img_vis = np.asarray(img).copy()
    cv2.drawContours(img_vis, contours, 0, (0, 255, 0), 2)
    cv2.imshow('Contours', img_vis)
    cv2.waitKey(delay)
    #cv2.destroyAllWindows()

def find_optimal_highlight_rect(img_before, img_after, width_height_ratio=None, vis=False):
    img_before, img_after = np.asarray(img_before), np.asarray(img_after)
    
    # 寻找差异区域的轮廓
    contours = find_contours(img_before, img_after)
    
    if vis:
        img_vis = img_after.copy()

    valid_rects = []

    for contour in contours:
        # # 对每个轮廓进行近似
        # perimeter = cv2.arcLength(contour, True)
        # approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        
        # # 筛选出近似为矩形的轮廓（有四个顶点）
        # if len(approx) == 4:
        rect = cv2.minAreaRect(contour)  # 获取最小外接矩形
        width, height = max(rect[1]), min(rect[1])

        if rect[2] % 90 != 0:
            continue

        if not (width >= 5 and 400 >= height >= 5):
            continue

        if cv2.contourArea(contour) == 0 or width * height / cv2.contourArea(contour) > 1.01:
            continue

        valid_rects.append(rect)

        if vis:
            cv2.drawContours(img_vis, [contour], 0, (0, 255, 0), 2)    
    
    if vis:
        if not valid_rects:
            for contour in contours:
                cv2.drawContours(img_vis, [contour], 0, (0, 255, 0), 2)    
        cv2.imshow('Changes', img_vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if not valid_rects:
        return None

    # select a best rect with the aspect ratio closest to the given aspect ratio
    if width_height_ratio is not None:
        valid_rects = sorted(valid_rects, key=lambda x: abs(max(rect[1]) / (min(rect[1]) + 1e-6) - width_height_ratio))
    
    best_rect = valid_rects[0]
    
    box = cv2.boxPoints(best_rect)
    box = np.int0(box)

    return box


if __name__ == '__main__':
    img_before = cv2.imread('img_before.png')
    img_after = cv2.imread('img_after.png')
    
    boxes = find_optimal_highlight_rect(img_before, img_after, width_height_ratio=10, vis=True)
    print(len(boxes))
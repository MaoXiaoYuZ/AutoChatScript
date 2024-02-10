from sklearn.cluster import DBSCAN
import numpy as np

def merge_hand_positions_using_dbscan(positions, eps=10, min_samples=2):
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
    clusters = [clusters[label] for label in clusters if label != -1]
    return clusters

# 示例数据：手形光标的位置
positions = [(10, 10), (12, 12), (20, 20), (100, 100), (105, 105)]

# 使用DBSCAN合并位置
merged_positions = merge_hand_positions_using_dbscan(positions, eps=15, min_samples=2)
print("Merged hand positions using DBSCAN:", merged_positions)

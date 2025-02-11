import cv2
import numpy as np

# 画像読み込み
image_path = "C:/Desktop/0013_0000.jpg"
image = cv2.imread(image_path)
original = image.copy()

# 色空間をHSVに変換
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 背景（黒系）の除去を目的にマスク処理
# 黒背景の範囲
lower_black = np.array([0, 0, 0])
upper_black = np.array([180, 255, 50])
mask_black = cv2.inRange(hsv, lower_black, upper_black)

# 背景除去処理
result = cv2.bitwise_not(mask_black)

# ノイズ除去
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
cleaned = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)

# 輪郭検出
contours, _ = cv2.findContours(
    cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 最大の四角形領域を抽出
book_contour = None
max_area = 0

for contour in contours:
    area = cv2.contourArea(contour)
    if area < 50000:  # 小さすぎる領域は無視
        continue

    approx = cv2.approxPolyDP(
        contour, 0.02 * cv2.arcLength(contour, True), True)
    if len(approx) == 4 and area > max_area:
        book_contour = approx
        max_area = area

if book_contour is None:
    print("本の領域が見つかりませんでした")
    exit()

# 透視変換処理
pts = book_contour.reshape(4, 2)
rect = np.zeros((4, 2), dtype="float32")

sums = pts.sum(axis=1)
rect[0] = pts[np.argmin(sums)]
rect[2] = pts[np.argmax(sums)]

diffs = np.diff(pts, axis=1)
rect[1] = pts[np.argmin(diffs)]
rect[3] = pts[np.argmax(diffs)]

width_a = np.linalg.norm(rect[2] - rect[3])
width_b = np.linalg.norm(rect[1] - rect[0])
max_width = max(int(width_a), int(width_b))

height_a = np.linalg.norm(rect[1] - rect[2])
height_b = np.linalg.norm(rect[0] - rect[3])
max_height = max(int(height_a), int(height_b))

dst = np.array([
    [0, 0],
    [max_width - 1, 0],
    [max_width - 1, max_height - 1],
    [0, max_height - 1]
], dtype="float32")

M = cv2.getPerspectiveTransform(rect, dst)
warped = cv2.warpPerspective(image, M, (max_width, max_height))

# 結果表示と保存
cv2.imshow("Extracted Book Page", warped)
cv2.imwrite("output_page.jpg", warped)
cv2.waitKey(0)
cv2.destroyAllWindows()

import cv2
import os


def crop_image_by_percentage(image, top_percentage: float, bottom_percentage: float, left_percentage: float, right_percentage: float):
    height, width = image.shape[:2]

    # 各辺の切り取り幅を計算
    top_crop = int(height * (top_percentage / 100))
    bottom_crop = int(height * (bottom_percentage / 100))
    left_crop = int(width * (left_percentage / 100))
    right_crop = int(width * (right_percentage / 100))

    # 画像の切り取り（上下左右を指定されたパーセント分切り取る）
    cropped_image = image[top_crop:height -
                          bottom_crop, left_crop:width - right_crop]

    return cropped_image


def crop_images_in_folder(folder_path: str, top_percentage: float = 10, bottom_percentage: float = 10, left_percentage: float = 10, right_percentage: float = 10, output_folder: str = "cropped_images"):
    # 出力ディレクトリを作成（必要なら）
    os.makedirs(output_folder, exist_ok=True)

    # 対象ファイル一覧取得（画像形式）
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    image_files = [f for f in os.listdir(
        folder_path) if f.lower().endswith(valid_extensions)]

    if not image_files:
        print("指定フォルダに画像ファイルが見つかりません。")
        return

    for file_name in image_files:
        image_path = os.path.join(folder_path, file_name)
        image = cv2.imread(image_path)

        if image is None:
            print(f"画像読み込みに失敗しました: {file_name}")
            continue

        # 画像切り取り処理
        cropped_image = crop_image_by_percentage(
            image, top_percentage, bottom_percentage, left_percentage, right_percentage)

        # 新しいファイル名作成
        name, ext = os.path.splitext(file_name)
        new_file_name = f"{name}_cropped{ext}"
        output_path = os.path.join(output_folder, new_file_name)

        # 保存
        cv2.imwrite(output_path, cropped_image)
        print(f"保存完了: {output_path}")

    print("すべての画像処理が完了しました。")


# 使用例
# folder_path = "path_to_your_image_folder"
folder_path = "C:/Desktop/aaa"

crop_images_in_folder(folder_path, top_percentage=10, bottom_percentage=10,
                      left_percentage=10, right_percentage=15, output_folder="cropped_images")

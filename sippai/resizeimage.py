import cv2
import os


def resize_images_in_folder(folder_path: str, scale_percent: int = 50):
    # 出力ディレクトリの作成（必要なら）
    output_folder = os.path.join(folder_path, "resized_images")
    os.makedirs(output_folder, exist_ok=True)

    # 対象ファイル一覧取得
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    image_files = [f for f in os.listdir(
        folder_path) if f.lower().endswith(valid_extensions)]

    if not image_files:
        print("指定フォルダに有効な画像が見つかりません。")
        return

    for file_name in image_files:
        image_path = os.path.join(folder_path, file_name)
        image = cv2.imread(image_path)

        if image is None:
            print(f"画像読み込みに失敗しました: {file_name}")
            continue

        # 新しいサイズを計算
        new_width = int(image.shape[1] * scale_percent / 100)
        new_height = int(image.shape[0] * scale_percent / 100)
        new_size = (new_width, new_height)

        # リサイズ処理
        resized_image = cv2.resize(
            image, new_size, interpolation=cv2.INTER_AREA)

        # 新しいファイル名作成
        name, ext = os.path.splitext(file_name)
        new_file_name = f"{name}_resized{ext}"
        output_path = os.path.join(output_folder, new_file_name)

        # 保存
        cv2.imwrite(output_path, resized_image)
        print(f"保存完了: {output_path}")

    print("すべての画像処理が完了しました。")


# フォルダパスと縮小率の指定例
folder_path = "C:/Desktop/aaa"
resize_images_in_folder(folder_path, scale_percent=50)

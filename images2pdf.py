# pip install pillow
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog


def images_to_pdf(folder_path: str, output_pdf_name: str = "output.pdf"):
    # ファイルリスト取得（番号順にソート）
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    image_files = sorted(
        [f for f in os.listdir(folder_path)
         if f.lower().endswith(valid_extensions)])
    #     key=lambda x: int(os.path.splitext(x)[0])  # ファイル名が番号前提の場合
    # )

    if not image_files:
        print("有効な画像ファイルが見つかりません。")
        return

    # 最初の画像をベースにPDF作成
    first_image_path = os.path.join(folder_path, image_files[0])
    first_image = Image.open(first_image_path).convert("RGB")

    # 他の画像を追加
    image_list = [
        Image.open(os.path.join(folder_path, img)).convert("RGB") for img in image_files[1:]
    ]

    # PDF保存
    output_pdf_path = os.path.join(folder_path, output_pdf_name)
    first_image.save(output_pdf_path, save_all=True, append_images=image_list)
    print(f"PDF変換完了: {output_pdf_path}")


def main():
    # フォルダ選択ダイアログを表示して処理対象フォルダを取得
    def select_folder_dialog(initial_dir: str = os.getcwd(), title: str = "PDFに結合する画像のフォルダを選択") -> str | None:
        root = tk.Tk()
        root.withdraw()  # メインウィンドウを表示しない
        folder = filedialog.askdirectory(initialdir=initial_dir, title=title)
        root.destroy()
        return folder if folder else None

    folder_path = select_folder_dialog()
    if not folder_path:
        print("フォルダが選択されませんでした。処理を終了します。")
        return

    images_to_pdf(folder_path, "merged_output.pdf")


if __name__ == "__main__":
    main()

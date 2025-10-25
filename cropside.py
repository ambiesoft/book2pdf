import cv2  # pip install opencv-python
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

import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

def show_folder_and_numbers_dialog():
    """フォルダ選択＋top,bottom,left,rightの整数を入力するダイアログ。
    OKなら dict を返し、キャンセルなら None を返す。
    前回の値はスクリプトと同じディレクトリに保存・復元する。
    """
    # --- 保存ファイルのパス ---
    save_path = os.path.join(os.path.dirname(__file__), "cropside.json")

    # --- 前回の値を読み込み ---
    defaults = {"folder": "", "top": 0, "bottom": 0, "left": 0, "right": 0}
    if os.path.exists(save_path):
        try:
            with open(save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            defaults.update({k: data.get(k, v) for k, v in defaults.items()})
        except Exception as e:
            print("設定ファイルの読み込みに失敗:", e)

    result = {}

    # --- フォルダ選択 ---
    def select_folder():
        folder = filedialog.askdirectory(initialdir=defaults["folder"] or os.getcwd())
        if folder:
            folder_var.set(folder)

    # --- OKボタン処理 ---
    def ok():
        try:
            numbers = {k: int(v.get()) for k, v in entries.items()}
        except ValueError:
            messagebox.showerror("エラー", "整数を入力してください。")
            return

        result.update({"folder": folder_var.get(), **numbers})

        # 保存
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showwarning("警告", f"設定の保存に失敗しました: {e}")

        root.destroy()

    def cancel():
        root.destroy()

    # --- GUI構築 ---
    root = tk.Tk()
    root.title("フォルダと整数入力")
    root.resizable(False, False)

    tk.Label(root, text="フォルダ:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    folder_var = tk.StringVar(value=defaults["folder"])
    tk.Entry(root, textvariable=folder_var, width=40).grid(row=0, column=1, padx=5)
    tk.Button(root, text="参照", command=select_folder).grid(row=0, column=2, padx=5)

    entries = {}
    for i, name in enumerate(["top", "bottom", "left", "right"], start=1):
        tk.Label(root, text=f"{name}:").grid(row=i, column=0, sticky="w", padx=5)
        var = tk.StringVar(value=str(defaults[name]))
        tk.Entry(root, textvariable=var, width=10).grid(row=i, column=1, sticky="w", padx=5, pady=2)
        entries[name] = var

    btn_frame = tk.Frame(root)
    btn_frame.grid(row=5, column=0, columnspan=3, pady=10)
    tk.Button(btn_frame, text="OK", width=10, command=ok).pack(side="left", padx=5)
    tk.Button(btn_frame, text="キャンセル", width=10, command=cancel).pack(side="left", padx=5)

    root.mainloop()
    return result if result else None


if __name__ == "__main__":
    res = show_folder_and_numbers_dialog()
    if res:
        print("結果:", res)
    else:
        print("キャンセルされました")

    crop_images_in_folder(res['folder'],
                            top_percentage=res['top'],
                            bottom_percentage=res['bottom'],
                            left_percentage=res['left'],
                            right_percentage=res['right'],
                            output_folder="cropped_images")

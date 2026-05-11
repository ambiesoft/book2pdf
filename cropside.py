import tkinter as tk
import json
from tkinter import filedialog, messagebox
import cv2  # pip install opencv-python
import os
import numpy as np
from PIL import Image, ImageTk


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

def cv_imread_unicode(path):
    try:
        data = np.fromfile(path, dtype=np.uint8)
        if data.size == 0:
            return None
        img = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
        return img
    except Exception:
        return None

def cv_imwrite_unicode(path, image):
    try:
        ext = os.path.splitext(path)[1]
        if ext == '':
            ext = '.png'
        result, buf = cv2.imencode(ext, image)
        if not result:
            return False
        # write bytes to file (handles unicode paths on Windows)
        with open(path, 'wb') as f:
            f.write(buf.tobytes())
        return True
    except Exception:
        return False

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
        # OpenCV on Windows may fail to open paths with non-ASCII characters.
        # Use numpy.fromfile + cv2.imdecode as a workaround.

        image = cv_imread_unicode(image_path)

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

        # 保存（Unicodeパス対応）
        saved = cv_imwrite_unicode(output_path, cropped_image)
        if saved:
            print(f"保存完了: {output_path}")
        else:
            print(f"保存に失敗しました: {output_path}")

def select_crop_from_image(folder_path=None):
    """画像を選択し、矩形を描いてクロップ領域を決定するダイアログ。
    戻り値: (top_percentage, bottom_percentage, left_percentage, right_percentage) または None
    """

    
    # 画像ファイル選択
    initialdir = folder_path if folder_path and os.path.isdir(folder_path) else None
    file_path = filedialog.askopenfilename(
        title="画像を選択",
        filetypes=[("画像ファイル", "*.jpg *.jpeg *.png *.bmp *.tiff")],
        initialdir=initialdir
    )
    if not file_path:
        return None

    # 画像読み込み
    image = cv_imread_unicode(file_path)
    if image is None:
        messagebox.showerror("エラー", "画像の読み込みに失敗しました。")
        return None

    height, width = image.shape[:2]

    # 画像をリサイズしてウィンドウに収める
    max_size = 800
    scale = min(max_size / width, max_size / height, 1.0)
    new_width = int(width * scale)
    new_height = int(height * scale)

    # Tkinterウィンドウ作成
    crop_window = tk.Toplevel()
    crop_window.title("画像からクロップ領域を選択")
    crop_window.resizable(False, False)

    # Canvas作成
    canvas = tk.Canvas(crop_window, width=new_width, height=new_height)
    canvas.pack()

    # PIL Imageに変換してリサイズ表示
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
    tk_image = ImageTk.PhotoImage(pil_image)
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)

    # 矩形描画用変数
    rect = None
    start_x = start_y = 0

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        if rect:
            canvas.delete(rect)
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

    def on_mouse_drag(event):
        nonlocal rect
        if rect:
            x = max(0, min(new_width, event.x))
            y = max(0, min(new_height, event.y))
            canvas.coords(rect, start_x, start_y, x, y)

    def on_mouse_up(event):
        nonlocal rect
        if rect:
            x = max(0, min(new_width, event.x))
            y = max(0, min(new_height, event.y))
            canvas.coords(rect, start_x, start_y, x, y)

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    result = {}

    def ok():
        if rect:
            coords = canvas.coords(rect)
            left = min(coords[0], coords[2]) / scale
            right = max(coords[0], coords[2]) / scale
            top = min(coords[1], coords[3]) / scale
            bottom = max(coords[1], coords[3]) / scale

            # パーセント計算
            left_percentage = (left / width) * 100
            right_percentage = ((width - right) / width) * 100
            top_percentage = (top / height) * 100
            bottom_percentage = ((height - bottom) / height) * 100

            result.update({
                'top': top_percentage,
                'bottom': bottom_percentage,
                'left': left_percentage,
                'right': right_percentage
            })
        crop_window.destroy()

    def cancel():
        crop_window.destroy()

    btn_frame = tk.Frame(crop_window)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="OK", width=10, command=ok).pack(side="left", padx=5)
    tk.Button(btn_frame, text="キャンセル", width=10, command=cancel).pack(side="left", padx=5)

    crop_window.wait_window()
    return result if result else None


def show_folder_and_numbers_dialog():
    # --- 保存ファイルのパス ---
    save_path = os.path.join(os.path.dirname(__file__), "cropside.json")

    # --- 前回の値を読み込み ---
    defaults = {"folder": "", "top": 0.0, "bottom": 0.0, "left": 0.0,
                "right": 0.0, "output_folder": "cropped_images"}
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
        folder = filedialog.askdirectory(
            initialdir=defaults["folder"] or os.getcwd())
        if folder:
            folder_var.set(folder)

    # --- 出力フォルダ選択 ---
    def select_output_folder():
        out = filedialog.askdirectory(
            initialdir=defaults.get("output_folder") or os.getcwd())
        if out:
            output_var.set(out)

    # --- OKボタン処理 ---
    def ok():
        try:
            numbers = {k: float(v.get()) for k, v in entries.items()}
        except ValueError:
            messagebox.showerror("エラー", "数値を入力してください。")
            return

        # 保存する値に output_folder を含める
        result.update({"folder": folder_var.get(),
                      "output_folder": output_var.get(), **numbers})

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

    tk.Label(root, text="フォルダ:").grid(
        row=0, column=0, sticky="w", padx=5, pady=5)
    folder_var = tk.StringVar(value=defaults["folder"])
    tk.Entry(root, textvariable=folder_var, width=40).grid(
        row=0, column=1, padx=5)
    tk.Button(root, text="参照", command=select_folder).grid(
        row=0, column=2, padx=5)

    # 出力フォルダ
    tk.Label(root, text="出力フォルダ:").grid(
        row=1, column=0, sticky="w", padx=5, pady=5)
    output_var = tk.StringVar(value=defaults.get("output_folder", ""))
    tk.Entry(root, textvariable=output_var, width=40).grid(
        row=1, column=1, padx=5)
    tk.Button(root, text="参照", command=select_output_folder).grid(
        row=1, column=2, padx=5)

    entries = {}
    for i, name in enumerate(["top", "bottom", "left", "right"], start=2):
        tk.Label(root, text=f"{name}:").grid(
            row=i, column=0, sticky="w", padx=5)
        var = tk.StringVar(value=str(defaults[name]))
        tk.Entry(root, textvariable=var, width=10).grid(
            row=i, column=1, sticky="w", padx=5, pady=2)
        entries[name] = var

    # 画像から選択ボタン
    def select_from_image():
        crop_values = select_crop_from_image(folder_var.get())
        if crop_values:
            for name, value in crop_values.items():
                entries[name].set(f"{value:.2f}")

    tk.Button(root, text="画像から選択", command=select_from_image).grid(
        row=2, column=2, rowspan=4, padx=5, pady=5)

    btn_frame = tk.Frame(root)
    btn_frame.grid(row=6, column=0, columnspan=3, pady=10)
    tk.Button(btn_frame, text="OK", width=10,
              command=ok).pack(side="left", padx=5)
    tk.Button(btn_frame, text="キャンセル", width=10,
              command=cancel).pack(side="left", padx=5)

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
                          output_folder=res.get('output_folder', "cropped_images"))

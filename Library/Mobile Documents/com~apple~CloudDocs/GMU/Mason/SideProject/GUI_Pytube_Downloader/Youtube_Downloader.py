import threading
import tkinter as tk
from tkinter import messagebox
import os
import subprocess

# 使用 pytubefix 取代 pytube
from pytubefix import YouTube

def download_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("錯誤", "請輸入影片連結！")
        return

    # 取得使用者選擇的下載格式：mp4 或 mp3
    selected_format = format_var.get()

    def run_download():
        try:
            yt = YouTube(url)
            video_title = yt.title
        except Exception as e:
            messagebox.showerror("錯誤", f"無法解析影片連結：{e}")
            return

        try:
            if selected_format == "mp4":
                # 檢查是否勾選高畫質選項
                if high_quality_var.get():
                    # 高畫質：依解析度由高到低排序後取第一個
                    stream = yt.streams.filter(progressive=True, file_extension='mp4')\
                                       .order_by('resolution')\
                                       .desc().first()
                else:
                    # 普通畫質：依解析度由低到高排序後取第一個
                    stream = yt.streams.filter(progressive=True, file_extension='mp4')\
                                       .order_by('resolution').first()
                if stream is None:
                    messagebox.showerror("錯誤", "找不到符合條件的影片串流！")
                    return
                stream.download()  # 下載至執行程式的工作目錄

            elif selected_format == "mp3":
                # 選擇僅音訊的串流
                stream = yt.streams.filter(only_audio=True)\
                                   .order_by('abr')\
                                   .desc().first()
                if stream is None:
                    messagebox.showerror("錯誤", "找不到符合條件的音訊串流！")
                    return
                # 下載音訊檔案
                temp_file = stream.download()
                # 轉換副檔名至 mp3
                base, _ = os.path.splitext(temp_file)
                mp3_file = base + ".mp3"
                try:
                    subprocess.run(
                        ["ffmpeg", "-i", temp_file, mp3_file, "-y"],
                        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    # 轉換成功後刪除原始檔案
                    os.remove(temp_file)
                except subprocess.CalledProcessError as conv_err:
                    messagebox.showerror("錯誤", f"轉換至 mp3 失敗：{conv_err}")
                    return
            else:
                messagebox.showerror("錯誤", "未選擇下載格式！")
                return

            # 根據下載格式與高畫質選項建立下載歷史的顯示字串
            if selected_format == "mp4":
                if high_quality_var.get():
                    info_text = f"MP4 High Resolution Downloaded: {video_title}"
                else:
                    info_text = f"MP4 Downloaded: {video_title}"
            elif selected_format == "mp3":
                info_text = f"MP3 Downloaded: {video_title}"
            else:
                info_text = video_title

            # 在 GUI 主執行緒中更新下載歷史
            def update_history():
                download_history_listbox.insert(tk.END, info_text)
            root.after(0, update_history)

            messagebox.showinfo("完成", f"{video_title} 下載完成！")
        except Exception as e:
            messagebox.showerror("錯誤", f"下載失敗：{e}")

    # 使用執行緒進行下載，避免 GUI 畫面凍結
    t = threading.Thread(target=run_download, daemon=True)
    t.start()

# 建立主視窗
root = tk.Tk()
root.title("YouTube 影片下載器")
root.geometry("600x450")

# 影片連結輸入區
url_label = tk.Label(root, text="請輸入 YouTube 影片連結：", font=("Arial", 12))
url_label.pack(pady=10)

url_entry = tk.Entry(root, width=60, font=("Arial", 10))
url_entry.pack(pady=5)

# 下載格式選擇：MP4 (影片) 與 MP3 (音訊)
format_var = tk.StringVar(value="mp4")
format_frame = tk.Frame(root)
format_frame.pack(pady=10)

format_label = tk.Label(format_frame, text="選擇下載格式：", font=("Arial", 12))
format_label.pack(side=tk.LEFT)

mp4_radio = tk.Radiobutton(format_frame, text="MP4 (影片)", variable=format_var, value="mp4", font=("Arial", 12))
mp4_radio.pack(side=tk.LEFT, padx=5)

mp3_radio = tk.Radiobutton(format_frame, text="MP3 (音訊)", variable=format_var, value="mp3", font=("Arial", 12))
mp3_radio.pack(side=tk.LEFT, padx=5)

# 高畫質下載選項（僅適用於 MP4）
high_quality_var = tk.BooleanVar(value=True)
quality_check = tk.Checkbutton(root, text="高畫質下載（僅限 MP4）", variable=high_quality_var, font=("Arial", 12))
quality_check.pack(pady=5)

# 下載按鈕
download_button = tk.Button(root, text="下載影片", font=("Arial", 12), command=download_video)
download_button.pack(pady=10)

# 下載歷史列表：顯示下載完成的影片與格式資訊
history_label = tk.Label(root, text="下載歷史：", font=("Arial", 12))
history_label.pack(pady=5)

download_history_listbox = tk.Listbox(root, width=80, font=("Arial", 10))
download_history_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

# 啟動 GUI 主循環
root.mainloop()
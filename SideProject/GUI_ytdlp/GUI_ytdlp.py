import threading
import tkinter as tk
from tkinter import messagebox
import os
from yt_dlp import YoutubeDL
from urllib.parse import urlparse


def is_youtube_url(url):
    return 'youtube.com' in url or 'youtu.be' in url

def download_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("錯誤", "請輸入影片連結！")
        return

    selected_format = format_var.get()
    high_quality = high_quality_var.get()


    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip().replace('%', '')
            try:
                progress = float(percent)
            except ValueError:
                pass

    def run_download():
        try:
            ydl_opts = {
                'outtmpl': '%(title)s.%(ext)s',
                'quiet': True,
                'noplaylist': True,
                'progress_hooks': [progress_hook],
            }

            if selected_format == "mp4":
                if is_youtube_url(url) and high_quality:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                else:
                    ydl_opts['format'] = 'worst'
            elif selected_format == "mp3":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                })
            else:
                messagebox.showerror("錯誤", "未知的下載格式！")
                return

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', '未命名影片')

            # 顯示紀錄文字
            if selected_format == "mp4":
                if is_youtube_url(url) and high_quality:
                    status = f"MP4 High Resolution Downloaded: {video_title}"
                else:
                    status = f"MP4 Downloaded: {video_title}"
            else:
                status = f"MP3 Downloaded: {video_title}"

            def update_history():
                download_history_listbox.insert(tk.END, status)
            root.after(0, update_history)

            messagebox.showinfo("完成", f"{video_title} 下載完成！")

        except Exception as e:
            messagebox.showerror("錯誤", f"下載失敗：{e}")

    threading.Thread(target=run_download, daemon=True).start()

# 自動切換高畫質選項（只對 YouTube 有效）
def on_url_change(*args):
    url = url_var.get()
    if is_youtube_url(url):
        quality_check.config(state=tk.NORMAL)
    else:
        high_quality_var.set(False)
        quality_check.config(state=tk.DISABLED)

# GUI 初始化
root = tk.Tk()
root.title("全平台影片下載器（YT / FB / IG / X / TikTok）")
root.geometry("600x500")


# 網址輸入欄
url_label = tk.Label(root, text="請貼上影片網址：", font=("Arial", 12))
url_label.pack(pady=10)

url_var = tk.StringVar()
url_var.trace_add("write", lambda *args: on_url_change())

url_entry = tk.Entry(root, textvariable=url_var, width=60, font=("Arial", 10))
url_entry.pack(pady=5)
url_entry.bind("<KeyRelease>", lambda event: on_url_change())

# 格式選擇
format_var = tk.StringVar(value="mp4")
format_frame = tk.Frame(root)
format_frame.pack(pady=10)

tk.Label(format_frame, text="選擇下載格式：", font=("Arial", 12)).pack(side=tk.LEFT)
tk.Radiobutton(format_frame, text="MP4 (影片)", variable=format_var, value="mp4", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
tk.Radiobutton(format_frame, text="MP3 (音訊)", variable=format_var, value="mp3", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

# 高畫質選項（僅適用於 YouTube）
high_quality_var = tk.BooleanVar(value=True)
quality_check = tk.Checkbutton(root, text="高畫質下載（僅限 YouTube）", variable=high_quality_var, font=("Arial", 12))
quality_check.pack(pady=5)


# 下載按鈕
tk.Button(root, text="下載影片", font=("Arial", 12), command=download_video).pack(pady=10)

# 下載歷史
tk.Label(root, text="下載歷史：", font=("Arial", 12)).pack(pady=5)
download_history_listbox = tk.Listbox(root, width=80, font=("Arial", 10))
download_history_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

# 啟動主程式
root.mainloop()
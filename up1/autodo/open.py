import datetime
import psutil
import tkinter as tk
import os
import requests
import webbrowser
from tkinter import messagebox

def load_data():
    try:
        with open("data.txt", "r", encoding="utf-8") as file:
            for line in file:
                name,file_path, time_str = line.strip().split(" - ")
                file_paths.append((name,file_path, time_str))
    except FileNotFoundError:
        pass

def check_and_open_files():
    now = datetime.datetime.now().strftime("%I:%M %p")  # Lấy thời gian hiện tại (ví dụ: 01:30 PM)
    for name,file_path, time_str in file_paths:
        if is_time_to_open(now, time_str) and not is_file_open(file_path):
            show_open_file_notification(name,file_path)


def is_time_to_open(now, time_str):
    now_hour, now_minute, now_ampm = parse_time(now)
    time_hour, time_minute, time_ampm = parse_time(time_str)

    if now_ampm == time_ampm:
        if now_hour == time_hour:
            if now_minute >= time_minute:
                return True
        elif now_hour > time_hour:
            return True

    return False


def parse_time(time_str):
    time_parts = time_str.split(" ")
    hour, minute = map(int, time_parts[0].split(":"))
    am_pm = time_parts[1].upper()
    return hour, minute, am_pm


def is_file_open(file_path):
    for proc in psutil.process_iter(['pid', 'name', 'cwd']):
        try:
            if file_path == proc.info['cwd']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def show_open_file_notification(name,path):
    message = f"Bạn có muốn mở {name}?\n\n =====>>>{path}"
    if tk.messagebox.askyesno("Open Path", message):
        open_path(path)


def open_path(path):
    try:
        if os.path.exists(path):
            os.startfile(path)  # Mở tệp bằng ứng dụng mặc định của hệ điều hành
            print(f"Opening {path}")
        else:
            try:
                response = requests.get(path)  # Thử gửi yêu cầu HTTP để kiểm tra xem có phải là liên kết web
                if response.status_code == 200:
                    webbrowser.open(path)  # Mở liên kết web trong trình duyệt mặc định
                    print(f"Opening web link: {path}")
                else:
                    print("Invalid path or web link.")
            except requests.RequestException:
                print("Invalid path or web link.")
    except Exception as e:
        print(f"Error opening path: {e}")

file_paths = []
load_data()
check_and_open_files()
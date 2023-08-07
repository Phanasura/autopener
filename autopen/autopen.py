import tkinter as tk
from tkinter import filedialog
import datetime
import time
import threading
import os
import psutil


class AutoOpenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto Open Application")
        self.iconbitmap("autopen.ico")
        self.file_paths = []

        self.create_widgets()

    def create_widgets(self):
        # Labels and Entries for file path
        tk.Label(self, text="File Path:").grid(row=0, column=0, sticky="w")
        self.file_path_var = tk.StringVar()
        self.file_path_entry = tk.Entry(self, width=50, textvariable=self.file_path_var, state="readonly")
        self.file_path_entry.grid(row=0, column=1, columnspan=3)
        tk.Button(self, text="Up", command=self.browse_file).grid(row=0, column=4, padx=10)

        # Labels and Entries for hour, minute, and AM/PM
        tk.Label(self, text="Hour:").grid(row=1, column=0, sticky="w")
        self.hour_var = tk.IntVar()
        self.hour_entry = tk.Entry(self, width=5, textvariable=self.hour_var)
        self.hour_entry.grid(row=1, column=1, sticky="w")
        tk.Label(self, text="Minute:").grid(row=1, column=2, padx=10, sticky="w")
        self.minute_var = tk.IntVar()
        self.minute_entry = tk.Entry(self, width=5, textvariable=self.minute_var)
        self.minute_entry.grid(row=1, column=3, sticky="w")
        tk.Label(self, text="AM/PM:").grid(row=1, column=4, padx=10, sticky="w")
        self.am_pm_var = tk.StringVar(value="AM")
        self.am_pm_entry = tk.Entry(self, width=5, textvariable=self.am_pm_var)
        self.am_pm_entry.grid(row=1, column=5, sticky="w")

        # Button to add file and time to listbox
        tk.Button(self, text="Add", command=self.add_to_listbox).grid(row=1, column=6, padx=10)

        # Listbox to display added files and times
        self.listbox = tk.Listbox(self, width=60, height=10)
        self.listbox.grid(row=2, column=0, columnspan=7, padx=10, pady=10)

        # Button to delete selected file and time from listbox
        tk.Button(self, text="Delete", command=self.delete_file).grid(row=3, column=0, pady=5)

        # Button to refresh the application
        tk.Button(self, text="Refresh", command=self.refresh_app).grid(row=3, column=6, pady=5)

        # Load saved data from file
        self.load_data()

        # Start a thread to check and open files on startup
        threading.Thread(target=self.check_and_open_files).start()

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path_var.set(file_path)

    def add_to_listbox(self):
        file_path = self.file_path_var.get()
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        am_pm = self.am_pm_var.get()

        if file_path and hour != "" and minute != "":
            time_str = f"{hour:02d}:{minute:02d} {am_pm.upper()}"
            self.listbox.insert(tk.END, f"{file_path} - {time_str}")
            self.file_paths.append((file_path, time_str))
            self.file_path_var.set('')
            self.hour_var.set(0)
            self.minute_var.set(0)
            self.am_pm_var.set("AM")
            self.save_data()

    def delete_file(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            self.listbox.delete(selected_index)
            del self.file_paths[selected_index[0]]
            self.save_data()

    def refresh_app(self):
        self.file_path_var.set('')
        self.hour_var.set(0)
        self.minute_var.set(0)
        self.am_pm_var.set("AM")

    def save_data(self):
        with open("data.txt", "w") as file:
            for file_path, time_str in self.file_paths:
                file.write(f"{file_path} - {time_str}\n")

    def load_data(self):
        try:
            with open("data.txt", "r") as file:
                for line in file:
                    file_path, time_str = line.strip().split(" - ")
                    self.file_paths.append((file_path, time_str))
                    self.listbox.insert(tk.END, f"{file_path} - {time_str}")
        except FileNotFoundError:
            pass

    def check_and_open_files(self):
        while True:
            now = datetime.datetime.now().strftime("%I:%M %p")  # Lấy thời gian hiện tại (ví dụ: 01:30 PM)

            for file_path, time_str in self.file_paths:
                if self.is_time_to_open(now, time_str) and not self.is_file_open(file_path):
                    self.show_open_file_notification(file_path)
            time.sleep(4500)

    def is_time_to_open(self, now, time_str):
        now_hour, now_minute, now_ampm = self.parse_time(now)
        time_hour, time_minute, time_ampm = self.parse_time(time_str)

        if now_ampm == time_ampm:
            if now_hour == time_hour:
                if now_minute >= time_minute:
                    return True
            elif now_hour > time_hour:
                return True

        return False

    def parse_time(self, time_str):
        time_parts = time_str.split(" ")
        hour, minute = map(int, time_parts[0].split(":"))
        am_pm = time_parts[1].upper()
        return hour, minute, am_pm

    def is_file_open(self, file_path):
        for proc in psutil.process_iter(['pid', 'name', 'cwd']):
            try:
                if file_path == proc.info['cwd']:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def show_open_file_notification(self, file_path):
        message = f"Do you want to open the following file?\n\n- {file_path}"
        if tk.messagebox.askyesno("Open File", message):
            self.open_file(file_path)

    def open_file(self, file_path):
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)  # Mở file bằng ứng dụng mặc định của hệ điều hành
                print(f"Opening {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error opening file: {e}")

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = AutoOpenApp()
    app.run()

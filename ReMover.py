import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from configparser import ConfigParser

def run_command(command):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    result = subprocess.run(command, shell=True, startupinfo=startupinfo)
    if result.returncode != 0:
        print("!! [ERROR] Failed to execute: {}".format(command))
        return False
    return True

def browse_source():
    source_path.set(filedialog.askdirectory())

def browse_dest():
    dest_path.set(filedialog.askdirectory())

def save_settings():
    config = ConfigParser()
    config['Paths'] = {
        'source_path_rem': source_path_rem.get(),
        'dest_path_rem': dest_path_rem.get(),
        'source_path_mov': source_path_mov.get(),
        'dest_path_mov': dest_path_mov.get()
    }
    config_path = os.path.join(os.path.dirname(__file__), 'settings.ini')
    with open(config_path, 'w') as configfile:
        config.write(configfile)
        print("Settings saved to settings.ini")

def load_settings():
    config = ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'settings.ini')
    config.read(config_path)
    if 'Paths' in config:
        source_path_rem.set(config['Paths'].get('source_path_rem', ''))
        dest_path_rem.set(config['Paths'].get('dest_path_rem', ''))
        source_path_mov.set(config['Paths'].get('source_path_mov', ''))
        dest_path_mov.set(config['Paths'].get('dest_path_mov', ''))

def execute_rem():
    archive_name = entry_archive_name.get()
    if not archive_name:
        messagebox.showwarning("Внимание", "Имя архива не заполнено!")
        return

    archive_name += ".7z"
    zip_path = r"C:\Program Files\7-Zip\7z.exe"

    commands = [
        f'"{zip_path}" a "{archive_name}" "{source_path_rem.get()}\\*"',
        f'del /q "{source_path_rem.get()}\\*"',
        f'move "{archive_name}" "{dest_path_rem.get()}"'
    ]

    results = [run_command(cmd) for cmd in commands]

    if all(results):
        messagebox.showinfo("Инфо", "Все ОК!")
        app.after(5000, app.quit)
    else:
        print("An error occurred during the task.")

def execute_mov():
    source = source_path_mov.get()
    dest = dest_path_mov.get()

    if not os.path.exists(source):
        messagebox.showwarning("Warning", "Source path does not exist!")
        return

    if not os.path.exists(dest):
        messagebox.showwarning("Warning", "Destination path does not exist!")
        return

    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(dest, item)
        shutil.move(s, d)

    messagebox.showinfo("Info", "Files moved successfully! The program will close in 5 seconds.")
    app.after(5000, app.quit)

def open_settings():
    settings_window = tk.Toplevel(app)
    settings_window.title("Настройки")

    tk.Label(settings_window, text="Remove:").grid(row=0, column=1)

    tk.Label(settings_window, text="Откуда:").grid(row=1, column=0)
    entry_source_path_rem = tk.Entry(settings_window, textvariable=source_path_rem)
    entry_source_path_rem.grid(row=1, column=1)
    tk.Button(settings_window, text="Обзор", command=lambda: source_path_rem.set(filedialog.askdirectory())).grid(row=1, column=2)

    tk.Label(settings_window, text="Куда:").grid(row=2, column=0)
    entry_dest_path_rem = tk.Entry(settings_window, textvariable=dest_path_rem)
    entry_dest_path_rem.grid(row=2, column=1)
    tk.Button(settings_window, text="Обзор", command=lambda: dest_path_rem.set(filedialog.askdirectory())).grid(row=2, column=2)

    tk.Label(settings_window, text="Move:").grid(row=3, column=1)

    tk.Label(settings_window, text="Откуда:").grid(row=4, column=0)
    entry_source_path_mov = tk.Entry(settings_window, textvariable=source_path_mov)
    entry_source_path_mov.grid(row=4, column=1)
    tk.Button(settings_window, text="Обзор", command=lambda: source_path_mov.set(filedialog.askdirectory())).grid(row=4, column=2)

    tk.Label(settings_window, text="Куда:").grid(row=5, column=0)
    entry_dest_path_mov = tk.Entry(settings_window, textvariable=dest_path_mov)
    entry_dest_path_mov.grid(row=5, column=1)
    tk.Button(settings_window, text="Обзор", command=lambda: dest_path_mov.set(filedialog.askdirectory())).grid(row=5, column=2)

    tk.Button(settings_window, text="Сохранить", command=save_settings).grid(row=6, column=1)

app = tk.Tk()
app.title("ReMover")

source_path_rem = tk.StringVar()
dest_path_rem = tk.StringVar()
source_path_mov = tk.StringVar()
dest_path_mov = tk.StringVar()

menu = tk.Menu(app)
app.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Файл", menu=file_menu)
file_menu.add_command(label="Настройки", command=open_settings)

tk.Label(app, text="Имя архива:").grid(row=0, column=0)
entry_archive_name = tk.Entry(app)
entry_archive_name.grid(row=0, column=1)

tk.Button(app, text="Remove", command=execute_rem, width=20, height=2).grid(row=1, column=0)
tk.Button(app, text="Move", command=execute_mov, width=20, height=2).grid(row=1, column=1)

# Автоматическая загрузка настроек при запуске
load_settings()

app.mainloop()

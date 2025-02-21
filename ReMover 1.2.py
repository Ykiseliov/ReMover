#v.1.2c

import os
import shutil
import subprocess
from tkinter import ttk, filedialog, messagebox, Tk, Label, Entry, StringVar, BooleanVar, Menu, Checkbutton, Toplevel
from configparser import ConfigParser
from time import strftime
from typing import List

class ReMoverApp:
    def __init__(self):
        self.app = Tk()
        self.app.title("ReMover")
        
        # Переменные
        self.source_path_rem = StringVar()
        self.dest_path_rem = StringVar()
        self.source_path_mov = StringVar()
        self.dest_path_mov = StringVar()
        self.auto_close = BooleanVar()
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        # Меню
        menu = Menu(self.app)
        self.app.config(menu=menu)
        file_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Настройки", command=self.open_settings)
        
        # Основной интерфейс
        Label(self.app, text="Количество:").grid(row=0, column=1)
        self.file_count_label = Label(self.app, text=" 0 ", font=("Arial", 8))
        self.file_count_label.grid(row=1, column=1, sticky="w")
        
        self.entry_archive_name = Entry(self.app)
        self.entry_archive_name.insert(0, strftime("%d-%m-%y"))
        self.entry_archive_name.grid(row=1, column=0)
        
        # Стиль кнопок
        style = ttk.Style()
        style.configure('Rounded.TButton', borderwidth=0, relief="flat", padding=10, 
                       background="#ccc", foreground="black")
        style.map('Rounded.TButton', background=[('active', '#aaa')])
        
        ttk.Button(self.app, text="Archive", command=self.execute_rem, 
                  style='Rounded.TButton').grid(row=2, column=0)
        ttk.Button(self.app, text="Move", command=self.execute_mov, 
                  style='Rounded.TButton').grid(row=2, column=1)

    def run_command(self, command: str) -> bool:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            result = subprocess.run(command, shell=True, startupinfo=startupinfo, 
                                  check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"!! [ERROR] Failed to execute: {command}\n{e.stderr.decode()}")
            return False

    def save_settings(self):
        config = ConfigParser()
        config['Paths'] = {
            'source_path_rem': self.source_path_rem.get(),
            'dest_path_rem': self.dest_path_rem.get(),
            'source_path_mov': self.source_path_mov.get(),
            'dest_path_mov': self.dest_path_mov.get()
        }
        config['Settings'] = {'auto_close': str(self.auto_close.get())}
        
        config_path = os.path.join(os.path.dirname(__file__), 'settings.ini')
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        print("Settings saved to settings.ini")
        self.update_file_count()

    def load_settings(self):
        config = ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'settings.ini')
        if config.read(config_path) and 'Paths' in config:
            self.source_path_rem.set(config['Paths'].get('source_path_rem', ''))
            self.dest_path_rem.set(config['Paths'].get('dest_path_rem', ''))
            self.source_path_mov.set(config['Paths'].get('source_path_mov', ''))
            self.dest_path_mov.set(config['Paths'].get('dest_path_mov', ''))
            self.auto_close.set(config['Settings'].getboolean('auto_close', False))
        self.update_file_count()

    def execute_rem(self):
        archive_name = self.entry_archive_name.get()
        if not archive_name:
            messagebox.showwarning("Внимание", "Имя архива не заполнено!")
            return

        month_year = '-'.join(archive_name.split('-')[1:])
        month_year_dir = os.path.join(self.dest_path_rem.get(), month_year)
        os.makedirs(month_year_dir, exist_ok=True)

        archive_full_path = os.path.join(month_year_dir, f"{archive_name}.7z")
        if os.path.exists(archive_full_path):
            messagebox.showwarning("Внимание", "Архив с таким именем уже существует!")
            return

        zip_path = r"C:\Program Files\7-Zip\7z.exe"
        commands = [
            f'"{zip_path}" a "{archive_name}.7z" "{self.source_path_rem.get()}\\*"',
            f'del /q "{self.source_path_rem.get()}\\*"',
            f'move "{archive_name}.7z" "{month_year_dir}"'
        ]

        if all(self.run_command(cmd) for cmd in commands):
            messagebox.showinfo("Инфо", "Все ОК!")
            if self.auto_close.get():
                self.app.after(5000, self.app.quit)

    def execute_mov(self):
        source, dest = self.source_path_mov.get(), self.dest_path_mov.get()
        
        if not os.path.exists(source) or not os.path.exists(dest):
            messagebox.showwarning("Warning", "Source or destination path does not exist!")
            return

        try:
            for item in os.listdir(source):
                shutil.move(os.path.join(source, item), os.path.join(dest, item))
            messagebox.showinfo("Info", "Files moved successfully!")
            if self.auto_close.get():
                self.app.after(5000, self.app.quit)
            self.update_file_count()
        except Exception as e:
            print(f"Error moving files: {e}")

    def count_files(self) -> int:
        dest = self.dest_path_mov.get()
        return len([f for f in os.listdir(dest) if os.path.isfile(os.path.join(dest, f))]) if os.path.exists(dest) else 0

    def update_file_count(self):
        self.file_count_label.config(text=f"                {self.count_files()} шт.")

    def open_settings(self):
        settings = Toplevel(self.app)
        settings.title("Настройки")
        
        # Структура настроек
        config = [
            ("Remove:", 0, 1),
            ("Откуда:", 1, 0, self.source_path_rem),
            ("Куда:", 2, 0, self.dest_path_rem),
            ("Move:", 3, 1),
            ("Откуда:", 4, 0, self.source_path_mov),
            ("Куда:", 5, 0, self.dest_path_mov)
        ]
        
        for text, row, col, *var in config:
            Label(settings, text=text).grid(row=row, column=col)
            if var:
                Entry(settings, textvariable=var[0]).grid(row=row, column=1)
                ttk.Button(settings, text="Обзор", 
                          command=lambda v=var[0]: v.set(filedialog.askdirectory())).grid(row=row, column=2)
        
        Checkbutton(settings, text="Автозакрытие через 5 сек", 
                   variable=self.auto_close).grid(row=6, column=1)
        ttk.Button(settings, text="Сохранить", 
                  command=self.save_settings).grid(row=7, column=1)
        
        settings.transient(self.app)  # Привязка к главному окну
        settings.grab_set()  # Модальное окно
        settings.focus_set()  # Фокус на окне настроек

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    ReMoverApp().run()

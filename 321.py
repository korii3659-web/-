import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# --- Настройки ---
DATA_FILE = "trainings.json"
DATE_FORMAT = "%Y-%m-%d"

class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Планировщик тренировок")
        self.root.geometry("750x550")

        # Загрузка данных из файла при запуске
        self.trainings = self.load_data()

        # --- Создание виджетов интерфейса ---
        # Поля ввода
        ttk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.date_entry = ttk.Entry(root, width=15)
        self.date_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(root, text="Тип тренировки:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(root, textvariable=self.type_var,
                                          values=["Кардио", "Силовая", "Растяжка", "Йога"],
                                          state="readonly")
        self.type_combobox.grid(row=1, column=1, padx=10, pady=5)
        self.type_combobox.current(0)

        ttk.Label(root, text="Длительность (мин):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.duration_entry = ttk.Entry(root, width=15)
        self.duration_entry.grid(row=2, column=1, padx=10, pady=5)

        # Кнопка добавления
        ttk.Button(root, text="Добавить тренировку", command=self.add_training).grid(row=3, column=0, columnspan=2, pady=10)

        # Таблица для отображения данных (Treeview)
        self.columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(root, columns=self.columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)
        
        self.tree.grid(row=4, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")

        # Полоса прокрутки для таблицы
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=4, column=3, sticky="ns")

        # Блок фильтрации
        ttk.Label(root, text="Фильтр по типу:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.filter_type_var = tk.StringVar()
        self.filter_type_combobox = ttk.Combobox(root, textvariable=self.filter_type_var,
                                                 values=["Все", "Кардио", "Силовая", "Растяжка", "Йога"],
                                                 state="readonly")
        self.filter_type_combobox.grid(row=5, column=1, padx=10, pady=5)
        self.filter_type_combobox.current(0)
        
        ttk.Label(root, text="Фильтр по дате:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        self.filter_date_entry = ttk.Entry(root, width=15)
        self.filter_date_entry.grid(row=6, column=1, padx=10, pady=(5, 10))
        
        ttk.Button(root, text="Применить фильтры", command=self.apply_filters).grid(row=7, column=0, columnspan=2)
        
         # Настройка сетки для растягивания окна
         root.grid_rowconfigure(4, weight=1)
         root.grid_columnconfigure(2, weight=1)

    def load_data(self):
         """Загрузка данных из JSON файла при старте."""
         if os.path.exists(DATA_FILE):
             try:
                 with open(DATA_FILE, 'r', encoding='utf-8') as f:
                     return json.load(f)
             except Exception as e:
                 messagebox.showerror("Ошибка загрузки", f"Не удалось прочитать файл: {e}")
                 return []
         return []

    def save_data(self):
         """Сохранение текущего списка тренировок в JSON файл."""
         try:
             with open(DATA_FILE, 'w', encoding='utf-8') as f:
                 json.dump(self.trainings, f, ensure_ascii=False, indent=4)
             return True
         except Exception as e:
             messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")
             return False

    def validate_input(self):
         """Проверка формата даты и корректности длительности."""
         date_str = self.date_entry.get().strip()
         
         # Валидация даты
         try:
             datetime.strptime(date_str, DATE_FORMAT)
         except ValueError:
             messagebox.showerror("Ошибка ввода", f"Дата должна быть в формате {DATE_FORMAT} (например: 2026-05-02)")
             return False

         # Валидация длительности
         duration_str = self.duration_entry.get().strip()
         if not duration_str.isdigit() or int(duration_str) <= 0:
             messagebox.showerror("Ошибка ввода", "Длительность должна быть положительным целым числом.")
             return False

         return True

    def add_training(self):
         """Обработчик кнопки 'Добавить тренировку'."""
         if not self.validate_input():
             return

         date = self.date_entry.get()
         tr_type = self.type_var.get()
         duration = int(self.duration_entry.get())
         
         # Добавление в список и сохранение
         self.trainings.append({"date": date, "type": tr_type, "duration": duration})
         
         if self.save_data():
             # Обновление таблицы в GUI
             self.tree.insert("", "end", values=(date, tr_type, duration))
             
             # Очистка полей ввода после успешного добавления
             self.date_entry.delete(0, tk.END)
             self.duration_entry.delete(0, tk.END)
             
             messagebox.showinfo("Успех", "Тренировка добавлена!")

    def apply_filters(self):
         """Фильтрация записей в таблице по типу и/или дате."""
         filter_type = self.filter_type_var.get()
         filter_date = self.filter_date_entry.get().strip()
         
         # Очистка текущей таблицы перед фильтрацией
         for item in self.tree.get_children():
             self.tree.delete(item)
         
         for training in self.trainings:
             date_match = (not filter_date) or (training["date"] == filter_date)
             type_match = (filter_type == "Все") or (training["type"] == filter_type)
             
             if date_match and type_match:
                 self.tree.insert("", "end", values=(training["date"], training["type"], training["duration"]))

    def run(self):
         """Запуск приложения и заполнение таблицы данными из файла."""
         for training in self.trainings:
             self.tree.insert("", "end", values=(training["date"], training["type"], training["duration"]))
         
         # Привязка функции к закрытию окна (сохранение перед выходом)
         self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
         
         self.root.mainloop()

    def on_closing(self):
         """Действие при закрытии окна приложения."""
         if messagebox.askokcancel("Выход", "Сохранить изменения и выйти?"):
             self.save_data()
             self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlannerApp(root)
    app.run()

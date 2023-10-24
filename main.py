import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# класс главного окна


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()
        self.db = db
        self.view_records()

    # Xранение и инициализация объектов GUI
    def init_main(self):
        # панель иструментов (просто цветной прямоугольник)
        toolbar = tk.Frame(bg='gray', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Cоздание кнопки добавления контакта
        self.add_img = tk.PhotoImage(file='./img/add.png')
        btn_add = tk.Button(toolbar, bg='gray', bd=0,
                            image=self.add_img,
                            command=self.open_dialog)
        btn_add.pack(side=tk.LEFT)

        # Cоздание кнопки редактирования контакта
        self.edit_img = tk.PhotoImage(file='./img/update.png')
        btn_edit = tk.Button(toolbar, bg='gray', bd=0,
                             image=self.edit_img,
                             command=self.open_edit)
        btn_edit.pack(side=tk.LEFT)

        # Cоздание кнопки удаления контакта
        self.del_img = tk.PhotoImage(file='./img/delete.png')
        btn_del = tk.Button(toolbar, bg='gray', bd=0,
                            image=self.del_img,
                            command=self.delete_records)
        btn_del.pack(side=tk.LEFT)

        # Cоздание кнопки поиска контакта
        self.search_img = tk.PhotoImage(file='./img/search.png')
        btn_search = tk.Button(toolbar, bg='gray', bd=0,
                               image=self.search_img,
                               command=self.open_search)
        btn_search.pack(side=tk.LEFT)

        # Cоздание кнопки обновления таблицы
        self.refresh_img = tk.PhotoImage(file='./img/refresh.png')
        btn_refresh = tk.Button(toolbar, bg='gray', bd=0,
                                image=self.refresh_img,
                                command=self.view_records)
        btn_refresh.pack(side=tk.LEFT)

        # Cоздание таблицы
        self.tree = ttk.Treeview(root, columns=(
                                 'id', 'name', 'tel', 'email', 'salary'),
                                 height=45,
                                 show='headings')

        # Добавляем параметры столбцам
        self.tree.column('id', width=30, anchor=tk.CENTER)
        self.tree.column('name', width=175, anchor=tk.CENTER)
        self.tree.column('tel', width=100, anchor=tk.CENTER)
        self.tree.column('email', width=200, anchor=tk.CENTER)
        self.tree.column('salary', width=140, anchor=tk.CENTER)

        self.tree.heading('id', text='id')
        self.tree.heading('name', text='ФИО')
        self.tree.heading('tel', text='Телефон')
        self.tree.heading('email', text='Электронная почта')
        self.tree.heading('salary', text='Заработная плата')
        self.tree.pack(side=tk.LEFT)

        # Добавление полосы прокрутки
        scroll = tk.Scrollbar(root, command=self.tree.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)

    # Метод добавления (посредник)
    def records(self, name, tel, email, salary):
        if salary.isdigit() == False:  # Если пользователь не ввёл значение зарплаты, то оно автоматически становится 0.0
            salary = 0.0
        self.db.insert_data(name, tel, email, salary)
        self.view_records()

    # Метод редактирования
    def edit_record(self, name, tel, email, salary):
        # Создание доп. переменной для взятия всех id из выделенных столбцов
        ind = self.tree.set(self.tree.selection()[0], '#1')
        self.db.cursor.execute('''
                              UPDATE users SET name = ?, tel = ?, email = ?, salary = ?
                              WHERE id = ?
                              ''', (name, tel, email, salary, ind))
        self.db.connect.commit()
        self.view_records()

    # Метод удаления записей
    def delete_records(self):
        if self.tree.selection() == ():  # Выдаётся предупреждение, если пользователь не выделил объекты для их удаления
            messagebox.showwarning(
                'Внимание!', 'Пожалуйста, выберите пользователя для его удаления')
        else:
            # Проходим циклом по всем выделенным строкам в таблице
            for i in self.tree.selection():
                # Берём id каждой строки
                id = self.tree.set(i, '#1')
                # Удаляем по id
                self.db.cursor.execute('''
                DELETE FROM users
                WHERE id = ?
            ''', (id, ))
            self.db.connect.commit()
            self.view_records()

    # Метод поиска записей
    def search_records(self, name):
        [self.tree.delete(i) for i in self.tree.get_children()]
        self.db.cursor.execute('SELECT * FROM users WHERE name LIKE ?',
                               ('%' + name + '%', ))
        [self.tree.insert('', 'end', values=i)
         for i in self.db.cursor.fetchall()]

    # Вызор дочернего окна
    def open_dialog(self):
        Child()

    # Вызов окна редактирования
    def open_edit(self):
        if len(self.tree.selection()) > 1:
            messagebox.showerror(
                'Ошибка!', 'Нельзя редактировать сразу нескольких пользователей')  # Выдаётся ошибка, если пользователь выделил больше 1-го объекта
        elif self.tree.selection() == ():
            messagebox.showwarning(
                'Внимание!', 'Пожалуйста, выберите пользователя для его редактирования')  # Выдаётся предупреждение, если пользователь ничего не выделил
        else:
            Update()

    # Вызов окна поиска
    def open_search(self):
        Search()

    # Обновление записей
    def view_records(self):
        [self.tree.delete(i) for i in self.tree.get_children()]
        self.db.cursor.execute('SELECT * FROM users')
        [self.tree.insert('', 'end', values=i)
         for i in self.db.cursor.fetchall()]

# Класс дочернего окна


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_child()
        self.view = app

    # Хранение и инициализация объектов GUI
    def init_child(self):
        self.title('Добавление контакта')
        self.geometry('400x250')
        # Запрет на изменение размеров
        self.resizable(False, False)
        # Перехват событий приложения
        self.grab_set()
        # Захват фокуса
        self.focus_set()
        # Установка иконки для дочернего окна
        self.iconbitmap('./img/icon.ico')

        # Создание формы
        label_name = tk.Label(self, text='ФИО')
        label_tel = tk.Label(self, text='Телефон')
        label_email = tk.Label(self, text='E-mail')
        label_salary = tk.Label(self, text='Зарплата')
        label_name.place(x=50, y=50)
        label_tel.place(x=50, y=80)
        label_email.place(x=50, y=110)
        label_salary.place(x=50, y=140)

        self.entry_name = tk.Entry(self)
        self.entry_tel = tk.Entry(self)
        self.entry_email = tk.Entry(self)
        self.entry_salary = tk.Entry(self)
        self.entry_name.place(x=200, y=50)
        self.entry_tel.place(x=200, y=80)
        self.entry_email.place(x=200, y=110)
        self.entry_salary.place(x=200, y=140)

        # Добавление кнопки, выполняющую функцию добавлять контакты в бд
        self.btn_ok = tk.Button(self, text='Добавить')
        self.btn_ok.bind('<Button-1>', lambda ev: self.view.records(
            self.entry_name.get(),
            self.entry_tel.get(),
            self.entry_email.get(),
            self.entry_salary.get()))

        # Добавление кнопки, выполняющую функцию закрывать окно
        btn_cancel = tk.Button(self, text='Закрыть', command=self.destroy)

        self.btn_ok.place(x=300, y=200)
        btn_cancel.place(x=220, y=200)

# Класс окна редактирования


class Update(Child):
    def __init__(self):
        super().__init__()
        self.db = db
        self.init_edit()
        self.load_data()

    # Хранение и инициализация объектов GUI
    def init_edit(self):
        self.title('Редактирование контакта')
        # Убираем кнопку добавления
        self.btn_ok.destroy()
        # Кнопка редактирования
        self.btn_ok = tk.Button(self, text='Редактировать')
        self.btn_ok.bind('<Button-1>', lambda ev: self.view.edit_record(
            self.entry_name.get(),
            self.entry_tel.get(),
            self.entry_email.get(),
            self.entry_salary.get()))
        self.btn_ok.bind('<Button-1>', lambda ev: self.destroy(), add='+')
        self.btn_ok.place(x=300, y=200)

    # Метод автозаполнения формы старыми данными
    def load_data(self):
        self.db.cursor.execute('''SELECT * FROM users WHERE id = ?''',
                               self.view.tree.set(self.view.tree.selection()[0], '#1'))
        row = self.db.cursor.fetchone()
        self.entry_name.insert(0, row[1])
        self.entry_tel.insert(0, row[2])
        self.entry_email.insert(0, row[3])
        self.entry_salary.insert(0, row[4])

# Класс окна поиска


class Search(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_search()
        self.view = app

    # Хранение и инициализация объектов GUI
    def init_search(self):
        self.title('Найти контакт')
        self.geometry('300x100')
        # Запрет на изменение размеров
        self.resizable(False, False)
        # Перехват событий приложения
        self.grab_set()
        # Захват фокуса
        self.focus_set()
        # Установка иконки для окна поиска
        self.iconbitmap('./img/icon.ico')

        # Создание формы
        label_name = tk.Label(self, text='ФИО')
        label_name.place(x=50, y=30)

        self.entry_name = tk.Entry(self)
        self.entry_name.place(x=150, y=30)

        # Добавление кнопки, выполняющую функцию поиска контактов в бд
        self.btn_ok = tk.Button(self, text='Найти')
        self.btn_ok.bind(
            '<Button-1>', lambda ev: self.view.search_records(self.entry_name.get()))
        self.btn_ok.bind('<Button-1>', lambda ev: self.destroy(), add='+')

        # Добавление кнопки, выполняющую функцию закрывать окно
        btn_cancel = tk.Button(self, text='Закрыть', command=self.destroy)

        self.btn_ok.place(x=230, y=70)
        btn_cancel.place(x=160, y=70)

# Класс БД


class Db:
    def __init__(self):
        self.connect = sqlite3.connect('employees.db')
        self.cursor = self.connect.cursor()
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            tel TEXT,
                            email TEXT,
                            salary FLOAT
                    )''')

    # Метод добавления в БД
    def insert_data(self, name, tel, email, salary):
        self.cursor.execute('''
                            INSERT INTO users (name, tel, email, salary)
                            VALUES (?, ?, ?, ?)''', (name, tel, email, salary))

        self.connect.commit()


# Действия при запуске программы
if __name__ == '__main__':
    root = tk.Tk()
    db = Db()
    app = Main(root)
    root.title('Список сотрудников компании')
    root.geometry('665x400')
    # Запрет на изменение размеров
    root.resizable(False, False)
    # Установка иконки для приложения
    root.iconbitmap('./img/icon.ico')
    root.mainloop()

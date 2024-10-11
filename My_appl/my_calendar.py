import SQL_application as sq
import tkinter as tk
from tkinter import ttk
# from PIL import Image, ImageTk
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar

conn = sq.sqlite3.connect("Omega_apl.db")
cur = conn.cursor()

months_dict = {
    1: "январь",
    2: "февраль",
    3: "март",
    4: "апрель",
    5: "май",
    6: "июнь",
    7: "июль",
    8: "август",
    9: "сентябрь",
    10: "октябрь",
    11: "ноябрь",
    12: "декабрь"
}

request_types = [
    "подключение квартиры",
    "подключение частного дома",
    "подключение юр.Лица",
    "диагностика",
    "ремонт",
    "настройка рутера",
    "другое",
]
# Глобальные переменные для хранения выбранного года и месяца
selected_year = None
selected_month = None
day_id = None
cal = None  # Объявляем cal как глобальную переменную

def create_tables():
    # Создание таблицы для заявок
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS requests_{months_dict[selected_month]}_20{selected_year} (
            Request_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Execution_Time TEXT,
            Address TEXT,
            Phone TEXT,
            Additional_Phone TEXT,
            Request_Type TEXT,
            Additional_Info TEXT,
            Status TEXT,
            Day_ID INTEGER
        )
    ''')
    
    # Создание таблицы для дней (пример)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS days_январь_2024 (
            Day_ID INTEGER PRIMARY KEY,
            Day INTEGER
        )
    ''')
    
    conn.commit()

def update_selected_date(event):
    global selected_year, selected_month, day_id, cal
    selected_date = cal.get_date()  # Получаем дату в формате 'мм/дд/гггг'
    month, day, year = map(int, selected_date.split('/'))  # Разделяем на месяц, день и год
    selected_month, day_id, selected_year = month, day, year  # Сохраняем год, месяц и день
    print(f"Выбранный год: 20{selected_year}, месяц: {months_dict[selected_month]}, день: {day_id}")
    
    # Обновляем заявки за выбранный день
    update_requests_display()

    
    
def add_request():
    global selected_month, selected_year, day_id
    if selected_month is None or selected_year is None or day_id is None:
        messagebox.showwarning("Предупреждение", "Сначала выберите год, месяц и день.")
        return

    requests_table_name = f"requests_{months_dict[selected_month]}_20{selected_year}"

    execution_time = simpledialog.askstring("Ввод", "Введите время исполнения заявки:")
    address = simpledialog.askstring("Ввод", "Введите адрес или лицевой счет:")
    phone = simpledialog.askstring("Ввод", "Введите телефон:")
    additional_phone = simpledialog.askstring("Ввод", "Введите дополнительный телефон (если есть):")

    # Создаем окно для выбора типа заявки
    type_window = tk.Toplevel(root)
    type_window.title("Выбор типа заявки")

    # Устанавливаем размеры и положение окна
    type_window.geometry("300x200+100+100")  # Ширина x Высота + X + Y

    selected_type = tk.StringVar(root)
    selected_type.set(request_types[0])  # Устанавливаем значение по умолчанию

    type_label = tk.Label(type_window, text="Выберите тип заявки:")
    type_label.pack(pady=10)

    # Создаем Combobox для выбора типа заявки
    type_menu = ttk.Combobox(type_window, textvariable=selected_type, values=request_types)
    type_menu.pack(pady=10)

    def on_submit():
        type_window.destroy()  # Закрываем окно выбора типа заявки
        request_type = selected_type.get()
        additional_info = simpledialog.askstring("Ввод", "Введите дополнительную информацию:")
        status = str("ожидает")
        
        try:
            cur.execute(f'''INSERT INTO {requests_table_name} 
                            (Execution_Time, Address, Phone, Additional_Phone, Request_Type, Additional_Info, Status, Day_ID) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (execution_time, address, phone, additional_phone, request_type, additional_info, status, day_id))
            conn.commit()
            messagebox.showinfo("Информация", "Заявка успешно добавлена.")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить заявку: {e}")
            
    submit_button = tk.Button(type_window, text="Подтвердить", command=on_submit)
    submit_button.pack(pady=10)
    

    type_window.mainloop()  # Запускаем главный цикл окна выбора типа заявки
    


def update_requests_display():
    global selected_year, selected_month, day_id
    requests_table_name = f"requests_{months_dict[selected_month]}_20{selected_year}"
    
    try:
        cur.execute(f'SELECT * FROM {requests_table_name} WHERE Day_ID = ?', (day_id,))
        requests = cur.fetchall()
        
        # Очищаем виджет перед обновлением
        requests_display.delete(1.0, tk.END)
        
        if requests:
            for request in requests:
                request_info = f"ID: {request[0]}, Время исполнения: {request[1]}, Адрес: {request[2]}, Телефон: {request[3]}, Доп. телефон: {request[4]}, Тип заявки: {request[5]}, Доп. информация: {request[6]}, Статус: {request[7]}\n"
                requests_display.insert(tk.END, request_info)
        else:
            requests_display.insert(tk.END, "Заявок не найдено.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось получить заявки: {e}")
        create_tables()
        
def delete_request(): #удаление заявки
    if selected_month is None or selected_year is None:
        messagebox.showwarning("Предупреждение", "Сначала выберите год и месяц.")
        return

    request_id = simpledialog.askinteger("Ввод", "Введите ID заявки для удаления:")

    requests_table_name = f"requests_{months_dict[selected_month]}_20{selected_year}"

    try:
        cur.execute(f'SELECT * FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
        request = cur.fetchone()

        if request:
            cur.execute(f'DELETE FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
            conn.commit()
            messagebox.showinfo("Информация", f"Заявка с ID {request_id} успешно удалена.")
        else:
            messagebox.showinfo("Информация", f"Заявка с ID {request_id} не найдена.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить заявку: {e}")

def search_requests_by_phone(): # поиск по номеру телефона
    if selected_month is None or selected_year is None:
        messagebox.showwarning("Предупреждение", "Сначала выберите год и месяц.")
        return

    phone_number = simpledialog.askstring("Ввод", "Введите номер телефона для поиска заявок:")

    requests_table_name = f"requests_{months_dict[selected_month]}_20{selected_year}"

    try:
        cur.execute(f'''SELECT r.*, d.Day 
                        FROM {requests_table_name} r
                        JOIN days_{months_dict[selected_month]}_20{selected_year} d ON r.Day_ID = d.Day_ID
                        WHERE r.Phone = ? OR r.Additional_Phone = ?''', (phone_number, phone_number))
        requests = cur.fetchall()

        if requests:
            request_list = "\n".join([f"ID: {request[0]}, Время исполнения: {request[1]}, Адрес: {request[2]}, "
                                       f"Телефон: {request[3]}, Доп. телефон: {request[4]}, "
                                       f"Тип заявки: {request[5]}, Доп. информация: {request[6]}, "
                                       f"Статус: {request[7]}, \n День: {request[8]}" for request in requests])
            messagebox.showinfo("Заявки по номеру телефона", f"Заявки с номером телефона {phone_number}:\n{request_list}")
        else:
            messagebox.showinfo("Информация", f"Заявок с номером телефона {phone_number} не найдено.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {e}")

def search_requests_by_type():  # отчет по типу заявки за месяц
    if selected_month is None or selected_year is None:
        messagebox.showwarning("Предупреждение", "Сначала выберите год и месяц.")
        return

    # Создаем окно для выбора типа заявки
    type_window = tk.Toplevel(root)
    type_window.title("Выбор типа заявки")

    # Устанавливаем размеры и положение окна
    type_window.geometry("300x200+100+100")  # Ширина x Высота + X + Y

    selected_type = tk.StringVar(root)
    selected_type.set(request_types[0])  # Устанавливаем значение по умолчанию

    type_label = tk.Label(type_window, text="Выберите тип заявки:")
    type_label.pack(pady=10)

    # Создаем Combobox для выбора типа заявки
    type_menu = ttk.Combobox(type_window, textvariable=selected_type, values=request_types)
    type_menu.pack(pady=10)

    def on_submit():
        request_type = selected_type.get()
        requests_table_name = f"requests_{months_dict[selected_month]}_20{selected_year}"

        try:
            cur.execute(f'''SELECT r.*, d.Day 
                            FROM {requests_table_name} r
                            JOIN days_{months_dict[selected_month]}_20{selected_year} d ON r.Day_ID = d.Day_ID
                            WHERE r.Request_Type = ?''', (request_type,))
            requests = cur.fetchall()
            total_requests = len(requests)
            if requests:
                request_list = "\n".join([f"ID: {request[0]}, Время исполнения: {request[1]}, Адрес: {request[2]}, "
                                           f"Телефон: {request[3]}, Доп. телефон: {request[4]}, "
                                           f"Тип заявки: {request[5]}, Доп. информация: {request[6]}, "
                                           f"Статус: {request[7]}" for request in requests])
                messagebox.showinfo("Заявки по типу", f"Заявки с типом '{request_type}':\n{request_list}\n\nОбщее число заявок: {total_requests}")
                type_window.destroy()  # Закрываем окно выбора типа заявки
            else:
                messagebox.showinfo("Информация", f"Заявок с типом '{request_type}' не найдено.")
                type_window.destroy()  # Закрываем окно выбора типа заявки
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {e}")
            type_window.destroy()  # Закрываем окно выбора типа заявки
    submit_button = tk.Button(type_window, text="Подтвердить", command=on_submit )
    submit_button.pack(pady=10)

    type_window.transient(root)  # Делает новое окно временным относительно главного окна
    type_window.grab_set()  # Блокирует взаимодействие с главным окном, пока открыто новое
    type_window.mainloop() 

def move_request(): #перенос заявки
    if selected_month is None or selected_year is None:
        messagebox.showwarning("Предупреждение", "Сначала выберите год и месяц.")
        return

    request_id = simpledialog.askinteger("Ввод", "Введите ID заявки для переноса:")
    
    requests_table_name = f"requests_{months_dict[selected_month]}_20{selected_year}"

    try:
        # Проверяем, существует ли заявка с указанным ID
        cur.execute(f'SELECT * FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
        request = cur.fetchone()

        if request:
            new_day_id = simpledialog.askinteger("Ввод", "Введите новый день для переноса заявки:")
            new_execution_time = simpledialog.askstring("Ввод", "Введите новое время исполнения заявки:")

            # Проверяем, существует ли новый день в таблице дней
            cur.execute(f'SELECT Day_ID FROM days_{months_dict[selected_month]}_20{selected_year} WHERE Day_ID = ?', (new_day_id,))
            day_exists = cur.fetchone()

            if day_exists:
                # Обновляем ID дня и время исполнения в заявке
                cur.execute(f'''UPDATE {requests_table_name} 
                                SET Day_ID = ?, Execution_Time = ? 
                                WHERE Request_ID = ?''', (new_day_id, new_execution_time, request_id))
                conn.commit()
                messagebox.showinfo("Информация", f"Заявка с ID {request_id} успешно перенесена на день {new_day_id}.")
            else:
                messagebox.showwarning("Предупреждение", f"Дня  {new_day_id} не существует в месяце {selected_month} года {selected_year}.")
        else:
            messagebox.showinfo("Информация", f"Заявка с ID {request_id} не найдена.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось перенести заявку: {e}")

def update_request_status(): #изменить статус заявки
    if selected_month is None or selected_year is None:
        messagebox.showwarning("Предупреждение", "Сначала выберите год и месяц.")
        return

    request_id = simpledialog.askinteger("Ввод", "Введите ID заявки для изменения статуса:")

    requests_table_name = f"requests_{months_dict[selected_month]}_20{selected_year}"

    try:
        # Проверяем, существует ли заявка с указанным ID
        cur.execute(f'SELECT * FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
        request = cur.fetchone()

        if request:
            # Создаем окно для выбора нового статуса
            status_window = tk.Toplevel(root)
            status_window.title("Изменение статуса заявки")

            # Устанавливаем размеры и положение окна
            status_window.geometry("300x150+100+100")  # Ширина x Высота + X + Y

            selected_status = tk.StringVar(status_window)
            selected_status.set("Готово")  # Устанавливаем значение по умолчанию

            status_label = tk.Label(status_window, text="Выберите новый статус заявки:")
            status_label.pack(pady=10)

            # Создаем Combobox для выбора статуса заявки
            status_menu = ttk.Combobox(status_window, textvariable=selected_status, values=["Готово", "Отмена"])
            status_menu.pack(pady=10)

            def on_submit():
                new_status = selected_status.get()

                try:
                    # Обновляем статус заявки в базе данных
                    cur.execute(f'''UPDATE {requests_table_name} 
                                    SET Status = ? 
                                    WHERE Request_ID = ?''', (new_status, request_id))
                    conn.commit()
                    messagebox.showinfo("Информация", f"Статус заявки с ID {request_id} успешно изменен на '{new_status}'.")
                    status_window.destroy()  # Закрываем окно выбора статуса
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось изменить статус заявки: {e}")

            submit_button = tk.Button(status_window, text="Подтвердить", command=on_submit)
            submit_button.pack(pady=10)

            status_window.transient(root)  # Делает новое окно временным относительно главного окна
            status_window.grab_set()  # Блокирует взаимодействие с главным окном, пока открыто новое
            status_window.mainloop()  # Запускаем главный цикл окна выбора статуса
        else:
            messagebox.showinfo("Информация", f"Заявка с ID {request_id} не найдена.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось получить заявку: {e}")

def update_additional_info(): # изменить доп инфу
    if selected_month is None or selected_year is None:
        messagebox.showwarning("Предупреждение", "Сначала выберите год и месяц.")
        return

    request_id = simpledialog.askinteger("Ввод", "Введите ID заявки для изменения дополнительной информации:")

    requests_table_name = f"requests_{months_dict[selected_month]}_20{selected_year}"

    try:
        # Проверяем, существует ли заявка с указанным ID
        cur.execute(f'SELECT * FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
        request = cur.fetchone()

        if request:
            new_additional_info = simpledialog.askstring("Ввод", "Введите новую дополнительную информацию:")

            # Обновляем дополнительную информацию в заявке
            cur.execute(f'''UPDATE {requests_table_name} 
                            SET Additional_Info = ? 
                            WHERE Request_ID = ?''', (new_additional_info, request_id))
            conn.commit()
            messagebox.showinfo("Информация", f"Дополнительная информация для заявки с ID {request_id} успешно обновлена.")
        else:
            messagebox.showinfo("Информация", f"Заявка с ID {request_id} не найдена.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось изменить дополнительную информацию: {e}")

def update_additional_phone():  # изменить дополнительный телефон
    if selected_month is None or selected_year is None:
        messagebox.showwarning("Предупреждение", "Сначала выберите год и месяц.")
        return

    request_id = simpledialog.askinteger("Ввод", "Введите ID заявки для изменения дополнительного телефона:")

    requests_table_name = f"requests_{months_dict[selected_month]}_20{selected_year}"

    try:
        # Проверяем, существует ли заявка с указанным ID
        cur.execute(f'SELECT * FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
        request = cur.fetchone()

        if request:
            new_additional_phone = simpledialog.askstring("Ввод", "Введите новый дополнительный телефон:")

            # Обновляем дополнительный телефон в заявке
            cur.execute(f'''UPDATE {requests_table_name} 
                            SET Additional_Phone = ? 
                            WHERE Request_ID = ?''', (new_additional_phone, request_id))
            conn.commit()
            messagebox.showinfo("Информация", f"Дополнительный телефон для заявки с ID {request_id} успешно обновлен.")
        else:
            messagebox.showinfo("Информация", f"Заявка с ID {request_id} не найдена.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось изменить дополнительный телефон: {e}")



def main_menu():
    global root, cal, requests_display
    root = tk.Tk()
    root.title("Управление Заявками")

    # Изменяем цвет фона главного окна
    root.configure(bg='old lace')

    # # Устанавливаем пустой значок
    # empty_image = Image.new("RGBA", (1, 1), (255, 255, 255, 0))  # Создаем пустое изображение
    # empty_photo = ImageTk.PhotoImage(empty_image)
    # root.iconphoto(False, empty_photo)

    # Создаем Frame для календаря
    calendar_frame = tk.Frame(root, bg='old lace')
    calendar_frame.grid(row=0, column=0, padx=10, pady=10)

    # Создаем календарь
    cal = Calendar(calendar_frame, selectmode='day', year=2024, month=10, day=6)
    cal.pack(pady=20)

    # Привязываем событие изменения даты к функции
    cal.bind("<<CalendarSelected>>", update_selected_date)

    # Создаем Frame для кнопок
    button_frame = tk.Frame(root, bg='old lace')
    button_frame.grid(row=1, column=0, padx=10, pady=10)

    # Кнопки для управления заявками
    button_labels = [
        ("Добавить Заявку", add_request),
        ("Удалить Заявку", delete_request),
        ("Поиск Заявок по Телефону", search_requests_by_phone),
        ("Отчет заявок за месяц", search_requests_by_type),
        ("Перенос Заявки", move_request),
        ("Изменить Статус Заявки", update_request_status),
        ("Изменить Доп. Информацию", update_additional_info),
        ("Изменить Доп. Телефон", update_additional_phone),
        ("Выход", on_closing)
    ]

    for i, (label, command) in enumerate(button_labels):
        button = tk.Button(button_frame, text=label, command=command, width=25)
        button.grid(row=i // 3, column=i % 3, padx=5, pady=5)

     # Создаем фрейм для текстового поля и полосы прокрутки
    text_frame = tk.Frame(root)
    text_frame.grid(row=2, column=0, padx=10, pady=10)

    # Создаем текстовое поле
    requests_display = tk.Text(text_frame, width=60, height=20, bg='white', fg='black', wrap=tk.WORD, font=('Arial', 12))
    requests_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    def copy_text(event):
    # Проверяем, нажата ли клавиша Control
        if event.state & 0x0004:  # 0x0004 - это состояние для нажатой клавиши Control
            try:
            # Получаем выделенный текст
                selected_text = requests_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            # Копируем выделенный текст в буфер обмена
                root.clipboard_clear()  # Очищаем буфер обмена
                root.clipboard_append(selected_text)  # Добавляем выделенный текст в буфер обмена
            except :
            # Если ничего не выделено, игнорируем ошибку
                pass

# Привязываем событие нажатия клавиш Ctrl+C к функции copy_text
    requests_display.bind("<KeyPress>", copy_text)
    # Создаем полосу прокрутки
    scrollbar = tk.Scrollbar(text_frame, command=requests_display.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Привязываем полосу прокрутки к текстовому полю
    requests_display.config(yscrollcommand=scrollbar.set)
    


    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

def on_closing():
    conn.close()
    root.quit()

# Вызов функции main_menu()
if __name__ == "__main__":
    main_menu()
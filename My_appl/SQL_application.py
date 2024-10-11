import sqlite3

def start():
    global conn
    global cur
    conn = sqlite3.connect("Omega_apl.db")
    cur = conn.cursor()
    
    try:
        age = int(input("Введите год: "))
        table_name = f"year_{age}"  # Формируем имя таблицы
        
        # Создаем таблицу для месяцев, если она не существует
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                        Month_ID INTEGER PRIMARY KEY NOT NULL,
                        Month TEXT)''')
        
        # Проверяем, есть ли уже месяцы в таблице
        cur.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cur.fetchone()[0]
        
        if count == 0:  # Если таблица пуста, добавляем месяцы
            months = [
                ("Январь",),
                ("Февраль",),
                ("Март",),
                ("Апрель",),
                ("Май",),
                ("Июнь",),
                ("Июль",),
                ("Август",),
                ("Сентябрь",),
                ("Октябрь",),
                ("Ноябрь",),
                ("Декабрь",)
            ]
            cur.executemany(f'INSERT INTO {table_name} (Month) VALUES (?)', months)
            conn.commit()
            print(f"Месяцы для года {age} успешно добавлены.")
        else:
            print(f"Месяцы для года {age} уже существуют.")
        
        return table_name  # Возвращаем имя таблицы
    except ValueError:
        print("Пожалуйста, введите корректный год.")
        return None

def create_days_table(month_name, year):
    days_table_name = f"days_{month_name}_{year}"
    
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {days_table_name} (
                    Day_ID INTEGER PRIMARY KEY NOT NULL,
                    Day INTEGER NOT NULL,
                    Month_ID INTEGER,
                    FOREIGN KEY (Month_ID) REFERENCES year_{year}(Month_ID))''')
    
    if month_name in ["Январь", "Март", "Май", "Июль", "Август", "Октябрь", "Декабрь"]:
        days_in_month = 31
    elif month_name in ["Апрель", "Июнь", "Сентябрь", "Ноябрь"]:
        days_in_month = 30
    else:
        days_in_month = 28

    for day in range(1, days_in_month + 1):
        cur.execute(f'INSERT INTO {days_table_name} (Day, Month_ID) VALUES (?, (SELECT Month_ID FROM year_{year} WHERE Month = ?))', (day, month_name))
    
    conn.commit()
    print(f"Таблица для дней месяца {month_name} года {year} успешно создана.")

def create_requests_table(month_name, year):
    requests_table_name = f"requests_{month_name}_{year}"
    
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {requests_table_name} (
                    Request_ID INTEGER PRIMARY KEY NOT NULL,
                    Execution_Time TEXT NOT NULL,
                    Address TEXT NOT NULL,
                    Phone TEXT NOT NULL,
                    Additional_Phone TEXT,
                    Request_Type TEXT NOT NULL,
                    Additional_Info TEXT,
                    Status TEXT NOT NULL,
                    Day_ID INTEGER,
                    FOREIGN KEY (Day_ID) REFERENCES days_{month_name}_{year}(Day_ID))''')
    
    conn.commit()
    print(f"Таблица для заявок месяца {month_name} года {year} успешно создана.")

def add_request(month_name, year):
    requests_table_name = f"requests_{month_name}_{year}"
    
    execution_time = input("Введите время исполнения заявки: ")
    address = input("Введите адрес: ")
    phone = input("Введите телефон: ")
    additional_phone = input("Введите дополнительный телефон (если есть): ")
    request_type = input("Введите тип заявки: ")
    additional_info = input("Введите дополнительную информацию: ")
    status = input("Введите статус заявки: ")
    day_id = int(input("Введите ID дня (например, 1 для 1-го числа): "))
    
    cur.execute(f'''INSERT INTO {requests_table_name} 
                    (Execution_Time, Address, Phone, Additional_Phone, Request_Type, Additional_Info, Status, Day_ID) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                (execution_time, address, phone, additional_phone, request_type, additional_info, status, day_id))
    
    conn.commit()
    print("Заявка успешно добавлена.")

def show_requests_for_day(month_name, year):
    requests_table_name = f"requests_{month_name}_{year}"
    day_id = int(input("Введите ID дня для просмотра заявок: "))
    
    # Получаем все заявки для указанного дня
    cur.execute(f'''SELECT * FROM {requests_table_name} WHERE Day_ID = ?''', (day_id,))
    requests = cur.fetchall()
    
    if requests:
        print(f"Заявки для дня {day_id} в месяце {month_name} года {year}:")
        for request in requests:
            print(f"ID: {request[0]}, Время исполнения: {request[1]}, Адрес: {request[2]}, Телефон: {request[3]}, "
                  f"Доп. телефон: {request[4]}, Тип заявки: {request[5]}, Доп. информация: {request[6]}, "
                  f"Статус: {request[7]}")
    else:
        print(f"Заявок для дня {day_id} в месяце {month_name} года {year} не найдено.")

def read_file(table_name):  # Принимаем table_name как параметр
    cur.execute(f'SELECT Month FROM {table_name}')  # Читаем месяцы из таблицы
    row = cur.fetchone()
    while row is not None:
        print(f"{row[0]:35}")  # Выводим месяцы
        row = cur.fetchone()
        
def update_request_status(month_name, year):
    requests_table_name = f"requests_{month_name}_{year}"
    request_id = int(input("Введите ID заявки для изменения статуса: "))
    
    # Получаем текущую заявку по ID
    cur.execute(f'SELECT * FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
    request = cur.fetchone()
    
    if request:
        new_status = input("Введите новый статус заявки: ")
        
        # Обновляем статус заявки
        cur.execute(f'''UPDATE {requests_table_name} 
                        SET Status = ? 
                        WHERE Request_ID = ?''', (new_status, request_id))
        
        conn.commit()
        print(f"Статус заявки с ID {request_id} успешно обновлен на '{new_status}'.")
    else:
        print(f"Заявка с ID {request_id} не найдена.")

def search_requests_by_phone(month_name, year): # поиск по номеру телефона
    requests_table_name = f"requests_{month_name}_{year}"
    phone_number = input("Введите номер телефона для поиска заявок: ")
    
    # Получаем все заявки с указанным номером телефона, включая ID дня
    cur.execute(f'''SELECT r.*, d.Day 
                    FROM {requests_table_name} r
                    JOIN days_{month_name}_{year} d ON r.Day_ID = d.Day_ID
                    WHERE r.Phone = ? OR r.Additional_Phone = ?''', (phone_number, phone_number))
    requests = cur.fetchall()
    
    if requests:
        print(f"Заявки с номером телефона {phone_number} в месяце {month_name} года {year}:")
        for request in requests:
            print(f"ID: {request[0]}, Время исполнения: {request[1]}, Адрес: {request[2]}, "
                  f"Телефон: {request[3]}, Доп. телефон: {request[4]}, Тип заявки: {request[5]}, "
                  f"Доп. информация: {request[6]}, Статус: {request[7]}, День: {request[8]}")
    else:
        print(f"Заявок с номером телефона {phone_number} не найдено.")

def search_requests_by_type(month_name, year): # отчет по типам заявок за месяц
    requests_table_name = f"requests_{month_name}_{year}"
    request_type = input("Введите тип заявки для поиска: ")
    
    # Получаем все заявки с указанным типом заявки
    cur.execute(f'''SELECT r.*, d.Day 
                    FROM {requests_table_name} r
                    JOIN days_{month_name}_{year} d ON r.Day_ID = d.Day_ID
                    WHERE r.Request_Type = ?''', (request_type,))
    requests = cur.fetchall()
    
    if requests:
        print(f"Заявки с типом '{request_type}' в месяце {month_name} года {year}:")
        for request in requests:
            print(f"ID: {request[0]}, Время исполнения: {request[1]}, Адрес: {request[2]}, "
                  f"Телефон: {request[3]}, Доп. телефон: {request[4]}, Тип заявки: {request[5]}, "
                  f"Доп. информация: {request[6]}, Статус: {request[7]}, День: {request[8]}")
    else:
        print(f"Заявок с типом '{request_type}' не найдено.")

def move_request(table_name):
    if table_name is None:
        print("Сначала создайте таблицу для месяцев.")
        return

    month_name = input("Введите месяц, в который хотите перенести заявку: ")
    year = table_name.split('_')[1]
    requests_table_name = f"requests_{month_name}_{year}"

    request_id = int(input("Введите ID заявки для переноса: "))
    
    # Получаем текущую заявку по ID
    cur.execute(f'SELECT * FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
    request = cur.fetchone()
    
    if request:
        new_day_id = int(input("Введите новый ID дня для переноса заявки: "))
        
        # Проверяем, существует ли новый день в таблице дней
        cur.execute(f'SELECT Day_ID FROM days_{month_name}_{year} WHERE Day_ID = ?', (new_day_id,))
        day_exists = cur.fetchone()
        
        if day_exists:
            # Обновляем ID дня в заявке
            cur.execute(f'''UPDATE {requests_table_name} 
                            SET Day_ID = ? 
                            WHERE Request_ID = ?''', (new_day_id, request_id))
            conn.commit()
            print(f"Заявка с ID {request_id} успешно перенесена на день с ID {new_day_id}.")
        else:
            print(f"Дня с ID {new_day_id} не существует в месяце {month_name} года {year}.")
    else:
        print(f"Заявка с ID {request_id} не найдена.")
        
def delete_request(table_name): #удаление заявки по ID
    if table_name is None:
        print("Сначала создайте таблицу для месяцев.")
        return

    month_name = input("Введите месяц, из которого хотите удалить заявку: ")
    year = table_name.split('_')[1]
    requests_table_name = f"requests_{month_name}_{year}"

    request_id = int(input("Введите ID заявки для удаления: "))
    
    # Проверяем, существует ли заявка с указанным ID
    cur.execute(f'SELECT * FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
    request = cur.fetchone()
    
    if request:
        # Удаляем заявку
        cur.execute(f'DELETE FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
        conn.commit()
        print(f"Заявка с ID {request_id} успешно удалена.")
    else:
        print(f"Заявка с ID {request_id} не найдена.")

def update_additional_info(table_name): #изменить доп информацию
    if table_name is None:
        print("Сначала создайте таблицу для месяцев.")
        return

    month_name = input("Введите месяц, в котором хотите изменить дополнительную информацию: ")
    year = table_name.split('_')[1]
    requests_table_name = f"requests_{month_name}_{year}"

    request_id = int(input("Введите ID заявки для изменения дополнительной информации: "))
    
    # Проверяем, существует ли заявка с указанным ID
    cur.execute(f'SELECT * FROM {requests_table_name} WHERE Request_ID = ?', (request_id,))
    request = cur.fetchone()
    
    if request:
        new_additional_info = input("Введите новую дополнительную информацию: ")
        
        # Обновляем дополнительную информацию в заявке
        cur.execute(f'''UPDATE {requests_table_name} 
                        SET Additional_Info = ? 
                        WHERE Request_ID = ?''', (new_additional_info, request_id))
        conn.commit()
        print(f"Дополнительная информация для заявки с ID {request_id} успешно обновлена.")
    else:
        print(f"Заявка с ID {request_id} не найдена.")


def main_menu():
    while True:
        print("\n Выберите действие:")
        print("1. Добавить заявку")
        print("2. Просмотреть заявки за день")
        print("3. Изменить статус заявки")
        print("4. Поиск заявок по номеру телефона")
        print("5. Отчет по типам заявок ")
        print("6. Перенос заявки")
        print("7. Удалить заявку")
        print("8. Изменить доп. информацию")
        print("10. Выход")

        choice = input("Введите номер действия: ")

        if choice == '1':
            if 'table_name' in locals():
                month_name = input("Введите месяц для добавления заявки: ")
                add_request(month_name, table_name.split('_')[1])  # Извлекаем год из имени таблицы
            else:
                print("Сначала создайте таблицу для месяцев.")
                table_name = start()
                month_name = input("Введите месяц для добавления заявки: ")
                add_request(month_name, table_name.split('_')[1])  # Извлекаем год из имени таблицы
        
        elif choice == '2':
            if 'table_name' in locals():
                month_name = input("Введите месяц для просмотра заявок: ")
                show_requests_for_day(month_name, table_name.split('_')[1])  # Извлекаем год из имени таблицы
            else:
                print("Сначала создайте таблицу для месяцев.")
                table_name = start()
                month_name = input("Введите месяц для просмотра заявок: ")
                show_requests_for_day(month_name, table_name.split('_')[1])  # Извлекаем год из имени таблицы
        elif choice == '3':  # Обработка изменения статуса
            if 'table_name' in locals():
                month_name = input("Введите месяц для изменения статуса заявки: ")  # Запрашиваем месяц
                year = table_name.split('_')[1]  # Извлекаем год из имени таблицы
                update_request_status(month_name, year)  # Вызов функции изменения статуса заявки с параметрами
            else:
                print("Сначала создайте таблицу для месяцев.")
                table_name = start()
                month_name = input("Введите месяц для изменения статуса заявки: ")  # Запрашиваем месяц
                year = table_name.split('_')[1]  # Извлекаем год из имени таблицы
                update_request_status(month_name, year)  # Вызов функции изменения статуса заявки с параметрами
                
        elif choice == '4':  # Обработка поиска заявки
            if 'table_name' in locals():
                month_name = input("Введите месяц для поиска заявок: ")
                year = table_name.split('_')[1]
                search_requests_by_phone(month_name, year)  # Вызов функции поиска заявок по номеру телефона
            else:
                print("Сначала создайте таблицу для месяцев.")
                table_name = start()
                month_name = input("Введите месяц для поиска заявок: ")
                year = table_name.split('_')[1]
                search_requests_by_phone(month_name, year)  # Вызов функции поиска заявок по номеру телефона
        
        elif choice == '5':  # Обработка нового выбора
            if 'table_name' in locals():
                month_name = input("Введите месяц для поиска заявок: ")
                year = table_name.split('_')[1]
                search_requests_by_type(month_name, year)  # Вызов функции поиска заявок по типу
            else:
                print("Сначала создайте таблицу для месяцев.")
                table_name = start()
                month_name = input("Введите месяц для поиска заявок: ")
                year = table_name.split('_')[1]
                search_requests_by_type(month_name, year)  # Вызов функции поиска заявок по типу
       
        elif choice == '6':  
            if 'table_name' in locals():
                move_request(table_name)  # Вызов функции переноса заявки с передачей table_name
            else:
                print("Сначала создайте таблицу для месяцев.")
                table_name = start()
                move_request(table_name)  # Вызов функции переноса заявки с передачей
                
        elif choice == '7':  # удаление заявки
            if 'table_name' in locals():
                delete_request(table_name)  # Вызов функции удаления заявки с передачей table_name
            else:
                print("Сначала создайте таблицу для месяцев.")
                table_name = start()
                delete_request(table_name)  # Вызов функции удаления заявки  
        elif choice == '8':  # Обработка нового выбора для изменения дополнительной информации
            if 'table_name' in locals():
                update_additional_info(table_name)  # Вызов функции изменения дополнительной информации с передачей table_name
            else:
                print("Сначала создайте таблицу для месяцев.")
                table_name = start()
                update_additional_info(table_name)  # Вызов функции изменения дополнительной информации с передачей table_name
        
        elif choice == '10':
            print("Выход из программы.")
            break
        else:
            print("Неверный ввод. Пожалуйста, попробуйте снова.")



#try:
 #   main_menu()
#finally:
  #  if 'conn' in globals():
   #     conn.close()  # Закрываем соединение с базой данных
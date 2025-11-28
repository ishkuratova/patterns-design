"""
Модуль репозиториев для работы с сотрудниками.
Поддерживает JSON, YAML и PostgreSQL хранилища.
"""

import json
import os
from abc import ABC, abstractmethod
from typing import List

import psycopg2
import yaml
from employee import Employee


class EmployeeRep(ABC):
    """Абстрактный базовый класс для репозиториев сотрудников."""

    def __init__(self):
        self._employees = []

    @abstractmethod
    def save_data(self):
        """Сохраняет данные в хранилище."""

    @abstractmethod
    def _read_all(self):
        """Читает все данные из хранилища."""

    def get_by_id(self, employee_id: int) -> Employee | None:
        """Возвращает сотрудника по ID."""
        for employee in self._employees:
            if employee.employee_id == employee_id:
                return employee
        return None

    def get_k_n_short_list(self, k: int, n: int) -> List['Employee']:
        """Возвращает страницу с сотрудниками."""
        start_index = (n - 1) * k
        end_index = start_index + k

        if start_index >= len(self._employees):
            raise IndexError("page (n) out of range")

        short_list = []
        for i in range(start_index, min(end_index, len(self._employees))):
            employee = self._employees[i]
            short_list.append(employee)

        return short_list

    def sort_by_field(self, field: str, reverse: bool = False) -> List['Employee']:
        """Сортирует сотрудников по указанному полю."""
        valid_fields = ['employee_id', 'first_name', 'last_name', 'salary']
        if field not in valid_fields:
            raise ValueError(f"Недопустимое поле для сортировки. Допустимые поля: {valid_fields}")

        employees_copy = self._employees.copy()

        if field == 'employee_id':
            employees_copy.sort(key=lambda x: x.employee_id, reverse=reverse)
        elif field == 'first_name':
            employees_copy.sort(key=lambda x: x.first_name, reverse=reverse)
        elif field == 'last_name':
            employees_copy.sort(key=lambda x: x.last_name, reverse=reverse)
        elif field == 'salary':
            employees_copy.sort(key=lambda x: x.salary, reverse=reverse)

        self.save_data()
        return employees_copy

    def add_employee(self, first_name: str, last_name: str, salary: int,
                     patronymic: str | None = None) -> Employee:
        """Добавляет нового сотрудника."""
        if self._employees:
            new_id = max(emp.employee_id for emp in self._employees) + 1
        else:
            new_id = 1

        new_employee = Employee(new_id, first_name, last_name, patronymic, salary)
        self._employees.append(new_employee)
        self.save_data()
        return new_employee

    def update_employee(self, employee_id: int, **kwargs) -> bool:
        """Обновляет данные сотрудника."""
        employee = self.get_by_id(employee_id)
        if not employee:
            return False

        valid_fields = ['first_name', 'last_name', 'patronymic', 'salary']
        for field, value in kwargs.items():
            if field in valid_fields:
                if field == 'salary':
                    employee.salary = value
                elif field == 'first_name':
                    employee.first_name = value
                elif field == 'last_name':
                    employee.last_name = value
                elif field == 'patronymic':
                    employee.patronymic = value

        self.save_data()
        return True

    def delete_employee(self, employee_id: int) -> bool:
        """Удаляет сотрудника по ID."""
        for i, employee in enumerate(self._employees):
            if employee.employee_id == employee_id:
                del self._employees[i]
                self.save_data()
                return True
        return False

    def get_count(self) -> int:
        """Возвращает количество сотрудников."""
        return len(self._employees)


class EmployeeRepJson(EmployeeRep):
    """Репозиторий для работы с JSON файлами."""
    def __init__(self, filename: str):
        super().__init__()
        self._filename: str = filename
        self._read_all()

    def _read_all(self):
        """Читает данные из JSON файла."""
        if os.path.exists(self._filename):
            try:
                with open(self._filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self._employees = [Employee(item) for item in data]
            except (json.JSONDecodeError, ValueError) as error:
                print(f"Ошибка загрузки данных: {error}")
                self._employees = []
        else:
            self._employees = []

    def save_data(self):
        """Сохраняет данные в JSON файл."""
        try:
            with open(self._filename, 'w', encoding='utf-8') as file:
                data = []
                for emp in self._employees:
                    emp_dict = {
                        'employee_id': emp.employee_id,
                        'first_name': emp.first_name,
                        'last_name': emp.last_name,
                        'patronymic': emp.patronymic,
                        'salary': emp.salary
                    }
                    data.append(emp_dict)
                json.dump(data, file, indent=2, ensure_ascii=False)
        except (IOError, TypeError) as error:
            print(f"Ошибка сохранения данных: {error}")


class EmployeeRepYaml(EmployeeRep):
    """Репозиторий для работы с YAML файлами."""
    def __init__(self, filename: str):
        super().__init__()
        self._filename = filename
        self._read_all()

    def _read_all(self):
        """Читает данные из YAML файла."""
        if os.path.exists(self._filename):
            try:
                with open(self._filename, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    if data is None:
                        data = []
                    self._employees = [Employee(item) for item in data]
            except (yaml.YAMLError, ValueError) as error:
                print(f"Ошибка загрузки данных из YAML: {error}")
                self._employees = []
        else:
            self._employees = []

    def save_data(self):
        """Сохраняет данные в YAML файл."""
        try:
            with open(self._filename, 'w', encoding='utf-8') as file:
                data = []
                for emp in self._employees:
                    emp_dict = {
                        'employee_id': emp.employee_id,
                        'first_name': emp.first_name,
                        'last_name': emp.last_name,
                        'patronymic': emp.patronymic,
                        'salary': emp.salary
                    }
                    data.append(emp_dict)
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True, indent=2)
        except (IOError, TypeError) as error:
            print(f"Ошибка сохранения данных в YAML: {error}")


class DatabaseConnection:
    """Класс для управления подключением к базе данных (Singleton)."""

    _instance = None
    connection_params: dict

    def __new__(cls, host: str, port: int, database: str, user: str, password: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # pylint: disable=no-member
            cls._instance.connection_params = {
                'host': host,
                'port': port,
                'database': database,
                'user': user,
                'password': password
            }
        return cls._instance

    def get_connection(self):
        """Возвращает соединение с базой данных."""
        return psycopg2.connect(**self.connection_params)


class EmployeeRepDB:
    """Репозиторий для работы с PostgreSQL базой данных."""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self._db = DatabaseConnection(host, port, database, user, password)
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Создает таблицу, если она не существует."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS employees (
            employee_id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            patronymic VARCHAR(100),
            salary INTEGER NOT NULL CHECK (salary >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_table_query)
                    conn.commit()
        except psycopg2.Error as error:
            print(f"Ошибка создания таблицы: {error}")

    def get_by_id(self, employee_id: int) -> Employee | None:
        """Возвращает сотрудника по ID из БД."""
        query = """
        SELECT employee_id, first_name, last_name, patronymic, salary 
        FROM employees 
        WHERE employee_id = %s
        """

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (employee_id,))
                    row = cursor.fetchone()

                    if row:
                        employee_data = {
                            'employee_id': row[0],
                            'first_name': row[1],
                            'last_name': row[2],
                            'patronymic': row[3],
                            'salary': row[4]
                        }
                        return Employee(employee_data)
                    return None

        except psycopg2.Error as error:
            print(f"Ошибка получения сотрудника по ID: {error}")
            return None

    def get_k_n_short_list(self, k: int, n: int) -> List['Employee']:
        """Возвращает страницу сотрудников из БД."""
        offset = (n - 1) * k
        query = """
        SELECT employee_id, first_name, last_name, patronymic, salary 
        FROM employees 
        ORDER BY employee_id 
        LIMIT %s OFFSET %s
        """

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (k, offset))
                    rows = cursor.fetchall()

                    short_list = []
                    for row in rows:
                        employee_data = {
                            'employee_id': row[0],
                            'first_name': row[1],
                            'last_name': row[2],
                            'patronymic': row[3],
                            'salary': row[4]
                        }
                        employee = Employee(employee_data)
                        short_list.append(employee)

                    return short_list

        except psycopg2.Error as error:
            print(f"Ошибка получения списка сотрудников: {error}")
            return []

    def add_employee(self, first_name: str, last_name: str, salary: int,
                     patronymic: str | None = None) -> Employee | None:
        """Добавляет сотрудника в БД."""
        query = """
        INSERT INTO employees (first_name, last_name, patronymic, salary) 
        VALUES (%s, %s, %s, %s) 
        RETURNING employee_id, first_name, last_name, patronymic, salary
        """

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (first_name, last_name, patronymic, salary))
                    row = cursor.fetchone()
                    conn.commit()

                    if row:
                        employee_data = {
                            'employee_id': row[0],
                            'first_name': row[1],
                            'last_name': row[2],
                            'patronymic': row[3],
                            'salary': row[4]
                        }
                        return Employee(employee_data)
                    return None

        except psycopg2.Error as error:
            print(f"Ошибка добавления сотрудника: {error}")
            return None

    def update_employee(self, employee_id: int, **kwargs) -> bool:
        """Обновляет данные сотрудника в БД."""
        valid_fields = ['first_name', 'last_name', 'patronymic', 'salary']
        updates = []
        values = []

        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = %s")
                values.append(value)

        if not updates:
            return False

        values.append(employee_id)
        set_clause = ", ".join(updates)
        query = f"UPDATE employees SET {set_clause} WHERE employee_id = %s"

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0

        except psycopg2.Error as error:
            print(f"Ошибка обновления сотрудника: {error}")
            return False

    def delete_employee(self, employee_id: int) -> bool:
        """Удаляет сотрудника из БД."""
        query = "DELETE FROM employees WHERE employee_id = %s"

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (employee_id,))
                    conn.commit()
                    return cursor.rowcount > 0

        except psycopg2.Error as error:
            print(f"Ошибка удаления сотрудника: {error}")
            return False

    def get_count(self) -> int:
        """Возвращает количество сотрудников в БД."""
        query = "SELECT COUNT(*) FROM employees"

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    return result[0] if result else 0

        except psycopg2.Error as error:
            print(f"Ошибка получения количества сотрудников: {error}")
            return 0

    def get_all_employees(self) -> List[Employee]:
        """Возвращает всех сотрудников из БД."""
        query = """
        SELECT employee_id, first_name, last_name, patronymic, salary 
        FROM employees 
        ORDER BY employee_id
        """

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()

                    employees = []
                    for row in rows:
                        employee_data = {
                            'employee_id': row[0],
                            'first_name': row[1],
                            'last_name': row[2],
                            'patronymic': row[3],
                            'salary': row[4]
                        }
                        employees.append(Employee(employee_data))

                    return employees

        except psycopg2.Error as error:
            print(f"Ошибка получения всех сотрудников: {error}")
            return []


class EmployeeRepDBAdapter(EmployeeRep):
    """Адаптер для работы с БД через единый интерфейс репозитория."""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self._db = EmployeeRepDB(host, port, database, user, password)
        super().__init__()
        self._read_all()

    def _read_all(self):
        """Читает всех сотрудников из БД."""
        self._employees = self._db.get_all_employees()

    def save_data(self):
        """Синхронизирует данные с БД - УПРОЩЕННАЯ ВЕРСИЯ."""
        self._read_all()

    def add_employee(self, first_name: str, last_name: str, salary: int,
                     patronymic: str | None = None) -> Employee | None:
        """Добавляет нового сотрудника через БД."""
        new_employee = self._db.add_employee(first_name, last_name, salary, patronymic)
        if new_employee:
            self._read_all()
            return new_employee
        return None

    def update_employee(self, employee_id: int, **kwargs) -> bool:
        """Обновляет данные сотрудника через БД."""
        result = self._db.update_employee(employee_id, **kwargs)
        if result:
            self._read_all()
        return result

    def delete_employee(self, employee_id: int) -> bool:
        """Удаляет сотрудника через БД."""
        result = self._db.delete_employee(employee_id)
        if result:
            self._read_all()
        return result

    def get_k_n_short_list(self, k: int, n: int) -> List['Employee']:
        """Используем БД для пагинации вместо локального списка."""
        return self._db.get_k_n_short_list(k, n)

    def sort_by_field(self, field: str, reverse: bool = False) -> List['Employee']:
        """Сортирует сотрудников по указанному полю."""
        valid_fields = ['employee_id', 'first_name', 'last_name', 'salary']
        if field not in valid_fields:
            raise ValueError(f"Недопустимое поле для сортировки. Допустимые поля: {valid_fields}")

        employees = self._db.get_all_employees()

        if field == 'employee_id':
            employees.sort(key=lambda x: x.employee_id, reverse=reverse)
        elif field == 'first_name':
            employees.sort(key=lambda x: x.first_name, reverse=reverse)
        elif field == 'last_name':
            employees.sort(key=lambda x: x.last_name, reverse=reverse)
        elif field == 'salary':
            employees.sort(key=lambda x: x.salary, reverse=reverse)

        return employees


class EmployeeRepDecorator:
    """Декоратор для добавления фильтрации и сортировки к репозиторию."""

    def __init__(self, file_repo: EmployeeRep):
        self._file_repo = file_repo

    def get_k_n_short_list(self, k: int, n: int, filter_func: callable = None,
                          sort_field: str = None, reverse: bool = False) -> List['Employee']:
        """Возвращает отфильтрованную и отсортированную страницу сотрудников."""
        employees_list = self._file_repo.get_k_n_short_list(self._file_repo.get_count(), 1)

        if filter_func:
            employees_list = [emp for emp in employees_list if filter_func(emp)]

        if sort_field:
            valid_fields = ['employee_id', 'first_name', 'last_name', 'salary']
            if sort_field not in valid_fields:
                raise ValueError(f"Недопустимое поле для сортировки: {sort_field}")

            if sort_field == 'employee_id':
                employees_list.sort(key=lambda x: x.employee_id, reverse=reverse)
            elif sort_field == 'first_name':
                employees_list.sort(key=lambda x: x.first_name, reverse=reverse)
            elif sort_field == 'last_name':
                employees_list.sort(key=lambda x: x.last_name, reverse=reverse)
            elif sort_field == 'salary':
                employees_list.sort(key=lambda x: x.salary, reverse=reverse)

        start_index = (n - 1) * k
        end_index = start_index + k

        if start_index >= len(employees_list):
            return []

        short_list = []
        for i in range(start_index, min(end_index, len(employees_list))):
            employee = employees_list[i]
            short_list.append(employee)

        return short_list

    def get_count(self, filter_func: callable = None) -> int:
        """Возвращает количество сотрудников после фильтрации."""
        employees_list = self._file_repo.get_k_n_short_list(self._file_repo.get_count(), 1)

        if filter_func:
            employees_list = [emp for emp in employees_list if filter_func(emp)]

        return len(employees_list)

from abc import ABC, abstractmethod
import psycopg2
import json
import yaml
import os
from typing import List, Dict, Any
from employee import Employee


class EmployeeRep(ABC):
    def __init__(self, filename: str):
        self.filename = filename
        self._employees = []
        self._load_data()

    @abstractmethod
    def _load_data(self):
        pass

    @abstractmethod
    def _save_data(self):
        pass

    def read_all(self) -> List['Employee']:
        self._load_data()
        return self._employees.copy()

    def write_all(self, employees: List['Employee']):
        self._employees = employees.copy()
        self._save_data()

    def get_by_id(self, employee_id: int) -> Employee | None:
        for employee in self._employees:
            if employee.employee_id == employee_id:
                return employee
        return None

    def get_k_n_short_list(self, k: int, n: int) -> List[Dict[str, Any]]:
        start_index = (n - 1) * k
        end_index = start_index + k

        if start_index >= len(self._employees):
            return []

        short_list = []
        for i in range(start_index, min(end_index, len(self._employees))):
            employee = self._employees[i]
            short_list.append({
                'employee_id': employee.employee_id,
                'short_info': employee.short_info()
            })

        return short_list

    def sort_by_field(self, field: str, reverse: bool = False) -> List['Employee']:
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

        self._save_data()
        return employees_copy

    def add_employee(self, first_name: str, last_name: str, salary: int,
                     patronymic: str | None = None) -> Employee:
        if self._employees:
            new_id = max(emp.employee_id for emp in self._employees) + 1
        else:
            new_id = 1

        new_employee = Employee(new_id, first_name, last_name, patronymic, salary)
        self._employees.append(new_employee)
        self._save_data()
        return new_employee

    def update_employee(self, employee_id: int, **kwargs) -> bool:
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

        self._save_data()
        return True

    def delete_employee(self, employee_id: int) -> bool:
        for i, employee in enumerate(self._employees):
            if employee.employee_id == employee_id:
                del self._employees[i]
                self._save_data()
                return True
        return False

    def get_count(self) -> int:
        return len(self._employees)

    def get_all_short_info(self) -> List[Dict[str, Any]]:
        return [{'employee_id': emp.employee_id, 'short_info': emp.short_info()}
                for emp in self._employees]


class EmployeeRepJson(EmployeeRep):
    def _load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self._employees = [Employee(item) for item in data]
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Ошибка загрузки данных: {e}")
                self._employees = []
        else:
            self._employees = []

    def _save_data(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
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
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")


class EmployeeRepYaml(EmployeeRep):
    def _load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    if data is None:
                        data = []
                    self._employees = [Employee(item) for item in data]
            except (yaml.YAMLError, ValueError) as e:
                print(f"Ошибка загрузки данных из YAML: {e}")
                self._employees = []
        else:
            self._employees = []

    def _save_data(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
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
        except Exception as e:
            print(f"Ошибка сохранения данных в YAML: {e}")

    def export_to_yaml_string(self) -> str:
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
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, indent=2)


class EmployeeRepDBAdapter(EmployeeRep):
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self._db = EmployeeRepDB(host, port, database, user, password)
        super().__init__("")

    def _load_data(self):
        self._employees = self._db.get_all_employees()

    def _save_data(self):
        try:
            print(f"DEBUG: Сохранение {len(self._employees)} сотрудников в БД")
            current_db_employees = self._db.get_all_employees()
            current_ids = {emp.employee_id for emp in current_db_employees}

            for emp_id in current_ids:
                if not any(e.employee_id == emp_id for e in self._employees):
                    self._db.delete_employee(emp_id)

            for employee in self._employees:
                if employee.employee_id in current_ids:
                    self._db.update_employee(
                        employee.employee_id,
                        first_name=employee.first_name,
                        last_name=employee.last_name,
                        patronymic=employee.patronymic,
                        salary=employee.salary
                    )
                else:
                    self._db.add_employee(
                        employee.first_name,
                        employee.last_name,
                        employee.salary,
                        employee.patronymic
                    )
        except Exception as e:
            print(f"DEBUG: Ошибка сохранения в БД: {e}")

    def read_all(self) -> List['Employee']:
        print(f"DEBUG: read_all() возвращает {len(self._employees)} сотрудников")
        return self._employees.copy()

    def write_all(self, employees: List['Employee']):
        current_employees = self._db.get_all_employees()

        current_ids = {emp.employee_id for emp in current_employees}
        new_ids = {emp.employee_id for emp in employees}

        for emp_id in current_ids - new_ids:
            self._db.delete_employee(emp_id)

        for employee in employees:
            if employee.employee_id in current_ids:
                self._db.update_employee(
                    employee.employee_id,
                    first_name=employee.first_name,
                    last_name=employee.last_name,
                    patronymic=employee.patronymic,
                    salary=employee.salary
                )
            else:
                self._db.add_employee(
                    employee.first_name,
                    employee.last_name,
                    employee.salary,
                    employee.patronymic
                )

    def sort_by_field(self, field: str, reverse: bool = False) -> List['Employee']:
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


class DatabaseConnection:
    _instance = None

    def __new__(cls, host: str, port: int, database: str, user: str, password: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection_params = {
                'host': host,
                'port': port,
                'database': database,
                'user': user,
                'password': password
            }
        return cls._instance

    def get_connection(self):
        return psycopg2.connect(**self.connection_params)


class EmployeeRepDB:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self._db = DatabaseConnection(host, port, database, user, password)
        self._ensure_table_exists()

    def _ensure_table_exists(self):
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
        except Exception as e:
            print(f"Ошибка создания таблицы: {e}")

    def get_by_id(self, employee_id: int) -> Employee | None:
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

        except Exception as e:
            print(f"Ошибка получения сотрудника по ID: {e}")
            return None

    def get_k_n_short_list(self, k: int, n: int) -> List[Dict[str, Any]]:
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
                        short_list.append({
                            'employee_id': employee.employee_id,
                            'short_info': employee.short_info()
                        })

                    return short_list

        except Exception as e:
            print(f"Ошибка получения списка сотрудников: {e}")
            return []

    def add_employee(self, first_name: str, last_name: str, salary: int,
                     patronymic: str | None = None) -> Employee | None:
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

        except Exception as e:
            print(f"Ошибка добавления сотрудника: {e}")
            return None

    def update_employee(self, employee_id: int, **kwargs) -> bool:
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

        except Exception as e:
            print(f"Ошибка обновления сотрудника: {e}")
            return False

    def delete_employee(self, employee_id: int) -> bool:
        query = "DELETE FROM employees WHERE employee_id = %s"

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (employee_id,))
                    conn.commit()
                    return cursor.rowcount > 0

        except Exception as e:
            print(f"Ошибка удаления сотрудника: {e}")
            return False

    def get_count(self) -> int:
        query = "SELECT COUNT(*) FROM employees"

        try:
            with self._db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    return result[0] if result else 0

        except Exception as e:
            print(f"Ошибка получения количества сотрудников: {e}")
            return 0

    def get_all_employees(self) -> List[Employee]:
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

        except Exception as e:
            print(f"Ошибка получения всех сотрудников: {e}")
            return []


class EmployeeRepDBDecorator:
    def __init__(self, db_repo: EmployeeRepDB):
        self._db_repo = db_repo

    def get_k_n_short_list(self, k: int, n: int, filter_func: callable = None, sort_field: str = None,
                           reverse: bool = False) -> List[Dict[str, Any]]:
        employees = self._db_repo.get_all_employees()

        if filter_func:
            employees = [emp for emp in employees if filter_func(emp)]

        if sort_field:
            valid_fields = ['employee_id', 'first_name', 'last_name', 'salary']
            if sort_field not in valid_fields:
                raise ValueError(f"Недопустимое поле для сортировки: {sort_field}")

            if sort_field == 'employee_id':
                employees.sort(key=lambda x: x.employee_id, reverse=reverse)
            elif sort_field == 'first_name':
                employees.sort(key=lambda x: x.first_name, reverse=reverse)
            elif sort_field == 'last_name':
                employees.sort(key=lambda x: x.last_name, reverse=reverse)
            elif sort_field == 'salary':
                employees.sort(key=lambda x: x.salary, reverse=reverse)

        offset = (n - 1) * k
        end_index = offset + k

        short_list = []
        for i in range(offset, min(end_index, len(employees))):
            employee = employees[i]
            short_list.append({
                'employee_id': employee.employee_id,
                'short_info': employee.short_info()
            })

        return short_list

    def get_count(self, filter_func: callable = None) -> int:
        employees = self._db_repo.get_all_employees()

        if filter_func:
            employees = [emp for emp in employees if filter_func(emp)]

        return len(employees)


class EmployeeRepFileDecorator:
    def __init__(self, file_repo: EmployeeRep):
        self._file_repo = file_repo

    def get_k_n_short_list(self, k: int, n: int, filter_func: callable = None, sort_field: str = None,
                           reverse: bool = False) -> List[Dict[str, Any]]:
        employees = self._file_repo.read_all()

        if filter_func:
            employees = [emp for emp in employees if filter_func(emp)]

        if sort_field:
            valid_fields = ['employee_id', 'first_name', 'last_name', 'salary']
            if sort_field not in valid_fields:
                raise ValueError(f"Недопустимое поле для сортировки: {sort_field}")

            if sort_field == 'employee_id':
                employees.sort(key=lambda x: x.employee_id, reverse=reverse)
            elif sort_field == 'first_name':
                employees.sort(key=lambda x: x.first_name, reverse=reverse)
            elif sort_field == 'last_name':
                employees.sort(key=lambda x: x.last_name, reverse=reverse)
            elif sort_field == 'salary':
                employees.sort(key=lambda x: x.salary, reverse=reverse)

        start_index = (n - 1) * k
        end_index = start_index + k

        if start_index >= len(employees):
            return []

        short_list = []
        for i in range(start_index, min(end_index, len(employees))):
            employee = employees[i]
            short_list.append({
                'employee_id': employee.employee_id,
                'short_info': employee.short_info()
            })

        return short_list

    def get_count(self, filter_func: callable = None) -> int:
        employees = self._file_repo.read_all()

        if filter_func:
            employees = [emp for emp in employees if filter_func(emp)]

        return len(employees)

from typing import List, Optional
from models import Employee


class EmployeeController:
    """Контроллер для операций с сотрудниками"""

    def __init__(self, repository):
        self.repository = repository

    def get_all_employees(self) -> List[Employee]:
        """Получение всех сотрудников"""
        try:
            count = self.repository.get_count()
            if count == 0:
                return []
            return self.repository.get_k_n_short_list(count, 1)
        except Exception as e:
            print(f"Error getting all employees: {e}")
            return []

    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Получение сотрудника по ID"""
        try:
            return self.repository.get_by_id(employee_id)
        except Exception as e:
            print(f"Error getting employee by ID: {e}")
            return None

    def get_employees_page(self, k: int, n: int) -> List[Employee]:
        """Получение страницы сотрудников"""
        try:
            return self.repository.get_k_n_short_list(k, n)
        except Exception as e:
            print(f"Error getting employees page: {e}")
            return []

    def get_employees_count(self) -> int:
        """Получение количества сотрудников"""
        try:
            return self.repository.get_count()
        except Exception as e:
            print(f"Error getting employees count: {e}")
            return 0

    def add_employee(self, first_name: str, last_name: str, salary: int,
                     passport: str, patronymic: Optional[str] = None) -> Employee:
        """Добавление нового сотрудника"""
        try:
            return self.repository.add_employee(
                first_name, last_name, salary, passport, patronymic
            )
        except Exception as e:
            print(f"Error adding employee: {e}")
            raise e

    def update_employee(self, employee_id: int, **kwargs) -> bool:
        """Обновление данных сотрудника"""
        try:
            return self.repository.update_employee(employee_id, **kwargs)
        except Exception as e:
            print(f"Error updating employee: {e}")
            raise e

    def delete_employee(self, employee_id: int) -> bool:
        """Удаление сотрудника"""
        try:
            return self.repository.delete_employee(employee_id)
        except Exception as e:
            print(f"Error deleting employee: {e}")
            raise e

    def validate_employee_data(self, first_name: str, last_name: str,
                               salary: int, passport: str,
                               patronymic: Optional[str] = None) -> dict:
        """Валидация данных сотрудника"""
        errors = {}

        if not first_name or not first_name.strip():
            errors['first_name'] = "Имя обязательно для заполнения"

        if not last_name or not last_name.strip():
            errors['last_name'] = "Фамилия обязательна для заполнения"

        try:
            salary_int = int(salary)
            if salary_int < 0:
                errors['salary'] = "Зарплата не может быть отрицательной"
        except (ValueError, TypeError):
            errors['salary'] = "Зарплата должна быть числом"

        if not passport or not passport.strip():
            errors['passport'] = "Паспорт обязателен для заполнения"

        return errors

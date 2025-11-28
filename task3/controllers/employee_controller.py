from typing import List, Optional
from models import Employee

class EmployeeController:
    """Контроллер для операций с сотрудниками (только чтение)"""
    
    def __init__(self, repository, observable_repository=None):
        self.repository = repository
        self.observable_repository = observable_repository
    
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
            # Используем observable репозиторий если доступен для уведомления о просмотре
            if self.observable_repository:
                return self.observable_repository.get_by_id(employee_id)
            else:
                return self.repository.get_by_id(employee_id)
        except Exception as e:
            print(f"Error getting employee by ID: {e}")
            return None
    
    def get_employees_count(self) -> int:
        """Получение количества сотрудников"""
        try:
            return self.repository.get_count()
        except Exception as e:
            print(f"Error getting employees count: {e}")
            return 0

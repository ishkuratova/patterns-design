from models.observer import EmployeeRepositorySubject
from models.reps import EmployeeRep

class ObservableEmployeeRepository(EmployeeRepositorySubject):
    """Декоратор репозитория с поддержкой паттерна Наблюдатель"""
    
    def __init__(self, repository: EmployeeRep):
        super().__init__()
        self._repository = repository
        # Уведомляем о первоначальной загрузке данных
        self.employee_loaded(self.get_all_employees())
    
    def get_by_id(self, employee_id: int):
        """Получение сотрудника по ID с уведомлением наблюдателей"""
        employee = self._repository.get_by_id(employee_id)
        if employee:
            self.employee_viewed({
                'employee_id': employee.employee_id,
                'full_name': employee.get_full_name()
            })
        return employee
    
    def get_k_n_short_list(self, k: int, n: int):
        """Получение страницы сотрудников"""
        return self._repository.get_k_n_short_list(k, n)
    
    def get_count(self):
        """Получение количества сотрудников"""
        return self._repository.get_count()
    
    def get_all_employees(self):
        """Получение всех сотрудников"""
        count = self.get_count()
        if count > 0:
            return self._repository.get_k_n_short_list(count, 1)
        return []
    
    def sort_by_field(self, field: str, reverse: bool = False):
        """Сортировка сотрудников"""
        return self._repository.sort_by_field(field, reverse)
    
    def save_data(self):
        """Сохранение данных"""
        self._repository.save_data()

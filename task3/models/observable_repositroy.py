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
    
    def add_employee(self, first_name: str, last_name: str, salary: int,
                    passport: str, patronymic: str = None):
        """Добавление сотрудника с уведомлением наблюдателей"""
        employee = self._repository.add_employee(
            first_name, last_name, salary, passport, patronymic
        )
        
        # Уведомляем наблюдателей о добавлении
        self.employee_added({
            'employee_id': employee.employee_id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'patronymic': employee.patronymic,
            'salary': employee.salary,
            'passport': employee.passport
        })
        
        return employee
    
    def update_employee(self, employee_id: int, **kwargs):
        """Обновление сотрудника с уведомлением наблюдателей"""
        success = self._repository.update_employee(employee_id, **kwargs)
        
        if success:
            # Получаем обновленные данные сотрудника
            employee = self._repository.get_by_id(employee_id)
            if employee:
                # Уведомляем наблюдателей об обновлении
                self.employee_updated({
                    'employee_id': employee.employee_id,
                    'first_name': employee.first_name,
                    'last_name': employee.last_name,
                    'patronymic': employee.patronymic,
                    'salary': employee.salary,
                    'passport': employee.passport,
                    'updated_fields': list(kwargs.keys())
                })
        
        return success
    
    def delete_employee(self, employee_id: int):
        """Удаление сотрудника с уведомлением наблюдателей"""
        success = self._repository.delete_employee(employee_id)
        
        if success:
            # Уведомляем наблюдателей об удалении
            self.employee_deleted(employee_id)
        
        return success
    
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

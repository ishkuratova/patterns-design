from abc import ABC, abstractmethod
from typing import List

class Subject(ABC):
    """Абстрактный класс Subject для паттерна Наблюдатель"""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: 'Observer') -> None:
        """Присоединяет наблюдателя к субъекту"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: 'Observer') -> None:
        """Отсоединяет наблюдателя от субъекта"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_type: str, data: dict = None) -> None:
        """Уведомляет всех наблюдателей о событии"""
        for observer in self._observers:
            observer.update(event_type, data)


class Observer(ABC):
    """Абстрактный класс Observer для паттерна Наблюдатель"""
    
    @abstractmethod
    def update(self, event_type: str, data: dict = None) -> None:
        """Метод для получения обновлений от субъекта"""
        pass


class EmployeeRepositorySubject(Subject):
    """Конкретный субъект для репозитория сотрудников"""
    
    def employee_loaded(self, employees_data: list) -> None:
        """Уведомляет о загрузке данных сотрудников"""
        self.notify('employees_loaded', {'count': len(employees_data)})
    
    def employee_viewed(self, employee_data: dict) -> None:
        """Уведомляет о просмотре сотрудника"""
        self.notify('employee_viewed', employee_data)
    
    def employee_added(self, employee_data: dict) -> None:
        """Уведомляет о добавлении сотрудника"""
        self.notify('employee_added', employee_data)
    
    def employee_updated(self, employee_data: dict) -> None:
        """Уведомляет об обновлении сотрудника"""
        self.notify('employee_updated', employee_data)
    
    def employee_deleted(self, employee_id: int) -> None:
        """Уведомляет об удалении сотрудника"""
        self.notify('employee_deleted', {'employee_id': employee_id})


class MainControllerObserver(Observer):
    """Наблюдатель для главного контроллера"""
    
    def __init__(self, main_controller):
        self.main_controller = main_controller
    
    def update(self, event_type: str, data: dict = None) -> None:
        """Обрабатывает обновления от репозитория"""
        print(f"Observer received event: {event_type} with data: {data}")
        
        if event_type == 'employees_loaded':
            self.main_controller.on_employees_loaded(data)
        elif event_type == 'employee_viewed':
            self.main_controller.on_employee_viewed(data)
        elif event_type == 'employee_added':
            self.main_controller.on_employee_added(data)
        elif event_type == 'employee_updated':
            self.main_controller.on_employee_updated(data)
        elif event_type == 'employee_deleted':
            self.main_controller.on_employee_deleted(data)

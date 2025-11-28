from flask import session
from .organization_controller import OrganizationController
from .employee_controller import EmployeeController
from models.observer import MainControllerObserver

class MainController:
    """Главный контроллер приложения"""
    
    def __init__(self):
        self.org_controller = OrganizationController()
        self._current_organization = None
        self._employee_controller = None
        self._observer = MainControllerObserver(self)
    
    def set_current_organization(self, organization_id):
        """Установка текущей организации"""
        if organization_id in self.org_controller.get_all_organizations():
            session['current_organization'] = organization_id
            self._current_organization = organization_id
            
            # Отписываемся от предыдущего репозитория
            if self._employee_controller and hasattr(self._employee_controller.observable_repository, 'detach'):
                self._employee_controller.observable_repository.detach(self._observer)
            
            repo = self.org_controller.get_repository(organization_id)
            observable_repo = self.org_controller.get_observable_repository(organization_id)
            
            # Подписываемся на уведомления от нового репозитория
            if observable_repo:
                observable_repo.attach(self._observer)
            
            self._employee_controller = EmployeeController(repo, observable_repo)
            return True
        return False
    
    def get_current_organization(self):
        """Получение текущей организации"""
        if not self._current_organization:
            org_id = session.get('current_organization')
            if org_id:
                self.set_current_organization(org_id)
        return self._current_organization
    
    def get_employee_controller(self):
        """Получение контроллера сотрудников для текущей организации"""
        if not self._employee_controller:
            current_org = self.get_current_organization()
            if not current_org:
                # Устанавливаем первую организацию по умолчанию
                orgs = self.org_controller.get_all_organizations()
                if orgs:
                    first_org = next(iter(orgs.keys()))
                    self.set_current_organization(first_org)
        return self._employee_controller
    
    def get_organizations_data(self):
        """Получение данных всех организаций"""
        return self.org_controller.get_all_organizations()
    
    def get_current_organization_name(self):
        """Получение названия текущей организации"""
        org_id = self.get_current_organization()
        return self.org_controller.get_organization_name(org_id) if org_id else None
    
    def on_employees_loaded(self, data):
        """Обработчик загрузки сотрудников"""
        print(f"Employees loaded: {data['count']} employees")
        # Можно добавить логирование, кэширование и т.д.
    
    def on_employee_viewed(self, data):
        """Обработчик просмотра сотрудника"""
        print(f"Employee viewed: {data['full_name']} (ID: {data['employee_id']})")
        # Можно добавить логирование активности, аналитику и т.д.

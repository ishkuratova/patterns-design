from flask import session
from .organization_controller import OrganizationController
from .employee_controller import EmployeeController


class MainController:
    """Главный контроллер приложения"""

    def __init__(self):
        self.org_controller = OrganizationController()
        self._current_organization = None
        self._employee_controller = None

    def set_current_organization(self, organization_id):
        """Установка текущей организации"""
        if organization_id in self.org_controller.get_all_organizations():
            session['current_organization'] = organization_id
            self._current_organization = organization_id

            repo = self.org_controller.get_repository(organization_id)
            self._employee_controller = EmployeeController(repo)
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

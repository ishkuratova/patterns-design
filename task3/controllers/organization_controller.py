from flask import current_app
from models.reps import EmployeeRepJson, EmployeeRepYaml, EmployeeRepDBAdapter


class OrganizationController:
    """Контроллер для управления организациями и их репозиториями"""

    def __init__(self):
        self.organizations = current_app.config['ORGANIZATIONS']
        self._repositories = {}
        self._initialize_repositories()

    def _initialize_repositories(self):
        """Инициализация репозиториев для всех организаций"""
        for org_id, org_config in self.organizations.items():
            repo = self._create_repository(org_id, org_config)
            self._repositories[org_id] = repo

    def _create_repository(self, org_id, org_config):
        """Создание репозитория по типу хранилища"""
        repo_type = org_config['type']

        if repo_type == 'json':
            return EmployeeRepJson(org_config['file_path'])
        elif repo_type == 'yaml':
            return EmployeeRepYaml(org_config['file_path'])
        elif repo_type == 'db':
            db_config = org_config['db_config']
            return EmployeeRepDBAdapter(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password']
            )
        else:
            raise ValueError(f"Unknown repository type: {repo_type}")

    def get_repository(self, organization_id):
        """Получение основного репозитория по ID организации"""
        return self._repositories.get(organization_id)

    def get_all_organizations(self):
        """Получение списка всех организаций"""
        return self.organizations

    def get_organization_name(self, organization_id):
        """Получение названия организации по ID"""
        org = self.organizations.get(organization_id)
        return org['name'] if org else None

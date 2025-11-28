import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # Database configuration
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'universitydb'
    DB_USER = 'postgres'
    DB_PASSWORD = '1234'

    # File paths
    JSON_FILE_PATH = 'data/google_employees.json'
    YAML_FILE_PATH = 'data/amazon_employees.yaml'

    # Organizations
    ORGANIZATIONS = {
        'google': {
            'name': 'Google',
            'type': 'json',
            'file_path': JSON_FILE_PATH
        },
        'amazon': {
            'name': 'Amazon',
            'type': 'yaml',
            'file_path': YAML_FILE_PATH
        },
        'netflix': {
            'name': 'Netflix',
            'type': 'db',
            'db_config': {
                'host': DB_HOST,
                'port': DB_PORT,
                'database': DB_NAME,
                'user': DB_USER,
                'password': DB_PASSWORD
            }
        }
    }

import json
import re

class Person:

    def __init__(self, first_name: str, last_name: str, patronymic: str | None = None):
        self._first_name = self.validate_name(first_name)
        self._last_name = self.validate_name(last_name)
        self._patronymic = self.validate_name(patronymic, True)

    @staticmethod
    def validate_name(value: str | None, is_patronymic: bool = False) -> str | None:
        if is_patronymic:
            if value is None:
                return None
            if not isinstance(value, str):
                raise ValueError("Patronymic must be None or a string")

            pattern = r'^[A-Za-zА-Яа-яЁё\- ]+$'
            if not re.match(pattern, value.strip()):
                raise ValueError("Name must contain only letters, hyphens and spaces")

            if len(value.strip()) == 0:
                return None
            return value.strip()
        else:
            if not isinstance(value, str):
                raise ValueError("Name must be a string")

            pattern = r'^[A-Za-zА-Яа-яЁё\- ]+$'
            if not re.match(pattern, value.strip()):
                raise ValueError("Name must contain only letters, hyphens and spaces")

            if len(value.strip()) == 0:
                raise ValueError("Name must be a non-empty string")
            return value.strip()

    @property
    def first_name(self) -> str:
        return self._first_name

    @first_name.setter
    def first_name(self, value: str):
        self._first_name = self.validate_name(value)

    @property
    def last_name(self) -> str:
        return self._last_name

    @last_name.setter
    def last_name(self, value: str):
        self._last_name = self.validate_name(value)

    @property
    def patronymic(self) -> str | None:
        return self._patronymic

    @patronymic.setter
    def patronymic(self, value: str | None):
        self._patronymic = self.validate_name(value, is_patronymic=True)

    def get_full_name(self) -> str:
        parts = [self._last_name, self._first_name]
        if self._patronymic:
            parts.append(self._patronymic)
        return " ".join(parts)

    def __str__(self) -> str:
        return f"Person: {self.get_full_name()}"

    def __repr__(self) -> str:
        return f"Person(first_name='{self._first_name}', last_name='{self._last_name}', patronymic='{self._patronymic}')"


class Employee(Person):

    def __init__(self, *args):
        if len(args) == 1:
            data = args[0]

            if isinstance(data, str):
                if data.strip().startswith('{') and data.strip().endswith('}'):
                    try:
                        data_dict = json.loads(data)
                        required_keys = ['employee_id', 'first_name', 'last_name', 'salary']
                        for key in required_keys:
                            if key not in data_dict:
                                raise ValueError(f"Missing required key in JSON: {key}")

                        try:
                            employee_id = int(data_dict['employee_id'])
                            first_name = data_dict['first_name']
                            last_name = data_dict['last_name']
                            patronymic = data_dict.get('patronymic')
                            salary = int(data_dict['salary'])
                            passport = data_dict.get('passport')
                        except (ValueError, TypeError) as e:
                            raise ValueError(f"Invalid data types in JSON: {e}")

                        super().__init__(first_name, last_name, patronymic)
                        self._employee_id = self.validate_employee_id(employee_id)
                        self._salary = self.validate_salary(salary)
                        self._passport = self.validate_passport(passport)

                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON format: {e}")
                else:
                    pattern = r'^\s*(\d+)\s*;\s*([^;]+)\s*;\s*([^;]+)\s*;\s*([^;]*)\s*;\s*(\d+)\s*;\s*([^;]*)\s*$'
                    match = re.match(pattern, data)
                    if not match:
                        raise ValueError(
                            "String must be in format: 'id;first_name;last_name;patronymic;salary;passport'")

                    try:
                        employee_id = int(match.group(1))
                        first_name = match.group(2).strip()
                        last_name = match.group(3).strip()
                        patronymic = match.group(4).strip() if match.group(4).strip() else None
                        salary = int(match.group(5))
                        passport = match.group(6).strip() if match.group(6).strip() else None
                    except ValueError as e:
                        raise ValueError(f"Invalid data format in string: {e}")

                    super().__init__(first_name, last_name, patronymic)
                    self._employee_id = self.validate_employee_id(employee_id)
                    self._salary = self.validate_salary(salary)
                    self._passport = self.validate_passport(passport)

            elif isinstance(data, list):
                if len(data) != 6:
                    raise ValueError("List must have exactly 6 elements")

                try:
                    employee_id = int(data[0])
                    first_name = str(data[1])
                    last_name = str(data[2])
                    patronymic = str(data[3]) if data[3] is not None else None
                    salary = int(data[4])
                    passport = str(data[5]) if data[5] is not None else None
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid data types in list: {e}")

                super().__init__(first_name, last_name, patronymic)
                self._employee_id = self.validate_employee_id(employee_id)
                self._salary = self.validate_salary(salary)
                self._passport = self.validate_passport(passport)

            elif isinstance(data, dict):
                required_keys = ['employee_id', 'first_name', 'last_name', 'salary']
                for key in required_keys:
                    if key not in data:
                        raise ValueError(f"Missing required key in dict: {key}")

                try:
                    employee_id = int(data['employee_id'])
                    first_name = data['first_name']
                    last_name = data['last_name']
                    patronymic = data.get('patronymic')
                    salary = int(data['salary'])
                    passport = data.get('passport')
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid data types in dict: {e}")

                super().__init__(first_name, last_name, patronymic)
                self._employee_id = self.validate_employee_id(employee_id)
                self._salary = self.validate_salary(salary)
                self._passport = self.validate_passport(passport)

            else:
                raise ValueError("Unsupported data type for single argument")

        elif len(args) == 6:
            employee_id, first_name, last_name, patronymic, salary, passport = args
            super().__init__(first_name, last_name, patronymic)
            self._employee_id = self.validate_employee_id(employee_id)
            self._salary = self.validate_salary(salary)
            self._passport = self.validate_passport(passport)

        else:
            raise ValueError("Invalid number of arguments")

    @staticmethod
    def validate_employee_id(employee_id: int) -> int:
        if not isinstance(employee_id, int) or employee_id <= 0:
            raise ValueError("Employee ID must be a positive integer")
        return employee_id

    @staticmethod
    def validate_salary(salary: int) -> int:
        if not isinstance(salary, int) or salary < 0:
            raise ValueError("Salary must be a non-negative integer")
        return salary

    @staticmethod
    def validate_passport(passport: str) -> str:
        if passport is None:
            raise ValueError("Passport cannot be None")

        if not isinstance(passport, str):
            raise ValueError("Passport must be a string")

        passport = passport.strip()

        # Проверка формата: "1234123456" или "1234 123456"
        pattern1 = r'^\d{10}$'  # 1234123456
        pattern2 = r'^\d{4}\s\d{6}$'  # 1234 123456

        if re.match(pattern1, passport):
            return passport
        elif re.match(pattern2, passport):
            # Убираем пробел и приводим к формату 1234123456
            return passport.replace(' ', '')
        else:
            raise ValueError("Passport must be in format '1234123456' or '1234 123456'")

    @property
    def employee_id(self) -> int:
        return self._employee_id

    @property
    def salary(self) -> int:
        return self._salary

    @salary.setter
    def salary(self, value: int):
        self._salary = self.validate_salary(value)

    @property
    def passport(self) -> str:
        return self._passport

    @passport.setter
    def passport(self, value: str):
        self._passport = self.validate_passport(value)

    def __str__(self) -> str:
        return f"Employee {self.employee_id}: {self.get_full_name()}, Salary: {self._salary}, Passport: {self._passport}"

    def __repr__(self) -> str:
        return (f"Employee(employee_id={self._employee_id}, first_name='{self._first_name}', "
                f"last_name='{self._last_name}', patronymic='{self._patronymic}', salary={self._salary}, "
                f"passport='{self._passport}')")

    def short_info(self) -> str:
        return f"ID: {self._employee_id}, Salary: {self._salary}, Passport: {self._passport}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Employee):
            return False

        return self._passport == other._passport

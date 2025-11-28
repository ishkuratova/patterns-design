from flask import Flask, render_template, request, jsonify, redirect, url_for, flash


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.secret_key = app.config['SECRET_KEY']

    # Инициализация главного контроллера будет происходить в контексте приложения
    main_controller = None

    def get_main_controller():
        nonlocal main_controller
        if main_controller is None:
            from controllers.main_controller import MainController
            main_controller = MainController()
        return main_controller

    @app.context_processor
    def inject_globals():
        """Добавление глобальных переменных в контекст шаблонов"""
        controller = get_main_controller()
        return {
            'current_organization': controller.get_current_organization(),
            'current_organization_name': controller.get_current_organization_name()
        }

    @app.route('/')
    def index():
        """Главная страница со списком сотрудников"""
        controller = get_main_controller()
        employee_controller = controller.get_employee_controller()

        if not employee_controller:
            flash('Пожалуйста, выберите организацию', 'warning')
            return redirect(url_for('organizations'))

        # Получаем ВСЕХ сотрудников для отображения
        employees = employee_controller.get_all_employees()

        return render_template('index.html', employees=employees)

    @app.route('/organizations')
    def organizations():
        """Страница выбора организации"""
        controller = get_main_controller()
        organizations_data = controller.get_organizations_data()
        return render_template('organizations.html', organizations=organizations_data)

    @app.route('/set_organization', methods=['POST'])
    def set_organization():
        """Установка текущей организации"""
        controller = get_main_controller()
        organization_id = request.form.get('organization_id')
        if controller.set_current_organization(organization_id):
            flash(f'Организация изменена на {controller.get_current_organization_name()}', 'success')
        else:
            flash('Ошибка при выборе организации', 'error')
        return redirect(url_for('index'))

    @app.route('/employee/<int:employee_id>')
    def get_employee(employee_id):
        """Получение детальной информации о сотруднике"""
        controller = get_main_controller()
        employee_controller = controller.get_employee_controller()

        if not employee_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))

        employee = employee_controller.get_employee_by_id(employee_id)

        if employee:
            return render_template('employee_detail.html', employee=employee)
        else:
            flash('Сотрудник не найден', 'error')
            return redirect(url_for('index'))

    @app.route('/employee/form')
    def employee_form():
        """Форма добавления сотрудника"""
        controller = get_main_controller()
        employee_controller = controller.get_employee_controller()

        if not employee_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))

        return render_template('employee_form.html',
                               employee=None,
                               title="Добавить сотрудника",
                               errors=None)

    @app.route('/employee/form/<int:employee_id>')
    def employee_form_edit(employee_id):
        """Форма редактирования сотрудника"""
        controller = get_main_controller()
        employee_controller = controller.get_employee_controller()

        if not employee_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))

        employee = employee_controller.get_employee_by_id(employee_id)

        if employee:
            return render_template('employee_form.html',
                                   employee=employee,
                                   title="Редактировать сотрудника",
                                   errors=None)
        else:
            flash('Сотрудник не найден', 'error')
            return redirect(url_for('index'))

    @app.route('/employee', methods=['POST'])
    def add_employee():
        """Добавление нового сотрудника"""
        controller = get_main_controller()
        employee_controller = controller.get_employee_controller()

        if not employee_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        patronymic = request.form.get('patronymic')
        salary = request.form.get('salary')
        passport = request.form.get('passport')

        # Валидация данных
        errors = employee_controller.validate_employee_data(
            first_name, last_name, salary, passport, patronymic
        )

        if errors:
            return render_template('employee_form.html',
                                   employee=None,
                                   title="Добавить сотрудника",
                                   errors=errors)

        try:
            employee = employee_controller.add_employee(
                first_name, last_name, int(salary), passport,
                patronymic if patronymic else None
            )
            flash('Сотрудник успешно добавлен', 'success')
            return redirect(url_for('index'))
        except ValueError as e:
            flash(f'Ошибка при добавлении сотрудника: {str(e)}', 'error')
            return render_template('employee_form.html',
                                   employee=None,
                                   title="Добавить сотрудника",
                                   errors={'passport': str(e)})
        except Exception as e:
            flash(f'Внутренняя ошибка: {str(e)}', 'error')
            return render_template('employee_form.html',
                                   employee=None,
                                   title="Добавить сотрудника",
                                   errors={})

    @app.route('/employee/<int:employee_id>', methods=['POST'])
    def update_employee(employee_id):
        """Обновление данных сотрудника"""
        controller = get_main_controller()
        employee_controller = controller.get_employee_controller()

        if not employee_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        patronymic = request.form.get('patronymic')
        salary = request.form.get('salary')
        passport = request.form.get('passport')

        # Валидация данных
        errors = employee_controller.validate_employee_data(
            first_name, last_name, salary, passport, patronymic
        )

        employee = employee_controller.get_employee_by_id(employee_id)
        if not employee:
            flash('Сотрудник не найден', 'error')
            return redirect(url_for('index'))

        if errors:
            return render_template('employee_form.html',
                                   employee=employee,
                                   title="Редактировать сотрудника",
                                   errors=errors)

        update_data = {
            'first_name': first_name,
            'last_name': last_name,
            'patronymic': patronymic if patronymic else None,
            'salary': int(salary),
            'passport': passport
        }

        try:
            success = employee_controller.update_employee(employee_id, **update_data)
            if success:
                flash('Данные сотрудника успешно обновлены', 'success')
                return redirect(url_for('index'))
            else:
                flash('Сотрудник не найден', 'error')
                return redirect(url_for('index'))
        except ValueError as e:
            flash(f'Ошибка при обновлении сотрудника: {str(e)}', 'error')
            return render_template('employee_form.html',
                                   employee=employee,
                                   title="Редактировать сотрудника",
                                   errors={'passport': str(e)})
        except Exception as e:
            flash(f'Внутренняя ошибка: {str(e)}', 'error')
            return render_template('employee_form.html',
                                   employee=employee,
                                   title="Редактировать сотрудника",
                                   errors={})

    @app.route('/employee/<int:employee_id>/delete', methods=['POST'])
    def delete_employee(employee_id):
        """Удаление сотрудника"""
        controller = get_main_controller()
        employee_controller = controller.get_employee_controller()

        if not employee_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))

        try:
            success = employee_controller.delete_employee(employee_id)
            if success:
                flash('Сотрудник успешно удален', 'success')
            else:
                flash('Сотрудник не найден', 'error')
        except Exception as e:
            flash(f'Ошибка при удалении сотрудника: {str(e)}', 'error')

        return redirect(url_for('index'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

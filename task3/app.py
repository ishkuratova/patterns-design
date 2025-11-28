from flask import Flask, render_template, request, redirect, url_for, flash

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
        
        # Получаем всех сотрудников для отображения
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
    
    @app.route('/employee/add', methods=['GET'])
    def add_employee_form():
        """Форма добавления сотрудника"""
        controller = get_main_controller()
        form_controller = controller.get_employee_form_controller()
        
        if not form_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))
        
        return form_controller.get_add_form()
    
    @app.route('/employee/add', methods=['POST'])
    def add_employee():
        """Добавление нового сотрудника"""
        controller = get_main_controller()
        form_controller = controller.get_employee_form_controller()
        
        if not form_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))
        
        return form_controller.handle_add_employee()
    
    @app.route('/employee/<int:employee_id>/edit', methods=['GET'])
    def edit_employee_form(employee_id):
        """Форма редактирования сотрудника"""
        controller = get_main_controller()
        form_controller = controller.get_employee_form_controller()
        
        if not form_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))
        
        return form_controller.get_edit_form(employee_id)
    
    @app.route('/employee/<int:employee_id>/edit', methods=['POST'])
    def edit_employee(employee_id):
        """Обновление данных сотрудника"""
        controller = get_main_controller()
        form_controller = controller.get_employee_form_controller()
        
        if not form_controller:
            flash('Организация не выбрана', 'error')
            return redirect(url_for('organizations'))
        
        return form_controller.handle_edit_employee(employee_id)
    
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

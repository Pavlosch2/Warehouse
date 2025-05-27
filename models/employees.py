import json
import os

class Employee:
    employees = []
    __users_data_file = os.path.join(os.path.dirname(__file__), "users.json")

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname
        self.disciplinary_records = []
        self.orders = []
        self.role = "Працівник"
        self.salary = 0
        self.bonus = 0
        self.username = None
        self.password = None
        self.id = None

    def get_name(self):
        return self.name

    def get_surname(self):
        return self.surname

    def save_to_json(self):
        employees_data = {}
        for emp in Employee.employees:
            emp_data = {
                "id": emp.id,
                "name": emp.name,
                "surname": emp.surname,
                "disciplinary_records": emp.disciplinary_records,
                "orders": emp.orders,
                "username": emp.username,
                "password": emp.password,
                "role": emp.role,
                "salary": emp.salary,
                "bonus": emp.bonus
            }
            employees_data[emp.id] = emp_data
        with open(Employee.__users_data_file, "w", encoding="utf-8") as f:
            json.dump(employees_data, f, ensure_ascii=False, indent=4)

    @classmethod
    def load_employees(cls):
        Employee.employees.clear()
        try:
            if os.path.exists(cls.__users_data_file):
                with open(cls.__users_data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        print(f"Помилка: users.json містить {type(data)}, очікується словник. Повертаємо порожній список.")
                        return
                    for emp_id, emp_data in data.items():
                        if emp_data["role"] == "Складський працівник":
                            emp = WarehouseWorker(emp_data["name"], emp_data["surname"], emp_data["salary"])
                        elif emp_data["role"] == "Менеджер":
                            emp = Manager(emp_data["name"], emp_data["surname"], emp_data["salary"])
                            emp.bonus = emp_data["bonus"]
                        elif emp_data["role"] == "Адміністратор":
                            emp = Admin(emp_data["name"], emp_data["surname"])
                        else:
                            emp = Employee(emp_data["name"], emp_data["surname"])
                        emp.id = emp_id
                        emp.disciplinary_records = emp_data["disciplinary_records"]
                        emp.orders = emp_data["orders"]
                        emp.username = emp_data["username"]
                        emp.password = emp_data["password"]
                        emp.role = emp_data["role"]
                        emp.salary = emp_data["salary"]
                        emp.bonus = emp_data["bonus"]
                        Employee.employees.append(emp)
            else:
                print(f"Файл {cls.__users_data_file} не існує. Повертаємо порожній список.")
        except json.JSONDecodeError as e:
            print(f"Помилка декодування JSON у users.json: {e}. Повертаємо порожній список.")
        except Exception as e:
            print(f"Невідома помилка при завантаженні users.json: {e}. Повертаємо порожній список.")

    @classmethod
    def get_all_employees(cls):
        return cls.employees

class WarehouseWorker(Employee):
    def __init__(self, name, surname, salary):
        super().__init__(name, surname)
        self.role = "Складський працівник"
        self.salary = salary if salary else 0

class Manager(Employee):
    def __init__(self, name, surname, salary):
        super().__init__(name, surname)
        self.role = "Менеджер"
        self.salary = salary if salary else 0
        self.bonus = 0

    def manager_update_order_status(self, order, new_status):
        if order.set_status(new_status):
            return f"Статус замовлення {order.get_id()} оновлено на {new_status}."
        return "Неправильний статус замовлення."

class Admin(Employee):
    def __init__(self, name, surname):
        super().__init__(name, surname)
        self.role = "Адміністратор"

    def add_employee(self, employee):
        for emp in Employee.employees:
            if emp.id == employee.id:
                return "Працівник із таким ID уже існує."
        Employee.employees.append(employee)
        employee.save_to_json()
        return f"Працівник {employee.get_name()} {employee.get_surname()} додано."

    def remove_employee(self, employee):
        if employee in Employee.employees:
            Employee.employees.remove(employee)
            employee.save_to_json()
            return f"Працівник {employee.get_name()} {employee.get_surname()} видалений."
        return "Працівник не знайдений."

    def impose_disciplinary_record(self, employee, record):
        if employee in Employee.employees:
            employee.disciplinary_records.append(record)
            employee.save_to_json()
            return f"Стягнення '{record}' накладено на {employee.get_name()} {employee.get_surname()}."
        return "Працівник не знайдений."

    def change_salary(self, employee, new_salary):
        if employee in Employee.employees and isinstance(employee, (WarehouseWorker, Manager)):
            employee.salary = new_salary
            employee.save_to_json()
            return f"Зарплата для {employee.get_name()} {employee.get_surname()} змінена на {new_salary}."
        return "Неможливо змінити зарплату для цього працівника."

    def change_bonus(self, manager, new_bonus):
        if employee in Employee.employees and isinstance(employee, Manager):
            manager.bonus = new_bonus
            employee.save_to_json()
            return f"Бонус для {manager.get_name()} {manager.get_surname()} змінений на {new_bonus}."
        return "Неможливо змінити бонус для цього працівника."

    def assign_order(self, employee, order):
        if employee in Employee.employees and isinstance(employee, (WarehouseWorker, Manager)):
            employee.orders.append(order.get_id())
            employee.save_to_json()
            return f"Замовлення {order.get_id()} призначено {employee.get_name()} {employee.get_surname()}."
        return "Неможливо призначити замовлення цьому працівнику."

    def cancel_order(self, order):
        for emp in Employee.employees:
            if order.get_id() in emp.orders:
                emp.orders.remove(order.get_id())
                emp.save_to_json()
                return f"Замовлення {order.get_id()} скасовано для {emp.get_name()} {emp.get_surname()}."
        return "Замовлення не знайдено."
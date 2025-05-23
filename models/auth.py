from models.employees import Employee
from models.logger import log_action

class AuthSystem:
    def __init__(self):
        log_action("Система авторизації ініціалізована.")

    def authenticate(self, username, password):
        for emp in Employee.get_all_employees():
            if emp.username == username and emp.password == password:
                log_action(f"Успішна автентифікація для {username}, роль: {emp.role}.")
                return {"success": True, "role": emp.role}
        log_action(f"Неуспішна автентифікація для {username}.")
        return {"success": False, "message": "Неправильний логін або пароль"}
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from models.auth import AuthSystem
from models.logger import log_login
from models.inventory import Good, Order
from models.employees import Employee, WarehouseWorker, Manager, Admin
import os
import json

class WarehouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Складська система")
        self.geometry("1200x800")
        self.minsize(700, 600)
        self.configure(bg="#2b2b2b")

        Employee.load_employees()
        self.auth = AuthSystem()
        self.current_user = None
        self.current_role = None
        self.current_admin = None
        self.orders = self.load_orders_from_json()
        print(f"Завантажено {len(self.orders)} замовлень при запуску програми")

        self.create_ui()

    def create_ui(self):
        self.title("Складська система - Логування")
        self.login_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.login_frame.pack(expand=True, fill="both")

        login_form = ctk.CTkFrame(self.login_frame, fg_color="#1c2526", corner_radius=10)
        login_form.pack(expand=True, pady=50)

        ctk.CTkLabel(login_form, text="Складська система", font=("Arial", 24), text_color="#ffd700").pack(pady=20)
        ctk.CTkLabel(login_form, text="Логін:", text_color="#ffd700").pack(pady=5)
        self.username_entry = ctk.CTkEntry(login_form, width=250, fg_color="#2b2b2b", text_color="#ffd700")
        self.username_entry.pack(pady=5)
        ctk.CTkLabel(login_form, text="Пароль:", text_color="#ffd700").pack(pady=5)
        self.password_entry = ctk.CTkEntry(login_form, width=250, show="*", fg_color="#2b2b2b", text_color="#ffd700")
        self.password_entry.pack(pady=5)
        ctk.CTkButton(login_form, text="Увійти", command=self.login, fg_color="#ffd700", font=("Arial", 14, "bold"), hover_color="#e6c200", text_color="#1c2526").pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        result = self.auth.authenticate(username, password)
        if result["success"]:
            log_login(username, result["role"])
            self.current_user = username
            self.current_role = result["role"]
            print(f"User logged in: {username}, role: {result['role']}")
            if result["role"] == "Адміністратор":
                print(f"Завантажені працівники: {[emp.id for emp in Employee.get_all_employees()]}")
                for emp in Employee.get_all_employees():
                    if emp.id.lower() == "pavlo_petrenko_3".lower() and isinstance(emp, Admin):
                        self.current_admin = emp
                        print(f"Знайдено адміністратора: {emp.id}")
                        break
                if not self.current_admin:
                    print("Адміністратор не знайдений, створюємо нового.")
                    self.current_admin = Admin("Павло", "Петренко")
                    self.current_admin.id = "pavlo_petrenko_3"
                    self.current_admin.username = username
                    self.current_admin.password = password
                    self.current_admin.role = "Адміністратор"
                    self.current_admin.save_to_json()
            CTkMessagebox(title="Успіх", message=f"Вхід виконано. Роль: {result['role']}", icon="check")
            self.login_frame.pack_forget()
            self.open_main_window(result["role"])
        else:
            CTkMessagebox(title="Помилка", message=result["message"], icon="cancel")

    def open_main_window(self, role):
        self.title("Складська система - Welcome")
        if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
            self.main_frame.pack_forget()
        self.main_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.main_frame.pack(expand=True, fill="both")

        ctk.CTkLabel(self.main_frame, text=f"Ласкаво просимо, {role}!", font=("Arial", 20), text_color="#ffd700").pack(pady=20)
        menu = ctk.CTkFrame(self.main_frame, fg_color="#333333")
        menu.pack(fill="x", padx=10, pady=10)
        if role == "Адміністратор":
            ctk.CTkButton(menu, text="Управління працівниками", command=self.open_employee_panel, fg_color="#ffd700",
                          text_color='black', font=("Arial", 14, "bold"), hover_color="#e6c200").pack(side="left", padx=5)
            ctk.CTkButton(menu, text="Управління товарами", command=self.open_goods_panel, fg_color="#ffd700",
                          text_color='black', font=("Arial", 14, "bold"), hover_color="#e6c200").pack(side="left", padx=5)
            ctk.CTkButton(menu, text="Управління замовленнями", command=self.open_order_panel, fg_color="#ffd700",
                          text_color='black', font=("Arial", 14, "bold"), hover_color="#e6c200").pack(side="left", padx=5)
        elif role in ["Менеджер", "Складський працівник"]:
            ctk.CTkButton(menu, text="Управління товарами", command=self.open_goods_panel, fg_color="#ffd700",
                          text_color='black', font=("Arial", 14, "bold"), hover_color="#e6c200").pack(side="left", padx=5)
            ctk.CTkButton(menu, text="Управління замовленнями", command=self.open_order_panel, fg_color="#ffd700",
                          text_color='black', font=("Arial", 14, "bold"),  hover_color="#e6c200").pack(side="left", padx=5)
        ctk.CTkButton(menu, text="Вихід", command=self.quit, fg_color="#ffd700",
                      text_color='black', font=("Arial", 14, "bold"), hover_color="#e6c200").pack(side="right", padx=5)

    def open_employee_panel(self):
        self.title("Складська система - Управління працівниками")
        if hasattr(self, 'employee_frame') and self.employee_frame.winfo_exists():
            self.employee_frame.pack_forget()
        self.employee_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.employee_frame.pack(expand=True, fill="both")

        ctk.CTkLabel(self.employee_frame, text="Управління працівниками", font=("Arial", 20), text_color="#ffd700").pack(pady=10)
        if self.current_role == "Адміністратор":
            ctk.CTkButton(self.employee_frame, text="Додати працівника", command=self.add_employee, fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(pady=5)

        filter_frame = ctk.CTkFrame(self.employee_frame, fg_color="#333333")
        filter_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(filter_frame, text="Фільтр за роллю:", text_color="#ffd700").pack(side="left", padx=5)
        role_option = ctk.CTkOptionMenu(filter_frame, values=["Усі", "Адміністратор", "Менеджер", "Складський працівник"], command=lambda _: self.update_employee_display(role_option.get(), sort_option.get(), sort_order.get(), search_entry.get()), fg_color="#1c2526", text_color="#ffd700")
        role_option.pack(side="left", padx=5)
        role_option.set("Усі")
        ctk.CTkLabel(filter_frame, text="Сортувати за:", text_color="#ffd700").pack(side="left", padx=5)
        sort_option = ctk.CTkOptionMenu(filter_frame, values=["За ім'ям", "За зарплатою"], command=lambda _: self.update_employee_display(role_option.get(), sort_option.get(), sort_order.get(), search_entry.get()), fg_color="#1c2526", text_color="#ffd700")
        sort_option.pack(side="left", padx=5)
        sort_option.set("За ім'ям")
        ctk.CTkLabel(filter_frame, text="Порядок:", text_color="#ffd700").pack(side="left", padx=5)
        sort_order = ctk.CTkOptionMenu(filter_frame, values=["Зростання", "Спадання"], command=lambda _: self.update_employee_display(role_option.get(), sort_option.get(), sort_order.get(), search_entry.get()), fg_color="#1c2526", text_color="#ffd700")
        sort_order.pack(side="left", padx=5)
        sort_order.set("Зростання")
        ctk.CTkLabel(filter_frame, text="Пошук:", text_color="#ffd700").pack(side="left", padx=5)
        search_entry = ctk.CTkEntry(filter_frame, width=200, fg_color="#1c2526", text_color="#ffd700")
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda event: self.update_employee_display(role_option.get(), sort_option.get(), sort_order.get(), search_entry.get()))

        self.employee_scroll = ctk.CTkScrollableFrame(self.employee_frame, fg_color="#1c2526", height=500)
        self.employee_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_employee_display(role_option.get(), sort_option.get(), sort_order.get())

        ctk.CTkButton(self.employee_frame, text="Повернутися", command=self.return_to_main, fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack()

    def update_employee_display(self, filter_role="Усі", sort_by="За ім'ям", sort_order="Зростання", search_query=""):
        for widget in self.employee_scroll.winfo_children():
            widget.destroy()

        employees = Employee.get_all_employees()
        seen_ids = set()
        filtered_employees = []
        for emp in employees:
            if emp.id in seen_ids:
                continue
            seen_ids.add(emp.id)
            filtered_employees.append(emp)

        if filter_role != "Усі":
            filtered_employees = [emp for emp in filtered_employees if emp.role == filter_role]

        if search_query:
            filtered_employees = [
                emp for emp in filtered_employees
                if search_query.lower() in emp.get_name().lower() or search_query.lower() in emp.get_surname().lower()]

        reverse = (sort_order == "Спадання")
        if sort_by == "За ім'ям":
            sorted_employees = sorted(filtered_employees, key=lambda emp: emp.get_name().lower(), reverse=reverse)
        elif sort_by == "За зарплатою":
            sorted_employees = sorted(filtered_employees, key=lambda emp: getattr(emp, 'salary', 0), reverse=reverse)
        else:
            sorted_employees = filtered_employees

        print(f"Displaying {len(sorted_employees)} employees in update_employee_display")
        for emp in sorted_employees:
            emp_frame = ctk.CTkFrame(self.employee_scroll, fg_color="#333333", corner_radius=5)
            emp_frame.pack(fill="x", pady=5, padx=5)
            info_text = (f"ID: {emp.id}\nІм'я: {emp.get_name()} {emp.get_surname()}\nРоль: {emp.role}\n"
                         f"Зарплата: {getattr(emp, 'salary', 0)}\nБонус: {getattr(emp, 'bonus', 0)}\n"
                         f"Стягнення: {emp.disciplinary_records}\nЗамовлення: {emp.orders}")
            ctk.CTkLabel(emp_frame, text=info_text, text_color="#ffd700", anchor="w", wraplength=1400, font=("Arial", 12), justify="left").pack(side="left", padx=10)
            if emp.id != (self.current_admin.id if self.current_admin else "") and self.current_role == "Адміністратор":
                ctk.CTkButton(emp_frame, text="Видалити", command=lambda e=emp: self.remove_employee(e), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)
            ctk.CTkButton(emp_frame, text="Накласти стягнення", command=lambda e=emp: self.impose_record(e), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)
            if isinstance(emp, (WarehouseWorker, Manager)):
                ctk.CTkButton(emp_frame, text="Змінити зарплату", command=lambda e=emp: self.change_salary(e), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)
            if isinstance(emp, Manager):
                ctk.CTkButton(emp_frame, text="Змінити бонус", command=lambda e=emp: self.change_bonus(e), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)

    def add_employee(self):
        if self.current_role != "Адміністратор":
            return
        dialog = ctk.CTkToplevel(self)
        dialog.focus()
        dialog.lift()
        dialog.grab_set()
        dialog.title("Додати працівника")
        dialog.geometry("400x500")
        dialog.configure(fg_color="#2b2b2b")
        dialog.resizable(False, False)
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color="#2b2b2b", height=400)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(scroll_frame, text="Ім'я:", text_color="#ffd700").pack(pady=5)
        name_entry = ctk.CTkEntry(scroll_frame, width=300, fg_color="#1c2526", text_color="#ffd700")
        name_entry.pack(pady=5)
        ctk.CTkLabel(scroll_frame, text="Прізвище:", text_color="#ffd700").pack(pady=5)
        surname_entry = ctk.CTkEntry(scroll_frame, width=300, fg_color="#1c2526", text_color="#ffd700")
        surname_entry.pack(pady=5)
        ctk.CTkLabel(scroll_frame, text="Роль:", text_color="#ffd700").pack(pady=5)
        role_var = ctk.StringVar(value="Складський працівник")
        role_menu = ctk.CTkOptionMenu(scroll_frame, values=["Складський працівник", "Менеджер"], variable=role_var, fg_color="#1c2526", text_color="#ffd700")
        role_menu.pack(pady=5)
        ctk.CTkLabel(scroll_frame, text="Зарплата:", text_color="#ffd700").pack(pady=5)
        salary_entry = ctk.CTkEntry(scroll_frame, width=300, fg_color="#1c2526", text_color="#ffd700")
        salary_entry.pack(pady=5)
        ctk.CTkLabel(scroll_frame, text="Бонус (для менеджера):", text_color="#ffd700").pack(pady=5)
        bonus_entry = ctk.CTkEntry(scroll_frame, width=300, fg_color="#1c2526", text_color="#ffd700")
        bonus_entry.pack(pady=5)
        ctk.CTkLabel(scroll_frame, text="Логін:", text_color="#ffd700").pack(pady=5)
        username_entry = ctk.CTkEntry(scroll_frame, width=300, fg_color="#1c2526", text_color="#ffd700")
        username_entry.pack(pady=5)
        ctk.CTkLabel(scroll_frame, text="Пароль:", text_color="#ffd700").pack(pady=5)
        password_entry = ctk.CTkEntry(scroll_frame, width=300, fg_color="#1c2526", text_color="#ffd700")
        password_entry.pack(pady=5)
        def submit_employee():
            name = name_entry.get().strip()
            surname = surname_entry.get().strip()
            role = role_var.get()
            salary = salary_entry.get().strip()
            bonus = bonus_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            if not name or not surname or not username or not password:
                CTkMessagebox(title="Помилка", message="Заповніть усі обов'язкові поля (ім'я, прізвище, логін, пароль)!", icon="cancel")
                return
            if not salary or not salary.replace('.', '').isdigit():
                salary = 0
            else:
                salary = float(salary)
            if role == "Менеджер":
                new_employee = Manager(name, surname, salary)
                bonus = float(bonus) if bonus and bonus.replace('.', '').isdigit() else 0
                new_employee.bonus = bonus
            else:
                new_employee = WarehouseWorker(name, surname, salary)
            new_employee.username = username
            new_employee.password = password
            new_employee.role = role
            result = self.current_admin.add_employee(new_employee)
            CTkMessagebox(title="Результат", message=result, icon="check")
            dialog.grab_release()
            dialog.after(100, lambda: [dialog.destroy(), self.open_employee_panel()])
        ctk.CTkButton(dialog, text="Підтвердити", command=submit_employee, fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(pady=10)

    def remove_employee(self, employee):
        if self.current_role == "Адміністратор":
            result = self.current_admin.remove_employee(employee)
            CTkMessagebox(title="Результат", message=result, icon="check")
            self.open_employee_panel()

    def impose_record(self, employee):
        if self.current_role == "Адміністратор":
            dialog = ctk.CTkToplevel(self)
            dialog.focus()
            dialog.lift()
            dialog.grab_set()
            dialog.title("Стягнення")
            dialog.geometry("400x200")
            dialog.configure(fg_color="#2b2b2b")
            dialog.resizable(False, False)
            ctk.CTkLabel(dialog, text="Введіть причину стягнення:", text_color="#ffd700").pack(pady=10)
            record_entry = ctk.CTkEntry(dialog, width=300, fg_color="#1c2526", text_color="#ffd700")
            record_entry.pack(pady=10)
            def submit_record(emp):
                record = record_entry.get()
                if record:
                    result = self.current_admin.impose_disciplinary_record(emp, record)
                    CTkMessagebox(title="Результат", message=result, icon="check")
                    dialog.destroy()
                    self.open_employee_panel()
            ctk.CTkButton(dialog, text="Підтвердити", command=lambda: submit_record(employee), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(pady=10)

    def change_salary(self, employee):
        if self.current_role == "Адміністратор":
            dialog = ctk.CTkToplevel(self)
            dialog.focus()
            dialog.lift()
            dialog.grab_set()
            dialog.title("Зміна зарплати")
            dialog.geometry("400x200")
            dialog.configure(fg_color="#2b2b2b")
            dialog.resizable(False, False)
            ctk.CTkLabel(dialog, text="Введіть нову зарплату:", text_color="#ffd700").pack(pady=10)
            salary_entry = ctk.CTkEntry(dialog, width=300, fg_color="#1c2526", text_color="#ffd700")
            salary_entry.pack(pady=10)
            def submit_salary(emp):
                new_salary = salary_entry.get()
                if new_salary and new_salary.replace('.', '').isdigit():
                    result = self.current_admin.change_salary(emp, float(new_salary))
                    CTkMessagebox(title="Результат", message=result, icon="check")
                    dialog.destroy()
                    self.open_employee_panel()
            ctk.CTkButton(dialog, text="Підтвердити", command=lambda: submit_salary(employee), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(pady=10)

    def change_bonus(self, manager):
        if self.current_role == "Адміністратор" and isinstance(manager, Manager):
            dialog = ctk.CTkToplevel(self)
            dialog.focus()
            dialog.lift()
            dialog.grab_set()
            dialog.title("Зміна бонусу")
            dialog.geometry("400x200")
            dialog.configure(fg_color="#2b2b2b")
            dialog.resizable(False, False)
            ctk.CTkLabel(dialog, text="Введіть новий бонус:", text_color="#ffd700").pack(pady=10)
            bonus_entry = ctk.CTkEntry(dialog, width=300, fg_color="#1c2526", text_color="#ffd700")
            bonus_entry.pack(pady=10)
            def submit_bonus(mgr):
                new_bonus = bonus_entry.get()
                if new_bonus and new_bonus.replace('.', '').isdigit():
                    result = self.current_admin.change_bonus(mgr, float(new_bonus))
                    CTkMessagebox(title="Результат", message=result, icon="check")
                    dialog.destroy()
                    self.open_employee_panel()
            ctk.CTkButton(dialog, text="Підтвердити", command=lambda: submit_bonus(manager), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(pady=10)

    def open_goods_panel(self):
        self.title("Складська система - Управління товарами")
        if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
            self.main_frame.pack_forget()
        if hasattr(self, 'goods_frame') and self.goods_frame.winfo_exists():
            for widget in self.goods_frame.winfo_children():
                widget.destroy()
        else:
            self.goods_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.goods_frame.pack(expand=True, fill="both")

        ctk.CTkLabel(self.goods_frame, text="Управління товарами", font=("Arial", 20), text_color="#ffd700").pack(pady=10)

        filter_frame = ctk.CTkFrame(self.goods_frame, fg_color="#333333")
        filter_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(filter_frame, text="Фільтр:", text_color="#ffd700").pack(side="left", padx=5)
        verified_option = ctk.CTkOptionMenu(filter_frame, values=["Усі", "Перевірені", "Неперевірені"], command=lambda _: self.update_goods_display(verified_option.get(), sort_option.get(), sort_order.get(), search_entry.get()), fg_color="#1c2526", text_color="#ffd700")
        verified_option.pack(side="left", padx=5)
        verified_option.set("Усі")
        ctk.CTkLabel(filter_frame, text="Сортувати за:", text_color="#ffd700").pack(side="left", padx=5)
        sort_option = ctk.CTkOptionMenu(filter_frame, values=["За назвою", "За ціною", "За кількістю"], command=lambda _: self.update_goods_display(verified_option.get(), sort_option.get(), sort_order.get(), search_entry.get()), fg_color="#1c2526", text_color="#ffd700")
        sort_option.pack(side="left", padx=5)
        sort_option.set("За назвою")
        ctk.CTkLabel(filter_frame, text="Порядок:", text_color="#ffd700").pack(side="left", padx=5)
        sort_order = ctk.CTkOptionMenu(filter_frame, values=["Зростання", "Спадання"], command=lambda _: self.update_goods_display(verified_option.get(), sort_option.get(), sort_order.get(), search_entry.get()), fg_color="#1c2526", text_color="#ffd700")
        sort_order.pack(side="left", padx=5)
        sort_order.set("Зростання")
        ctk.CTkLabel(filter_frame, text="Пошук:", text_color="#ffd700").pack(side="left", padx=5)
        search_entry = ctk.CTkEntry(filter_frame, width=200, fg_color="#1c2526", text_color="#ffd700")
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda event: self.update_goods_display(verified_option.get(), sort_option.get(), sort_order.get(), search_entry.get()))

        self.goods_scroll = ctk.CTkScrollableFrame(self.goods_frame, fg_color="#1c2526", height=500)
        self.goods_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_goods_display(verified_option.get(), sort_option.get(), sort_order.get())

        add_frame = ctk.CTkFrame(self.goods_frame, fg_color="#333333")
        add_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(add_frame, text="Назва:", text_color="#ffd700").pack(side="left", padx=5)
        name_entry = ctk.CTkEntry(add_frame, width=150, fg_color="#1c2526", text_color="#ffd700")
        name_entry.pack(side="left", padx=5)
        ctk.CTkLabel(add_frame, text="Опис:", text_color="#ffd700").pack(side="left", padx=5)
        desc_entry = ctk.CTkEntry(add_frame, width=150, fg_color="#1c2526", text_color="#ffd700")
        desc_entry.pack(side="left", padx=5)
        ctk.CTkLabel(add_frame, text="Кількість:", text_color="#ffd700").pack(side="left", padx=5)
        qty_entry = ctk.CTkEntry(add_frame, width=100, fg_color="#1c2526", text_color="#ffd700")
        qty_entry.pack(side="left", padx=5)
        ctk.CTkLabel(add_frame, text="Ціна:", text_color="#ffd700").pack(side="left", padx=5)
        price_entry = ctk.CTkEntry(add_frame, width=100, fg_color="#1c2526", text_color="#ffd700")
        price_entry.pack(side="left", padx=5)
        ctk.CTkButton(add_frame, text="Додати товар", command=lambda: self.add_good(name_entry.get(), desc_entry.get(), qty_entry.get(), price_entry.get()), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="left", padx=10)

        ctk.CTkButton(self.goods_frame, text="Повернутися", command=self.return_to_main, fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(pady=10)

    def update_goods_display(self, filter_status="Усі", sort_by="За назвою", sort_order="Зростання", search_query=""):
        for widget in self.goods_scroll.winfo_children():
            widget.destroy()

        goods = Good.load_goods()
        if filter_status == "Перевірені":
            goods = {k: v for k, v in goods.items() if v["verified"]}
        elif filter_status == "Неперевірені":
            goods = {k: v for k, v in goods.items() if not v["verified"]}
        if search_query:
            goods = {k: v for k, v in goods.items() if search_query.lower() in v["name"].lower() or search_query.lower() in v["description"].lower()}
        reverse = (sort_order == "Спадання")
        if sort_by == "За назвою":
            sorted_goods = dict(sorted(goods.items(), key=lambda x: x[1]["name"].lower(), reverse=reverse))
        elif sort_by == "За ціною":
            sorted_goods = dict(sorted(goods.items(), key=lambda x: x[1]["price"], reverse=reverse))
        elif sort_by == "За кількістю":
            sorted_goods = dict(sorted(goods.items(), key=lambda x: x[1]["quantity"], reverse=reverse))
        else:
            sorted_goods = goods

        for good_id, data in sorted_goods.items():
            good_frame = ctk.CTkFrame(self.goods_scroll, fg_color="#333333", corner_radius=5)
            good_frame.pack(fill="x", pady=5, padx=5)
            info_text = (f"ID: {good_id}\nНазва: {data['name']}\nОпис: {data['description']}\n"
                         f"Кількість: {data['quantity']}\nЦіна: {data['price']} грн\nПеревірено: {data['verified']}")
            ctk.CTkLabel(good_frame, text=info_text, text_color="#ffd700", anchor="w", wraplength=1400, font=("Arial", 12), justify="left").pack(side="left", padx=10)
            if self.current_role == "Адміністратор":
                ctk.CTkButton(good_frame, text="Видалити", command=lambda g_id=good_id: self.remove_good(g_id), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)
                ctk.CTkButton(good_frame, text="Оновити кількість", command=lambda g_id=good_id: self.update_good_quantity(g_id), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)
                ctk.CTkButton(good_frame, text="Оновити ціну", command=lambda g_id=good_id: self.update_good_price(g_id), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)
                ctk.CTkButton(good_frame, text="Перевірити", command=lambda g_id=good_id: self.verify_good(g_id), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)
            elif self.current_role == "Складський працівник":
                ctk.CTkButton(good_frame, text="Оновити кількість", command=lambda g_id=good_id: self.update_good_quantity(g_id), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)
            elif self.current_role == "Менеджер":
                ctk.CTkButton(good_frame, text="Оновити ціну", command=lambda g_id=good_id: self.update_good_price(g_id), fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)

    def add_good(self, name, description, quantity, price):
        try:
            if not name:
                raise ValueError("Назва товару є обов'язковою")
            quantity = int(quantity) if quantity and quantity.isdigit() else 0
            price = float(price) if price and price.replace('.', '').replace('-', '').isdigit() else 0.0
            good = Good(name, description, quantity, price)
            CTkMessagebox(title="Успіх", message=f"Товар '{name}' додано з ID {good.get_id()}.", icon="check")
            self.open_goods_panel()
        except Exception as e:
            CTkMessagebox(title="Помилка", message=str(e), icon="cancel")

    def remove_good(self, good_id):
        if self.current_role == "Адміністратор":
            if CTkMessagebox(title="Підтвердження", message=f"Видалити товар з ID {good_id}?", icon="warning", option_1="Так", option_2="Ні").get() == "Так":
                try:
                    print(f"Спроба видалити товар з ID: {good_id}")
                    goods = Good.load_goods()
                    print(f"Завантажені товари: {goods}")
                    if str(good_id) in goods:
                        del goods[str(good_id)]
                        print(f"Товар з ID {good_id} видалено зі словника. Оновлений словник: {goods}")
                        if not hasattr(Good, '_goods_data_file'):
                            print("Діагностика: атрибут _goods_data_file відсутній у класі Good")
                            print(f"Атрибути класу Good: {dir(Good)}")
                            raise AttributeError("Атрибут _goods_data_file відсутній у класі Good")
                        goods_data_file = Good.get_data_file()
                        print(f"Шлях до goods.json: {goods_data_file}")
                        with open(goods_data_file, "w", encoding="utf-8") as f:
                            json.dump(goods, f, ensure_ascii=False, indent=4)
                        print(f"Дані успішно збережені у {goods_data_file}")
                        CTkMessagebox(title="Успіх", message=f"Товар з ID {good_id} видалено.", icon="check")
                        self.open_goods_panel()
                    else:
                        print(f"Товар з ID {good_id} не знайдено у словнику.")
                        CTkMessagebox(title="Помилка", message="Товар не знайдено.", icon="cancel")
                except Exception as e:
                    print(f"Помилка при видаленні товару: {str(e)}")
                    CTkMessagebox(title="Помилка", message=str(e), icon="cancel")

    def update_good_quantity(self, good_id):
        dialog = ctk.CTkInputDialog(text="Введіть нову кількість:", title="Оновлення кількості")
        dialog.focus()
        dialog.lift()
        dialog.grab_set()
        new_qty = dialog.get_input()
        if new_qty:
            try:
                new_qty = int(new_qty)
                goods = Good.load_goods()
                if str(good_id) not in goods:
                    raise ValueError("Товар не знайдено")
                good_data = goods[str(good_id)]
                current_qty = good_data["quantity"]
                result = Good.update_quantity(good_id, new_qty - current_qty)
                CTkMessagebox(title="Результат", message=result, icon="info")
                self.open_goods_panel()
            except Exception as e:
                CTkMessagebox(title="Помилка", message=str(e), icon="cancel")

    def update_good_price(self, good_id):
        dialog = ctk.CTkInputDialog(text="Введіть нову ціну:", title="Оновлення ціни")
        dialog.focus()
        dialog.lift()
        dialog.grab_set()
        new_price = dialog.get_input()
        if new_price:
            try:
                new_price = float(new_price)
                result = Good.set_price(good_id, new_price)
                CTkMessagebox(title="Результат", message=result, icon="info")
                self.open_goods_panel()
            except Exception as e:
                CTkMessagebox(title="Помилка", message=str(e), icon="cancel")

    def verify_good(self, good_id):
        if self.current_role == "Адміністратор":
            try:
                result = Good.set_verified(good_id, True)
                CTkMessagebox(title="Успіх", message=result, icon="check")
                self.open_goods_panel()
            except Exception as e:
                CTkMessagebox(title="Помилка", message=str(e), icon="cancel")

    def load_orders_from_json(self):
        if not hasattr(self, '_orders_loaded'):
            self._orders_loaded = True
            orders_data = Order.load_orders()
            orders = []
            for order_id, data in orders_data.items():
                order = Order(data["description"])
                order.__dict__["_Order__order_id"] = int(order_id)
                order.__dict__["_Order__status"] = data["status"]
                order.__dict__["_Order__assigned_employee"] = data["assigned_employee"]
                orders.append(order)
                current_counter = getattr(Order, '__order_counter', 0)
                if int(order_id) > current_counter:
                    setattr(Order, '__order_counter', int(order_id))
                print(f"Оновлено лічильник: {getattr(Order, '__order_counter', 0)}")
            print(f"Створено об'єкти замовлень: {[str(order) for order in orders]}")
        else:
            orders = self.orders
        return orders

    def add_order(self, description):
        try:
            description = description.strip()
            print(f"Спроба додати замовлення з описом: '{description}'")
            if not description:
                raise ValueError("Опис замовлення є обов'язковим")
            order = Order(description)
            self.orders.append(order)
            print(f"Додано нове замовлення: {str(order)}")
            self.open_order_panel()
            CTkMessagebox(title="Успіх", message="Замовлення додано.", icon="check")
        except Exception as e:
            print(f"Помилка при додаванні замовлення: {str(e)}")
            CTkMessagebox(title="Помилка", message=str(e), icon="cancel")

    def open_order_panel(self):
        self.title("Складська система - Управління замовленнями")
        if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
            self.main_frame.pack_forget()
        if hasattr(self, 'order_frame') and self.order_frame.winfo_exists():
            for widget in self.order_frame.winfo_children():
                widget.destroy()
        else:
            self.order_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.order_frame.pack(expand=True, fill="both")

        ctk.CTkLabel(self.order_frame, text="Управління замовленнями", font=("Arial", 20), text_color="#ffd700").pack(
            pady=10)

        main_content = ctk.CTkFrame(self.order_frame, fg_color="#2b2b2b")
        main_content.pack(expand=True, fill="both", padx=10, pady=10)

        scroll_frame = ctk.CTkScrollableFrame(main_content, fg_color="#333333")
        scroll_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        main_content.grid_rowconfigure(0, weight=1)
        main_content.grid_columnconfigure(0, weight=1)

        if not self.orders:
            ctk.CTkLabel(scroll_frame, text="Немає замовлень", font=("Arial", 16), text_color="#ffd700").pack(pady=20)
            print("Відображено повідомлення: Немає замовлень")
        else:
            print(f"Відображаємо {len(self.orders)} замовлень у панелі")
            for order in self.orders:
                order_frame = ctk.CTkFrame(scroll_frame, fg_color="#3b3b3b")
                order_frame.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(order_frame, text=str(order), text_color="#ffd700", anchor="w", wraplength=1400,
                             font=("Arial", 12)).pack(side="left", padx=10)
                if self.current_role in ["Менеджер", "Складський працівник"]:
                    ctk.CTkButton(order_frame, text="Оновити статус",
                                  command=lambda o=order: self.update_order_status(o), fg_color="#ffd700",
                                  hover_color="#e6c200", text_color="#1c2526").pack(side="right", padx=5)
                if self.current_role == "Адміністратор":
                    ctk.CTkButton(order_frame, text="Скасувати", command=lambda o=order: self.cancel_order(o),
                                  fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right",
                                                                                                        padx=5)
                    ctk.CTkButton(order_frame, text="Призначити", command=lambda o=order: self.assign_order(o),
                                  fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(side="right",
                                                                                                        padx=5)

        add_frame = ctk.CTkFrame(main_content, fg_color="#333333")
        add_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(add_frame, text="Опис замовлення:", text_color="#ffd700").pack(side="left", padx=5)
        desc_entry = ctk.CTkEntry(add_frame, width=300, fg_color="#1c2526", text_color="#ffd700")
        desc_entry.pack(side="left", padx=5)
        ctk.CTkButton(add_frame, text="Додати замовлення",
                      command=lambda: [self.add_order(desc_entry.get()), self.open_order_panel()], fg_color="#ffd700",
                      hover_color="#e6c200", text_color="#1c2526").pack(side="left", padx=10)

        ctk.CTkButton(self.order_frame, text="Повернутися", command=self.return_to_main, fg_color="#ffd700",
                      hover_color="#e6c200", text_color="#1c2526").pack(pady=10)

    def update_order_status(self, order):
        dialog = ctk.CTkToplevel(self)
        dialog.focus()
        dialog.lift()
        dialog.grab_set()
        dialog.title("Оновлення статусу")
        dialog.geometry("300x150")
        dialog.configure(fg_color="#2b2b2b")
        ctk.CTkOptionMenu(dialog, values=["Очікує", "Відправлено", "Доставлено", "Скасовано"], command=lambda x: self.confirm_update_status(order, x), fg_color="#1c2526", text_color="#ffd700").pack(pady=10)
        ctk.CTkButton(dialog, text="Закрити", command=dialog.destroy, fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(pady=5)

    def confirm_update_status(self, order, status):
        try:
            if self.current_role == "Менеджер":
                worker = next((e for e in Employee.get_all_employees() if isinstance(e, Manager)), Manager("Temp", "Manager", 0))
                result = worker.manager_update_order_status(order, status)
            else:
                worker = next((e for e in Employee.get_all_employees() if isinstance(e, WarehouseWorker)), WarehouseWorker("Temp", "Worker", 0))
                result = worker.update_order_status(order, status)
            print(f"Статус замовлення {order.get_id()} оновлено: {status}")
            CTkMessagebox(title="Результат", message=result, icon="info")
            self.open_order_panel()
        except Exception as e:
            CTkMessagebox(title="Помилка", message=str(e), icon="cancel")

    def assign_order(self, order):
        if self.current_role == "Адміністратор":
            employees = [emp for emp in Employee.get_all_employees() if isinstance(emp, (WarehouseWorker, Manager))]
            if not employees:
                CTkMessagebox(title="Помилка", message="Немає працівників для призначення.", icon="cancel")
                return
            names = [f"{emp.get_name()} {emp.get_surname()}" for emp in employees]
            dialog = ctk.CTkToplevel(self)
            dialog.title("Призначення замовлення")
            dialog.geometry("300x150")
            dialog.configure(fg_color="#2b2b2b")
            ctk.CTkOptionMenu(dialog, values=names, command=lambda x: self.confirm_assign_order(order, employees[names.index(x)]), fg_color="#1c2526", text_color="#ffd700").pack(pady=10)
            ctk.CTkButton(dialog, text="Закрити", command=dialog.destroy, fg_color="#ffd700", hover_color="#e6c200", text_color="#1c2526").pack(pady=5)

    def confirm_assign_order(self, order, employee):
        try:
            result = self.current_admin.assign_order(employee, order)
            order.assign_employee(employee)
            print(f"Замовлення {order.get_id()} призначено працівнику: {employee.id}")
            CTkMessagebox(title="Успіх", message=result, icon="check")
            self.open_order_panel()
        except Exception as e:
            CTkMessagebox(title="Помилка", message=str(e), icon="cancel")

    def cancel_order(self, order):
        if self.current_role == "Адміністратор":
            if CTkMessagebox(title="Підтвердження", message=f"Скасувати замовлення {order.get_id()}?", icon="warning", option_1="Так", option_2="Ні").get() == "Так":
                try:
                    result = self.current_admin.cancel_order(order)
                    Order.remove_order(order.get_id())
                    self.orders.remove(order)
                    print(f"Замовлення {order.get_id()} скасовано")
                    CTkMessagebox(title="Успіх", message=result, icon="check")
                    self.open_order_panel()
                except Exception as e:
                    CTkMessagebox(title="Помилка", message=str(e), icon="cancel")

    def return_to_main(self):
        if hasattr(self, 'employee_frame') and self.employee_frame.winfo_exists():
            self.employee_frame.pack_forget()
        if hasattr(self, 'goods_frame') and self.goods_frame.winfo_exists():
            self.goods_frame.pack_forget()
        if hasattr(self, 'order_frame') and self.order_frame.winfo_exists():
            self.order_frame.pack_forget()
        self.open_main_window(self.current_role)


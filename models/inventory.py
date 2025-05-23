import json
import os

class Order:
    __order_counter = 0
    _orders_data_file = os.path.join(os.path.dirname(__file__), "orders.json")

    @classmethod
    def get_orders_data_file(cls):
        return cls._orders_data_file

    def __init__(self, description):
        Order.__order_counter += 1
        self.__order_id = Order.__order_counter
        self.__description = description
        self.__status = "Очікує"
        self.__assigned_employee = None
        self.save_to_json()

    def get_id(self):
        return self.__order_id

    def get_description(self):
        return self.__description

    def get_status(self):
        return self.__status

    def get_assigned_employee(self):
        return self.__assigned_employee

    def set_status(self, new_status):
        allowed_statuses = ["Очікує", "Відправлено", "Доставлено", "Скасовано"]
        if new_status in allowed_statuses:
            self.__status = new_status
            self.save_to_json()
            return True
        return False

    def assign_employee(self, employee):
        self.__assigned_employee = employee.id if employee else None
        self.save_to_json()
        return f"Замовлення призначено працівнику: {employee.get_name()} {employee.get_surname()}"

    def save_to_json(self):
        orders = Order.load_orders()
        orders[str(self.__order_id)] = {
            "description": self.__description,
            "status": self.__status,
            "assigned_employee": self.__assigned_employee
        }
        with open(Order._orders_data_file, "w", encoding="utf-8") as f:
            json.dump(orders, f, ensure_ascii=False, indent=4)

    @classmethod
    def load_orders(cls):
        try:
            if os.path.exists(cls._orders_data_file):
                with open(cls._orders_data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        print(f"Помилка: orders.json містить {type(data)}, очікується словник. Повертаємо порожній словник.")
                        return {}
                    print(f"Завантажено замовлення з orders.json: {data}")
                    return data
            else:
                print(f"Файл {cls._orders_data_file} не існує. Створюємо порожній файл.")
                with open(cls._orders_data_file, "w", encoding="utf-8") as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
                return {}
        except json.JSONDecodeError as e:
            print(f"Помилка декодування JSON у orders.json: {e}. Повертаємо порожній словник.")
            return {}
        except Exception as e:
            print(f"Невідома помилка при завантаженні orders.json: {e}. Повертаємо порожній словник.")
            return {}

    @classmethod
    def remove_order(cls, order_id):
        orders = cls.load_orders()
        if str(order_id) in orders:
            del orders[str(order_id)]
            with open(cls._orders_data_file, "w", encoding="utf-8") as f:
                json.dump(orders, f, ensure_ascii=False, indent=4)
            print(f"Замовлення з ID {order_id} видалено з orders.json")
            return f"Замовлення з ID {order_id} видалено."
        return "Замовлення не знайдено."

    def __str__(self):
        employee_info = (f", Призначено: {self.__assigned_employee}" if self.__assigned_employee else "")
        return f"Замовлення {self.__order_id}: {self.__description} - статус: {self.__status}{employee_info}"

class Good:
    __good_counter = 0
    _goods_data_file = os.path.join(os.path.dirname(__file__), "goods.json")

    @classmethod
    def get_data_file(cls):
        return cls._goods_data_file

    def __init__(self, name, description="", quantity=0, price=0.0, verified=False):
        Good.__good_counter += 1
        self.__good_id = Good.__good_counter
        self.__name = name
        self.__description = description
        self.__quantity = quantity
        self.__price = price
        self.__verified = verified
        self.save_to_json()

    def get_id(self):
        return self.__good_id

    def get_name(self):
        return self.__name

    def get_description(self):
        return self.__description

    def get_quantity(self):
        return self.__quantity

    def get_price(self):
        return self.__price

    def is_verified(self):
        return self.__verified

    def set_verified(self, verified: bool):
        self.__verified = verified
        self.save_to_json()
        return f"Статус перевірки оновлено: {self.__verified}"

    def update_quantity(self, amount):
        if self.__quantity + amount < 0:
            return "Неможливо зменшити кількість нижче 0."
        self.__quantity += amount
        self.save_to_json()
        return f"Кількість оновлено. Нова кількість: {self.__quantity}"

    def set_price(self, new_price):
        if new_price >= 0:
            self.__price = new_price
            self.save_to_json()
            return f"Ціна оновлена. Нова ціна: {new_price}"
        return "Ціна не може бути від'ємною."

    def save_to_json(self):
        goods = Good.load_goods()
        goods[str(self.__good_id)] = {
            "name": self.__name,
            "description": self.__description,
            "quantity": self.__quantity,
            "price": self.__price,
            "verified": self.__verified
        }
        with open(Good._goods_data_file, "w", encoding="utf-8") as f:
            json.dump(goods, f, ensure_ascii=False, indent=4)

    @classmethod
    def load_goods(cls):
        try:
            if os.path.exists(cls._goods_data_file):
                with open(cls._goods_data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        print(f"Помилка: goods.json містить {type(data)}, очікується словник. Повертаємо порожній словник.")
                        return {}
                    return data
            else:
                print(f"Файл {cls._goods_data_file} не існує. Повертаємо порожній словник.")
                return {}
        except json.JSONDecodeError as e:
            print(f"Помилка декодування JSON у goods.json: {e}. Повертаємо порожній словник.")
            return {}
        except Exception as e:
            print(f"Невідома помилка при завантаженні goods.json: {e}. Повертаємо порожній словник.")
            return {}

    @classmethod
    def update_quantity(cls, good_id, amount):
        goods = cls.load_goods()
        if str(good_id) not in goods:
            raise ValueError("Товар не знайдено")
        good_data = goods[str(good_id)]
        current_qty = good_data["quantity"]
        new_qty = current_qty + amount
        if new_qty < 0:
            return "Неможливо зменшити кількість нижче 0."
        good_data["quantity"] = new_qty
        goods[str(good_id)] = good_data
        with open(cls._goods_data_file, "w", encoding="utf-8") as f:
            json.dump(goods, f, ensure_ascii=False, indent=4)
        return f"Кількість оновлено. Нова кількість: {new_qty}"

    @classmethod
    def set_price(cls, good_id, new_price):
        goods = cls.load_goods()
        if str(good_id) not in goods:
            raise ValueError("Товар не знайдено")
        if new_price < 0:
            return "Ціна не може бути від'ємною."
        good_data = goods[str(good_id)]
        good_data["price"] = new_price
        goods[str(good_id)] = good_data
        with open(cls._goods_data_file, "w", encoding="utf-8") as f:
            json.dump(goods, f, ensure_ascii=False, indent=4)
        return f"Ціна оновлена. Нова ціна: {new_price}"

    @classmethod
    def set_verified(cls, good_id, verified):
        goods = cls.load_goods()
        if str(good_id) not in goods:
            raise ValueError("Товар не знайдено")
        good_data = goods[str(good_id)]
        good_data["verified"] = verified
        goods[str(good_id)] = good_data
        with open(cls._goods_data_file, "w", encoding="utf-8") as f:
            json.dump(goods, f, ensure_ascii=False, indent=4)
        return f"Статус перевірки оновлено: {verified}"

    def __str__(self):
        return (f"Товар: {self.__name}, ID: {self.__good_id}, Опис: {self.__description}, "
                f"Кількість: {self.__quantity}, Ціна: {self.__price}, Перевірено: {self.__verified}")
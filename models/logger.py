import os
import logging

log_file = os.path.join(os.path.dirname(__file__), "..", "logins.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%d.%m.%Y %H:%M:%S', encoding='utf-8')

def log_login(username, role):
    logging.info(f"Користувач: {username}, роль: {role} увійшов у систему.")

def log_action(action: str):
    logging.info(action)
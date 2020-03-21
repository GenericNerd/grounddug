# GroundDug Logger Utility

from datetime import datetime
from colorama import Fore

def info(data):
    print(f"\n{Fore.CYAN} INFO - {datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')}{Fore.WHITE} | {data}")

def error(data):
    print(f"\n{Fore.RED} ERROR - {datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')}{Fore.WHITE} | {data}")

def work(data):
    print(f"\n{Fore.GREEN} WORK - {datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')}{Fore.WHITE} | {data}")